from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from flask_mail import Mail, Message
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///congresso.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações do Doity (substitua pelos seus dados reais)
app.config['DOITY_EVENT_ID'] = 'seu_event_id_do_doity'
app.config['DOITY_API_KEY'] = 'sua_api_key_do_doity'
app.config['DOITY_WEBHOOK_SECRET'] = 'seu_webhook_secret_do_doity'
app.config['DOITY_BASE_URL'] = 'https://api.doity.com.br'

# Configuração do email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seu_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'sua_senha_app'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Modelos do banco de dados
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    genero = db.Column(db.String(20))
    profissao = db.Column(db.String(50))
    cro = db.Column(db.String(20))
    instituicao = db.Column(db.String(100))
    especialidade = db.Column(db.String(50))
    endereco = db.Column(db.Text)
    senha_hash = db.Column(db.String(200))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

class Inscricao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo_inscricao = db.Column(db.String(20), nullable=False)  # early, regular, premium
    valor = db.Column(db.Float, nullable=False)
    status_pagamento = db.Column(db.String(20), default='pendente')  # pendente, aprovado, cancelado
    codigo_pagamento = db.Column(db.String(50), unique=True)
    data_inscricao = db.Column(db.DateTime, default=datetime.utcnow)
    data_pagamento = db.Column(db.DateTime)
    usuario = db.relationship('Usuario', backref='inscricoes')

class Palestrante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    biografia = db.Column(db.Text)
    credenciais = db.Column(db.Text)
    foto = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    website = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)

class Palestra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    palestrante_id = db.Column(db.Integer, db.ForeignKey('palestrante.id'), nullable=False)
    dia = db.Column(db.Integer, nullable=False)  # 1 ou 2
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    tipo = db.Column(db.String(20), default='palestra')  # palestra, workshop, mesa_redonda
    sala = db.Column(db.String(50))
    palestrante = db.relationship('Palestrante', backref='palestras')

class Configuracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descricao = db.Column(db.String(200))

# Rotas principais
@app.route('/')
def index():
    palestrantes = Palestrante.query.filter_by(ativo=True).limit(4).all()
    inscricoes_count = Inscricao.query.filter_by(status_pagamento='aprovado').count()
    return render_template('index.html', palestrantes=palestrantes, inscricoes_count=inscricoes_count)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/palestrantes')
def palestrantes():
    especialidade = request.args.get('especialidade', 'all')
    if especialidade == 'all':
        palestrantes = Palestrante.query.filter_by(ativo=True).all()
    else:
        palestrantes = Palestrante.query.filter_by(ativo=True, especialidade=especialidade).all()
    
    especialidades = db.session.query(Palestrante.especialidade).distinct().all()
    especialidades = [esp[0] for esp in especialidades]
    
    return render_template('palestrantes.html', palestrantes=palestrantes, especialidades=especialidades, filtro_atual=especialidade)

@app.route('/programacao')
def programacao():
    dia = request.args.get('dia', '1')
    palestras_dia1 = Palestra.query.filter_by(dia=1).order_by(Palestra.horario_inicio).all()
    palestras_dia2 = Palestra.query.filter_by(dia=2).order_by(Palestra.horario_inicio).all()
    
    return render_template('programacao.html', 
                         palestras_dia1=palestras_dia1, 
                         palestras_dia2=palestras_dia2, 
                         dia_atual=dia)

