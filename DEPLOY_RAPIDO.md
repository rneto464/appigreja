# 🚀 Guia Rápido de Deploy na Vercel com Supabase

## ✅ Checklist Pré-Deploy

- [x] Código atualizado para Supabase (PostgreSQL)
- [x] Código no GitHub (repositório: rneto464/appigreja)
- [x] Arquivos de configuração prontos (vercel.json, api/index.py)
- [x] Dependências atualizadas (requirements.txt)

## 📝 Passos para Deploy

### 1. Configurar Supabase

1. **Crie uma conta**: https://supabase.com
2. **Crie um projeto**:
   - Nome: `appigreja`
   - Senha do banco: (anote esta senha!)
   - Região: escolha a mais próxima
3. **Obtenha a DATABASE_URL**:
   - Settings → Database → Connection string → URI
   - Copie a URL completa
   - **IMPORTANTE**: Substitua `[YOUR-PASSWORD]` pela senha real
4. **Crie as tabelas**:
   - SQL Editor → New query
   - Execute o SQL do arquivo `SUPABASE_SETUP.md`

### 2. Configurar Variáveis na Vercel

1. **Acesse**: https://vercel.com
2. **Vá no seu projeto** → Settings → Environment Variables
3. **Adicione**:

   **DATABASE_URL**:
   - Key: `DATABASE_URL`
   - Value: `postgresql://postgres:[SENHA]@db.xxxxx.supabase.co:5432/postgres`
   - Environments: ✅ Production, ✅ Preview, ✅ Development

   **SECRET_KEY**:
   - Key: `SECRET_KEY`
   - Value: (gere com: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - Environments: ✅ Production, ✅ Preview, ✅ Development

### 3. Deploy

A Vercel fará deploy automaticamente ao fazer push, ou:

```bash
vercel --prod
```

## 🔍 Verificar Deploy

Após o deploy, acesse:
- URL da aplicação: `https://seu-projeto.vercel.app`
- Página de gerenciar pessoas: `https://seu-projeto.vercel.app/gerenciar_pessoas`
- Cadastrar pessoas: `https://seu-projeto.vercel.app/cadastrar_pessoas`

## ⚠️ Importante

1. **Supabase**: Banco PostgreSQL gratuito (500MB)
   - ✅ Persistente (não reseta)
   - ✅ Backup automático
   - ✅ Dashboard completo

2. **Primeira Requisição**: A primeira requisição pode ser mais lenta pois inicializa o banco

3. **Cadastrar Pessoas**: Após o deploy, as pessoas serão cadastradas automaticamente na primeira requisição

## 🐛 Troubleshooting

### Erro: "Connection refused"
- Verifique se a `DATABASE_URL` está correta
- Verifique se substituiu `[YOUR-PASSWORD]` pela senha real
- Verifique se o projeto Supabase está ativo

### Erro: "Table doesn't exist"
- Execute o script SQL no Supabase SQL Editor
- Verifique se todas as tabelas foram criadas

### Erro: "Module not found"
- Verifique se todas as dependências estão em `requirements.txt`

## 📚 Recursos

- [Guia Completo Supabase](SUPABASE_SETUP.md)
- [Documentação Supabase](https://supabase.com/docs)
- [Vercel Dashboard](https://vercel.com/dashboard)
