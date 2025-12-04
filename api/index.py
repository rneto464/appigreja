"""
Entry point para Vercel Serverless Functions
Este arquivo importa a aplicação Flask e a expõe como uma função serverless
"""
import sys
import os

# Adicionar o diretório raiz ao path para importar app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Detectar se estamos na Vercel
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'))

# Na Vercel, usar /tmp para o banco de dados (único diretório gravável)
# IMPORTANTE: Definir ANTES de importar app.py
if IS_VERCEL:
    # Estamos na Vercel, usar /tmp para o banco
    db_path = '/tmp/dados_escala.db'
    os.environ['DATABASE_PATH'] = db_path
else:
    # Desenvolvimento local
    db_path = os.path.join(parent_dir, 'dados_escala.db')
    os.environ['DATABASE_PATH'] = db_path

# Importar a aplicação Flask
from app import app, init_app

# Inicializar o banco de dados na primeira importação
try:
    if not os.path.exists(db_path):
        # Garantir que o diretório existe
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        with app.app_context():
            init_app()
            print(f"Banco de dados inicializado em: {db_path}")
except Exception as e:
    print(f"AVISO: Erro ao inicializar banco: {e}")
    import traceback
    traceback.print_exc()

# Para Flask na Vercel, exportar o app diretamente
# A Vercel com @vercel/python detecta automaticamente apps Flask
handler = app

