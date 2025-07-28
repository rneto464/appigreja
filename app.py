import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, Response, g
import sqlite3
import os
import pandas as pd 
import io
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# --- CONFIGURAÇÕES E CONSTANTES GLOBAIS ---
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
DATABASE = 'dados_escala.db'
EXCEL_FILE = 'BASE DE DADOS COROINHAS.xlsx'

# Listas para popular os templates iniciais
g_terca_template_initial = ['Alejandro', 'André', 'Armando', 'Gabriel Carvalho', 'João Gabriel', 'Karla','Lucas', 'Luiza', 'Mariana Jansen', 'Mateus', 'Pedro Barroso', 'Pedro Reis','Sofia Reis']
g_quinta_template_initial = ['Alejandro', 'André', 'Armando', 'Gabriel Carvalho', 'João Gabriel', 'Karla','Lucas', 'Luiza', 'Mariana Jansen', 'Mateus', 'Pedro Barroso', 'Pedro Cutrim','Pedro Reis']
g_turibulo_template_initial = ['Armando', 'Karla', 'Mateus', 'Alejandro', 'João Pedro', 'Pedro Reis','Adriano', 'Lucas', 'André', 'Pedro Barroso', 'Ana Julia']
g_naveta_template_initial = ['João Gabriel', 'Luiza', 'Miguel', 'Rafael', 'Antony', 'Maria Celida','Cauan', 'Theo', 'Alexia', 'Davi Barbalho', 'Helisa', 'Thiago Alex','Gabriel Carvalho', 'Mariana Jansen', 'Bernardo', 'Sofia Reis','João Raffael', 'Pedro Cutrim', 'Gabriel Mendes']
g_tochas_template_initial = list(set(['Alejandro', 'João Pedro', 'Pedro Reis', 'Adriano', 'Lucas', 'André','Pedro Barroso', 'Ana Julia', 'Vitória', 'Sofia Reis', 'Armando','Karla', 'Mateus', 'João Raffael', 'Pedro Cutrim', 'Gabriel Mendes','João Gabriel', 'Luiza', 'Miguel', 'Rafael']))
g_domingo_18h_template_initial = ['Adriano', 'Alejandro', 'Alexia', 'Ana Julia', 'André', 'Antony', 'Armando','Bernardo', 'Cauan', 'Davi Barbalho', 'Gabriel Carvalho', 'Gabriel Mendes','Helisa', 'João Gabriel', 'João Raffael', 'Karla', 'Lucas', 'Luiza','Maria Celida', 'Mariana Jansen', 'Mateus', 'Miguel', 'Pedro Cutrim','Pedro Reis', 'Rafael', 'Sofia Reis', 'Theo', 'Thiago Alex', 'Vitória']
g_domingo_07h_template_initial = ['Adriano', 'Alejandro', 'Alexia', 'Ana Julia', 'Antony', 'Armando','Bernardo', 'Cauan', 'Gabriel Mendes', 'João Pedro', 'João Raffael','Karla', 'Mariana Jansen', 'Mateus', 'Pedro Barroso', 'Pedro Cutrim','Pedro Reis', 'Theo', 'Thiago Alex', 'Vitória']
g_demais_dias_semana_template_initial = ['Adriano', 'Alejandro', 'André', 'Armando', 'Davi Barbalho','Gabriel Carvalho', 'Helisa', 'João Gabriel', 'Karla', 'Lucas', 'Luiza','Mateus', 'Pedro Reis']


# --- GESTÃO DA LIGAÇÃO AO BANCO DE DADOS ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# --- FUNÇÕES AUXILIARES DE GERAÇÃO E FORMATAÇÃO ---
def selecionar_nomes(candidatos, usados_dia, quantidade):
    if not candidatos: return []
    candidatos_unicos = [n for n in candidatos if n not in usados_dia]
    random.shuffle(candidatos_unicos)
    selecionados = candidatos_unicos[:quantidade]
    if len(selecionados) < quantidade:
        print(f"AVISO: Poucos candidatos únicos. A reutilizar nomes para preencher {quantidade - len(selecionados)} vaga(s).")
        candidatos_reutilizaveis = list(candidatos)
        random.shuffle(candidatos_reutilizaveis)
        for nome in candidatos_reutilizaveis:
            if len(selecionados) >= quantidade: break
            if nome not in selecionados: selecionados.append(nome)
    usados_dia.update(selecionados)
    return selecionados