@app.route('/inscricao', methods=['GET', 'POST'])
def inscricao():
    if request.method == 'POST':
        # Processar dados do formulário
        dados = request.get_json()
        
        # Verificar se usuário já existe
        usuario_existente = Usuario.query.filter_by(email=dados['email']).first()
        if usuario_existente:
            return jsonify({'success': False, 'message': 'Email já cadastrado'})
        
        # Criar novo usuário
        novo_usuario = Usuario(
            nome=dados['nome'],
            email=dados['email'],
            cpf=dados['cpf'],
            telefone=dados['telefone'],
            data_nascimento=datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date() if dados['data_nascimento'] else None,
            genero=dados['genero'],
            profissao=dados['profissao'],
            cro=dados['cro'],
            instituicao=dados['instituicao'],
            especialidade=dados['especialidade'],
            endereco=dados['endereco']
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        # Criar inscrição
        valores = {
            'early': 297.00,
            'regular': 397.00,
            'premium': 597.00
        }
        
        nova_inscricao = Inscricao(
            usuario_id=novo_usuario.id,
            tipo_inscricao=dados['tipo_inscricao'],
            valor=valores[dados['tipo_inscricao']],
            codigo_pagamento=str(uuid.uuid4())
        )
        
        db.session.add(nova_inscricao)
        db.session.commit()
        
        # Enviar email de confirmação
        try:
            enviar_email_confirmacao(novo_usuario, nova_inscricao)
        except:
            pass  # Não falhar se email não enviar
        
        return jsonify({
            'success': True, 
            'message': 'Inscrição realizada com sucesso!',
            'codigo_pagamento': nova_inscricao.codigo_pagamento,
            'doity_url': gerar_url_doity(nova_inscricao)
        })
    
    return render_template('inscricao.html')

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        assunto = request.form['assunto']
        mensagem = request.form['mensagem']
        
        # Enviar email de contato
        try:
            msg = Message(
                f'Contato JOP 2025: {assunto}',
                sender=email,
                recipients=['contato@jop2025.com.br']
            )
            msg.body = f"""
            Nome: {nome}
            Email: {email}
            Assunto: {assunto}
            
            Mensagem:
            {mensagem}
            """
            mail.send(msg)
            flash('Mensagem enviada com sucesso!', 'success')
        except:
            flash('Erro ao enviar mensagem. Tente novamente.', 'error')
        
        return redirect(url_for('contato'))
    
    return render_template('contato.html')

# Rotas da API
@app.route('/api/palestrantes')
def api_palestrantes():
    palestrantes = Palestrante.query.filter_by(ativo=True).all()
    return jsonify([{
        'id': p.id,
        'nome': p.nome,
        'especialidade': p.especialidade,
        'biografia': p.biografia,
        'foto': p.foto
    } for p in palestrantes])

@app.route('/api/inscricoes/stats')
def api_inscricoes_stats():
    total = Inscricao.query.count()
    aprovadas = Inscricao.query.filter_by(status_pagamento='aprovado').count()
    pendentes = Inscricao.query.filter_by(status_pagamento='pendente').count()
    
    return jsonify({
        'total': total,
        'aprovadas': aprovadas,
        'pendentes': pendentes
    })

# Rotas administrativas
@app.route('/admin')
def admin():
    if 'admin_logado' not in session:
        return redirect(url_for('admin_login'))
    
    inscricoes = Inscricao.query.order_by(Inscricao.data_inscricao.desc()).limit(10).all()
    stats = {
        'total_inscricoes': Inscricao.query.count(),
        'inscricoes_aprovadas': Inscricao.query.filter_by(status_pagamento='aprovado').count(),
        'total_palestrantes': Palestrante.query.count(),
        'total_palestras': Palestra.query.count()
    }
    
    return render_template('admin/dashboard.html', inscricoes=inscricoes, stats=stats)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        # Aqui você implementaria a autenticação do admin
        if email == 'admin@jop2025.com.br' and senha == 'admin123':
            session['admin_logado'] = True
            return redirect(url_for('admin'))
        else:
            flash('Credenciais inválidas', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logado', None)
    return redirect(url_for('admin_login'))

# Funções auxiliares
def enviar_email_confirmacao(usuario, inscricao):
    msg = Message(
        'Confirmação de Inscrição - JOP 2025',
        sender='noreply@jop2025.com.br',
        recipients=[usuario.email]
    )
    
    msg.html = render_template('emails/confirmacao_inscricao.html', 
                             usuario=usuario, 
                             inscricao=inscricao)
    
    mail.send(msg)

def popular_banco_dados():
    """Função para popular o banco com dados iniciais"""
    
    # Adicionar palestrantes
    palestrantes_data = [
        {
            'nome': 'Dra. Priscila Prosini',
            'especialidade': 'Ortodontia',
            'biografia': 'Cirurgiã-dentista especialista em Ortodontia e Ortopedia Facial com mais de 15 anos de experiência.',
            'credenciais': 'Mestrado em Ortodontia - USP\nEspecialista em Ortodontia - CRO',
            'foto': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300&h=300&fit=crop&crop=face'
        },
        {
            'nome': 'Dr. Carlos Mendes',
            'especialidade': 'Implantodontia',
            'biografia': 'Especialista em Implantodontia com mais de 20 anos de experiência clínica.',
            'credenciais': 'Doutorado em Implantodontia - UNICAMP\nEspecialista em Implantodontia - CRO',
            'foto': 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=300&h=300&fit=crop&crop=face'
        },
        {
            'nome': 'Dra. Ana Silva',
            'especialidade': 'Endodontia',
            'biografia': 'Endodontista com especialização em Microendodontia e Cirurgia Endodôntica.',
            'credenciais': 'Mestrado em Endodontia - UFMG\nEspecialista em Endodontia - CRO',
            'foto': 'https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=300&h=300&fit=crop&crop=face'
        },
        {
            'nome': 'Dr. Roberto Santos',
            'especialidade': 'Periodontia',
            'biografia': 'Periodontista com mais de 18 anos de experiência em cirurgia periodontal e implantes.',
            'credenciais': 'Doutorado em Periodontia - USP\nEspecialista em Periodontia - CRO',
            'foto': 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300&h=300&fit=crop&crop=face'
        }
    ]
    
    for palestrante_data in palestrantes_data:
        palestrante = Palestrante(**palestrante_data)
        db.session.add(palestrante)
    
    db.session.commit()
    
    # Adicionar palestras
    palestras_data = [
        {
            'titulo': 'Inovações em Ortodontia',
            'descricao': 'Abordagem completa das inovações tecnológicas em ortodontia.',
            'palestrante_id': 1,
            'dia': 1,
            'horario_inicio': datetime.strptime('09:30', '%H:%M').time(),
            'horario_fim': datetime.strptime('11:00', '%H:%M').time(),
            'tipo': 'palestra'
        },
        {
            'titulo': 'Implantes Dentários: Técnicas Modernas',
            'descricao': 'Técnicas avançadas em implantodontia e cirurgia guiada.',
            'palestrante_id': 2,
            'dia': 1,
            'horario_inicio': datetime.strptime('11:45', '%H:%M').time(),
            'horario_fim': datetime.strptime('13:15', '%H:%M').time(),
            'tipo': 'palestra'
        },
        {
            'titulo': 'Endodontia Contemporânea',
            'descricao': 'Técnicas modernas em endodontia e retratamento.',
            'palestrante_id': 3,
            'dia': 1,
            'horario_inicio': datetime.strptime('14:30', '%H:%M').time(),
            'horario_fim': datetime.strptime('16:00', '%H:%M').time(),
            'tipo': 'palestra'
        },
        {
            'titulo': 'Periodontia e Saúde Gengival',
            'descricao': 'Técnicas modernas em periodontia e cirurgia plástica periodontal.',
            'palestrante_id': 4,
            'dia': 2,
            'horario_inicio': datetime.strptime('09:00', '%H:%M').time(),
            'horario_fim': datetime.strptime('10:30', '%H:%M').time(),
            'tipo': 'palestra'
        }
    ]
    
    for palestra_data in palestras_data:
        palestra = Palestra(**palestra_data)
        db.session.add(palestra)
    
    db.session.commit()

# Funções para integração com Doity
def gerar_url_doity(inscricao):
    """Gera URL de pagamento do Doity"""
    try:
        # Aqui você implementaria a integração real com a API do Doity
        # Por enquanto, retornamos uma URL de exemplo
        return f"https://doity.com.br/eventos/jop-2025/inscricao/{inscricao.codigo_pagamento}"
    except Exception as e:
        print(f"Erro ao gerar URL do Doity: {e}")
        return None

@app.route('/webhook/doity', methods=['POST'])
def webhook_doity():
    """Webhook para receber notificações do Doity"""
    try:
        # Verificar assinatura do webhook (implementar conforme documentação do Doity)
        # dados = request.get_json()
        
        # Processar notificação de pagamento
        # if dados['status'] == 'paid':
        #     codigo = dados['codigo_pagamento']
        #     inscricao = Inscricao.query.filter_by(codigo_pagamento=codigo).first()
        #     if inscricao:
        #         inscricao.status_pagamento = 'aprovado'
        #         inscricao.data_pagamento = datetime.utcnow()
        #         db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/doity/evento')
def api_doity_evento():
    """API para obter informações do evento no Doity"""
    try:
        # Aqui você implementaria a chamada real para a API do Doity
        evento_info = {
            'id': app.config['DOITY_EVENT_ID'],
            'nome': 'Jornada Odontológica de Pernambuco 2025',
            'data_inicio': '2025-08-30',
            'data_fim': '2025-08-31',
            'local': 'Centro de Convenções de Pernambuco',
            'capacidade': 500,
            'inscritos': Inscricao.query.filter_by(status_pagamento='aprovado').count()
        }
        return jsonify(evento_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Descomente a linha abaixo para popular o banco com dados iniciais
        # popular_banco_dados()
    
    app.run(debug=True) 