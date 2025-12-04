# Guia de Deploy na Vercel

Este guia explica como fazer o deploy desta aplicação Flask na Vercel.

## 📋 Pré-requisitos

1. Conta na [Vercel](https://vercel.com)
2. [Vercel CLI](https://vercel.com/cli) instalado (opcional, mas recomendado)
3. Git configurado (recomendado)

## 🚀 Passo a Passo

### 1. Preparar o Ambiente

A aplicação já está configurada com os arquivos necessários:
- `vercel.json` - Configuração da Vercel
- `api/index.py` - Entry point para serverless functions
- `requirements-vercel.txt` - Dependências otimizadas

### 2. Instalar Vercel CLI (Opcional)

```bash
npm install -g vercel
```

### 3. Fazer Login na Vercel

```bash
vercel login
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (ou configure na dashboard da Vercel):

```bash
SECRET_KEY=sua_chave_secreta_segura_aqui
```

**IMPORTANTE**: Gere uma chave secreta segura:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Deploy via CLI

```bash
# Deploy para produção
vercel --prod

# Ou apenas para preview
vercel
```

### 6. Deploy via Dashboard da Vercel

1. Acesse [vercel.com](https://vercel.com)
2. Clique em "Add New Project"
3. Conecte seu repositório Git (GitHub, GitLab, Bitbucket)
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (deixe vazio)
   - **Output Directory**: (deixe vazio)
5. Adicione variáveis de ambiente:
   - `SECRET_KEY`: sua chave secreta
6. Clique em "Deploy"

## ⚙️ Configurações Importantes

### Variáveis de Ambiente

Configure na dashboard da Vercel ou no arquivo `.env`:

- `SECRET_KEY` (obrigatória): Chave secreta do Flask para sessões

### Banco de Dados

⚠️ **ATENÇÃO**: A Vercel usa sistema de arquivos efêmero. O banco SQLite será resetado a cada deploy ou após inatividade.

**Soluções recomendadas**:
1. **Usar banco de dados externo** (PostgreSQL, MySQL) via serviços como:
   - [Supabase](https://supabase.com) (PostgreSQL gratuito)
   - [PlanetScale](https://planetscale.com) (MySQL gratuito)
   - [Railway](https://railway.app) (PostgreSQL)

2. **Usar Vercel KV** (Redis) para dados temporários

3. **Usar Vercel Blob** para armazenar o arquivo SQLite

### Arquivos Estáticos

Os arquivos em `static/` e `templates/` são incluídos automaticamente no deploy.

## 📝 Estrutura de Arquivos

```
.
├── api/
│   └── index.py          # Entry point para Vercel
├── static/               # Arquivos estáticos (CSS, imagens)
├── templates/            # Templates HTML
├── app.py               # Aplicação Flask principal
├── vercel.json          # Configuração da Vercel
├── requirements-vercel.txt  # Dependências otimizadas
└── .vercelignore        # Arquivos ignorados no deploy
```

## 🔧 Troubleshooting

### Erro: "Module not found"
- Verifique se todas as dependências estão em `requirements-vercel.txt`
- A Vercel usa automaticamente `requirements.txt` ou `requirements-vercel.txt`

### Erro: "Database locked"
- O SQLite pode ter problemas em ambiente serverless
- Considere migrar para PostgreSQL ou MySQL

### Erro: "Function timeout"
- A Vercel tem limite de 10s (hobby) ou 60s (pro)
- Configurado para 30s no `vercel.json`
- Otimize operações pesadas ou use background jobs

### Banco de dados resetado
- Normal em ambiente serverless com SQLite
- Migre para banco de dados externo para persistência

## 🔄 Atualizações

Para atualizar a aplicação:

```bash
# Via CLI
vercel --prod

# Ou faça push para o repositório Git conectado
git push origin main
```

## 📚 Recursos

- [Documentação Vercel Python](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel CLI Docs](https://vercel.com/docs/cli)
- [Flask na Vercel](https://vercel.com/guides/deploying-flask-with-vercel)

## ⚠️ Limitações da Vercel (Plano Hobby)

- **Timeout**: 10 segundos por função
- **Memória**: 1024 MB
- **Sistema de arquivos**: Efêmero (resetado após inatividade)
- **Banco SQLite**: Não recomendado para produção

## 💡 Recomendações

1. **Migre para PostgreSQL** para produção
2. **Use variáveis de ambiente** para configurações sensíveis
3. **Configure domínio personalizado** na Vercel
4. **Monitore logs** na dashboard da Vercel
5. **Use Vercel Analytics** para monitoramento

