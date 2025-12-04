# Como Fazer Push para o GitHub

Siga estes passos para enviar sua aplicação para o GitHub:

## 📋 Passo 1: Criar Repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique no botão **"+"** no canto superior direito e selecione **"New repository"**
3. Preencha:
   - **Repository name**: `appigreja` (ou outro nome de sua preferência)
   - **Description**: "Sistema de gerenciamento de escalas de coroinhas"
   - **Visibility**: Escolha **Public** ou **Private**
   - **NÃO marque** "Initialize this repository with a README" (já temos um)
4. Clique em **"Create repository"**

## 🚀 Passo 2: Conectar e Fazer Push

Após criar o repositório, o GitHub mostrará instruções. Execute os seguintes comandos no terminal:

```bash
# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/appigreja.git

# Fazer push do código
git push -u origin main
```

**Exemplo:**
Se seu usuário for `rneto464`, o comando seria:
```bash
git remote add origin https://github.com/rneto464/appigreja.git
git push -u origin main
```

## 🔐 Autenticação

Se solicitado, você precisará:
- **Username**: Seu username do GitHub
- **Password**: Use um **Personal Access Token** (não sua senha)

### Como criar um Personal Access Token:

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Dê um nome (ex: "appigreja")
4. Selecione o escopo **`repo`** (acesso completo aos repositórios)
5. Clique em **"Generate token"**
6. **Copie o token** (você só verá ele uma vez!)
7. Use este token como senha quando solicitado

## ✅ Verificação

Após o push, acesse seu repositório no GitHub e verifique se todos os arquivos foram enviados corretamente.

## 📝 Próximos Passos

Após fazer o push, você pode:
- Configurar o deploy automático na Vercel (veja `DEPLOY_VERCEL.md`)
- Adicionar colaboradores ao repositório
- Configurar GitHub Actions para CI/CD

