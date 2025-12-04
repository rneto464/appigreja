# 🗄️ Configuração MySQL para Vercel

Este guia explica como configurar MySQL para a aplicação na Vercel.

## 📋 Opções de Banco MySQL

### Opção 1: PlanetScale (Recomendado - Gratuito)
- **URL**: https://planetscale.com
- **Plano gratuito**: 1 banco, 1GB storage, 1 bilhão de reads/mês
- **Vantagens**: Serverless, escalável, fácil setup

### Opção 2: Railway
- **URL**: https://railway.app
- **Plano gratuito**: $5 crédito/mês
- **Vantagens**: Fácil deploy, PostgreSQL também disponível

### Opção 3: Supabase (PostgreSQL - Alternativa)
- **URL**: https://supabase.com
- **Plano gratuito**: 500MB database, 2GB bandwidth
- **Vantagens**: PostgreSQL gratuito, dashboard completo

## 🚀 Setup com PlanetScale (Recomendado)

### 1. Criar Conta no PlanetScale

1. Acesse https://planetscale.com
2. Crie uma conta (pode usar GitHub)
3. Crie um novo banco de dados:
   - Nome: `escalas_db`
   - Região: escolha a mais próxima
   - Clique em "Create database"

### 2. Obter Credenciais

1. No dashboard do PlanetScale, vá em "Settings" → "Passwords"
2. Clique em "New password"
3. Dê um nome (ex: "vercel-production")
4. Copie as credenciais:
   - **Host**: `xxxx.psdb.cloud`
   - **Username**: `xxxx`
   - **Password**: `xxxx`
   - **Database**: `escalas_db`
   - **Port**: `3306`

### 3. Criar Tabelas

Execute o script SQL abaixo no PlanetScale (SQL Editor):

```sql
CREATE TABLE IF NOT EXISTS escalas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data VARCHAR(10) NOT NULL,
    tipo_escala VARCHAR(100) NOT NULL,
    bata_cor VARCHAR(50),
    cerimoniarios TEXT,
    veteranos TEXT,
    mirins TEXT,
    turibulo TEXT,
    naveta TEXT,
    tochas TEXT,
    INDEX idx_data (data),
    INDEX idx_tipo_escala (tipo_escala)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pessoas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    grupo VARCHAR(50) NOT NULL,
    funcoes TEXT,
    INDEX idx_grupo (grupo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS escala_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_escala VARCHAR(100) NOT NULL UNIQUE,
    cerimoniarios_template TEXT,
    veteranos_template TEXT,
    mirins_template TEXT,
    turibulo_template TEXT,
    naveta_template TEXT,
    tochas_template TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dias_missa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dia_semana INT NOT NULL,
    tipo_escala VARCHAR(100) NOT NULL,
    horario VARCHAR(10),
    ativo INT DEFAULT 1,
    ordem INT DEFAULT 0,
    INDEX idx_dia_semana (dia_semana),
    INDEX idx_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 4. Configurar Variáveis de Ambiente na Vercel

Na dashboard da Vercel, adicione as seguintes variáveis de ambiente:

```
MYSQL_HOST=xxxx.psdb.cloud
MYSQL_PORT=3306
MYSQL_USER=xxxx
MYSQL_PASSWORD=xxxx
MYSQL_DATABASE=escalas_db
```

**OU** use `DATABASE_URL` (formato PlanetScale):

```
DATABASE_URL=mysql://username:password@host:port/database
```

### 5. Fazer Deploy

Após configurar as variáveis, faça um novo deploy na Vercel. A aplicação detectará automaticamente o MySQL e usará ele ao invés do SQLite.

## 🔍 Verificar Funcionamento

Após o deploy:

1. Acesse a aplicação
2. As pessoas serão cadastradas automaticamente na primeira requisição
3. Gere uma escala para testar

## 📝 Notas Importantes

- **PlanetScale**: Requer SSL. O PyMySQL já configura isso automaticamente.
- **Conexões**: PlanetScale tem limite de conexões simultâneas no plano gratuito
- **Backup**: PlanetScale faz backup automático
- **Migrações**: Use o dashboard do PlanetScale para gerenciar o schema

## 🐛 Troubleshooting

### Erro: "Access denied"
- Verifique se as credenciais estão corretas
- Verifique se o IP está permitido (PlanetScale permite todos por padrão)

### Erro: "Table doesn't exist"
- Execute o script SQL acima para criar as tabelas

### Erro: "Too many connections"
- PlanetScale plano gratuito tem limite de conexões
- A aplicação fecha conexões automaticamente, mas pode precisar de pool de conexões

## 🔄 Migração de SQLite para MySQL

Se você já tem dados no SQLite local:

1. Exporte os dados do SQLite
2. Importe no MySQL usando o PlanetScale dashboard ou ferramentas de migração
3. Ou use a rota `/cadastrar_pessoas` para recadastrar as pessoas

