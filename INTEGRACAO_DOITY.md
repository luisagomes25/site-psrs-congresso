# Integração com Doity - JOP 2025

## Visão Geral

Este documento explica como integrar o site da Jornada Odontológica de Pernambuco 2025 com a plataforma Doity para gerenciamento de inscrições e pagamentos.

## Configuração Inicial

### 1. Criar Evento no Doity

1. Acesse [doity.com.br](https://doity.com.br)
2. Crie uma conta ou faça login
3. Crie um novo evento chamado "Jornada Odontológica de Pernambuco 2025"
4. Configure as datas: 30 e 31 de Agosto de 2025
5. Configure o local: Centro de Convenções de Pernambuco
6. Configure os tipos de ingresso:
   - Early Bird: R$ 297,00
   - Regular: R$ 397,00
   - Premium: R$ 597,00

### 2. Obter Credenciais da API

1. No painel do Doity, vá em "Configurações" > "API"
2. Gere uma API Key
3. Anote o Event ID
4. Configure o Webhook Secret

### 3. Configurar o Site

Edite o arquivo `app.py` e substitua as configurações:

```python
# Configurações do Doity (substitua pelos seus dados reais)
app.config['DOITY_EVENT_ID'] = 'seu_event_id_do_doity'
app.config['DOITY_API_KEY'] = 'sua_api_key_do_doity'
app.config['DOITY_WEBHOOK_SECRET'] = 'seu_webhook_secret_do_doity'
app.config['DOITY_BASE_URL'] = 'https://api.doity.com.br'
```

## Funcionalidades Implementadas

### 1. Redirecionamento para Pagamento

Quando um usuário se inscreve no site, ele é redirecionado automaticamente para a página de pagamento do Doity.

### 2. Webhook para Notificações

O site recebe notificações do Doity quando um pagamento é confirmado, atualizando automaticamente o status da inscrição.

### 3. API para Informações do Evento

Endpoint `/api/doity/evento` retorna informações atualizadas sobre o evento.

## Como Funciona

### Fluxo de Inscrição

1. Usuário preenche o formulário de inscrição no site
2. Dados são salvos no banco de dados local
3. Sistema gera uma URL única do Doity
4. Usuário é redirecionado para a página de pagamento
5. Após o pagamento, Doity envia notificação via webhook
6. Sistema atualiza o status da inscrição

### Webhook

O webhook está configurado em `/webhook/doity` e recebe notificações do Doity sobre:
- Pagamentos aprovados
- Pagamentos cancelados
- Alterações no status do evento

## Configuração do Webhook no Doity

1. No painel do Doity, vá em "Configurações" > "Webhooks"
2. Adicione um novo webhook:
   - URL: `https://seudominio.com/webhook/doity`
   - Eventos: `payment.paid`, `payment.cancelled`
   - Método: POST

## Personalização

### Modificar Tipos de Ingresso

Para alterar os tipos de ingresso, edite a função `gerar_url_doity()` no arquivo `app.py`:

```python
def gerar_url_doity(inscricao):
    # Mapear tipos de inscrição para IDs do Doity
    tipo_mapping = {
        'early': 'doity_ticket_id_early',
        'regular': 'doity_ticket_id_regular',
        'premium': 'doity_ticket_id_premium'
    }
    
    ticket_id = tipo_mapping.get(inscricao.tipo_inscricao)
    return f"https://doity.com.br/eventos/jop-2025/inscricao/{ticket_id}?code={inscricao.codigo_pagamento}"
```

### Adicionar Campos Personalizados

Para enviar dados adicionais para o Doity, modifique a função de inscrição:

```python
# No formulário de inscrição
dados_extras = {
    'profissao': dados['profissao'],
    'cro': dados['cro'],
    'especialidade': dados['especialidade']
}

# Enviar para Doity via API
```

## Troubleshooting

### Problemas Comuns

1. **Webhook não recebe notificações**
   - Verifique se a URL está correta
   - Confirme se o domínio é HTTPS
   - Teste a URL com um serviço como webhook.site

2. **Erro na API do Doity**
   - Verifique se a API Key está correta
   - Confirme se o Event ID existe
   - Verifique os logs do servidor

3. **Redirecionamento não funciona**
   - Teste a URL do Doity manualmente
   - Verifique se o evento está ativo
   - Confirme se os tipos de ingresso estão configurados

### Logs

Para debug, adicione logs na função `gerar_url_doity()`:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gerar_url_doity(inscricao):
    logger.info(f"Gerando URL do Doity para inscrição {inscricao.id}")
    # ... resto do código
```

## Segurança

### Recomendações

1. **Validação de Webhook**
   - Sempre valide a assinatura do webhook
   - Use HTTPS para todas as comunicações
   - Implemente rate limiting

2. **Dados Sensíveis**
   - Nunca exponha API Keys no frontend
   - Use variáveis de ambiente para configurações
   - Implemente autenticação adequada

3. **Backup**
   - Mantenha backup dos dados de inscrição
   - Implemente sincronização com Doity
   - Monitore falhas de comunicação

## Suporte

Para dúvidas sobre a integração:

1. Consulte a [documentação oficial do Doity](https://doity.com.br/api)
2. Entre em contato com o suporte do Doity
3. Verifique os logs do sistema

## Próximos Passos

1. Implementar sincronização bidirecional
2. Adicionar relatórios integrados
3. Implementar sistema de cupons de desconto
4. Adicionar integração com certificados 