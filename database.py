"""
Módulo de conexão com banco de dados
Suporta MySQL (produção) e SQLite (desenvolvimento)
"""
import os
import sys

# Detectar tipo de banco de dados
USE_MYSQL = bool(os.environ.get('MYSQL_HOST') or os.environ.get('DATABASE_URL'))

if USE_MYSQL:
    import pymysql
    pymysql.install_as_MySQLdb()
    from pymysql.cursors import DictCursor
    
    def get_db_connection():
        """Cria conexão com MySQL"""
        try:
            # Suportar DATABASE_URL (formato: mysql://user:pass@host:port/db)
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                # Parse DATABASE_URL
                from urllib.parse import urlparse
                parsed = urlparse(database_url)
                host = parsed.hostname
                port = parsed.port or 3306
                user = parsed.username
                password = parsed.password
                database = parsed.path.lstrip('/')
            else:
                # Usar variáveis de ambiente individuais
                host = os.environ.get('MYSQL_HOST', 'localhost')
                port = int(os.environ.get('MYSQL_PORT', 3306))
                user = os.environ.get('MYSQL_USER', 'root')
                password = os.environ.get('MYSQL_PASSWORD', '')
                database = os.environ.get('MYSQL_DATABASE', 'escalas_db')
            
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=False
            )
            return conn
        except Exception as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            raise
    
    def get_row_factory():
        """Retorna factory para rows (MySQL usa DictCursor)"""
        return None  # DictCursor já retorna dicts
    
    def execute_query(conn, query, params=None):
        """Executa query e retorna cursor"""
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    DB_TYPE = 'MySQL'
    
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
if USE_MYSQL:
    import pymysql
    IntegrityError = pymysql.IntegrityError
    OperationalError = pymysql.OperationalError
else:
    import sqlite3
    IntegrityError = sqlite3.IntegrityError
    OperationalError = sqlite3.OperationalError

def format_date_for_query(date_str, format_type='month'):
    """
    Converte data do formato DD/MM/YYYY para uso em queries
    format_type: 'month', 'year', ou 'full'
    """
    if USE_MYSQL:
        # MySQL: converter DD/MM/YYYY para YYYY-MM-DD
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year = parts
            mysql_date = f"{year}-{month}-{day}"
            if format_type == 'month':
                return f"MONTH(STR_TO_DATE('{mysql_date}', '%Y-%m-%d'))"
            elif format_type == 'year':
                return f"YEAR(STR_TO_DATE('{mysql_date}', '%Y-%m-%d'))"
            else:
                return f"STR_TO_DATE('{mysql_date}', '%Y-%m-%d')"
    else:
        # SQLite: usar strftime
        if format_type == 'month':
            return f"strftime('%m', substr('{date_str}', 7, 4) || '-' || substr('{date_str}', 4, 2) || '-' || substr('{date_str}', 1, 2))"
        elif format_type == 'year':
            return f"strftime('%Y', substr('{date_str}', 7, 4) || '-' || substr('{date_str}', 4, 2) || '-' || substr('{date_str}', 1, 2))"
        else:
            return f"substr('{date_str}', 7, 4) || '-' || substr('{date_str}', 4, 2) || '-' || substr('{date_str}', 1, 2)"

def build_date_filter_query(month, year):
    """
    Constrói query para filtrar por mês e ano
    Retorna (query_string, params)
    """
    if USE_MYSQL:
        # MySQL: usar DATE_FORMAT
        query = """
            WHERE MONTH(STR_TO_DATE(data, '%d/%m/%Y')) = %s 
            AND YEAR(STR_TO_DATE(data, '%d/%m/%Y')) = %s
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
    
    if USE_MYSQL:
        # SQL para MySQL
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escalas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data VARCHAR(10) NOT NULL,
                tipo_escala VARCHAR(100) NOT NULL,
                bata_cor VARCHAR(50),
                cerimoniarios TEXT,
                veteranos TEXT,
                mirins TEXT,
                turibulo TEXT,
                naveta TEXT,
                tochas TEXT,
                INDEX idx_data (data),
                INDEX idx_tipo_escala (tipo_escala)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pessoas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL UNIQUE,
                grupo VARCHAR(50) NOT NULL,
                funcoes TEXT,
                INDEX idx_grupo (grupo)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escala_templates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tipo_escala VARCHAR(100) NOT NULL UNIQUE,
                cerimoniarios_template TEXT,
                veteranos_template TEXT,
                mirins_template TEXT,
                turibulo_template TEXT,
                naveta_template TEXT,
                tochas_template TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dias_missa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                dia_semana INT NOT NULL,
                tipo_escala VARCHAR(100) NOT NULL,
                horario VARCHAR(10),
                ativo INT DEFAULT 1,
                ordem INT DEFAULT 0,
                INDEX idx_dia_semana (dia_semana),
                INDEX idx_ativo (ativo)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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