def gerar_datas(mes, ano):
    datas_escalas = []
    data_atual = datetime(ano, mes, 1)
    try:
        ultimo_dia = (datetime(ano, mes + 1, 1) if mes < 12 else datetime(ano + 1, 1, 1)) - timedelta(days=1)
    except ValueError:
        ultimo_dia = datetime(ano, 12, 31)
    while data_atual <= ultimo_dia:
        if data_atual.weekday() == 6: datas_escalas.extend([(data_atual, 'Domingo 1', 2), (data_atual, 'Domingo 2', 2)])
        elif data_atual.weekday() == 1: datas_escalas.append((data_atual, 'Terça', 1))
        elif data_atual.weekday() == 3: datas_escalas.append((data_atual, 'Quinta', 1))
        data_atual += timedelta(days=1)
    return datas_escalas

def formatar_escalas_para_calendario(escalas):
    calendar_events = []
    if not escalas: return []
    for escala in escalas:
        description = (f"<b>Cerimoniários:</b> {escala['cerimoniarios']}<br>" f"<b>Veteranos:</b> {escala['veteranos']}<br>" f"<b>Crianças:</b> {escala['criancas']}")
        if escala['turibulo']: description += f"<br><b>Turíbulo:</b> {escala['turibulo']}"
        if escala['naveta']: description += f"<br><b>Naveta:</b> {escala['naveta']}"
        if escala['tochas']: description += f"<br><b>Tochas:</b> {escala['tochas']}"
        calendar_events.append({'id': escala['id'], 'title': escala['tipo_escala'], 'start': escala['data'], 'extendedProps': {'description': description}})
    return calendar_events


