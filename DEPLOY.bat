@echo off
REM Script rápido para deploy na Vercel (Windows)

echo 🚀 Preparando deploy na Vercel...
echo.

REM Verificar se Vercel CLI está instalado
where vercel >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Vercel CLI não encontrado!
    echo 📦 Instalando Vercel CLI...
    npm install -g vercel
)

REM Verificar se está logado
echo 🔐 Verificando login...
vercel whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Não está logado. Fazendo login...
    vercel login
)

REM Gerar SECRET_KEY se não existir
if "%SECRET_KEY%"=="" (
    echo 🔑 Gerando SECRET_KEY...
    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_hex(32))" 2^>nul') do set SECRET_KEY=%%i
    if "%SECRET_KEY%"=="" (
        for /f "delims=" %%i in ('python3 -c "import secrets; print(secrets.token_hex(32))" 2^>nul') do set SECRET_KEY=%%i
    )
    if not "%SECRET_KEY%"=="" (
        echo ✅ SECRET_KEY gerada: %SECRET_KEY%
        echo ⚠️  IMPORTANTE: Configure esta variável na dashboard da Vercel!
        echo.
    )
)

REM Fazer deploy
echo 📤 Fazendo deploy...
vercel --prod

echo.
echo ✅ Deploy concluído!
echo 📝 Não esqueça de configurar a variável SECRET_KEY na dashboard da Vercel!
pause

