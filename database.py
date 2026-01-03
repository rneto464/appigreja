"""
Módulo de conexão com banco de dados
Suporta PostgreSQL (Supabase) para produção e SQLite para desenvolvimento local
"""
import os
import sys

# Detectar tipo de banco de dados
# Supabase usa DATABASE_URL no formato: postgresql://user:pass@host:port/db
USE_POSTGRES = bool(os.environ.get('DATABASE_URL') or os.environ.get('SUPABASE_DB_URL'))

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    class ConnectionWrapper:
        """Wrapper para conexão PostgreSQL que simula interface SQLite"""
        def __init__(self, conn):
            self.conn = conn
            self._cursor = None
        
        def execute(self, query, params=None):
            """Executa query e retorna cursor compatível com SQLite"""
            try:
                # Fechar cursor anterior se existir para evitar vazamento de recursos
                if self._cursor is not None:
                    try:
                        self._cursor.close()
                    except Exception:
                        pass  # Ignorar erros ao fechar cursor anterior
                
                # Criar novo cursor
                self._cursor = self.conn.cursor()
                if params:
                    # Converter ? para %s para PostgreSQL
                    # Contar quantos ? existem e garantir que temos params suficientes
                    query_pg = query.replace('?', '%s')
                    self._cursor.execute(query_pg, params)
                else:
                    self._cursor.execute(query)
                # Garantir que retornamos o cursor, não None
                if self._cursor is None:
                    raise ValueError("Cursor não foi criado corretamente")
                return self._cursor
            except Exception as e:
                print(f"❌ Erro no ConnectionWrapper.execute(): {e}")
                import traceback
                traceback.print_exc()
                raise
        
        def commit(self):
            """Commit das alterações"""
            self.conn.commit()
        
        def close(self):
            """Fecha conexão"""
            if self._cursor:
                self._cursor.close()
            self.conn.close()
        
        def cursor(self):
            """Retorna cursor"""
            return self.conn.cursor()
        
        def __getattr__(self, name):
            """Delega outros atributos para a conexão"""
            return getattr(self.conn, name)
    
    def get_db_connection():
        """Cria conexão com PostgreSQL (Supabase)"""
        try:
            # Suportar DATABASE_URL (formato Supabase)
            database_url = os.environ.get('DATABASE_URL') or os.environ.get('SUPABASE_DB_URL')
            
            if not database_url:
                raise ValueError("DATABASE_URL ou SUPABASE_DB_URL não configurado")
            
            # Parse DATABASE_URL se necessário
            # Supabase já fornece no formato correto: postgresql://user:pass@host:port/db
            raw_conn = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
            # Retornar wrapper para compatibilidade com SQLite
            wrapped_conn = ConnectionWrapper(raw_conn)
            print(f"✅ Conexão PostgreSQL criada e envolvida com ConnectionWrapper")
            print(f"✅ Tipo do objeto retornado: {type(wrapped_conn).__name__}")
            # Verificar se o wrapper tem o método execute
            if not hasattr(wrapped_conn, 'execute'):
                raise ValueError("ConnectionWrapper não tem método execute!")
            return wrapped_conn
        except Exception as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_row_factory():
        """Retorna factory para rows (PostgreSQL usa RealDictCursor)"""
        return None  # RealDictCursor já retorna dicts
    
    def execute_query(conn, query, params=None):
        """Executa query e retorna cursor"""
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    DB_TYPE = 'PostgreSQL (Supabase)'
    
else:
    # SQLite para desenvolvimento local
    import sqlite3
    
    def get_db_connection():
        """Cria conexão com SQLite"""
        database_path = os.environ.get('DATABASE_PATH', 'dados_escala.db')
        
        # Garantir que o diretório existe
        db_dir = os.path.dirname(database_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_row_factory():
        """Retorna factory para rows (SQLite)"""
        return sqlite3.Row
    
    def execute_query(conn, query, params=None):
        """Executa query e retorna cursor"""
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    DB_TYPE = 'SQLite'

# Exceções de banco de dados
if USE_POSTGRES:
    import psycopg2
    IntegrityError = psycopg2.IntegrityError
    OperationalError = psycopg2.OperationalError
else:
    import sqlite3
    IntegrityError = sqlite3.IntegrityError
    OperationalError = sqlite3.OperationalError

def build_date_filter_query(month, year):
    """
    Constrói query para filtrar por mês e ano
    Retorna (query_string, params)
    """
    if USE_POSTGRES:
        # PostgreSQL: usar TO_DATE e EXTRACT
        query = """
            WHERE EXTRACT(MONTH FROM TO_DATE(data, 'DD/MM/YYYY')) = %s 
            AND EXTRACT(YEAR FROM TO_DATE(data, 'DD/MM/YYYY')) = %s
        """
        params = (month, year)
    else:
        # SQLite: usar strftime
        query = """
            WHERE strftime('%m', substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)) = ?
            AND strftime('%Y', substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)) = ?
        """
        params = (f"{month:02d}", str(year))
    
    return query, params

def create_tables(conn):
    """Cria todas as tabelas necessárias"""
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        # SQL para PostgreSQL
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escalas (
                id SERIAL PRIMARY KEY,
                data VARCHAR(10) NOT NULL,
                tipo_escala VARCHAR(100) NOT NULL,
                bata_cor VARCHAR(50),
                cerimoniarios TEXT,
                veteranos TEXT,
                mirins TEXT,
                turibulo TEXT,
                naveta TEXT,
                tochas TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_escalas_data ON escalas(data);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_escalas_tipo ON escalas(tipo_escala);
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pessoas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL UNIQUE,
                grupo VARCHAR(50) NOT NULL,
                funcoes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pessoas_grupo ON pessoas(grupo);
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escala_templates (
                id SERIAL PRIMARY KEY,
                tipo_escala VARCHAR(100) NOT NULL UNIQUE,
                cerimoniarios_template TEXT,
                veteranos_template TEXT,
                mirins_template TEXT,
                turibulo_template TEXT,
                naveta_template TEXT,
                tochas_template TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dias_missa (
                id SERIAL PRIMARY KEY,
                dia_semana INTEGER NOT NULL,
                tipo_escala VARCHAR(100) NOT NULL,
                horario VARCHAR(10),
                ativo INTEGER DEFAULT 1,
                ordem INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_dias_missa_dia ON dias_missa(dia_semana);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_dias_missa_ativo ON dias_missa(ativo);
        ''')
    else:
        # SQL para SQLite
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escalas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                tipo_escala TEXT NOT NULL,
                bata_cor TEXT,
                cerimoniarios TEXT,
                veteranos TEXT,
                mirins TEXT,
                turibulo TEXT,
                naveta TEXT,
                tochas TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                grupo TEXT NOT NULL,
                funcoes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escala_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_escala TEXT NOT NULL UNIQUE,
                cerimoniarios_template TEXT,
                veteranos_template TEXT,
                mirins_template TEXT,
                turibulo_template TEXT,
                naveta_template TEXT,
                tochas_template TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dias_missa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia_semana INTEGER NOT NULL,
                tipo_escala TEXT NOT NULL,
                horario TEXT,
                ativo INTEGER DEFAULT 1,
                ordem INTEGER DEFAULT 0
            )
        ''')
    
    conn.commit()
    print(f"Tabelas criadas/verificadas no {DB_TYPE}")
