"""
Script para adicionar missas em todos os dias da semana que ainda não têm.
Este script adiciona Segunda, Quarta, Sexta e Sábado com configurações padrão.
"""
import sqlite3
import os

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'dados_escala.db')

# Configuração de dias da semana
# 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo
NOMES_DIAS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

def adicionar_todos_dias_missa():
    """Adiciona missas para todos os dias da semana que ainda não têm"""
    print(f"Conectando ao banco de dados em: {DATABASE_PATH}")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print("Conexão bem-sucedida.\n")
        
        # Verificar quais dias já têm missas configuradas
        dias_existentes = cursor.execute(
            "SELECT DISTINCT dia_semana FROM dias_missa WHERE ativo = 1"
        ).fetchall()
        dias_com_missa = {row['dia_semana'] for row in dias_existentes}
        
        print("Dias que já têm missas configuradas:")
        for dia_num in sorted(dias_com_missa):
            print(f"  - {NOMES_DIAS[dia_num]} (dia {dia_num})")
        
        # Verificar quais templates existem
        templates_existentes = cursor.execute(
            "SELECT tipo_escala FROM escala_templates"
        ).fetchall()
        tipos_template = {row['tipo_escala'] for row in templates_existentes}
        
        print(f"\nTemplates disponíveis: {', '.join(sorted(tipos_template))}")
        
        # Configuração de novos dias a adicionar
        # Formato: (dia_semana, nome_tipo_escala, horario)
        novos_dias = []
        
        # Segunda-feira (0)
        if 0 not in dias_com_missa:
            novos_dias.append((0, 'Segunda', '19:00'))
        
        # Quarta-feira (2)
        if 2 not in dias_com_missa:
            novos_dias.append((2, 'Quarta', '19:00'))
        
        # Sexta-feira (4)
        if 4 not in dias_com_missa:
            novos_dias.append((4, 'Sexta', '19:00'))
        
        # Sábado (5)
        if 5 not in dias_com_missa:
            novos_dias.append((5, 'Sábado', '19:00'))
        
        if not novos_dias:
            print("\n✓ Todos os dias da semana já têm missas configuradas!")
            return
        
        print(f"\n--- Adicionando {len(novos_dias)} novos dias de missa ---\n")
        
        # Buscar maior ordem atual
        max_ordem_result = cursor.execute('SELECT MAX(ordem) as max_ord FROM dias_missa').fetchone()
        max_ordem = max_ordem_result['max_ord'] if max_ordem_result['max_ord'] else 0
        
        # Adicionar templates para os novos dias (se não existirem)
        templates_adicionados = []
        for dia_semana, tipo_escala, horario in novos_dias:
            if tipo_escala not in tipos_template:
                # Criar template básico para o novo dia
                # Usar os mesmos candidatos de Terça/Quinta como padrão
                cursor.execute('''
                    INSERT INTO escala_templates 
                    (tipo_escala, cerimoniarios_template, veteranos_template, mirins_template, 
                     turibulo_template, naveta_template, tochas_template)
                    SELECT 
                        ? as tipo_escala,
                        cerimoniarios_template,
                        veteranos_template,
                        mirins_template,
                        '' as turibulo_template,
                        '' as naveta_template,
                        '' as tochas_template
                    FROM escala_templates
                    WHERE tipo_escala = 'Terça'
                    LIMIT 1
                ''', (tipo_escala,))
                
                templates_adicionados.append(tipo_escala)
                print(f"  [+] Template '{tipo_escala}' criado (baseado em 'Terça')")
        
        # Adicionar os dias de missa
        dias_adicionados = 0
        for dia_semana, tipo_escala, horario in novos_dias:
            max_ordem += 1
            cursor.execute('''
                INSERT INTO dias_missa (dia_semana, tipo_escala, horario, ativo, ordem)
                VALUES (?, ?, ?, ?, ?)
            ''', (dia_semana, tipo_escala, horario, 1, max_ordem))
            
            print(f"  [+] {NOMES_DIAS[dia_semana]} - {tipo_escala} às {horario} (ordem {max_ordem})")
            dias_adicionados += 1
        
        conn.commit()
        
        print(f"\n✓ Operação concluída com sucesso!")
        print(f"  - {dias_adicionados} dias de missa adicionados")
        if templates_adicionados:
            print(f"  - {len(templates_adicionados)} templates criados: {', '.join(templates_adicionados)}")
        
        print("\nDias de missa configurados agora:")
        todos_dias = cursor.execute(
            "SELECT dia_semana, tipo_escala, horario FROM dias_missa WHERE ativo = 1 ORDER BY dia_semana, ordem"
        ).fetchall()
        
        for dia in todos_dias:
            print(f"  - {NOMES_DIAS[dia['dia_semana']]}: {dia['tipo_escala']} às {dia['horario']}")
        
    except sqlite3.Error as e:
        print(f"\n✗ ERRO: Ocorreu um problema com o banco de dados: {e}")
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
    finally:
        if conn:
            conn.close()
            print("\nConexão com o banco de dados fechada.")

if __name__ == '__main__':
    adicionar_todos_dias_missa()

