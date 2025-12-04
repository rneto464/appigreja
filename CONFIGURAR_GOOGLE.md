# 🔐 Configuração do Google Calendar API

Este guia explica como configurar as credenciais do Google Calendar para funcionar na Vercel.

## 📋 Credenciais Fornecidas

Você já possui as credenciais do Google OAuth. Configure-as como variáveis de ambiente na Vercel (veja seção abaixo).

## 🚀 Configuração Local

### 1. Criar arquivo credentials.json localmente

Execute o script:
```bash
python criar_credentials.py
```

Ou crie manualmente o arquivo `credentials.json` na raiz do projeto:
```json
{
  "web": {
    "client_id": "SEU_CLIENT_ID_AQUI",
    "project_id": "escala-coroinhas-app",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "SEU_CLIENT_SECRET_AQUI",
    "redirect_uris": [
      "http://localhost:5000/oauth2callback",
      "http://localhost:3000/oauth2callback"
    ]
  }
}
```

⚠️ **Substitua** `SEU_CLIENT_ID_AQUI` e `SEU_CLIENT_SECRET_AQUI` pelas suas credenciais reais.

⚠️ **IMPORTANTE**: O arquivo `credentials.json` está no `.gitignore` e não será commitado no Git.

## ☁️ Configuração na Vercel

### Opção 1: Variáveis de Ambiente (Recomendado)

1. Acesse a dashboard da Vercel: [vercel.com/dashboard](https://vercel.com/dashboard)
2. Selecione seu projeto
3. Vá em **Settings** → **Environment Variables**
4. Adicione as seguintes variáveis:

```
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
GOOGLE_PROJECT_ID=escala-coroinhas-app
PRODUCTION_URL=https://seu-app.vercel.app
```

⚠️ **Substitua** `seu_client_id_aqui` e `seu_client_secret_aqui` pelas suas credenciais reais.

5. Marque todas as opções: **Production**, **Preview**, **Development**
6. Clique em **Save**

### Opção 2: Adicionar Redirect URI no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Selecione o projeto: **escala-coroinhas-app**
3. Vá em **APIs & Services** → **Credentials**
4. Clique no OAuth 2.0 Client ID
5. Em **Authorized redirect URIs**, adicione:
   - `https://seu-app.vercel.app/oauth2callback`
   - `https://seu-app-git-main.vercel.app/oauth2callback` (para preview)
6. Clique em **Save**

## 🔄 Como Funciona

O código foi atualizado para:
1. **Localmente**: Usa o arquivo `credentials.json` se existir
2. **Na Vercel**: Cria automaticamente `credentials.json` a partir das variáveis de ambiente
3. **Fallback**: Se não encontrar credenciais, a funcionalidade do Google Calendar será desabilitada (mas a app continua funcionando)

## ⚠️ Limitações na Vercel

A autenticação OAuth com `run_local_server()` não funciona em ambiente serverless. Para usar o Google Calendar na Vercel, você precisará:

1. **Autenticar manualmente** uma vez e salvar o `token.json`
2. **Ou usar Service Account** (mais complexo, mas funciona melhor em serverless)
3. **Ou fazer autenticação via web interface** antes de usar

## 📝 Notas Importantes

- O `token.json` também não será commitado (está no `.gitignore`)
- Na Vercel, o sistema de arquivos é efêmero, então o `token.json` será perdido após inatividade
- Para produção, considere usar **Google Service Account** ou armazenar tokens em banco de dados externo

## 🔗 Links Úteis

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Calendar API Docs](https://developers.google.com/calendar/api)
- [OAuth 2.0 para Serverless](https://developers.google.com/identity/protocols/oauth2/web-server)

