# Jornada Odontológica de Pernambuco 2025

Site oficial da Jornada Odontológica de Pernambuco 2025, desenvolvido em Flask com integração à plataforma Doity para gerenciamento de inscrições.

## 🚀 Funcionalidades

- **Design Moderno e Responsivo**: Interface elegante com paleta de cores roxa
- **Sistema de Inscrições**: Formulário completo com 4 passos
- **Integração Doity**: Redirecionamento automático para pagamento
- **Gestão de Palestrantes**: Perfis detalhados com filtros por especialidade
- **Programação Completa**: Agenda detalhada dos dois dias do evento
- **Sistema de Contato**: Formulário com FAQ integrado
- **Painel Administrativo**: Gestão de inscrições e estatísticas
- **API REST**: Endpoints para integração externa

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask 3.0.0
- **Banco de Dados**: SQLAlchemy + SQLite
- **Frontend**: Bootstrap 5.3.3 + Font Awesome
- **Email**: Flask-Mail
- **Integração**: API Doity

## 📋 Pré-requisitos

- Python 3.12 (ou 3.11)
- pip
- Conta no Doity (para integração de pagamentos)

## 🔧 Instalação

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd congresso
   ```

2. **Crie um ambiente virtual**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=sua_chave_secreta_aqui
   DATABASE_URL=sqlite:///congresso.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=seu_email@gmail.com
   MAIL_PASSWORD=sua_senha_de_app
   DOITY_EVENT_ID=seu_event_id_do_doity
   DOITY_API_KEY=sua_api_key_do_doity
   DOITY_WEBHOOK_SECRET=seu_webhook_secret_do_doity
   ```

5. **Execute o projeto**
   ```bash
   python app.py
   ```

6. **Acesse o site**
   Abra http://localhost:5000 no seu navegador

## 📁 Estrutura do Projeto

```
congresso/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Página inicial
│   ├── inscricao.html    # Formulário de inscrição
│   ├── palestrantes.html # Lista de palestrantes
│   ├── programacao.html  # Programação do evento
│   ├── sobre.html        # Sobre o evento
│   └── contato.html      # Página de contato
├── static/               # Arquivos estáticos
│   ├── css/             # Estilos CSS
│   ├── js/              # JavaScript
│   └── images/          # Imagens
├── venv/                # Ambiente virtual
├── congresso.db         # Banco de dados SQLite
├── INTEGRACAO_DOITY.md  # Documentação da integração
└── README.md           # Este arquivo
```

## 🎨 Design e UX

### Paleta de Cores
- **Primária**: Roxo (#6b46c1)
- **Secundária**: Cinza claro (#f8f9fa)
- **Destaque**: Laranja (#ff6b35)
- **Texto Escuro**: (#2c3e50)
- **Texto Claro**: (#6c757d)

### Características
- Design responsivo para todos os dispositivos
- Animações suaves e transições
- Tipografia moderna (Poppins)
- Ícones Font Awesome
- Contagem regressiva para o evento

## 🔗 Integração com Doity

O site está integrado com a plataforma Doity para gerenciamento de inscrições e pagamentos. Veja o arquivo `INTEGRACAO_DOITY.md` para detalhes completos.

### Funcionalidades da Integração:
- Redirecionamento automático para pagamento
- Webhook para notificações de pagamento
- API para sincronização de dados
- Gestão de tipos de ingresso

## 📊 Funcionalidades Administrativas

### Painel Admin
- Acesso: `/admin`
- Credenciais padrão:
  - Email: admin@jop2025.com.br
  - Senha: admin123

### Funcionalidades:
- Visualização de inscrições
- Estatísticas do evento
- Gestão de palestrantes
- Relatórios de pagamento

## 🚀 Deploy

### Para Produção

1. **Configure um servidor web** (Nginx/Apache)
2. **Use WSGI** (Gunicorn/uWSGI)
3. **Configure HTTPS**
4. **Configure o banco de dados** (PostgreSQL/MySQL)
5. **Configure as variáveis de ambiente**

### Exemplo com Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🔧 Configurações Avançadas

### Banco de Dados
Para usar PostgreSQL ou MySQL, altere a configuração:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
```

### Email
Configure o servidor de email no arquivo `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_de_app
```

### Doity
Configure as credenciais do Doity:
```env
DOITY_EVENT_ID=seu_event_id
DOITY_API_KEY=sua_api_key
DOITY_WEBHOOK_SECRET=seu_webhook_secret
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de importação Flask**
   - Verifique se está usando Python 3.12
   - Reinstale as dependências: `pip install -r requirements.txt`

2. **Erro de banco de dados**
   - Delete o arquivo `congresso.db`
   - Execute `python app.py` novamente

3. **Imagens não carregam**
   - Verifique se a pasta `static/images` existe
   - Use URLs absolutas para imagens externas

4. **Email não envia**
   - Configure corretamente as credenciais SMTP
   - Use senha de app do Gmail

## 📈 Próximas Funcionalidades

- [ ] Sistema de cupons de desconto
- [ ] Certificados digitais
- [ ] App mobile
- [ ] Sistema de avaliação
- [ ] Chat em tempo real
- [ ] Streaming das palestras

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Suporte

Para suporte técnico:
- Email: contato@jop2025.com.br
- WhatsApp: (81) 99999-9999

## 🙏 Agradecimentos

- Equipe de desenvolvimento
- Palestrantes confirmados
- Parceiros e apoiadores
- Comunidade odontológica de Pernambuco 