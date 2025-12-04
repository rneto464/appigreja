# 🚀 Deploy na Vercel - Guia Rápido

## 📦 Arquivos Criados

A aplicação está pronta para deploy na Vercel com os seguintes arquivos:

- ✅ `vercel.json` - Configuração da Vercel
- ✅ `api/index.py` - Entry point para serverless functions
- ✅ `requirements-vercel.txt` - Dependências otimizadas
- ✅ `.vercelignore` - Arquivos ignorados no deploy
- ✅ `.gitignore` - Arquivos ignorados no Git

## 🎯 Deploy Rápido

### Opção 1: Via Dashboard da Vercel (Recomendado)

1. Acesse [vercel.com](https://vercel.com) e faça login
2. Clique em **"Add New Project"**
3. Conecte seu repositório Git (GitHub/GitLab/Bitbucket)
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (deixe vazio)
   - **Output Directory**: (deixe vazio)
5. Adicione variável de ambiente:
   - **Name**: `SECRET_KEY`
   - **Value**: Gere uma chave: `python -c "import secrets; print(secrets.token_hex(32))"`
6. Clique em **"Deploy"**

### Opção 2: Via CLI

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Fazer login
vercel login

# 3. Deploy
vercel --prod
```

## ⚙️ Configurações Importantes

### Variáveis de Ambiente (Obrigatórias)

Configure na dashboard da Vercel:

**1. SECRET_KEY (obrigatória):**
```
SECRET_KEY=sua_chave_secreta_aqui
```

**Gerar chave secreta:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Banco de Dados ⚠️

**IMPORTANTE**: A Vercel usa sistema de arquivos **efêmero**. O SQLite será resetado após inatividade ou novo deploy.

**Soluções:**
1. **Migrar para PostgreSQL** (recomendado para produção)
   - [Supabase](https://supabase.com) - PostgreSQL gratuito
   - [Railway](https://railway.app) - PostgreSQL gratuito
   - [PlanetScale](https://planetscale.com) - MySQL gratuito

2. **Usar Vercel Blob** para armazenar o arquivo SQLite

3. **Usar banco externo** via API

## 📋 Checklist de Deploy

- [ ] Variável `SECRET_KEY` configurada
- [ ] Arquivo `vercel.json` presente
- [ ] Arquivo `api/index.py` presente
- [ ] `requirements-vercel.txt` ou `requirements.txt` presente
- [ ] Testar localmente antes do deploy
- [ ] Verificar logs após deploy

## 🔍 Verificar Deploy

Após o deploy, verifique:

1. **Logs**: Dashboard Vercel → Deployments → Logs
2. **Funções**: Dashboard Vercel → Functions
3. **Variáveis**: Dashboard Vercel → Settings → Environment Variables

## 🐛 Troubleshooting

### Erro: "Module not found"
- Verifique se `requirements-vercel.txt` está na raiz
- Renomeie para `requirements.txt` se necessário

### Erro: "Database locked"
- SQLite não é ideal para serverless
- Migre para PostgreSQL/MySQL

### Erro: "Function timeout"
- Limite: 10s (hobby) ou 60s (pro)
- Configurado para 30s no `vercel.json`
- Otimize operações pesadas

### Banco resetado
- Normal com SQLite em serverless
- Use banco externo para persistência

## 📚 Próximos Passos

1. **Configurar domínio personalizado** (opcional)
2. **Migrar para PostgreSQL** (recomendado)
3. **Configurar CI/CD** (deploy automático via Git)
4. **Monitorar performance** (Vercel Analytics)

## 🔗 Links Úteis

- [Documentação Vercel Python](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Guia Completo](./DEPLOY_VERCEL.md)

