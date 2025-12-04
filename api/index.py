"""
Entry point para Vercel Serverless Functions
Este arquivo importa a aplicação Flask e a expõe como uma função serverless
"""
import sys
import os
from http.server import BaseHTTPRequestHandler
from io import BytesIO

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
    # Garantir que /tmp existe (sempre existe na Vercel, mas vamos garantir)
    try:
        os.makedirs('/tmp', exist_ok=True)
    except:
        pass
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
    # Continuar mesmo se houver erro - o banco será criado na primeira requisição

# Criar handler compatível com Vercel
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def do_PATCH(self):
        self.handle_request()
    
    def do_OPTIONS(self):
        self.handle_request()
    
    def handle_request(self):
        # Garantir que o banco existe antes de processar a requisição
        try:
            if not os.path.exists(db_path):
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                with app.app_context():
                    init_app()
        except Exception as e:
            print(f"Erro ao garantir banco na requisição: {e}")
        
        # Converter a requisição HTTP para WSGI
        path_parts = self.path.split('?', 1)
        path = path_parts[0]
        query = path_parts[1] if len(path_parts) > 1 else ''
        
        # Ler body se houver
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        environ = {
            'REQUEST_METHOD': self.command,
            'SCRIPT_NAME': '',
            'PATH_INFO': path,
            'QUERY_STRING': query,
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': str(content_length),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https' if IS_VERCEL else 'http',
            'wsgi.input': BytesIO(body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Adicionar headers HTTP
        for key, value in self.headers.items():
            key = 'HTTP_' + key.upper().replace('-', '_')
            environ[key] = value
        
        # Criar resposta
        response_headers = []
        status_code = [200]
        
        def start_response(status, headers):
            status_code[0] = int(status.split()[0])
            response_headers[:] = headers
        
        # Executar app Flask
        try:
            response = app(environ, start_response)
            
            # Enviar resposta
            self.send_response(status_code[0])
            for header, value in response_headers:
                self.send_header(header, value)
            self.end_headers()
            
            # Enviar body
            for chunk in response:
                self.wfile.write(chunk)
            
            if hasattr(response, 'close'):
                response.close()
        except Exception as e:
            print(f"Erro ao processar requisição: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Internal Server Error: {str(e)}'.encode())

