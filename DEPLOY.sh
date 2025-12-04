#!/bin/bash
# Script rápido para deploy na Vercel

echo "🚀 Preparando deploy na Vercel..."
echo ""

# Verificar se Vercel CLI está instalado
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI não encontrado!"
    echo "📦 Instalando Vercel CLI..."
    npm install -g vercel
fi

# Verificar se está logado
echo "🔐 Verificando login..."
vercel whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Não está logado. Fazendo login..."
    vercel login
fi

# Gerar SECRET_KEY se não existir
if [ -z "$SECRET_KEY" ]; then
    echo "🔑 Gerando SECRET_KEY..."
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "✅ SECRET_KEY gerada: $SECRET_KEY"
    echo "⚠️  IMPORTANTE: Configure esta variável na dashboard da Vercel!"
    echo ""
fi

# Fazer deploy
echo "📤 Fazendo deploy..."
vercel --prod

echo ""
echo "✅ Deploy concluído!"
echo "📝 Não esqueça de configurar a variável SECRET_KEY na dashboard da Vercel!"

