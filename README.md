# Sistema de Gerenciamento de Escalas de Coroinhas

Sistema web para gerenciar escalas de coroinhas, incluindo cadastro de pessoas, modelos de escala, configuração de dias de missa e geração automática de escalas mensais.

## 🚀 Tecnologias

- **Backend**: Flask (Python)
- **Banco de Dados**: PostgreSQL (Supabase) / SQLite (desenvolvimento)
- **Deploy**: Vercel
- **Frontend**: HTML, CSS, JavaScript

## 📋 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)
- Conta no Supabase (para produção)
- Conta na Vercel (para deploy)

## 🛠️ Instalação Local

### 1. Clone o repositório

```bash
git clone https://github.com/rneto464/appigreja.git
cd appigreja
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure o ambiente (opcional)

Para desenvolvimento local, o SQLite será usado automaticamente. Se quiser usar Supabase localmente:

```bash
cp .env.example .env
# Edite .env e adicione sua DATABASE_URL do Supabase
```

### 4. Execute a aplicação

```bash
python app.py
```

A aplicação estará disponível em: **http://localhost:5000**

## 🌐 Deploy na Vercel

### 1. Configure o Supabase

Siga o guia completo em: [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

### 2. Configure variáveis de ambiente na Vercel

1. Acesse seu projeto na Vercel
2. Vá em **Settings** → **Environment Variables**
3. Adicione:
   - `DATABASE_URL`: String de conexão do Supabase
   - `SECRET_KEY`: Chave secreta do Flask

### 3. Deploy

A Vercel fará deploy automaticamente ao fazer push para o GitHub, ou:

```bash
vercel --prod
```

## 📝 Funcionalidades

- ✅ Gerenciamento de pessoas (cadastro, edição, remoção)
- ✅ Modelos de escala configuráveis
- ✅ Configuração flexível de dias de missa
- ✅ Geração automática de escalas mensais
- ✅ Visualização em calendário
- ✅ Filtro por pessoa
- ✅ Exportação para Excel
- ✅ Relatório de frequência
- ✅ Interface responsiva para celular
- ✅ Destaque visual da cor da túnica no calendário

## 🗄️ Estrutura do Banco de Dados

### Tabelas

- **pessoas**: Cadastro de coroinhas (cerimoniários, veteranos, mirins)
- **escalas**: Escalas geradas por data
- **escala_templates**: Modelos de escala
- **dias_missa**: Configuração de dias de missa

## 📁 Estrutura do Projeto

```
appigreja/
├── api/
│   └── index.py          # Entry point para Vercel
├── static/               # Arquivos estáticos (CSS, imagens)
├── templates/            # Templates HTML
├── app.py                # Aplicação Flask principal
├── database.py           # Módulo de conexão com banco
├── vercel.json           # Configuração da Vercel
├── requirements.txt      # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente
└── README.md             # Este arquivo
```

## 🔧 Configurações

### Variáveis de Ambiente

- `DATABASE_URL`: String de conexão do Supabase (PostgreSQL)
- `SECRET_KEY`: Chave secreta do Flask para sessões
- `DATABASE_PATH`: Caminho do SQLite (apenas desenvolvimento local)

## 🐛 Solução de Problemas

### Erro ao instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Banco de dados não conecta

- Verifique se a `DATABASE_URL` está correta
- Verifique se o projeto Supabase está ativo
- Verifique se as tabelas foram criadas

### Porta já em uso

Altere a porta no `app.py` ou pare o processo que está usando a porta.

## 📚 Documentação Adicional

- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Guia completo de configuração do Supabase
- [DEPLOY_RAPIDO.md](DEPLOY_RAPIDO.md) - Guia rápido de deploy

## 📞 Suporte

Para problemas ou dúvidas, verifique os logs no terminal ou na dashboard da Vercel.

## 📄 Licença

Este projeto é de uso interno.
