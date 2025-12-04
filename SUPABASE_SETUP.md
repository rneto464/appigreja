# 🚀 Configuração Supabase para Vercel

Este guia explica como configurar o Supabase (PostgreSQL) para a aplicação na Vercel.

## 📋 Pré-requisitos

1. Conta no [Supabase](https://supabase.com) (gratuita)
2. Projeto criado no Supabase

## 🗄️ Passo 1: Criar Projeto no Supabase

1. Acesse https://supabase.com
2. Faça login (pode usar GitHub)
3. Clique em "New Project"
4. Preencha:
   - **Name**: `appigreja` (ou outro nome)
   - **Database Password**: Crie uma senha forte (anote ela!)
   - **Region**: Escolha a região mais próxima
5. Clique em "Create new project"
6. Aguarde o projeto ser criado (2-3 minutos)

## 🔑 Passo 2: Obter Credenciais

1. No dashboard do Supabase, vá em **Settings** → **Database**
2. Role até a seção **Connection string**
3. Selecione **URI** no dropdown
4. Copie a string de conexão (formato):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
5. **IMPORTANTE**: Substitua `[YOUR-PASSWORD]` pela senha que você criou

## 📝 Passo 3: Criar Tabelas

1. No Supabase, vá em **SQL Editor**
2. Clique em **New query**
3. Cole e execute o seguinte SQL:

```sql
-- Tabela de escalas
CREATE TABLE IF NOT EXISTS escalas (
    id SERIAL PRIMARY KEY,
    data VARCHAR(10) NOT NULL,
    tipo_escala VARCHAR(100) NOT NULL,
    bata_cor VARCHAR(50),
    cerimoniarios TEXT,
    veteranos TEXT,
    mirins TEXT,
    turibulo TEXT,
    naveta TEXT,
    tochas TEXT
);

CREATE INDEX IF NOT EXISTS idx_escalas_data ON escalas(data);
CREATE INDEX IF NOT EXISTS idx_escalas_tipo ON escalas(tipo_escala);

-- Tabela de pessoas
CREATE TABLE IF NOT EXISTS pessoas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    grupo VARCHAR(50) NOT NULL,
    funcoes TEXT
);

CREATE INDEX IF NOT EXISTS idx_pessoas_grupo ON pessoas(grupo);

-- Tabela de templates de escala
CREATE TABLE IF NOT EXISTS escala_templates (
    id SERIAL PRIMARY KEY,
    tipo_escala VARCHAR(100) NOT NULL UNIQUE,
    cerimoniarios_template TEXT,
    veteranos_template TEXT,
    mirins_template TEXT,
    turibulo_template TEXT,
    naveta_template TEXT,
    tochas_template TEXT
);

-- Tabela de dias de missa
CREATE TABLE IF NOT EXISTS dias_missa (
    id SERIAL PRIMARY KEY,
    dia_semana INTEGER NOT NULL,
    tipo_escala VARCHAR(100) NOT NULL,
    horario VARCHAR(10),
    ativo INTEGER DEFAULT 1,
    ordem INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_dias_missa_dia ON dias_missa(dia_semana);
CREATE INDEX IF NOT EXISTS idx_dias_missa_ativo ON dias_missa(ativo);
```

4. Clique em **Run** para executar
5. Verifique se todas as tabelas foram criadas (deve aparecer "Success")

## ⚙️ Passo 4: Configurar Variáveis na Vercel

1. Acesse https://vercel.com
2. Vá no seu projeto
3. Clique em **Settings** → **Environment Variables**
4. Adicione as seguintes variáveis:

### Variável 1: DATABASE_URL
- **Key**: `DATABASE_URL`
- **Value**: Cole a string de conexão completa (com a senha substituída)
- **Environments**: ✅ Production, ✅ Preview, ✅ Development

### Variável 2: SECRET_KEY
- **Key**: `SECRET_KEY`
- **Value**: Gere uma chave secreta:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- **Environments**: ✅ Production, ✅ Preview, ✅ Development

5. Clique em **Save** para cada variável

## 🚀 Passo 5: Deploy

1. Faça commit e push das mudanças para o GitHub
2. A Vercel fará deploy automaticamente
3. Ou faça deploy manual:
   ```bash
   vercel --prod
   ```

## ✅ Verificar Funcionamento

Após o deploy:

1. Acesse a URL da aplicação na Vercel
2. A aplicação detectará automaticamente o Supabase
3. As pessoas serão cadastradas automaticamente na primeira requisição
4. Gere uma escala para testar

## 🔒 Segurança

- ✅ Nunca commite o arquivo `.env` no Git
- ✅ Use variáveis de ambiente na Vercel
- ✅ A senha do banco está na `DATABASE_URL` - mantenha segura
- ✅ O Supabase tem firewall - apenas IPs permitidos podem conectar

## 🐛 Troubleshooting

### Erro: "Connection refused"
- Verifique se a `DATABASE_URL` está correta
- Verifique se substituiu `[YOUR-PASSWORD]` pela senha real
- Verifique se o projeto Supabase está ativo

### Erro: "Table doesn't exist"
- Execute o script SQL acima no Supabase SQL Editor
- Verifique se todas as tabelas foram criadas

### Erro: "Too many connections"
- Supabase plano gratuito tem limite de conexões
- A aplicação fecha conexões automaticamente
- Considere usar connection pooling se necessário

## 📚 Recursos

- [Documentação Supabase](https://supabase.com/docs)
- [Supabase Dashboard](https://app.supabase.com)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## 💡 Dicas

- O Supabase oferece 500MB de banco gratuito
- Backup automático incluído
- Dashboard completo para gerenciar dados
- API REST automática (não usada nesta aplicação, mas disponível)

