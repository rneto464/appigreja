import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import pandas as pd
from calendar import monthrange
import io
import json
from database import (
    get_db_connection, create_tables, USE_POSTGRES, DB_TYPE,
    IntegrityError, OperationalError, build_date_filter_query
)
# xlsxwriter é usado como engine do pandas, não precisa importar diretamente

# --- Configurações do Flask ---
# Configurar caminhos absolutos para static e templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, 
            static_folder=STATIC_DIR,
            static_url_path='/static',
            template_folder=TEMPLATES_DIR)
# Chave secreta - em produção, usar variável de ambiente
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui_altere_em_producao')
# Configuração de banco de dados
# Se MYSQL_HOST ou DATABASE_URL estiver definido, usa MySQL
# Caso contrário, usa SQLite para desenvolvimento local
EXCEL_FILE = os.path.join(BASE_DIR, 'BASE DE DADOS COROINHAS.xlsx')

# --- GRUPOS E TIPOS DE ESCALA (PADRONIZADO) ---
GRUPO_MIRINS = 'mirins'
GRUPO_VETERANO = 'veterano'
GRUPO_CERIMONIARIO = 'cerimoniario'
TIPO_ESCALA_DOMINGO_MANHA = 'Domingo Manhã'
TIPO_ESCALA_DOMINGO_NOITE = 'Domingo Noite'

# --- CONSTANTES DE HORÁRIOS ---
HORARIO_DOMINGO_MANHA = '07:00'
HORARIO_DOMINGO_NOITE = '18:00'
HORARIO_SEMANA = '19:00'

# --- SEPARADOR DE NOMES (PADRONIZADO) ---
SEPARADOR_NOMES = ', '  # Vírgula e espaço

# --- Listas de Candidatos para Templates Iniciais ---
g_terca_template_initial = [
    'Alejandro', 'André', 'Armando', 'Gabriel Carvalho', 'João Gabriel', 'Karla',
    'Lucas', 'Luiza', 'Mariana Jansen', 'Mateus', 'Pedro Barroso', 'Pedro Reis',
    'Sofia Reis'
]
g_quinta_template_initial = [
    'Alejandro', 'André', 'Armando', 'Gabriel Carvalho', 'João Gabriel', 'Karla',
    'Lucas', 'Luiza', 'Mariana Jansen', 'Mateus', 'Pedro Barroso', 'Pedro Cutrim',
    'Pedro Reis'
]
g_turibulo_template_initial = [
    'Armando', 'Karla', 'Mateus', 'Alejandro', 'João Pedro', 'Pedro Reis',
    'Adriano', 'Lucas', 'André', 'Pedro Barroso', 'Ana Julia'
]
g_naveta_template_initial = [
    'João Gabriel', 'Luiza', 'Miguel', 'Rafael', 'Antony', 'Maria Celida',
    'Cauan', 'Theo', 'Alexia', 'Davi Barbalho', 'Helisa', 'Thiago Alex',
    'Gabriel Carvalho', 'Mariana Jansen', 'Bernardo', 'Sofia Reis',
    'João Raffael', 'Pedro Cutrim', 'Gabriel Mendes'
]
g_tochas_template_initial = list(set([
    'Alejandro', 'João Pedro', 'Pedro Reis', 'Adriano', 'Lucas', 'André',
    'Pedro Barroso', 'Ana Julia', 'Vitória', 'Sofia Reis', 'Armando',
    'Karla', 'Mateus', 'João Raffael', 'Pedro Cutrim', 'Gabriel Mendes',
    'João Gabriel', 'Luiza', 'Miguel', 'Rafael'
]))
g_domingo_18h_template_initial = [
    'Adriano', 'Alejandro', 'Alexia', 'Ana Julia', 'André', 'Antony', 'Armando',
    'Bernardo', 'Cauan', 'Davi Barbalho', 'Gabriel Carvalho', 'Gabriel Mendes',
    'Helisa', 'João Gabriel', 'João Raffael', 'Karla', 'Lucas', 'Luiza',
    'Maria Celida', 'Mariana Jansen', 'Mateus', 'Miguel', 'Pedro Cutrim',
    'Pedro Reis', 'Rafael', 'Sofia Reis', 'Theo', 'Thiago Alex', 'Vitória'
]
g_domingo_07h_template_initial = [
    'Adriano', 'Alejandro', 'Alexia', 'Ana Julia', 'Antony', 'Armando',
    'Bernardo', 'Cauan', 'Gabriel Mendes', 'João Pedro', 'João Raffael',
    'Karla', 'Mariana Jansen', 'Mateus', 'Pedro Barroso', 'Pedro Cutrim',
    'Pedro Reis', 'Theo', 'Thiago Alex', 'Vitória'
]

# --- Funções Auxiliares (Padronização) ---
def formatar_data_pt_br(data_obj):
    """Formata uma data datetime para formato português completo"""
    dias_semana = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']
    meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    dia_semana_nome = dias_semana[data_obj.weekday()]
    mes_nome = meses_nomes[data_obj.month - 1]
    return f"{dia_semana_nome}, {data_obj.day} De {mes_nome} De {data_obj.year}"

def obter_horario_por_tipo_escala(tipo_escala, dias_missa_horarios=None):
    """Obtém o horário de um tipo de escala, com fallback para padrões"""
    if dias_missa_horarios and tipo_escala in dias_missa_horarios:
        horario = dias_missa_horarios[tipo_escala]
        if horario:
            return horario
    
    # Fallback baseado no tipo de escala
    if 'Manhã' in tipo_escala:
        return HORARIO_DOMINGO_MANHA
    elif 'Noite' in tipo_escala:
        return HORARIO_DOMINGO_NOITE
    else:
        return HORARIO_SEMANA

def parsear_nomes(campo):
    """Parseia uma string de nomes separados por vírgula, suportando ambos os formatos"""
    if not campo:
        return []
    # Suporta tanto ', ' quanto ',' como separador
    return [nome.strip() for nome in campo.replace(', ', ',').split(',') if nome.strip()]

def juntar_nomes(lista_nomes):
    """Junta uma lista de nomes usando o separador padronizado"""
    return SEPARADOR_NOMES.join(lista_nomes)

def contar_membros(campo):
    """Conta o número de membros em um campo de nomes"""
    return len(parsear_nomes(campo))

# --- Funções do Banco de Dados ---
def get_db():
    """Obtém conexão com o banco de dados (MySQL ou SQLite)"""
    conn = get_db_connection()
    
    # Verificar se as tabelas existem (apenas para SQLite)
    if not USE_POSTGRES:
        # Para SQLite, verificar se o banco existe
        database_path = os.environ.get('DATABASE_PATH', 'dados_escala.db')
        if not os.path.exists(database_path):
            # Criar tabelas na primeira vez
            try:
                create_tables(conn)
                with app.app_context():
                    popular_templates_iniciais()
                    popular_dias_missa_iniciais()
                print(f"Banco de dados {DB_TYPE} criado e inicializado")
            except Exception as e:
                print(f"Erro ao criar banco de dados: {e}")
                import traceback
                traceback.print_exc()
    
    return conn

def init_db():
    """Inicializa o banco de dados criando as tabelas se não existirem"""
    conn = get_db_connection()
    try:
        create_tables(conn)
        print(f"Banco de dados {DB_TYPE} inicializado/verificado.")
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        raise
    finally:
        conn.close()

def popular_templates_iniciais():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        if cursor.execute("SELECT COUNT(*) FROM escala_templates").fetchone()[0] == 0:
            print("Populando tabela de modelos de escala (templates).")
            templates_map = { TIPO_ESCALA_DOMINGO_MANHA: {'cerims': g_domingo_07h_template_initial, 'vets': g_domingo_07h_template_initial, 'kids': g_domingo_07h_template_initial, 'turib': g_turibulo_template_initial, 'nav': g_naveta_template_initial, 'tochas': g_tochas_template_initial}, TIPO_ESCALA_DOMINGO_NOITE: {'cerims': g_domingo_18h_template_initial, 'vets': g_domingo_18h_template_initial, 'kids': g_domingo_18h_template_initial, 'turib': g_turibulo_template_initial, 'nav': g_naveta_template_initial, 'tochas': g_tochas_template_initial}, 'Terça': {'cerims': g_terca_template_initial, 'vets': g_terca_template_initial, 'kids': g_terca_template_initial, 'turib': [], 'nav': [], 'tochas': []}, 'Quinta': {'cerims': g_quinta_template_initial, 'vets': g_quinta_template_initial, 'kids': g_quinta_template_initial, 'turib': [], 'nav': [], 'tochas': []}, }
            for tipo, data in templates_map.items():
                cursor.execute(''' INSERT INTO escala_templates (tipo_escala, cerimoniarios_template, veteranos_template, mirins_template, turibulo_template, naveta_template, tochas_template) VALUES (?, ?, ?, ?, ?, ?, ?) ''', ( tipo, SEPARADOR_NOMES.join(data.get('cerims', [])), SEPARADOR_NOMES.join(data.get('vets', [])), SEPARADOR_NOMES.join(data.get('kids', [])), SEPARADOR_NOMES.join(data.get('turib', [])), SEPARADOR_NOMES.join(data.get('nav', [])), SEPARADOR_NOMES.join(data.get('tochas', [])) ))
            db.commit()
            print("Modelos de escala (templates) populados!")
        db.close()

def popular_dias_missa_iniciais():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        if cursor.execute("SELECT COUNT(*) FROM dias_missa").fetchone()[0] == 0:
            print("Populando tabela de dias de missa.")
            # 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo
            dias_iniciais = [
                (6, TIPO_ESCALA_DOMINGO_MANHA, HORARIO_DOMINGO_MANHA, 1, 1),  # Domingo Manhã
                (6, TIPO_ESCALA_DOMINGO_NOITE, HORARIO_DOMINGO_NOITE, 1, 2),  # Domingo Noite
                (1, 'Terça', HORARIO_SEMANA, 1, 3),  # Terça
                (3, 'Quinta', HORARIO_SEMANA, 1, 4),  # Quinta
            ]
            for dia_semana, tipo_escala, horario, ativo, ordem in dias_iniciais:
                cursor.execute(''' INSERT INTO dias_missa (dia_semana, tipo_escala, horario, ativo, ordem) VALUES (?, ?, ?, ?, ?) ''', (dia_semana, tipo_escala, horario, ativo, ordem))
            db.commit()
            print("Dias de missa populados!")
        db.close()