# --- FUNÇÕES DE INTERAÇÃO COM O BANCO DE DADOS ---
def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS escalas (id INTEGER PRIMARY KEY, data TEXT, tipo_escala TEXT, cerimoniarios TEXT, veteranos TEXT, criancas TEXT, turibulo TEXT, naveta TEXT, tochas TEXT)''')
    db.execute('''CREATE TABLE IF NOT EXISTS pessoas (id INTEGER PRIMARY KEY, nome TEXT UNIQUE, grupo TEXT, funcoes_adicionais TEXT)''')
    db.execute('''CREATE TABLE IF NOT EXISTS escala_templates (id INTEGER PRIMARY KEY, tipo_escala TEXT UNIQUE, cerimoniarios_template TEXT, veteranos_template TEXT, criancas_template TEXT, turibulo_template TEXT, naveta_template TEXT, tochas_template TEXT)''')
    db.commit()
    print("Banco de dados inicializado.")

def popular_templates_iniciais():
    db = get_db()
    if db.execute("SELECT COUNT(*) FROM escala_templates").fetchone()[0] == 0:
        print("Populando templates de escala.")
        templates = {
            'Domingo 1': {'cerims': g_domingo_18h_template_initial, 'vets': g_domingo_18h_template_initial, 'kids': g_domingo_18h_template_initial, 'turib': g_turibulo_template_initial, 'nav': g_naveta_template_initial, 'tochas': g_tochas_template_initial},
            'Domingo 2': {'cerims': g_domingo_07h_template_initial, 'vets': g_domingo_07h_template_initial, 'kids': g_domingo_07h_template_initial, 'turib': g_turibulo_template_initial, 'nav': g_naveta_template_initial, 'tochas': g_tochas_template_initial},
            'Terça': {'cerims': g_terca_template_initial, 'vets': g_terca_template_initial, 'kids': g_terca_template_initial},
            'Quinta': {'cerims': g_quinta_template_initial, 'vets': g_quinta_template_initial, 'kids': g_quinta_template_initial},
            'DEMAIS DIAS DA SEMANA': {'cerims': g_demais_dias_semana_template_initial, 'vets': g_demais_dias_semana_template_initial, 'kids': g_demais_dias_semana_template_initial},
        }
        for nome, data in templates.items():
            db.execute('INSERT INTO escala_templates VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)', (nome, ", ".join(data.get('cerims', [])), ", ".join(data.get('vets', [])), ", ".join(data.get('kids', [])), ", ".join(data.get('turib', [])), ", ".join(data.get('nav', [])), ", ".join(data.get('tochas', []))))
        db.commit()

def ler_dados_do_excel(filepath):
    if not os.path.exists(filepath): return []
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        df.columns = df.columns.str.strip().str.lower()
        pessoas = []
        for _, row in df.iterrows():
            nome = str(row.get('nome', '')).strip()
            if nome:
                grupo = 'crianca'
                if str(row.get('mestre de cerimonia', '')).strip(): grupo = 'cerimoniario'
                elif str(row.get('experientes', '')).strip(): grupo = 'veterano'
                pessoas.append({'nome': nome, 'grupo': grupo})
        return pessoas
    except Exception as e:
        print(f"ERRO ao ler Excel: {e}")
        return []

def importar_dados_iniciais_do_excel():
    db = get_db()
    if db.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0] == 0:
        print(f"Importando de {EXCEL_FILE}")
        pessoas = ler_dados_do_excel(EXCEL_FILE)
        if pessoas:
            pessoas_com_funcoes = [dict(p, funcoes_adicionais='') for p in pessoas]
            db.executemany("INSERT OR IGNORE INTO pessoas (nome, grupo, funcoes_adicionais) VALUES (:nome, :grupo, :funcoes_adicionais)", pessoas_com_funcoes)
            db.commit()
            print(f"{len(pessoas)} pessoas importadas.")

def limpar_db_e_reimportar():
    db = get_db()
    db.execute("DROP TABLE IF EXISTS escalas")
    db.execute("DROP TABLE IF EXISTS pessoas")
    db.execute("DROP TABLE IF EXISTS escala_templates")
    db.commit()
    init_db()
    importar_dados_iniciais_do_excel()
    popular_templates_iniciais()
    flash("Banco de dados reiniciado com sucesso!", 'success')

def inserir_escala(data):
    db = get_db()
    db.execute('INSERT INTO escalas VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)', [data['data'], data['tipo_escala'], data['cerimoniarios'], data['veteranos'], data['criancas'], data['turibulo'], data['naveta'], data['tochas']])
    db.commit()

def limpar_escalas_do_mes(mes, ano):
    db = get_db()
    db.execute("DELETE FROM escalas WHERE substr(data, 4, 2) = ? AND substr(data, 7, 4) = ?", (f"{mes:02d}", str(ano)))
    db.commit()

def buscar_escalas_do_mes(mes, ano):
    db = get_db()
    return db.execute("SELECT * FROM escalas WHERE substr(data, 4, 2) = ? AND substr(data, 7, 4) = ? ORDER BY data", (f"{mes:02d}", str(ano))).fetchall()

def buscar_escala_por_id(escala_id):
    db = get_db()
    return db.execute("SELECT * FROM escalas WHERE id = ?", (escala_id,)).fetchone()

def atualizar_escala(escala_id, data):
    db = get_db()
    db.execute('UPDATE escalas SET cerimoniarios=?, veteranos=?, criancas=?, turibulo=?, naveta=?, tochas=? WHERE id=?', [data['cerimoniarios'], data['veteranos'], data['criancas'], data['turibulo'], data['naveta'], data['tochas'], escala_id])
    db.commit()
    flash('Escala atualizada!', 'success')

def adicionar_pessoa(nome, grupo, funcoes_adicionais):
    try:
        db = get_db()
        funcoes_str = ",".join(funcoes_adicionais)
        db.execute("INSERT INTO pessoas (nome, grupo, funcoes_adicionais) VALUES (?, ?, ?)", (nome, grupo, funcoes_str))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def remover_pessoa(pessoa_id):
    db = get_db()
    db.execute("DELETE FROM pessoas WHERE id = ?", (pessoa_id,))
    db.commit()
    
def remover_escala_por_id(escala_id):
    db = get_db()
    db.execute("DELETE FROM escalas WHERE id = ?", (escala_id,))
    db.commit()

def buscar_pessoas_por_grupo(grupo=None):
    db = get_db()
    if grupo:
        query = "SELECT * FROM pessoas WHERE LOWER(grupo) = ? ORDER BY nome"
        pessoas = db.execute(query, (grupo.lower(),)).fetchall()
    else:
        query = "SELECT * FROM pessoas ORDER BY grupo, nome"
        pessoas = db.execute(query).fetchall()
    return pessoas

def buscar_template_por_tipo(tipo_escala):
    db = get_db()
    return db.execute("SELECT * FROM escala_templates WHERE tipo_escala = ?", (tipo_escala,)).fetchone()

def atualizar_template_no_db(tipo_escala, data):
    db = get_db()
    db.execute('UPDATE escala_templates SET cerimoniarios_template = ?, veteranos_template = ?, criancas_template = ?, turibulo_template = ?, naveta_template = ?, tochas_template = ? WHERE tipo_escala = ?', (data['cerimoniarios'], data['veteranos'], data['criancas'], data['turibulo'], data['naveta'], data['tochas'], tipo_escala))
    db.commit()


# --- GOOGLE CALENDAR API ---
def get_google_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"ERRO GOOGLE CALENDAR API: {error}")
        flash(f"Erro ao conectar ao Google Calendar: {error}", 'error')
        return None

def create_calendar_event(service, scale_data):
    summary = f"Escala: {scale_data['tipo_escala']}"
    description = (f"Cerimoniários: {scale_data['cerimoniarios']}\n" f"Veteranos: {scale_data['veteranos']}\n" f"Crianças: {scale_data['criancas']}")
    if scale_data.get('turibulo'): description += f"\nTuríbulo: {scale_data['turibulo']}"
    if scale_data.get('naveta'): description += f"\nNaveta: {scale_data['naveta']}"
    if scale_data.get('tochas'): description += f"\nTochas: {scale_data['tochas']}"
    try:
        event_date_obj = datetime.strptime(scale_data['data'], "%d/%m/%Y")
        event_date_str = event_date_obj.strftime('%Y-%m-%d')
    except ValueError:
        print(f"AVISO: Formato de data inválido para evento: {scale_data['data']}.")
        return
    event = {'summary': summary, 'description': description, 'start': {'date': event_date_str, 'timeZone': 'America/Sao_Paulo'}, 'end': {'date': event_date_str, 'timeZone': 'America/Sao_Paulo'}, 'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 60}]}}
    try:
        event_created = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Evento criado: {event_created.get('htmlLink')}")
        flash(f"Evento '{summary}' criado no Google Calendar para {scale_data['data']}.", 'success')
    except HttpError as error:
        print(f"ERRO ao criar evento: {error}")
        flash(f"Erro ao criar evento '{summary}': {error}", 'error')


# --- LÓGICA PRINCIPAL DE GERAÇÃO DE ESCALA ---
def gerar_e_salvar_escala_do_mes(mes, ano):
    print("A obter o serviço do Google Calendar...")
    service = get_google_calendar_service()
    if not service:
        flash("Não foi possível conectar ao Google Calendar. A escala será gerada apenas localmente.", "warning")

    limpar_escalas_do_mes(mes, ano)
    todos_os_grupos = ['cerimoniario', 'veterano', 'crianca']
    pessoas_por_grupo = {grupo: buscar_pessoas_por_grupo(grupo) for grupo in todos_os_grupos}
    if not all(pessoas_por_grupo.values()):
        flash("Faltam pessoas cadastradas em um ou mais grupos. Verifique a página 'Gerenciar Pessoas'.", 'error')
        return
    db = get_db()
    templates = {row['tipo_escala']: {k.replace('_template', ''): [n.strip() for n in (row[k] or '').split(',') if n.strip()] for k in row.keys() if k.endswith('_template')} for row in db.execute("SELECT * FROM escala_templates").fetchall()}
    if not templates:
        flash("Nenhum modelo de escala encontrado.", 'error')
        return

    ultimos_nomes_domingo = set()
    for data, nome_escala, qtd_cerim in gerar_datas(mes, ano):
        usados_dia = ultimos_nomes_domingo.copy() if 'Domingo' in nome_escala else set()
        template_do_dia = templates.get(nome_escala, templates.get('DEMAIS DIAS DA SEMANA', {}))
        escala_dia = {'data': data.strftime("%d/%m/%Y"), 'tipo_escala': nome_escala}
        
        lista_combinada_de_experientes = pessoas_por_grupo['veterano'] + pessoas_por_grupo['cerimoniario']
        funcoes_a_preencher = {
            'cerimoniarios': (pessoas_por_grupo['cerimoniario'], qtd_cerim),
            'veteranos': (lista_combinada_de_experientes, 2),
            'criancas': (pessoas_por_grupo['crianca'], 2)
        }
        if 'Domingo' in nome_escala:
            funcoes_a_preencher['turibulo'] = (pessoas_por_grupo['cerimoniario'], 1)
            funcoes_a_preencher['naveta'] = (pessoas_por_grupo['veterano'] + pessoas_por_grupo['crianca'], 1)
            funcoes_a_preencher['tochas'] = (lista_combinada_de_experientes, 2)
        else:
            escala_dia['turibulo'], escala_dia['naveta'], escala_dia['tochas'] = '', '', ''

        for func, (lista_de_pessoas_aptas, qtd) in funcoes_a_preencher.items():
            nomes_de_pessoas_aptas = [p['nome'] for p in lista_de_pessoas_aptas]
            candidatos_do_modelo = template_do_dia.get(func, [])
            candidatos_finais = [nome for nome in candidatos_do_modelo if nome in nomes_de_pessoas_aptas]
            escala_dia[func] = ", ".join(selecionar_nomes(candidatos_finais, usados_dia, qtd))

        inserir_escala(escala_dia)
        if service:
            print(f"A criar evento no Google Calendar para {escala_dia['data']}...")
            create_calendar_event(service, escala_dia)
        if 'Domingo' in nome_escala:
            ultimos_nomes_domingo = usados_dia

    flash(f'Escalas de {mes:02d}/{ano} geradas com sucesso!', 'success')


# --- ROTAS FLASK (ENDPOINTS DA APLICAÇÃO) ---
@app.route('/')
def index():
    mes, ano = datetime.now().month, datetime.now().year
    escalas = buscar_escalas_do_mes(mes, ano)
    if not escalas:
        gerar_e_salvar_escala_do_mes(mes, ano)
        escalas = buscar_escalas_do_mes(mes, ano)
    calendar_events = formatar_escalas_para_calendario(escalas)
    return render_template('index.html', escalas=escalas, mes=mes, ano=ano, calendar_events=calendar_events, is_view_only=False)

@app.route('/reiniciar_importar', methods=['POST'])
def reiniciar_importar_web():
    limpar_db_e_reimportar()
    return redirect(url_for('index'))

@app.route('/gerar_escala', methods=['POST'])
def gerar_escala_web():
    mes, ano = int(request.form['mes']), int(request.form['ano'])
    gerar_e_salvar_escala_do_mes(mes, ano)
    return redirect(url_for('ver_escala_post_redirect', mes=mes, ano=ano))

@app.route('/ver_escala/<int:mes>/<int:ano>')
def ver_escala_post_redirect(mes, ano):
    escalas = buscar_escalas_do_mes(mes, ano)
    if not escalas:
        flash(f"Não há escalas para {mes:02d}/{ano}.", 'warning')
    calendar_events = formatar_escalas_para_calendario(escalas)
    return render_template('index.html', escalas=escalas, mes=mes, ano=ano, calendar_events=calendar_events, is_view_only=False)

@app.route('/ver_escala', methods=['POST'])
def ver_escala_web():
    mes, ano = int(request.form['mes']), int(request.form['ano'])
    return redirect(url_for('ver_escala_post_redirect', mes=mes, ano=ano))

@app.route('/visualizar')
def visualizar_escala():
    mes, ano = datetime.now().month, datetime.now().year
    return redirect(url_for('visualizar_escala_mes_ano', mes=mes, ano=ano))

@app.route('/visualizar/<int:mes>/<int:ano>')
def visualizar_escala_mes_ano(mes, ano):
    escalas = buscar_escalas_do_mes(mes, ano)
    if not escalas:
        flash(f"Não há escalas geradas para {mes:02d}/{ano}.", 'warning')
    calendar_events = formatar_escalas_para_calendario(escalas)
    return render_template('index.html', escalas=escalas, mes=mes, ano=ano, calendar_events=calendar_events, is_view_only=True)

# No app.py, substitua a sua função adicionar_escala por esta:

@app.route('/adicionar_escala/<int:ano>/<int:mes>/<int:dia>')
def adicionar_escala(ano, mes, dia):
    data_formatada = datetime(ano, mes, dia).strftime("%d/%m/%Y")
    todos_cerimoniarios = buscar_pessoas_por_grupo('cerimoniario')
    todos_veteranos = buscar_pessoas_por_grupo('veterano')
    todas_criancas = buscar_pessoas_por_grupo('crianca')
    todas_as_pessoas = buscar_pessoas_por_grupo()
    todos_os_nomes = sorted([p['nome'] for p in todas_as_pessoas])
    
    return render_template('adicionar_escala.html', 
                           data_formatada=data_formatada,
                           todos_cerimoniarios=todos_cerimoniarios,
                           todos_veteranos=todos_veteranos,
                           todas_criancas=todas_criancas,
                           candidatos_funcoes_especiais=todos_os_nomes) 

@app.route('/salvar_nova_escala', methods=['POST'])
def salvar_nova_escala():
    data_str = request.form['data']
    nova_escala_data = {'data': data_str, 'tipo_escala': request.form['tipo_escala'], 'cerimoniarios': ", ".join(request.form.getlist('cerimoniarios')), 'veteranos': ", ".join(request.form.getlist('veteranos')), 'criancas': ", ".join(request.form.getlist('criancas')), 'turibulo': ", ".join(request.form.getlist('turibulo')), 'naveta': ", ".join(request.form.getlist('naveta')), 'tochas': ", ".join(request.form.getlist('tochas'))}
    inserir_escala(nova_escala_data)
    flash(f"Nova escala para {data_str} adicionada com sucesso!", 'success')
    data_obj = datetime.strptime(data_str, "%d/%m/%Y")
    return redirect(url_for('ver_escala_post_redirect', mes=data_obj.month, ano=data_obj.year))

# No seu app.py, substitua a função editar_escala por esta:

@app.route('/editar_escala/<int:escala_id>')
def editar_escala(escala_id):
    escala = buscar_escala_por_id(escala_id)
    if not escala:
        flash("Escala não encontrada.", "error")
        return redirect(url_for('index'))

    # Busca as listas de pessoas para as funções principais (isto não muda)
    todos_cerimoniarios = buscar_pessoas_por_grupo('cerimoniario')
    todos_veteranos = buscar_pessoas_por_grupo('veterano')
    todas_criancas = buscar_pessoas_por_grupo('crianca')

    # --- NOVA LÓGICA ---
    # Para as funções especiais, a lista de candidatos será TODAS as pessoas cadastradas.
    todas_as_pessoas = buscar_pessoas_por_grupo() # Chama a função sem argumento para pegar todos
    todos_os_nomes = sorted([p['nome'] for p in todas_as_pessoas]) # Extrai apenas os nomes e ordena
    
    candidatos_turibulo = todos_os_nomes
    candidatos_naveta = todos_os_nomes
    candidatos_tochas = todos_os_nomes
    
    return render_template('editar_escala.html',
                           escala=escala,
                           todos_cerimoniarios=todos_cerimoniarios,
                           todos_veteranos=todos_veteranos,
                           todas_criancas=todas_criancas,
                           candidatos_turibulo=candidatos_turibulo,
                           candidatos_naveta=candidatos_naveta,
                           candidatos_tochas=candidatos_tochas)

@app.route('/atualizar_escala/<int:escala_id>', methods=['POST'])
def atualizar_escala_web(escala_id):
    data = {k: ", ".join(request.form.getlist(k)) for k in ['cerimoniarios', 'veteranos', 'criancas', 'turibulo', 'naveta', 'tochas']}
    atualizar_escala(escala_id, data)
    escala = buscar_escala_por_id(escala_id)
    data_obj = datetime.strptime(escala['data'], "%d/%m/%Y")
    return redirect(url_for('ver_escala_post_redirect', mes=data_obj.month, ano=data_obj.year))
    
@app.route('/remover_escala/<int:escala_id>', methods=['POST'])
def remover_escala(escala_id):
    escala = buscar_escala_por_id(escala_id)
    if escala:
        data_obj = datetime.strptime(escala['data'], "%d/%m/%Y")
        remover_escala_por_id(escala_id)
        flash(f"Escala de {escala['data']} ({escala['tipo_escala']}) removida com sucesso!", 'success')
        return redirect(url_for('ver_escala_post_redirect', mes=data_obj.month, ano=data_obj.year))
    else:
        flash("Escala não encontrada.", 'error')
        return redirect(url_for('index'))

@app.route('/gerenciar_pessoas')
def gerenciar_pessoas():
    mestres_de_cerimonia = buscar_pessoas_por_grupo('cerimoniario')
    experientes = buscar_pessoas_por_grupo('veterano')
    criancas = buscar_pessoas_por_grupo('crianca')
    return render_template('gerenciar_pessoas.html', mestres_de_cerimonia=mestres_de_cerimonia, experientes=experientes, criancas=criancas)

@app.route('/adicionar_pessoa', methods=['POST'])
def adicionar_pessoa_web():
    nome = request.form['nome'].strip()
    grupo = request.form['grupo'].strip().lower()
    funcoes_adicionais = request.form.getlist('funcoes')
    if not nome:
        flash("O nome não pode ser vazio.", 'error')
    elif adicionar_pessoa(nome, grupo, funcoes_adicionais):
        flash(f"Pessoa '{nome}' adicionada com sucesso!", 'success')
    else:
        flash(f"Pessoa '{nome}' já existe!", 'error')
    return redirect(url_for('gerenciar_pessoas'))

@app.route('/editar_pessoa/<int:pessoa_id>', methods=['GET', 'POST'])
def editar_pessoa(pessoa_id):
    db = get_db()
    pessoa = db.execute("SELECT * FROM pessoas WHERE id = ?", (pessoa_id,)).fetchone()
    if not pessoa:
        flash("Pessoa não encontrada.", "error")
        return redirect(url_for('gerenciar_pessoas'))
    if request.method == 'POST':
        novo_grupo = request.form['grupo'].strip().lower()
        novas_funcoes = request.form.getlist('funcoes')
        funcoes_str = ",".join(novas_funcoes)
        db.execute("UPDATE pessoas SET grupo = ?, funcoes_adicionais = ? WHERE id = ?", (novo_grupo, funcoes_str, pessoa_id))
        db.commit()
        flash(f"Dados de '{pessoa['nome']}' atualizados com sucesso!", "success")
        return redirect(url_for('gerenciar_pessoas'))
    return render_template('editar_pessoa.html', pessoa=pessoa)

@app.route('/remover_pessoa/<int:pessoa_id>', methods=['POST'])
def remover_pessoa_web(pessoa_id):
    remover_pessoa(pessoa_id)
    flash("Pessoa removida.", 'success')
    return redirect(url_for('gerenciar_pessoas'))

@app.route('/gerenciar_modelos')
def gerenciar_modelos():
    db = get_db()
    templates = db.execute("SELECT * FROM escala_templates ORDER BY tipo_escala").fetchall()
    return render_template('gerenciar_modelos.html', templates=templates)

@app.route('/editar_modelo/<string:tipo_escala>')
def editar_modelo(tipo_escala):
    template = buscar_template_por_tipo(tipo_escala)
    if not template:
        return redirect(url_for('gerenciar_modelos'))
    todos_os_nomes = sorted([p['nome'] for p in buscar_pessoas_por_grupo()])
    return render_template('editar_modelo.html', template=template, todos_os_nomes=todos_os_nomes)

@app.route('/atualizar_modelo/<string:tipo_escala>', methods=['POST'])
def atualizar_modelo(tipo_escala):
    data = {'cerimoniarios': ", ".join(request.form.getlist('cerimoniarios')),'veteranos': ", ".join(request.form.getlist('veteranos')),'criancas': ", ".join(request.form.getlist('criancas')),'turibulo': ", ".join(request.form.getlist('turibulo')),'naveta': ", ".join(request.form.getlist('naveta')),'tochas': ", ".join(request.form.getlist('tochas'))}
    atualizar_template_no_db(tipo_escala, data)
    flash(f"Modelo '{tipo_escala}' atualizado com sucesso!", 'success')
    return redirect(url_for('gerenciar_modelos'))

@app.route('/exportar_modelo/<string:tipo_escala>')
def exportar_modelo(tipo_escala):
    template = buscar_template_por_tipo(tipo_escala)
    if not template:
        flash(f"Modelo '{tipo_escala}' não encontrado!", 'error')
        return redirect(url_for('gerenciar_modelos'))
    def formatar_secao(titulo, nomes_str):
        if not nomes_str or not nomes_str.strip(): return ""
        nomes_lista = [nome.strip() for nome in nomes_str.split(',')]
        secao_texto = f"{titulo}:\n"
        for nome in nomes_lista: secao_texto += f"- {nome}\n"
        return secao_texto + "\n"
    conteudo_exportado = f"Modelo de Escala: {template['tipo_escala']}\n===================================\n\n"
    conteudo_exportado += formatar_secao("Cerimoniários", template['cerimoniarios_template'])
    conteudo_exportado += formatar_secao("Veteranos", template['veteranos_template'])
    conteudo_exportado += formatar_secao("Crianças", template['criancas_template'])
    conteudo_exportado += formatar_secao("Turíbulo", template['turibulo_template'])
    conteudo_exportado += formatar_secao("Naveta", template['naveta_template'])
    conteudo_exportado += formatar_secao("Tochas", template['tochas_template'])
    nome_ficheiro = f"modelo_{tipo_escala.replace(' ', '_').lower()}.txt"
    return Response(conteudo_exportado, mimetype="text/plain", headers={"Content-Disposition": f"attachment;filename={nome_ficheiro}"})
    
@app.route('/exportar_mes/<int:ano>/<int:mes>')
def exportar_mes(mes, ano):
    """Busca todas as escalas do mês e as exporta como um ficheiro Excel .xlsx."""
    
    escalas = buscar_escalas_do_mes(mes, ano)

    if not escalas:
        flash(f"Nenhuma escala para exportar para o mês {mes:02d}/{ano}.", "warning")
        return redirect(url_for('ver_escala_post_redirect', mes=mes, ano=ano))

    # 1. Converte os dados do banco de dados para um formato que o pandas entende
    escalas_data = [dict(row) for row in escalas]
    df = pd.DataFrame(escalas_data)

    # 2. Seleciona, reordena e renomeia as colunas para o relatório final
    colunas_finais = {
        'data': 'Data',
        'tipo_escala': 'Tipo de Escala',
        'cerimoniarios': 'Cerimoniários',
        'veteranos': 'Veteranos',
        'criancas': 'Crianças',
        'turibulo': 'Turíbulo',
        'naveta': 'Naveta',
        'tochas': 'Tochas'
    }
    df = df[list(colunas_finais.keys())] # Garante a ordem
    df = df.rename(columns=colunas_finais)

    # 3. Cria um ficheiro Excel em memória (buffer)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Escala_{mes:02d}_{ano}')
    output.seek(0)
    
    # 4. Prepara o nome do ficheiro e envia a resposta para o navegador
    nome_ficheiro = f"escala_{mes:02d}_{ano}.xlsx"

    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment;filename={nome_ficheiro}"}
    )


@app.route('/limpar_mes', methods=['POST'])
def limpar_mes_web():
    """Apaga todas as escalas de um mês específico."""
    try:
        mes = int(request.form['mes'])
        ano = int(request.form['ano'])
        
        limpar_escalas_do_mes(mes, ano)
        
        flash(f"Todas as escalas de {mes:02d}/{ano} foram removidas com sucesso.", "success")
        return redirect(url_for('ver_escala_post_redirect', mes=mes, ano=ano))
    except (ValueError, KeyError):
        flash("Mês ou ano inválido.", "error")
        return redirect(url_for('index'))
# --- INICIALIZAÇÃO DA APLICAÇÃO ---
if __name__ == '__main__':
    with app.app_context():
        init_db()
        importar_dados_iniciais_do_excel()
        popular_templates_iniciais()
    app.run(debug=True, port=5001)