"""
Script para criar um novo banco de dados com todas as tabelas necessárias.
Execute este script para reinicializar o banco de dados do zero.
"""
import sqlite3
import os

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'dados_escala.db')

def criar_banco_novo():
    """Cria um novo banco de dados com todas as tabelas necessárias"""
    
    # Remove o banco antigo se existir
    if os.path.exists(DATABASE):
        resposta = input(f"O banco de dados '{DATABASE}' já existe. Deseja apagá-lo e criar um novo? (s/n): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
        os.remove(DATABASE)
        print(f"Banco de dados antigo removido: {DATABASE}")
    
    # Conecta ao banco (cria se não existir)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("Criando tabelas...")
    
    # Tabela de escalas
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
    print("✓ Tabela 'escalas' criada")
    
    # Tabela de pessoas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            grupo TEXT NOT NULL,
            funcoes TEXT
        )
    ''')
    print("✓ Tabela 'pessoas' criada")
    
    # Tabela de modelos de escala (templates)
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
    print("✓ Tabela 'escala_templates' criada")
    
    # Tabela de dias de missa
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
    print("✓ Tabela 'dias_missa' criada")
    
    # Salva as alterações
    conn.commit()
    conn.close()
    
    print(f"\n✅ Banco de dados criado com sucesso em: {DATABASE}")
    print("\nTabelas criadas:")
    print("  - escalas")
    print("  - pessoas")
    print("  - escala_templates")
    print("  - dias_missa")
    print("\n⚠️  IMPORTANTE: Execute a aplicação (python app.py) para popular os dados iniciais!")

if __name__ == '__main__':
    try:
        criar_banco_novo()
    except Exception as e:
        print(f"\n❌ Erro ao criar banco de dados: {e}")
        import traceback
        traceback.print_exc()