def importar_dados_iniciais_do_excel():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        if cursor.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0] == 0:
            print(f"Tentando importar pessoas do arquivo: {EXCEL_FILE}")
            try:
                if os.path.exists(EXCEL_FILE):
                    # Tenta ler o arquivo Excel se existir
                    df = pd.read_excel(EXCEL_FILE)
                    print(f"Arquivo Excel encontrado. Use o script cadastra_pessoas.py para importar dados.")
                else:
                    print(f"Arquivo Excel não encontrado em {EXCEL_FILE}. Use o script cadastra_pessoas.py para importar dados.")
            except Exception as e:
                print(f"Erro ao tentar ler arquivo Excel: {e}. Use o script cadastra_pessoas.py para importar dados.")
            print("Importação do Excel concluída (se aplicável).")
        db.close()

def limpar_db_e_reimportar():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS escalas"); cursor.execute("DROP TABLE IF EXISTS pessoas"); cursor.execute("DROP TABLE IF EXISTS escala_templates"); cursor.execute("DROP TABLE IF EXISTS dias_missa")
        db.commit()
        print("Tabelas removidas.")
        init_db()
        importar_dados_iniciais_do_excel()
        popular_templates_iniciais()
        popular_dias_missa_iniciais()
        db.close()
        flash("Banco de dados reiniciado e dados reimportados com sucesso!", 'success')



