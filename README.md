# Sistema de Gerenciamento de Escalas de Coroinhas

Sistema web para gerenciar escalas de coroinhas, incluindo cadastro de pessoas, modelos de escala, configuração de dias de missa e geração automática de escalas mensais.

## 📋 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

## 🚀 Como Iniciar a Aplicação

### 1. Instalar as Dependências

Abra o terminal na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

**Nota:** Se estiver usando Windows, você pode precisar usar `python -m pip` ao invés de apenas `pip`.

### 2. Executar a Aplicação

Execute o arquivo principal:

```bash
python app.py
```

Ou no Windows PowerShell:

```bash
python app.py
```

### 3. Acessar a Aplicação

Após iniciar, você verá uma mensagem similar a:

```
 * Running on http://127.0.0.1:5000
 * Running on http://[seu-ip]:5000
```

Abra seu navegador e acesse:

**http://localhost:5000** ou **http://127.0.0.1:5000**

## 📝 Primeiros Passos

1. **Cadastrar Pessoas**: Acesse "Gerenciar Pessoas" e adicione os coroinhas, classificando-os em:
   - Cerimoniários
   - Veteranos
   - Mirins

2. **Configurar Modelos de Escala**: Acesse "Gerenciar Modelos" e defina quais pessoas podem participar de cada tipo de escala.

3. **Configurar Dias de Missa**: Acesse "Gerenciar Dias de Missa" e configure quais dias da semana terão missas e quais tipos de escala serão gerados.

4. **Gerar Escalas**: Na página principal, selecione o mês e ano e clique em "Gerar Escala" para criar as escalas automaticamente.

## 🗄️ Banco de Dados

O banco de dados SQLite (`dados_escala.db`) é criado automaticamente na primeira execução. As tabelas são inicializadas automaticamente com:
- Tabela de escalas
- Tabela de pessoas
- Tabela de modelos de escala
- Tabela de dias de missa (com configuração padrão)

## 🔧 Configurações Adicionais

### Porta Personalizada

Para executar em uma porta diferente, modifique a última linha do `app.py`:

```python
app.run(debug=True, port=8080)  # Altere 8080 para a porta desejada
```

### Modo de Produção

Para produção, desative o modo debug:

```python
app.run(debug=False)
```

Ou use o Gunicorn (já está nas dependências):

```bash
gunicorn app:app
```

## 📱 Funcionalidades

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

## 🐛 Solução de Problemas

### Erro ao instalar dependências

Se houver erro ao instalar alguma dependência, tente:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Banco de dados não criado

O banco é criado automaticamente. Se houver problemas, delete o arquivo `dados_escala.db` e execute novamente.

### Porta já em uso

Se a porta 5000 estiver em uso, altere a porta no `app.py` ou pare o processo que está usando a porta.

## 📞 Suporte

Para problemas ou dúvidas, verifique os logs no terminal onde a aplicação está rodando.



http://localhost:5000/visualizar