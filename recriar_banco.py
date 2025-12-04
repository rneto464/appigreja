"""
Script para recriar o banco de dados do zero.
ATENÇÃO: Este script apaga o banco de dados existente e cria um novo vazio.

IMPORTANTE: Pare a aplicação Flask antes de executar este script!
"""
import sqlite3
import os
import sys

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'dados_escala.db')

def recriar_banco():
    """Recria o banco de dados do zero"""
    
    # Remove o banco antigo se existir
    if os.path.exists(DATABASE):
        try:
            os.remove(DATABASE)
            print(f"[OK] Banco de dados antigo removido: {DATABASE}")
        except PermissionError:
            print("\n[ERRO] O banco de dados esta em uso!")
            print("   Por favor, pare a aplicacao Flask (Ctrl+C) e tente novamente.")
            sys.exit(1)
    
    # Conecta ao banco (cria se não existir)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("\nCriando tabelas...")
    
    # Tabela de escalas
    cursor.execute(''' 
        CREATE TABLE escalas (
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
    print("[OK] Tabela 'escalas' criada")
    
    # Tabela de pessoas
    cursor.execute('''
        CREATE TABLE pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            grupo TEXT NOT NULL,
            funcoes TEXT
        )
    ''')
    print("[OK] Tabela 'pessoas' criada")
    
    # Tabela de modelos de escala (templates)
    cursor.execute('''
        CREATE TABLE escala_templates (
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
    print("[OK] Tabela 'escala_templates' criada")
    
    # Tabela de dias de missa
    cursor.execute('''
        CREATE TABLE dias_missa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dia_semana INTEGER NOT NULL,
            tipo_escala TEXT NOT NULL,
            horario TEXT,
            ativo INTEGER DEFAULT 1,
            ordem INTEGER DEFAULT 0
        )
    ''')
    print("[OK] Tabela 'dias_missa' criada")
    
    # Salva as alterações
    conn.commit()
    conn.close()
    
    print(f"\n[SUCESSO] Banco de dados recriado com sucesso em: {DATABASE}")
    print("\nTabelas criadas:")
    print("  - escalas - Armazena as escalas geradas")
    print("  - pessoas - Cadastro de coroinhas")
    print("  - escala_templates - Modelos de escala")
    print("  - dias_missa - Configuracao de dias de missa")
    print("\n[IMPORTANTE] PROXIMO PASSO: Execute 'python app.py' para popular os dados iniciais!")

if __name__ == '__main__':
    try:
        recriar_banco()
    except Exception as e:
        print(f"\n[ERRO] Erro ao recriar banco de dados: {e}")
        import traceback
        traceback.print_exc()