def gerar_escala_para_mes(mes, ano):
    """
    Gera a escala para o mês com regras avançadas de sorteio, distribuição e
    um relatório de frequência ao final.
    """
    QUANTIDADES_POR_FUNCAO = {
        'domingo_e_solenidade': {
            # DOMINGOS: 2 Cerimoniários, 2 Veteranos, 2 Mirins, 2 Tochas, 1 Turíbulo, 1 Naveta
            'cerimoniarios': 2, 'veteranos': 2, 'mirins': 2,
            'turibulo': 1, 'naveta': 1, 'tochas': 2
        },
        'semana': {
            # TERÇA E QUINTA: 1 Cerimoniário, 2 Veteranos, 2 Mirins
            'cerimoniarios': 1, 'veteranos': 2, 'mirins': 2,
            'turibulo': 0, 'naveta': 0, 'tochas': 0
        }
    }
    DIAS_SOLENES = {
        "01-01": "Solenidade de Santa Maria, Mãe de Deus",
        "08-12": "Solenidade da Imaculada Conceição",
        "25-12": "Natal do Senhor"
    }

    def sortear_pessoas(lista_candidatos, quantidade, ja_escalados):
        if not lista_candidatos: return []

        candidatos_disponiveis = [nome for nome in lista_candidatos if nome not in ja_escalados]
        
        # ESTRATÉGIA MELHORADA: Priorizar fortemente pessoas que ainda não serviram 2 vezes
        # Ordenar por: primeiro quem tem menos de 2 serviços (0 ou 1), depois por quantidade de serviços
        def prioridade_servico(nome):
            servicos = contagem_servicos.get(nome, 0)
            # Prioridade máxima: quem tem 0 serviços
            if servicos == 0:
                return (0, 0)  # Máxima prioridade
            # Segunda prioridade: quem tem 1 serviço
            elif servicos == 1:
                return (1, 1)  # Alta prioridade
            # Terceira prioridade: quem tem exatamente 2 serviços
            elif servicos == 2:
                return (2, 2)  # Prioridade média
            # Última prioridade: quem já tem 3 ou mais serviços
            else:
                return (3, servicos)  # Baixa prioridade
        
        # Separar candidatos por prioridade
        candidatos_0_servicos = [n for n in candidatos_disponiveis if contagem_servicos.get(n, 0) == 0]
        candidatos_1_servico = [n for n in candidatos_disponiveis if contagem_servicos.get(n, 0) == 1]
        candidatos_2_servicos = [n for n in candidatos_disponiveis if contagem_servicos.get(n, 0) == 2]
        candidatos_3_mais = [n for n in candidatos_disponiveis if contagem_servicos.get(n, 0) >= 3]
        
        # Embaralhar cada grupo para ter aleatoriedade dentro da mesma prioridade
        random.shuffle(candidatos_0_servicos)
        random.shuffle(candidatos_1_servico)
        random.shuffle(candidatos_2_servicos)
        random.shuffle(candidatos_3_mais)
        
        # Montar lista ordenada por prioridade
        candidatos_ordenados = candidatos_0_servicos + candidatos_1_servico + candidatos_2_servicos + candidatos_3_mais
        
        # Selecionar apenas a quantidade necessária, respeitando a prioridade
        quantidade_real = min(len(candidatos_ordenados), quantidade)
        selecionados = candidatos_ordenados[:quantidade_real]

        for nome in selecionados:
            ja_escalados.add(nome)
            contagem_servicos[nome] = contagem_servicos.get(nome, 0) + 1

        return selecionados

    # --- LÓGICA PRINCIPAL ---
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Validar mês e ano
        if mes < 1 or mes > 12:
            raise ValueError(f"Mês inválido: {mes}. Deve ser entre 1 e 12.")
        if ano < 2000 or ano > 2100:
            raise ValueError(f"Ano inválido: {ano}. Deve ser entre 2000 e 2100.")
        
        # Deletar escalas do mês/ano usando função compatível
        date_filter, date_params = build_date_filter_query(mes, ano)
        cursor.execute(f"DELETE FROM escalas {date_filter}", date_params)

        templates = {row['tipo_escala']: row for row in cursor.execute('SELECT * FROM escala_templates').fetchall()}
        pessoas_e_grupos = {row['nome']: row['grupo'] for row in cursor.execute('SELECT nome, grupo FROM pessoas').fetchall()}
        
        # Validar que há pessoas cadastradas
        if not pessoas_e_grupos:
            raise ValueError("Não há pessoas cadastradas no sistema. Por favor, cadastre pessoas antes de gerar escalas.")
        
        # Validar que há templates configurados
        if not templates:
            raise ValueError("Não há modelos de escala configurados. Por favor, configure os modelos antes de gerar escalas.")
        
        # Verificar se há pelo menos um template para os tipos de escala necessários
        tipos_necessarios = {TIPO_ESCALA_DOMINGO_MANHA, TIPO_ESCALA_DOMINGO_NOITE, 'Terça', 'Quinta'}
        templates_encontrados = set(templates.keys())
        templates_faltando = tipos_necessarios - templates_encontrados
        if templates_faltando:
            print(f"AVISO: Alguns templates não foram encontrados: {templates_faltando}. A função tentará usar fallback.")
        
        contagem_servicos = {nome: 0 for nome in pessoas_e_grupos.keys()}

        primeiro_dia = datetime(ano, mes, 1)
        num_dias = monthrange(ano, mes)[1]
        ultimo_dia = datetime(ano, mes, num_dias)
        data_atual = primeiro_dia


        # Buscar configuração de dias de missa do banco
        # IMPORTANTE: Na geração automática, apenas gerar para Domingo, Terça e Quinta
        # 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo
        DIAS_PERMITIDOS_GERACAO = {6, 1, 3}  # Domingo, Terça, Quinta
        
        try:
            dias_missa_config = cursor.execute('SELECT * FROM dias_missa WHERE ativo = 1 ORDER BY ordem').fetchall()
        except OperationalError:
            # Tabela pode não existir ainda, usar configuração padrão
            print("Tabela dias_missa não encontrada, usando configuração padrão.")
            dias_missa_config = []
        
        dias_missa_map = {}  # {dia_semana: [(tipo_escala, horario), ...]}
        for config in dias_missa_config:
            try:
                dia_sem = config['dia_semana']
                # FILTRO: Apenas incluir dias permitidos na geração automática
                if dia_sem not in DIAS_PERMITIDOS_GERACAO:
                    continue
                    
                tipo_escala = config['tipo_escala']
                # Verificar se a coluna horario existe e não é None
                horario = ''
                try:
                    horario_val = config['horario']
                    horario = horario_val if horario_val else ''
                except (KeyError, IndexError):
                    horario = ''
                
                if dia_sem not in dias_missa_map:
                    dias_missa_map[dia_sem] = []
                dias_missa_map[dia_sem].append((tipo_escala, horario))
            except (KeyError, IndexError) as e:
                print(f"Erro ao processar configuração de dia de missa: {e}")
                continue
        
        # Se não houver configuração no banco, usar padrão: Domingo (manhã e noite), Terça, Quinta
        if not dias_missa_map:
            print("Usando configuração padrão: Domingo (Manhã e Noite), Terça, Quinta")
            dias_missa_map = {
                6: [(TIPO_ESCALA_DOMINGO_MANHA, HORARIO_DOMINGO_MANHA), (TIPO_ESCALA_DOMINGO_NOITE, HORARIO_DOMINGO_NOITE)],  # Domingo
                1: [('Terça', HORARIO_SEMANA)],  # Terça
                3: [('Quinta', HORARIO_SEMANA)]  # Quinta
            }
        
        print(f"Configuração de dias de missa: {dias_missa_map}")
        print(f"Templates disponíveis: {list(templates.keys())}")
        print(f"Total de pessoas cadastradas: {len(pessoas_e_grupos)}")

        escalas_geradas = 0
        while data_atual <= ultimo_dia:
            data_chave = data_atual.strftime("%d-%m")
            dia_da_semana = data_atual.weekday()
            escalados_no_dia_inteiro = set()  # Previne repetição no mesmo dia em funções diferentes
            escalados_domingo = set()  # Previne repetição entre manhã e noite no domingo
            
            # Verificar se é solenidade (dia solene que não é domingo)
            is_solenidade = data_chave in DIAS_SOLENES and dia_da_semana != 6
            
            # Se for domingo solene, tratar como domingo normal
            is_domingo_solenidade = data_chave in DIAS_SOLENES and dia_da_semana == 6
            
            # Buscar tipos de escala configurados para este dia da semana
            tipos_escala_do_dia = []
            if is_solenidade:
                # Dia solene que não é domingo - usar regras de domingo (solenidade)
                tipos_escala_do_dia = [DIAS_SOLENES[data_chave]]
            elif is_domingo_solenidade:
                # Domingo que é solenidade - usar regras normais de domingo (manhã e noite)
                tipos_escala_do_dia = [tipo for tipo, _ in dias_missa_map.get(6, [])]
            elif dia_da_semana in dias_missa_map:
                tipos_escala_do_dia = [tipo for tipo, _ in dias_missa_map[dia_da_semana]]
            
            # Se não houver tipos de escala para este dia, pular (não gerar escala)
            if not tipos_escala_do_dia:
                data_atual += timedelta(days=1)
                continue
            
            # Se for domingo (incluindo domingo solene), garantir que ninguém serve na manhã E à noite
            is_domingo = dia_da_semana == 6
            
            for tipo_escala in tipos_escala_do_dia:
                # Determinar template base - SEMPRE usar o template correspondente ao tipo_escala
                if is_solenidade:
                    # Dia solene que não é domingo - usar template de domingo manhã
                    template_base_nome = TIPO_ESCALA_DOMINGO_MANHA
                elif "Noite" in tipo_escala or tipo_escala == TIPO_ESCALA_DOMINGO_NOITE:
                    template_base_nome = TIPO_ESCALA_DOMINGO_NOITE
                elif "Manhã" in tipo_escala or tipo_escala == TIPO_ESCALA_DOMINGO_MANHA:
                    template_base_nome = TIPO_ESCALA_DOMINGO_MANHA
                # Remover verificação de 'Manha' sem til - usar sempre 'Manhã'
                else:
                    # Usar o tipo_escala diretamente como nome do template
                    template_base_nome = tipo_escala
                
                # SEMPRE tentar usar o template - se não existir, criar um básico ou usar fallback
                if template_base_nome in templates:
                    template = templates[template_base_nome]
                else:
                    # Se o template não existe, criar um template vazio para usar fallback
                    print(f"AVISO: Template '{template_base_nome}' não encontrado. Usando fallback com todas as pessoas.")
                    template = {
                        'cerimoniarios_template': '',
                        'veteranos_template': '',
                        'mirins_template': '',
                        'turibulo_template': '',
                        'naveta_template': '',
                        'tochas_template': ''
                    }
                
                # CORREÇÃO: Usar todos os nomes do template, não filtrar por grupo
                # Isso resolve a inconsistência onde nomes não aparecem
                # Função auxiliar para acessar chaves do template com segurança
                def get_template_value(key, default=''):
                    try:
                        val = template[key] if key in template.keys() else default
                        return val if val else default
                    except (KeyError, IndexError):
                        return default
                
                # Obter candidatos do template - se vazio, usar todas as pessoas do banco como fallback
                candidatos_cerim_modelo = parsear_nomes(get_template_value('cerimoniarios_template', ''))
                candidatos_vet_modelo = parsear_nomes(get_template_value('veteranos_template', ''))
                candidatos_mir_modelo = parsear_nomes(get_template_value('mirins_template', ''))
                candidatos_turib_modelo = parsear_nomes(get_template_value('turibulo_template', ''))
                candidatos_nav_modelo = parsear_nomes(get_template_value('naveta_template', ''))
                candidatos_tochas_modelo = parsear_nomes(get_template_value('tochas_template', ''))
                
                # Verificar se é evento especial (pelo nome do tipo de escala)
                # Eventos especiais podem ter turíbulo, naveta e tochas mesmo em dias de semana
                palavras_eventos_especiais = ['festejo', 'casamento', 'solenidade', 'especial', 'batizado', 'primeira comunhão', 'confirmação', 'ordenação']
                is_evento_especial = any(palavra.lower() in tipo_escala.lower() for palavra in palavras_eventos_especiais)
                
                # Determinar regras de quantidade
                # Domingos e solenidades usam regras de domingo
                if is_solenidade or is_domingo or tipo_escala in [TIPO_ESCALA_DOMINGO_MANHA, TIPO_ESCALA_DOMINGO_NOITE]:
                    regras_qtd = QUANTIDADES_POR_FUNCAO['domingo_e_solenidade']
                else:
                    regras_qtd = QUANTIDADES_POR_FUNCAO['semana'].copy()  # Usar copy() para não modificar o original
                    
                    # Se for evento especial E o template tiver candidatos configurados, permitir funções especiais
                    if is_evento_especial:
                        # Verificar se há candidatos configurados no template
                        tem_turibulo = len(candidatos_turib_modelo) > 0
                        tem_naveta = len(candidatos_nav_modelo) > 0
                        tem_tochas = len(candidatos_tochas_modelo) > 0
                        
                        # Se houver candidatos configurados, usar quantidade padrão de domingo
                        if tem_turibulo:
                            regras_qtd['turibulo'] = 1
                        if tem_naveta:
                            regras_qtd['naveta'] = 1
                        if tem_tochas:
                            regras_qtd['tochas'] = 2
                
                # Se o template estiver vazio, usar todas as pessoas do banco como fallback
                todas_pessoas_nomes = list(pessoas_e_grupos.keys())
                
                # Filtrar apenas pessoas que existem no banco
                # Se o template estiver vazio, usar todas as pessoas do grupo correspondente
                cerimoniarios_aptos = candidatos_cerim_modelo if candidatos_cerim_modelo else [nome for nome in todas_pessoas_nomes if pessoas_e_grupos.get(nome) == GRUPO_CERIMONIARIO]
                veteranos_aptos = candidatos_vet_modelo if candidatos_vet_modelo else [nome for nome in todas_pessoas_nomes if pessoas_e_grupos.get(nome) == GRUPO_VETERANO]
                mirins_aptos = candidatos_mir_modelo if candidatos_mir_modelo else [nome for nome in todas_pessoas_nomes if pessoas_e_grupos.get(nome) == GRUPO_MIRINS]
                
                # Para funções especiais:
                # - Se for evento especial OU domingo OU solenidade: usar candidatos do template ou todas as pessoas
                # - Se for dia de semana normal: usar apenas se o template tiver candidatos configurados
                if is_evento_especial or is_domingo or is_solenidade:
                    turibulo_aptos = candidatos_turib_modelo if candidatos_turib_modelo else todas_pessoas_nomes
                    naveta_aptos = candidatos_nav_modelo if candidatos_nav_modelo else todas_pessoas_nomes
                    tochas_aptos = candidatos_tochas_modelo if candidatos_tochas_modelo else todas_pessoas_nomes
                else:
                    # Dia de semana normal: só usar se o template tiver candidatos configurados
                    turibulo_aptos = candidatos_turib_modelo  # Pode ser lista vazia
                    naveta_aptos = candidatos_nav_modelo  # Pode ser lista vazia
                    tochas_aptos = candidatos_tochas_modelo  # Pode ser lista vazia
                
                # Garantir que apenas pessoas que existem no banco sejam consideradas
                cerimoniarios_aptos = [nome for nome in cerimoniarios_aptos if nome in pessoas_e_grupos]
                veteranos_aptos = [nome for nome in veteranos_aptos if nome in pessoas_e_grupos]
                mirins_aptos = [nome for nome in mirins_aptos if nome in pessoas_e_grupos]
                turibulo_aptos = [nome for nome in turibulo_aptos if nome in pessoas_e_grupos]
                naveta_aptos = [nome for nome in naveta_aptos if nome in pessoas_e_grupos]
                tochas_aptos = [nome for nome in tochas_aptos if nome in pessoas_e_grupos]
                
                # Para domingos, garantir que ninguém serve na manhã E à noite
                # Se for domingo, usar escalados_domingo além de escalados_no_dia_inteiro
                conjunto_restricao = escalados_no_dia_inteiro.copy()
                if is_domingo:
                    conjunto_restricao.update(escalados_domingo)
                
                # ESTRATÉGIA: Sempre priorizar pessoas com menos de 2 serviços
                # Se houver pessoas com menos de 2 serviços disponíveis, tentar usá-las primeiro
                cerimoniarios = sortear_pessoas(cerimoniarios_aptos, regras_qtd['cerimoniarios'], conjunto_restricao)
                veteranos = sortear_pessoas(veteranos_aptos, regras_qtd['veteranos'], conjunto_restricao)
                mirins = sortear_pessoas(mirins_aptos, regras_qtd['mirins'], conjunto_restricao)
                turibulo = sortear_pessoas(turibulo_aptos, regras_qtd['turibulo'], conjunto_restricao)
                naveta = sortear_pessoas(naveta_aptos, regras_qtd['naveta'], conjunto_restricao)
                tochas = sortear_pessoas(tochas_aptos, regras_qtd['tochas'], conjunto_restricao)
                
                # Adicionar todos os escalados ao conjunto do dia
                todos_escalados_esta_missa = set(cerimoniarios + veteranos + mirins + turibulo + naveta + tochas)
                escalados_no_dia_inteiro.update(todos_escalados_esta_missa)
                
                # Se for domingo, adicionar também ao conjunto de domingo para prevenir repetição entre manhã/noite
                if is_domingo:
                    escalados_domingo.update(todos_escalados_esta_missa)
                cursor.execute('''INSERT INTO escalas (data, tipo_escala, bata_cor, cerimoniarios, veteranos, mirins, turibulo, naveta, tochas)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (data_atual.strftime('%d/%m/%Y'), tipo_escala, 'Branca', juntar_nomes(cerimoniarios), juntar_nomes(veteranos), juntar_nomes(mirins), juntar_nomes(turibulo), juntar_nomes(naveta), juntar_nomes(tochas)))
                escalas_geradas += 1

            data_atual += timedelta(days=1)
        
        print(f"Total de escalas geradas: {escalas_geradas}")


        print("\n" + "="*50)
        print(f"RELATÓRIO DE FREQUÊNCIA PARA O MÊS {mes}/{ano}")
        print("="*50)

        serviram_0 = sorted([nome for nome, count in contagem_servicos.items() if count == 0])
        serviram_1 = sorted([nome for nome, count in contagem_servicos.items() if count == 1])
        serviram_2 = sorted([nome for nome, count in contagem_servicos.items() if count == 2])
        serviram_3_ou_mais = sorted([f"{nome} ({count}x)" for nome, count in contagem_servicos.items() if count >= 3])

        total_pessoas = len(contagem_servicos)
        pessoas_com_2_ou_mais = len([n for n, c in contagem_servicos.items() if c >= 2])
        percentual_meta = (pessoas_com_2_ou_mais / total_pessoas * 100) if total_pessoas > 0 else 0

        print(f"\n[META] Pessoas que serviram 2+ vezes: {pessoas_com_2_ou_mais}/{total_pessoas} ({percentual_meta:.1f}%)")
        
        # Priorizar exibição: mostrar primeiro quem precisa servir mais
        if serviram_0:
            print(f"\n[URGENTE] Não serviram nenhuma vez ({len(serviram_0)} pessoas) - PRECISAM SERVIR:")
            print(", ".join(serviram_0))
        
        if serviram_1:
            print(f"\n[ATENÇÃO] Serviram apenas 1 vez ({len(serviram_1)} pessoas) - PRECISAM SERVIR MAIS:")
            print(", ".join(serviram_1))
        
        if serviram_2:
            print(f"\n[OK] Serviram exatamente 2 vezes ({len(serviram_2)} pessoas) - META ATINGIDA:")
            print(", ".join(serviram_2))

        if serviram_3_ou_mais:
            print(f"\n[INFO] Serviram 3 ou mais vezes ({len(serviram_3_ou_mais)} pessoas):")
            print(", ".join(serviram_3_ou_mais))
        print("="*50 + "\n")
        # --- FIM DO RELATÓRIO ---

        db.commit()
        db.close()
        flash(f'Escalas geradas com sucesso para {mes}/{ano} com as novas regras de grupo!', 'success')
    except Exception as e:
        if db:
            try:
                db.rollback()
                db.close()
            except:
                pass
        import traceback
        error_msg = f"Erro ao gerar escala para {mes}/{ano}: {str(e)}"
        print(f"ERRO: {error_msg}")
        print(traceback.format_exc())
        flash(error_msg, 'error')
        raise  # Re-raise para ser capturado pela rota

def get_escala_por_id(escala_id):
    conn = get_db()
    try:
        escala = conn.execute('SELECT * FROM escalas WHERE id = ?', (escala_id,)).fetchone()
        return escala
    finally:
        conn.close()

def atualizar_escala(escala_id, dados):
    conn = get_db()
    try:
        conn.execute( '''UPDATE escalas SET bata_cor=?, cerimoniarios=?, veteranos=?, mirins=?, turibulo=?, naveta=?, tochas=? WHERE id=?''', (dados['bata_cor'], dados['cerimoniarios'], dados['veteranos'], dados['mirins'], dados['turibulo'], dados['naveta'], dados['tochas'], escala_id) )
        conn.commit(); flash('Escala atualizada com sucesso!', 'success')
    except Exception as e: flash(f'Erro ao atualizar a escala: {e}', 'error')
    finally: conn.close()


###############################################################
## ROTA PRINCIPAL (INDEX)
###############################################################
@app.route('/favicon.ico')
def favicon():
    """Evita erro 404 no log para favicon"""
    return '', 204

@app.route('/')
def index():
    hoje = datetime.today()
    mes = int(request.args.get('mes', hoje.month))
    ano = int(request.args.get('ano', hoje.year))
    filtro_nome = request.args.get('filtro_nome', None)

    conn = get_db()
    todas_as_pessoas = conn.execute("SELECT nome FROM pessoas ORDER BY nome").fetchall()
    date_filter, date_params = build_date_filter_query(mes, ano)
    query = f"SELECT * FROM escalas {date_filter}"
    params = list(date_params)

    if filtro_nome:
        query += " AND (cerimoniarios LIKE ? OR veteranos LIKE ? OR mirins LIKE ? OR turibulo LIKE ? OR naveta LIKE ? OR tochas LIKE ?)"
        for _ in range(6):
            params.append(f'%{filtro_nome}%')

    query += " ORDER BY data, tipo_escala"
    escalas = conn.execute(query, params).fetchall()
    conn.close()

    # Buscar horários dos dias_missa
    conn = get_db()
    dias_missa_horarios = {}
    try:
        dias_missa_rows = conn.execute('SELECT tipo_escala, horario FROM dias_missa WHERE ativo = 1').fetchall()
        for row in dias_missa_rows:
            dias_missa_horarios[row['tipo_escala']] = row['horario'] or ''
    except Exception as e:
        print(f"Erro ao buscar horários dos dias_missa: {e}")
    finally:
        conn.close()

    # Processar escalas para adicionar informações extras
    escalas_processadas = []
    calendar_events = []
    
    for escala in escalas:
        try:
            # Converter Row para dict se necessário
            escala_dict = dict(escala) if hasattr(escala, 'keys') else escala
            
            data_obj = datetime.strptime(escala_dict['data'], '%d/%m/%Y')
            data_correta_calendario = data_obj.strftime('%Y-%m-%d')
            
            # Formatar data para exibição
            dias_semana = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']
            meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            dia_semana_nome = dias_semana[data_obj.weekday()]
            mes_nome = meses_nomes[data_obj.month - 1]
            data_formatada = f"{dia_semana_nome}, {data_obj.day} De {mes_nome} De {data_obj.year}"
            
            # Obter horário
            horario = dias_missa_horarios.get(escala_dict.get('tipo_escala', ''), '')
            if not horario:
                tipo_escala = escala_dict.get('tipo_escala', '')
                if 'Manhã' in tipo_escala or 'Manha' in tipo_escala:
                    horario = '08:00'
                elif 'Noite' in tipo_escala:
                    horario = '19:00'
                else:
                    horario = '08:00'
            
            # Contar membros
            def contar_membros(campo):
                if not campo:
                    return 0
                return len([n for n in campo.split(', ') if n.strip()])
            
            total_membros = (contar_membros(escala_dict.get('cerimoniarios')) + 
                           contar_membros(escala_dict.get('veteranos')) + 
                           contar_membros(escala_dict.get('mirins')) + 
                           contar_membros(escala_dict.get('turibulo')) + 
                           contar_membros(escala_dict.get('naveta')) + 
                           contar_membros(escala_dict.get('tochas')))
            
            # Mapear cor da bata
            bata_cor = escala_dict.get('bata_cor') or 'Bata Branca'
            cor_class = 'branco'
            if 'Vermelha' in bata_cor or 'vermelha' in bata_cor or 'Vermelho' in bata_cor:
                cor_class = 'vermelho'
                bata_cor = 'Bata Vermelha'
            else:
                cor_class = 'branco'
                bata_cor = 'Bata Branca'
            
            # Adicionar informações extras à escala
            escala_dict['data_formatada'] = data_formatada
            escala_dict['horario'] = horario
            escala_dict['bata_cor_class'] = cor_class
            escala_dict['bata_cor'] = bata_cor
            escalas_processadas.append(escala_dict)
            
            # Preparar evento do calendário
            desc = ""
            if escala_dict.get('bata_cor'):
                desc += f"<b>Cor da Túnica:</b> {bata_cor}<br><br>"
            desc += f"<b>Cerimoniários:</b> {escala_dict.get('cerimoniarios') or ''}<br><b>Veteranos:</b> {escala_dict.get('veteranos') or ''}<br><b>Mirins:</b> {escala_dict.get('mirins') or ''}"
            if escala_dict.get('turibulo'): desc += f"<br><b>Turíbulo:</b> {escala_dict['turibulo']}"
            if escala_dict.get('naveta'): desc += f"<br><b>Naveta:</b> {escala_dict['naveta']}"
            if escala_dict.get('tochas'): desc += f"<br><b>Tochas:</b> {escala_dict['tochas']}"
            
            # Preparar membros estruturados por categoria (usando função auxiliar)
            members_structured = {
                'cerimoniarios': parsear_nomes(escala_dict.get('cerimoniarios')),
                'veteranos': parsear_nomes(escala_dict.get('veteranos')),
                'mirins': parsear_nomes(escala_dict.get('mirins')),
                'turibulo': parsear_nomes(escala_dict.get('turibulo')),
                'naveta': parsear_nomes(escala_dict.get('naveta')),
                'tochas': parsear_nomes(escala_dict.get('tochas'))
            }
            
            calendar_events.append({
                'id': escala_dict['id'],
                'title': escala_dict.get('tipo_escala', ''),
                'start': data_correta_calendario,
                'extendedProps': { 
                    'description': desc,
                    'bataCor': bata_cor,
                    'corClass': cor_class,
                    'horario': horario,
                    'memberCount': total_membros,
                    'members': members_structured
                },
                'classNames': [cor_class]
            })
        except (ValueError, TypeError) as e:
            continue

    # Nome do mês
    meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mes_nome = meses_nomes[mes - 1]

    return render_template('index.html',
                           escalas=escalas_processadas,
                           mes=mes,
                           ano=ano,
                           mes_nome=mes_nome,
                           todas_as_pessoas=todas_as_pessoas,
                           filtro_nome_ativo=filtro_nome,
                           calendar_events=calendar_events,
                           is_view_only=False)


@app.route('/visualizar')
def visualizar_escala():
    """
    Nova rota para a visualização pública da escala, sem painéis de admin.
    """
    hoje = datetime.today()
    mes = int(request.args.get('mes', hoje.month))
    ano = int(request.args.get('ano', hoje.year))
    filtro_nome = request.args.get('filtro_nome', None)

    conn = get_db()
    todas_as_pessoas = conn.execute("SELECT nome FROM pessoas ORDER BY nome").fetchall()

    date_filter, date_params = build_date_filter_query(mes, ano)
    query = f"SELECT * FROM escalas {date_filter}"
    params = list(date_params)
    if filtro_nome:
        query += " AND (cerimoniarios LIKE ? OR veteranos LIKE ? OR mirins LIKE ? OR turibulo LIKE ? OR naveta LIKE ? OR tochas LIKE ?)"
        for _ in range(6):
            params.append(f'%{filtro_nome}%')
    query += " ORDER BY data, tipo_escala"

    escalas = conn.execute(query, params).fetchall()
    conn.close()

    # Buscar horários dos dias_missa
    conn = get_db()
    dias_missa_horarios = {}
    try:
        dias_missa_rows = conn.execute('SELECT tipo_escala, horario FROM dias_missa WHERE ativo = 1').fetchall()
        for row in dias_missa_rows:
            dias_missa_horarios[row['tipo_escala']] = row['horario'] or ''
    except Exception as e:
        print(f"Erro ao buscar horários dos dias_missa: {e}")
    finally:
        conn.close()

    # Processar escalas para adicionar informações extras
    escalas_processadas = []
    calendar_events = []
    
    for escala in escalas:
        try:
            # Converter Row para dict se necessário
            escala_dict = dict(escala) if hasattr(escala, 'keys') else escala
            
            data_obj = datetime.strptime(escala_dict['data'], '%d/%m/%Y')
            data_correta_calendario = data_obj.strftime('%Y-%m-%d')
            
            # Formatar data para exibição
            dias_semana = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']
            meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            dia_semana_nome = dias_semana[data_obj.weekday()]
            mes_nome = meses_nomes[data_obj.month - 1]
            data_formatada = f"{dia_semana_nome}, {data_obj.day} De {mes_nome} De {data_obj.year}"
            
            # Obter horário
            horario = dias_missa_horarios.get(escala_dict.get('tipo_escala', ''), '')
            if not horario:
                tipo_escala = escala_dict.get('tipo_escala', '')
                if 'Manhã' in tipo_escala or 'Manha' in tipo_escala:
                    horario = '08:00'
                elif 'Noite' in tipo_escala:
                    horario = '19:00'
                else:
                    horario = '08:00'
            
            # Contar membros
            def contar_membros(campo):
                if not campo:
                    return 0
                return len([n for n in campo.split(', ') if n.strip()])
            
            total_membros = (contar_membros(escala_dict.get('cerimoniarios')) + 
                           contar_membros(escala_dict.get('veteranos')) + 
                           contar_membros(escala_dict.get('mirins')) + 
                           contar_membros(escala_dict.get('turibulo')) + 
                           contar_membros(escala_dict.get('naveta')) + 
                           contar_membros(escala_dict.get('tochas')))
            
            # Mapear cor da bata
            bata_cor = escala_dict.get('bata_cor') or 'Bata Branca'
            cor_class = 'branco'
            if 'Vermelha' in bata_cor or 'vermelha' in bata_cor or 'Vermelho' in bata_cor:
                cor_class = 'vermelho'
                bata_cor = 'Bata Vermelha'
            else:
                cor_class = 'branco'
                bata_cor = 'Bata Branca'
            
            # Adicionar informações extras à escala
            escala_dict['data_formatada'] = data_formatada
            escala_dict['horario'] = horario
            escala_dict['bata_cor_class'] = cor_class
            escala_dict['bata_cor'] = bata_cor
            escalas_processadas.append(escala_dict)
            
            # Preparar evento do calendário
            desc = f"<b>Cor da Túnica:</b> {bata_cor}<br><br>"
            desc += f"<b>Cerimoniários:</b> {escala_dict.get('cerimoniarios') or ''}<br><b>Veteranos:</b> {escala_dict.get('veteranos') or ''}<br><b>Mirins:</b> {escala_dict.get('mirins') or ''}"
            if escala_dict.get('turibulo'): desc += f"<br><b>Turíbulo:</b> {escala_dict['turibulo']}"
            if escala_dict.get('naveta'): desc += f"<br><b>Naveta:</b> {escala_dict['naveta']}"
            if escala_dict.get('tochas'): desc += f"<br><b>Tochas:</b> {escala_dict['tochas']}"

            # Preparar membros estruturados por categoria (usando função auxiliar)
            members_structured = {
                'cerimoniarios': parsear_nomes(escala_dict.get('cerimoniarios')),
                'veteranos': parsear_nomes(escala_dict.get('veteranos')),
                'mirins': parsear_nomes(escala_dict.get('mirins')),
                'turibulo': parsear_nomes(escala_dict.get('turibulo')),
                'naveta': parsear_nomes(escala_dict.get('naveta')),
                'tochas': parsear_nomes(escala_dict.get('tochas'))
            }

            calendar_events.append({
                'id': escala_dict['id'], 
                'title': escala_dict.get('tipo_escala', ''), 
                'start': data_correta_calendario,
                'extendedProps': { 
                    'description': desc,
                    'bataCor': bata_cor,
                    'corClass': cor_class,
                    'horario': horario,
                    'memberCount': total_membros,
                    'members': members_structured
                },
                'classNames': [cor_class]
            })
        except (ValueError, TypeError) as e:
            continue

    # Nome do mês
    meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mes_nome = meses_nomes[mes - 1]

    return render_template('index.html',
                           escalas=escalas_processadas, mes=mes, ano=ano, mes_nome=mes_nome,
                           todas_as_pessoas=todas_as_pessoas,
                           filtro_nome_ativo=filtro_nome,
                           calendar_events=calendar_events,
                           is_view_only=True)

###############################################################
## ROTAS DE AÇÃO E GERENCIAMENTO
###############################################################
@app.route('/gerar_escala', methods=['POST'])
def gerar_escala_web():
    try:
        mes = int(request.form['mes'])
        ano = int(request.form['ano'])
        
        # Validação básica
        if mes < 1 or mes > 12:
            flash(f'Erro: Mês inválido ({mes}). Deve ser entre 1 e 12.', 'error')
            return redirect(url_for('index', mes=mes if 1 <= mes <= 12 else datetime.today().month, ano=ano))
        
        if ano < 2020 or ano > 2050:
            flash(f'Erro: Ano inválido ({ano}). Deve ser entre 2020 e 2050.', 'error')
            return redirect(url_for('index', mes=mes, ano=datetime.today().year))
        
        print(f"Iniciando geração de escala para {mes}/{ano}...")
        try:
            gerar_escala_para_mes(mes, ano)
            print(f"Escala gerada com sucesso para {mes}/{ano}")
            return redirect(url_for('index', mes=mes, ano=ano))
        except Exception as e:
            # Re-raise para ser capturado pelo except externo
            raise
    except ValueError as e:
        error_msg = f'Erro ao processar os dados: {str(e)}'
        flash(error_msg, 'error')
        print(f"ERRO (ValueError): {error_msg}")
        return redirect(url_for('index', mes=mes if 1 <= mes <= 12 else datetime.today().month, ano=ano))
    except Exception as e:
        import traceback
        error_msg = f'Erro inesperado ao gerar escala: {str(e)}'
        flash(error_msg, 'error')
        print(f"ERRO (Exception): {error_msg}")
        print(f"Traceback completo:\n{traceback.format_exc()}")
        return redirect(url_for('index', mes=mes if 1 <= mes <= 12 else datetime.today().month, ano=ano))

@app.route('/reiniciar_db', methods=['POST'])
def reiniciar_db_web():
    limpar_db_e_reimportar()
    return redirect(url_for('index'))

@app.route('/gerenciar_pessoas')
def gerenciar_pessoas_web():
    conn = get_db()
    todas_as_pessoas = conn.execute("SELECT * FROM pessoas ORDER BY nome").fetchall()
    conn.close()
    mestres_de_cerimonia = [p for p in todas_as_pessoas if p['grupo'] == GRUPO_CERIMONIARIO]
    experientes = [p for p in todas_as_pessoas if p['grupo'] == GRUPO_VETERANO]
    mirins = [p for p in todas_as_pessoas if p['grupo'] == GRUPO_MIRINS]
    # Debug: verificar se está lendo corretamente
    print(f"[DEBUG] Total de pessoas lidas: {len(todas_as_pessoas)}")
    print(f"[DEBUG] Mestres: {len(mestres_de_cerimonia)}, Experientes: {len(experientes)}, Mirins: {len(mirins)}")
    return render_template('gerenciar_pessoas.html', mestres_de_cerimonia=mestres_de_cerimonia, experientes=experientes, mirins=mirins)

@app.route('/adicionar_pessoa', methods=['POST'])
def adicionar_pessoa_web():
    nome = request.form['nome'].strip()
    grupo = request.form['grupo'].strip()
    funcoes = ','.join(request.form.getlist('funcoes'))
    if nome and grupo:
        conn = get_db()
        try:
            conn.execute('INSERT INTO pessoas (nome, grupo, funcoes) VALUES (?, ?, ?)', (nome, grupo, funcoes))
            conn.commit()
            flash(f'"{nome}" adicionado(a) com sucesso!', 'success')
        except IntegrityError:
            flash(f'Erro: Já existe uma pessoa com o nome "{nome}".', 'error')
        finally:
            conn.close()
    else:
        flash('Erro: Nome e grupo são obrigatórios.', 'error')
    return redirect(url_for('gerenciar_pessoas_web'))

@app.route('/remover_pessoa/<int:pessoa_id>', methods=['POST'])
def remover_pessoa_web(pessoa_id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM pessoas WHERE id = ?', (pessoa_id,))
        conn.commit()
        flash('Pessoa removida com sucesso!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao remover pessoa: {str(e)}', 'error')
        print(f"ERRO ao remover pessoa: {e}")
    finally:
        conn.close()
    return redirect(url_for('gerenciar_pessoas_web'))

@app.route('/editar_pessoa/<int:pessoa_id>', methods=['GET', 'POST'])
def editar_pessoa_web(pessoa_id):
    conn = get_db()
    try:
        pessoa = conn.execute('SELECT * FROM pessoas WHERE id = ?', (pessoa_id,)).fetchone()
        if pessoa is None:
            flash('Pessoa não encontrada.', 'error')
            return redirect(url_for('gerenciar_pessoas_web'))
        
        if request.method == 'POST':
            novo_grupo = request.form['grupo']
            novas_funcoes = ','.join(request.form.getlist('funcoes'))
            conn.execute('UPDATE pessoas SET grupo = ?, funcoes = ? WHERE id = ?', (novo_grupo, novas_funcoes, pessoa_id))
            conn.commit()
            flash(f'Dados de "{pessoa["nome"]}" atualizados com sucesso!', 'success')
            return redirect(url_for('gerenciar_pessoas_web'))
        
        return render_template('editar_pessoa.html', pessoa=pessoa)
    except Exception as e:
        flash(f'Erro ao processar: {str(e)}', 'error')
        return redirect(url_for('gerenciar_pessoas_web'))
    finally:
        conn.close()

# Em app.py, substitua a função inteira

@app.route('/editar_escala/<int:escala_id>', methods=['GET', 'POST'])
def editar_escala_web(escala_id):
    if request.method == 'POST':
        dados = {
            'bata_cor': request.form.get('bata_cor'),
            'cerimoniarios': juntar_nomes(request.form.getlist('cerimoniarios')),
            'veteranos': juntar_nomes(request.form.getlist('veteranos')),
            'mirins': juntar_nomes(request.form.getlist('mirins')),
            'turibulo': juntar_nomes(request.form.getlist('turibulo')),
            'naveta': juntar_nomes(request.form.getlist('naveta')),
            'tochas': juntar_nomes(request.form.getlist('tochas'))
        }
        atualizar_escala(escala_id, dados)
        escala = get_escala_por_id(escala_id)
        data_obj = datetime.strptime(escala['data'], '%d/%m/%Y')
        return redirect(url_for('index', mes=data_obj.month, ano=data_obj.year))

    escala = get_escala_por_id(escala_id)
    if not escala:
        flash('Escala não encontrada.', 'error')
        return redirect(url_for('index'))

    escala_editavel = dict(escala)
    for key in ['cerimoniarios', 'veteranos', 'mirins', 'turibulo', 'naveta', 'tochas']:
        if key in escala_editavel and escala_editavel[key]:
            # Usar função auxiliar para parsear nomes
            escala_editavel[key] = parsear_nomes(escala_editavel[key])
        else:
            escala_editavel[key] = []

    conn = get_db()

    # 1. Pega a lista de todas as pessoas que PERTENCEM atualmente a cada grupo
    todos_cerimoniarios_atuais = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_CERIMONIARIO,))]
    todos_veteranos_atuais = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_VETERANO,))]
    todas_mirins_atuais = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_MIRINS,))]

    # 2. Une a lista atual com a lista de quem JÁ ESTAVA selecionado na escala,
    opcoes_cerimoniarios = sorted(list(set(todos_cerimoniarios_atuais + escala_editavel['cerimoniarios'])))
    opcoes_veteranos = sorted(list(set(todos_veteranos_atuais + escala_editavel['veteranos'])))
    opcoes_mirins = sorted(list(set(todas_mirins_atuais + escala_editavel['mirins'])))

    # Buscar TODAS as pessoas para disponibilizar em Turíbulo, Naveta e Tochas
    todas_as_pessoas = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas ORDER BY nome").fetchall()]
    
    # Incluir também os nomes já selecionados (caso não estejam mais no banco)
    candidatos_funcoes = sorted(list(set(
        todas_as_pessoas +
        escala_editavel['turibulo'] +
        escala_editavel['naveta'] +
        escala_editavel['tochas']
    )))

    conn.close()

    # Buscar horário do dias_missa (usando função auxiliar)
    conn = get_db()
    dias_missa_horarios = {}
    try:
        dias_missa_rows = conn.execute('SELECT tipo_escala, horario FROM dias_missa WHERE ativo = 1').fetchall()
        for row in dias_missa_rows:
            dias_missa_horarios[row['tipo_escala']] = row['horario'] or ''
    except:
        pass
    conn.close()
    
    horario = obter_horario_por_tipo_escala(escala['tipo_escala'], dias_missa_horarios)
    
    # Formatar data (usando função auxiliar)
    try:
        data_obj = datetime.strptime(escala['data'], '%d/%m/%Y')
        data_formatada = formatar_data_pt_br(data_obj)
    except (ValueError, TypeError) as e:
        print(f"Erro ao formatar data: {e}")
        data_formatada = escala['data']
    
    escala_editavel['horario'] = horario
    escala_editavel['data_formatada'] = data_formatada

    return render_template('editar_escala.html',
                           escala=escala_editavel,
                           todos_cerimoniarios=opcoes_cerimoniarios,
                           todos_veteranos=opcoes_veteranos,
                           todas_mirins=opcoes_mirins,
                           candidatos_funcoes=candidatos_funcoes)

@app.route('/adicionar_escala/<int:ano>/<int:mes>/<int:dia>')
def adicionar_escala_web(ano, mes, dia):
    try:
        data_obj = datetime(ano, mes, dia)
        data_para_db = data_obj.strftime('%d/%m/%Y')
        # Formatar data para exibição (usando função auxiliar)
        data_para_exibir = formatar_data_pt_br(data_obj)
        conn = get_db()
        
        try:
            # Buscar escalas existentes para este dia
            escalas_existentes = conn.execute(
                "SELECT * FROM escalas WHERE data = ? ORDER BY tipo_escala",
                (data_para_db,)
            ).fetchall()
            
            todos_cerimoniarios = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_CERIMONIARIO,)).fetchall()]
            todos_veteranos = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_VETERANO,)).fetchall()]
            todas_mirins = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_MIRINS,)).fetchall()]
            # Buscar TODAS as pessoas para disponibilizar em Turíbulo, Naveta e Tochas
            todas_as_pessoas = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas ORDER BY nome").fetchall()]
            candidatos_funcoes = sorted(todas_as_pessoas)
        finally:
            conn.close()
        
        return render_template('adicionar_escala.html', data_para_db=data_para_db, data_para_exibir=data_para_exibir, todos_cerimoniarios=todos_cerimoniarios, todos_veteranos=todos_veteranos, todas_mirins=todas_mirins, candidatos_funcoes=candidatos_funcoes, escalas_existentes=escalas_existentes)
    except (ValueError, TypeError) as e:
        flash(f'Erro ao processar data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/salvar_nova_escala', methods=['POST'])
def salvar_nova_escala_web():
    try:
        data = request.form.get('data', '').strip()
        tipo_escala = request.form.get('tipo_escala', '').strip()
        bata_cor = request.form.get('bata_cor', 'Bata Branca')
        cerimoniarios = juntar_nomes(request.form.getlist('cerimoniarios'))
        veteranos = juntar_nomes(request.form.getlist('veteranos'))
        mirins = juntar_nomes(request.form.getlist('mirins'))
        turibulo = juntar_nomes(request.form.getlist('turibulo'))
        naveta = juntar_nomes(request.form.getlist('naveta'))
        tochas = juntar_nomes(request.form.getlist('tochas'))
        adicionar_outro = request.form.get('adicionar_outro', '0')
        
        if not data or not tipo_escala:
            flash('Erro: Data e tipo de escala são obrigatórios.', 'error')
            return redirect(url_for('index'))
        
        conn = get_db()
        try:
            conn.execute('INSERT INTO escalas (data, tipo_escala, bata_cor, cerimoniarios, veteranos, mirins, turibulo, naveta, tochas) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (data, tipo_escala, bata_cor, cerimoniarios, veteranos, mirins, turibulo, naveta, tochas))
            conn.commit()
            flash(f'Nova escala para {data} foi adicionada com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao adicionar escala: {str(e)}', 'error')
            print(f"ERRO ao adicionar escala: {e}")
            return redirect(url_for('index'))
        finally:
            conn.close()
        
        try:
            data_obj = datetime.strptime(data, '%d/%m/%Y')
            # Se o usuário clicou em "Salvar e Adicionar Outro", redirecionar para a mesma página
            if adicionar_outro == '1':
                return redirect(url_for('adicionar_escala_web', ano=data_obj.year, mes=data_obj.month, dia=data_obj.day))
            return redirect(url_for('index', mes=data_obj.month, ano=data_obj.year))
        except (ValueError, TypeError):
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro ao processar formulário: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/remover_escala/<int:escala_id>', methods=['POST'])
def remover_escala_web(escala_id):
    conn = get_db()
    try:
        escala = conn.execute('SELECT data FROM escalas WHERE id = ?', (escala_id,)).fetchone()
        if escala:
            conn.execute('DELETE FROM escalas WHERE id = ?', (escala_id,))
            conn.commit()
            flash('Escala removida com sucesso!', 'success')
            try:
                data_obj = datetime.strptime(escala['data'], '%d/%m/%Y')
                return redirect(url_for('index', mes=data_obj.month, ano=data_obj.year))
            except (ValueError, TypeError):
                return redirect(url_for('index'))
        else:
            flash('Erro: Escala não encontrada.', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao remover escala: {str(e)}', 'error')
        print(f"ERRO ao remover escala: {e}")
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/gerenciar_modelos')
def gerenciar_modelos_web():
    conn = get_db()
    try:
        templates = conn.execute("SELECT * FROM escala_templates ORDER BY tipo_escala").fetchall()
        return render_template('gerenciar_modelos.html', templates=templates)
    except Exception as e:
        flash(f'Erro ao carregar modelos: {str(e)}', 'error')
        return render_template('gerenciar_modelos.html', templates=[])
    finally:
        conn.close()

@app.route('/editar_modelo/<tipo_escala>', methods=['GET'])
def editar_modelo_web(tipo_escala):
    conn = get_db()
    try:
        template = conn.execute('SELECT * FROM escala_templates WHERE tipo_escala = ?', (tipo_escala,)).fetchone()
        if template is None:
            flash(f'Modelo "{tipo_escala}" não encontrado.', 'error')
            return redirect(url_for('gerenciar_modelos_web'))
        
        # Filtrar pessoas por grupo para cada campo
        cerimoniarios = [row['nome'] for row in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_CERIMONIARIO,)).fetchall()]
        veteranos = [row['nome'] for row in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_VETERANO,)).fetchall()]
        mirins = [row['nome'] for row in conn.execute("SELECT nome FROM pessoas WHERE grupo = ? ORDER BY nome", (GRUPO_MIRINS,)).fetchall()]
        
        # Para funções especiais, permitir cerimoniários e veteranos
        # Buscar TODAS as pessoas para disponibilizar em Turíbulo, Naveta e Tochas
        todas_as_pessoas = [p['nome'] for p in conn.execute("SELECT nome FROM pessoas ORDER BY nome").fetchall()]
        candidatos_funcoes = sorted(todas_as_pessoas)
        
        return render_template('editar_modelo.html', 
                             template=template, 
                             cerimoniarios=cerimoniarios,
                             veteranos=veteranos,
                             mirins=mirins,
                             candidatos_funcoes=candidatos_funcoes)
    except Exception as e:
        flash(f'Erro ao carregar modelo: {str(e)}', 'error')
        return redirect(url_for('gerenciar_modelos_web'))
    finally:
        conn.close()

@app.route('/atualizar_modelo/<tipo_escala>', methods=['POST'])
def atualizar_modelo_web(tipo_escala):
    cerimoniarios = juntar_nomes(request.form.getlist('cerimoniarios'))
    veteranos = juntar_nomes(request.form.getlist('veteranos'))
    mirins = juntar_nomes(request.form.getlist('mirins'))
    turibulo = juntar_nomes(request.form.getlist('turibulo'))
    naveta = juntar_nomes(request.form.getlist('naveta'))
    tochas = juntar_nomes(request.form.getlist('tochas'))
    conn = get_db()
    try:
        conn.execute(''' UPDATE escala_templates SET cerimoniarios_template = ?, veteranos_template = ?, mirins_template = ?, turibulo_template = ?, naveta_template = ?, tochas_template = ? WHERE tipo_escala = ? ''', (cerimoniarios, veteranos, mirins, turibulo, naveta, tochas, tipo_escala))
        conn.commit()
        flash(f'Modelo "{tipo_escala}" atualizado com sucesso!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao atualizar modelo: {str(e)}', 'error')
        print(f"ERRO ao atualizar modelo: {e}")
    finally:
        conn.close()
    return redirect(url_for('gerenciar_modelos_web'))

# Em app.py

@app.route('/exportar/<int:ano>/<int:mes>')
def exportar_mes(ano, mes):
    conn = get_db()
    try:
        date_filter, date_params = build_date_filter_query(mes, ano)
        escalas_db = conn.execute(
            f"SELECT * FROM escalas {date_filter} ORDER BY data, tipo_escala",
            date_params
        ).fetchall()
    finally:
        conn.close()

    if not escalas_db:
        flash(f"Nenhuma escala encontrada para {mes}/{ano} para exportar.", 'warning')
        return redirect(url_for('index', mes=mes, ano=ano))

    try:
        # Converte os dados para um DataFrame do pandas
        df = pd.DataFrame([dict(row) for row in escalas_db])
        # Remove colunas que não são úteis na exportação
        if 'id' in df.columns: df = df.drop(columns=['id'])
        if 'bata_cor' in df.columns: df = df.drop(columns=['bata_cor'])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name=f'Escalas_{mes}_{ano}')
            # Opcional: Ajusta a largura das colunas
            for column in df:
                column_length = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                writer.sheets[f'Escalas_{mes}_{ano}'].set_column(col_idx, col_idx, column_length + 2)

        output.seek(0)

        nome_arquivo = f"escala_coroinhas_{mes}_{ano}.xlsx"

        # Envia o arquivo para o navegador
        return send_file(
            output,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"ERRO AO EXPORTAR EXCEL: {e}")
        flash(f"Ocorreu um erro ao gerar o arquivo Excel: {e}", 'error')
        return redirect(url_for('index', mes=mes, ano=ano))

@app.route('/exportar_modelo/<tipo_escala>')
def exportar_modelo_web(tipo_escala):
    conn = get_db()
    try:
        template = conn.execute('SELECT * FROM escala_templates WHERE tipo_escala = ?', (tipo_escala,)).fetchone()
        if not template:
            flash(f'Modelo "{tipo_escala}" não encontrado.', 'error')
            return redirect(url_for('gerenciar_modelos_web'))
    finally:
        conn.close()
    
    # Função auxiliar para acessar chaves do template com segurança
    def get_template_value(key, default=''):
        try:
            val = template[key] if key in template.keys() else default
            return val if val else default
        except (KeyError, IndexError):
            return default
    
    try:
        dados = { 
            'Cerimoniarios': parsear_nomes(get_template_value('cerimoniarios_template', '')), 
            'Veteranos': parsear_nomes(get_template_value('veteranos_template', '')), 
            'Mirins': parsear_nomes(get_template_value('mirins_template', '')), 
            'Turibulo': parsear_nomes(get_template_value('turibulo_template', '')), 
            'Naveta': parsear_nomes(get_template_value('naveta_template', '')), 
            'Tochas': parsear_nomes(get_template_value('tochas_template', '')) 
        }
        df = pd.DataFrame.from_dict(dados, orient='index').transpose()
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name=tipo_escala)
        output.seek(0)
        nome_arquivo = f"modelo_{tipo_escala.replace(' ', '_')}.xlsx"
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=nome_arquivo)
    except Exception as e:
        print(f"ERRO AO EXPORTAR MODELO: {e}")
        flash(f"Ocorreu um erro ao gerar o arquivo Excel: {e}", 'error')
        return redirect(url_for('gerenciar_modelos_web'))

@app.route('/limpar_mes', methods=['POST'])
def limpar_mes_web():
    try:
        mes = int(request.form['mes'])
        ano = int(request.form['ano'])
        
        # Validação básica
        if mes < 1 or mes > 12:
            flash(f'Erro: Mês inválido ({mes}). Deve ser entre 1 e 12.', 'error')
            return redirect(url_for('index', mes=mes if 1 <= mes <= 12 else datetime.today().month, ano=ano))
        
        if ano < 2000 or ano > 2100:
            flash(f'Erro: Ano inválido ({ano}). Deve ser entre 2000 e 2100.', 'error')
            return redirect(url_for('index', mes=mes, ano=datetime.today().year))
        
        conn = get_db()
        try:
            # Contar quantas escalas serão removidas
            date_filter, date_params = build_date_filter_query(mes, ano)
            count_query = f"SELECT COUNT(*) as total FROM escalas {date_filter}"
            count_result = conn.execute(count_query, date_params).fetchone()
            total_escalas = count_result['total'] if count_result else 0
            
            if total_escalas == 0:
                flash(f"Nenhuma escala encontrada para o mês {mes}/{ano}.", 'warning')
                return redirect(url_for('index', mes=mes, ano=ano))
            
            # Deletar as escalas
            date_filter, date_params = build_date_filter_query(mes, ano)
            conn.execute(f"DELETE FROM escalas {date_filter}", date_params)
            conn.commit()
            flash(f"Todas as {total_escalas} escala(s) do mês {mes}/{ano} foram apagadas com sucesso.", 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao limpar escalas do mês {mes}/{ano}: {str(e)}', 'error')
            print(f"ERRO ao limpar mês: {e}")
        finally:
            conn.close()
        
        return redirect(url_for('index', mes=mes, ano=ano))
    except (ValueError, KeyError) as e:
        flash(f'Erro ao processar os dados: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/forcar_populacao_modelos_12345')
def forcar_populacao_modelos():
    try:
        popular_templates_iniciais()
        flash("Tentativa de popular os modelos foi executada com sucesso!", "success")
    except Exception as e:
        flash(f"Ocorreu um erro ao tentar popular os modelos: {e}", "error")
        print(f"ERRO AO FORÇAR POPULAÇÃO: {e}")

    return redirect(url_for('gerenciar_modelos_web'))

@app.route('/gerenciar_dias_missa')
def gerenciar_dias_missa_web():
    conn = get_db()
    try:
        dias_missa = conn.execute('SELECT * FROM dias_missa ORDER BY ordem, dia_semana').fetchall()
        todos_tipos = conn.execute('SELECT tipo_escala FROM escala_templates ORDER BY tipo_escala').fetchall()
        nomes_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        return render_template('gerenciar_dias_missa.html', dias_missa=dias_missa, todos_tipos=todos_tipos, nomes_dias=nomes_dias)
    except Exception as e:
        flash(f'Erro ao carregar dias de missa: {str(e)}', 'error')
        return render_template('gerenciar_dias_missa.html', dias_missa=[], todos_tipos=[], nomes_dias=['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'])
    finally:
        conn.close()

@app.route('/adicionar_dia_missa', methods=['POST'])
def adicionar_dia_missa_web():
    try:
        dia_semana = int(request.form.get('dia_semana', 0))
        tipo_escala = request.form.get('tipo_escala', '').strip()
        horario = request.form.get('horario', '').strip()
        ativo = 1 if request.form.get('ativo') == 'on' else 0
        
        if not tipo_escala or dia_semana < 0 or dia_semana > 6:
            flash('Erro: Dados inválidos.', 'error')
            return redirect(url_for('gerenciar_dias_missa_web'))
        
        conn = get_db()
        try:
            # Buscar maior ordem atual
            max_ordem_result = conn.execute('SELECT MAX(ordem) as max_ord FROM dias_missa').fetchone()
            max_ordem = max_ordem_result['max_ord'] if max_ordem_result and max_ordem_result['max_ord'] else 0
            conn.execute('INSERT INTO dias_missa (dia_semana, tipo_escala, horario, ativo, ordem) VALUES (?, ?, ?, ?, ?)',
                        (dia_semana, tipo_escala, horario, ativo, max_ordem + 1))
            conn.commit()
            flash('Dia de missa adicionado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao adicionar dia de missa: {str(e)}', 'error')
            print(f"ERRO ao adicionar dia de missa: {e}")
        finally:
            conn.close()
        return redirect(url_for('gerenciar_dias_missa_web'))
    except (ValueError, KeyError) as e:
        flash(f'Erro ao processar dados: {str(e)}', 'error')
        return redirect(url_for('gerenciar_dias_missa_web'))

@app.route('/editar_dia_missa/<int:dia_id>', methods=['POST'])
def editar_dia_missa_web(dia_id):
    try:
        dia_semana = int(request.form.get('dia_semana', 0))
        tipo_escala = request.form.get('tipo_escala', '').strip()
        horario = request.form.get('horario', '').strip()
        ativo = 1 if request.form.get('ativo') == 'on' else 0
        ordem = int(request.form.get('ordem', 0))
        
        if not tipo_escala or dia_semana < 0 or dia_semana > 6:
            flash('Erro: Dados inválidos.', 'error')
            return redirect(url_for('gerenciar_dias_missa_web'))
        
        conn = get_db()
        try:
            conn.execute('UPDATE dias_missa SET dia_semana=?, tipo_escala=?, horario=?, ativo=?, ordem=? WHERE id=?',
                        (dia_semana, tipo_escala, horario, ativo, ordem, dia_id))
            conn.commit()
            flash('Dia de missa atualizado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao atualizar dia de missa: {str(e)}', 'error')
            print(f"ERRO ao atualizar dia de missa: {e}")
        finally:
            conn.close()
        return redirect(url_for('gerenciar_dias_missa_web'))
    except (ValueError, KeyError) as e:
        flash(f'Erro ao processar dados: {str(e)}', 'error')
        return redirect(url_for('gerenciar_dias_missa_web'))

@app.route('/remover_dia_missa/<int:dia_id>', methods=['POST'])
def remover_dia_missa_web(dia_id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM dias_missa WHERE id = ?', (dia_id,))
        conn.commit()
        flash('Dia de missa removido com sucesso!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao remover dia de missa: {str(e)}', 'error')
        print(f"ERRO ao remover dia de missa: {e}")
    finally:
        conn.close()
    return redirect(url_for('gerenciar_dias_missa_web'))


def contar_frequencia_no_mes(mes, ano):
    """
    Busca todas as escalas de um mês e conta quantas vezes cada pessoa aparece.
    Retorna um dicionário {'Nome': contagem}.
    """
    conn = get_db()
    date_filter, date_params = build_date_filter_query(mes, ano)
    escalas = conn.execute(
        f"SELECT * FROM escalas {date_filter}",
        date_params
    ).fetchall()
    conn.close()

    contagem = {}
    if not escalas:
        return contagem

    for escala in escalas:
        for funcao in ['cerimoniarios', 'veteranos', 'mirins', 'turibulo', 'naveta', 'tochas']:
            valor = escala[funcao] if funcao in escala.keys() else None
            if valor:
                # Usar função auxiliar para parsear nomes
                nomes = parsear_nomes(valor)
                for nome in nomes:
                    contagem[nome] = contagem.get(nome, 0) + 1

    return contagem

@app.route('/relatorio_frequencia')
def relatorio_frequencia_web():
    """
    Rota para a nova página que exibe o relatório de frequência.
    """
    hoje = datetime.today()
    mes = int(request.args.get('mes', hoje.month))
    ano = int(request.args.get('ano', hoje.year))

    frequencia = contar_frequencia_no_mes(mes, ano)
    frequencia_ordenada = sorted(frequencia.items(), key=lambda item: item[1], reverse=True)

    return render_template('relatorio.html',
                           mes=mes,
                           ano=ano,
                           frequencia=frequencia_ordenada)


@app.route('/cadastrar_pessoas', methods=['GET', 'POST'])
def cadastrar_pessoas():
    """Rota administrativa para cadastrar todas as pessoas em massa"""
    # Dados das pessoas para cadastrar
    pessoas_para_cadastrar = {
        'cerimoniario': [
            "Alejandro", "João Pedro", "Pedro Reis", "Adriano",
            "Lucas", "André", "Pedro Barroso"
        ],
        'veterano': [
            "Ana Julia", "Vitória", "Sofia Reis", "Armando", "Karla",
            "Mateus", "João Raffael", "Pedro Cutrim", "Gabriel Mendes"
        ],
        'mirins': [
            "João Gabriel", "Luiza", "Miguel", "Rafael", "Antony",
            "Maria Celida", "Cauan", "Theo", "Alexia", "Davi Barbalho",
            "Helisa", "Thiago Alex", "Gabriel Carvalho", "Mariana Jansen",
            "Bernardo"
        ]
    }
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        total_cadastrados = 0
        total_ignorados = 0
        pessoas_cadastradas = []
        pessoas_ignoradas = []
        
        # Itera sobre cada grupo e sua lista de nomes
        for grupo, nomes in pessoas_para_cadastrar.items():
            for nome in nomes:
                nome_limpo = nome.strip()
                
                # Verifica se a pessoa já existe no banco
                cursor.execute("SELECT grupo FROM pessoas WHERE nome = ?", (nome_limpo,))
                pessoa_existente = cursor.fetchone()
                
                if pessoa_existente:
                    grupo_existente = pessoa_existente[0]
                    if grupo_existente == grupo:
                        pessoas_ignoradas.append(f"'{nome_limpo}' já está cadastrado(a) no grupo '{grupo}'")
                    else:
                        pessoas_ignoradas.append(f"'{nome_limpo}' já existe no grupo '{grupo_existente}' (não alterado para '{grupo}')")
                    total_ignorados += 1
                else:
                    # Pessoa não existe, pode cadastrar
                    try:
                        cursor.execute(
                            "INSERT INTO pessoas (nome, grupo, funcoes) VALUES (?, ?, ?)",
                            (nome_limpo, grupo, '')
                        )
                        pessoas_cadastradas.append(f"'{nome_limpo}' cadastrado(a) no grupo '{grupo}'")
                        total_cadastrados += 1
                    except IntegrityError:
                        pessoas_ignoradas.append(f"Erro ao cadastrar '{nome_limpo}' (pode já existir)")
                        total_ignorados += 1
        
        conn.commit()
        conn.close()
        
        mensagem = f"Cadastro concluído! {total_cadastrados} pessoas novas cadastradas, {total_ignorados} nomes ignorados."
        flash(mensagem, 'success')
        
        # Retornar página com resultado
        return render_template('cadastro_pessoas_resultado.html',
                             total_cadastrados=total_cadastrados,
                             total_ignorados=total_ignorados,
                             pessoas_cadastradas=pessoas_cadastradas,
                             pessoas_ignoradas=pessoas_ignoradas)
        
    except Exception as e:
        flash(f'Erro ao cadastrar pessoas: {str(e)}', 'error')
        return redirect(url_for('index'))


# Inicialização do banco de dados (executada apenas uma vez)
# Na Vercel, isso será executado automaticamente quando a função for chamada pela primeira vez
def init_app():
    """Inicializa a aplicação e o banco de dados"""
    with app.app_context():
        init_db()
        importar_dados_iniciais_do_excel()
        popular_templates_iniciais()
        popular_dias_missa_iniciais()
        
        # Cadastrar pessoas automaticamente se o banco estiver vazio
        db = get_db()
        cursor = db.cursor()
        count_pessoas = cursor.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0]
        db.close()
        
        if count_pessoas == 0:
            print("Banco vazio detectado. Cadastrando pessoas automaticamente...")
            # Chamar a função de cadastro de pessoas
            try:
                pessoas_para_cadastrar = {
                    'cerimoniario': [
                        "Alejandro", "João Pedro", "Pedro Reis", "Adriano",
                        "Lucas", "André", "Pedro Barroso"
                    ],
                    'veterano': [
                        "Ana Julia", "Vitória", "Sofia Reis", "Armando", "Karla",
                        "Mateus", "João Raffael", "Pedro Cutrim", "Gabriel Mendes"
                    ],
                    'mirins': [
                        "João Gabriel", "Luiza", "Miguel", "Rafael", "Antony",
                        "Maria Celida", "Cauan", "Theo", "Alexia", "Davi Barbalho",
                        "Helisa", "Thiago Alex", "Gabriel Carvalho", "Mariana Jansen",
                        "Bernardo"
                    ]
                }
                
                db = get_db()
                cursor = db.cursor()
                total = 0
                for grupo, nomes in pessoas_para_cadastrar.items():
                    for nome in nomes:
                        nome_limpo = nome.strip()
                        try:
                            cursor.execute(
                                "INSERT INTO pessoas (nome, grupo, funcoes) VALUES (?, ?, ?)",
                                (nome_limpo, grupo, '')
                            )
                            total += 1
                        except IntegrityError:
                            pass  # Já existe
                db.commit()
                db.close()
                print(f"✅ {total} pessoas cadastradas automaticamente!")
            except Exception as e:
                print(f"⚠️ Erro ao cadastrar pessoas automaticamente: {e}")

# Executar inicialização apenas se não estiver em ambiente serverless (Vercel)
# Na Vercel, a inicialização será feita na primeira requisição
if __name__ == '__main__':
    init_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    # Em ambiente serverless (Vercel), inicializar na primeira importação
    # A inicialização será feita automaticamente quando get_db() for chamado
    # Não precisamos inicializar aqui pois pode causar problemas com PostgreSQL
    pass