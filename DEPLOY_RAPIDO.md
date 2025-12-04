# 🚀 Guia Rápido de Deploy na Vercel

## ✅ Checklist Pré-Deploy

- [x] Código corrigido (recursão infinita resolvida)
- [x] Código no GitHub (repositório: rneto464/appigreja)
- [x] Arquivos de configuração prontos (vercel.json, api/index.py)
- [x] Dependências atualizadas (requirements.txt)

## 📝 Passos para Deploy

### Opção 1: Via Dashboard da Vercel (Recomendado)

1. **Acesse**: https://vercel.com
2. **Faça login** na sua conta
3. **Clique em "Add New Project"**
4. **Conecte o repositório GitHub**:
   - Selecione o repositório: `rneto464/appigreja`
   - Clique em "Import"
5. **Configure o projeto**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (deixe como está)
   - **Build Command**: (deixe vazio)
   - **Output Directory**: (deixe vazio)
6. **Adicione Variáveis de Ambiente**:
   - Clique em "Environment Variables"
   - Adicione:
     - **Nome**: `SECRET_KEY`
     - **Valor**: (gere uma chave secreta - veja abaixo)
     - **Environments**: Production, Preview, Development
7. **Clique em "Deploy"**

### Opção 2: Via Vercel CLI

```bash
# 1. Instalar Vercel CLI (se ainda não tiver)
npm install -g vercel

# 2. Fazer login
vercel login

# 3. Gerar SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# 4. Configurar variável de ambiente (ou fazer via dashboard)
vercel env add SECRET_KEY

# 5. Deploy para produção
vercel --prod
```

## 🔑 Gerar SECRET_KEY

Execute no terminal:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado e use como valor da variável `SECRET_KEY` na Vercel.

## ⚠️ Importante

1. **Banco de Dados**: Na Vercel, o banco SQLite será criado em `/tmp/dados_escala.db`
   - ⚠️ Este banco é **efêmero** (reseta após inatividade)
   - Para produção, considere usar PostgreSQL ou MySQL

2. **Primeira Requisição**: A primeira requisição pode ser mais lenta pois inicializa o banco

3. **Cadastrar Pessoas**: Após o deploy, acesse `/cadastrar_pessoas` para cadastrar as 31 pessoas

## 🔍 Verificar Deploy

Após o deploy, acesse:
- URL da aplicação: `https://seu-projeto.vercel.app`
- Página de gerenciar pessoas: `https://seu-projeto.vercel.app/gerenciar_pessoas`
- Cadastrar pessoas: `https://seu-projeto.vercel.app/cadastrar_pessoas`

## 🐛 Troubleshooting

### Erro: "Module not found"
- Verifique se todas as dependências estão em `requirements.txt`

### Erro: "Database locked"
- Normal em ambiente serverless com SQLite
- Considere migrar para PostgreSQL

### Erro: "Function timeout"
- A Vercel tem limite de 10s (hobby) ou 60s (pro)
- Otimize operações pesadas

## 📚 Recursos

- [Documentação Vercel Python](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel Dashboard](https://vercel.com/dashboard)

