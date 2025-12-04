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

# Na Vercel, usar /tmp para o banco de dados (único diretório gravável)
# Definir variável de ambiente antes de importar app
if os.environ.get('VERCEL'):
    # Estamos na Vercel, usar /tmp para o banco
    os.environ['DATABASE_PATH'] = '/tmp/dados_escala.db'
else:
    # Desenvolvimento local
    os.environ['DATABASE_PATH'] = os.path.join(parent_dir, 'dados_escala.db')

# Importar a aplicação Flask
from app import app, init_app

# Inicializar o banco de dados na primeira importação (apenas se necessário)
# Na Vercel, isso garante que o banco esteja pronto
try:
    db_path = os.environ.get('DATABASE_PATH', os.path.join(parent_dir, 'dados_escala.db'))
    if not os.path.exists(db_path):
        with app.app_context():
            init_app()
except Exception as e:
    print(f"AVISO: Erro ao inicializar banco: {e}")
    # Continuar mesmo se houver erro - o banco será criado na primeira requisição

# Exportar a aplicação para a Vercel
# Para Flask com @vercel/python, exportamos o app diretamente
# A Vercel detecta automaticamente que é um app Flask
handler = app

