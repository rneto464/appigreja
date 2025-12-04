import sqlite3
import os

# --- CONFIGURAÇÃO ---
# Usa caminho relativo ao diretório do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'dados_escala.db')

# --- DADOS FORNECIDOS PELO USUÁRIO ---
# IMPORTANTE: Pessoas que estão em MESTRE DE CERIMONIA não devem estar também em EXPERIENTES
# Para evitar duplicação, cadastramos primeiro os Mestres de Cerimonia, depois os Experientes (sem os que já são Mestres)

# MESTRE DE CERIMONIA (prioridade - não devem estar em outras categorias)
mestres_cerimonia = [
    "Alejandro", "João Pedro", "Pedro Reis", "Adriano",
    "Lucas", "André", "Pedro Barroso"
]

# EXPERIENTES (apenas os que NÃO são Mestres de Cerimonia)
experientes = [
    "Ana Julia", "Vitória", "Sofia Reis", "Armando", "Karla",
    "Mateus", "João Raffael", "Pedro Cutrim", "Gabriel Mendes"
]

# CRIANÇAS (Mirins)
mirins = [
    "João Gabriel", "Luiza", "Miguel", "Rafael", "Antony",
    "Maria Celida", "Cauan", "Theo", "Alexia", "Davi Barbalho",
    "Helisa", "Thiago Alex", "Gabriel Carvalho", "Mariana Jansen",
    "Bernardo"
]

# Estrutura final para cadastro
pessoas_para_cadastrar = {
    'cerimoniario': mestres_cerimonia,
    'veterano': experientes,
    'mirins': mirins
}

# --- LÓGICA DO SCRIPT ---
def cadastrar_em_massa():
    print(f"Conectando ao banco de dados em: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        print("Conexão bem-sucedida.")
        
        total_cadastrados = 0
        total_ignorados = 0

        # Itera sobre cada grupo e sua lista de nomes
        # IMPORTANTE: Ordem de cadastro importa - Mestres primeiro, depois Experientes
        for grupo, nomes in pessoas_para_cadastrar.items():
            print(f"\n--- Cadastrando grupo: {grupo} ---")
            for nome in nomes:
                nome_limpo = nome.strip()
                
                # Verifica se a pessoa já existe no banco
                cursor.execute("SELECT grupo FROM pessoas WHERE nome = ?", (nome_limpo,))
                pessoa_existente = cursor.fetchone()
                
                if pessoa_existente:
                    grupo_existente = pessoa_existente[0]
                    if grupo_existente == grupo:
                        print(f"  [=] '{nome_limpo}' já está cadastrado(a) no grupo '{grupo}'. Mantendo.")
                    else:
                        print(f"  [!] '{nome_limpo}' já existe no grupo '{grupo_existente}'. Não alterando para '{grupo}'.")
                    total_ignorados += 1
                else:
                    # Pessoa não existe, pode cadastrar
                    try:
                        cursor.execute(
                            "INSERT INTO pessoas (nome, grupo, funcoes) VALUES (?, ?, ?)",
                            (nome_limpo, grupo, '')
                        )
                        print(f"  [+] '{nome_limpo}' cadastrado(a) com sucesso no grupo '{grupo}'.")
                        total_cadastrados += 1
                    except sqlite3.IntegrityError:
                        print(f"  [!] Erro ao cadastrar '{nome_limpo}'. Pode já existir.")
                        total_ignorados += 1

        conn.commit()
        print("\nOperação finalizada. Alterações salvas no banco de dados.")
        print(f"Resumo: {total_cadastrados} pessoas novas cadastradas, {total_ignorados} nomes duplicados foram ignorados.")

    except sqlite3.Error as e:
        print(f"\nERRO: Ocorreu um problema com o banco de dados: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

# --- Executa a função ---
if __name__ == '__main__':
    cadastrar_em_massa()