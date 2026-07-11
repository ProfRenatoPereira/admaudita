import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# CONEXAO AUTOMATICA COM O BANCO DE DADOS POSTGRESQL DO RENDER
def obter_conexao_db():
    url_banco = os.environ.get('DATABASE_URL')
    if url_banco:
        if url_banco.startswith("postgres://"):
            url_banco = url_banco.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url_banco)
    return None

# Inicializacao automatica das tabelas lendo o schema.sql
def inicializar_banco():
    conn = obter_conexao_db()
    if conn:
        try:
            cursor = conn.cursor()
            if os.path.exists('schema.sql'):
                with open('schema.sql', 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                conn.commit()
                print("Banco de dados PostgreSQL sincronizado com sucesso.")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Falha na sincronizacao inicial do banco: {e}")

# Executa a checagem estrutural ao subir o servidor
inicializar_banco()

# ROTAS DE NAVEGACAO DE PAGINAS (ARQUITETURA MULTI-PAGINAS)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terreno')
def pagina_terreno():
    return render_template('terreno.html')

@app.route('/maquinas')
def pagina_maquinas():
    return render_template('maquinas.html')

@app.route('/processos')
def pagina_processos():
    return render_template('processos.html')

@app.route('/materiais')
def pagina_materiais():
    return render_template('materiais.html')

@app.route('/precificacao')
def pagina_precificacao():
    return render_template('precificacao.html')

@app.route('/retorno')
def pagina_retorno():
    return render_template('retorno.html')

# ENDPOINT 1: SALVAR E PROCESSAR CUSTOS IMOBILIARIOS
@app.route('/api/imobiliario', methods=['POST'])
def salvar_imobiliario():
    data = request.get_json()
    valor_terreno = float(data.get('valor_terreno', 0))
    custo_edificacao = float(data.get('custo_edificacao', 0))
    impostos_anuais = float(data.get('impostos_anuais', 0))
    vida_util_anos = int(data.get('vida_util_anos', 20))
    horas_operacionais_ano = int(data.get('horas_operacionais_ano', 2400))

    amortizacao_anual = (valor_terreno + custo_edificacao) / vida_util_anos
    custo_imobiliario_anual = amortizacao_anual + impostos_anuais
    minutos_ano = horas_operacionais_ano * 60
    
    custo_minuto_instalacao = custo_imobiliario_anual / minutos_ano if minutos_ano > 0 else 0

    conn = obter_conexao_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO investimentos_iniciais (descricao_terreno, valor_terreno, 
                                                    custo_edificacao, impostos_transferencia) 
                   VALUES (%s, %s, %s, %s);""",
                ('Galpao Industrial Metalurgico', valor_terreno, custo_edificacao, impostos_anuais)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({
        'status': 'sucesso',
        'amortizacaoAnual': round(amortizacao_anual, 2),
        'custoAnualTotal': round(custo_imobiliario_anual, 2),
        'custoMinutoInstalacao': round(custo_minuto_instalacao, 4)
    })
# ENDPOINT 2: REGISTRAR ATIVOS E MAQUINAS NO BANCO POSTGRESQL
@app.route('/api/maquinas', methods=['GET', 'POST'])
def gerenciar_maquinas():
    conn = obter_conexao_db()
    if not conn:
        return jsonify([])
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        data = request.get_json()
        nome = data.get('nome')
        preco = float(data.get('preco', 0))
        vida_util = int(data.get('vida_util', 1))
        valor_revenda = float(data.get('valor_revenda', 0))
        manutencao = float(data.get('manutencao', 0))
        horas_ano = int(data.get('horas_ano', 1))
        
        depreciacao_anual = (preco - valor_revenda) / vida_util
        custo_fixo_anual = depreciacao_anual + manutencao
        minutos_ano = horas_ano * 60
        custo_minuto = custo_fixo_anual / minutos_ano

        try:
            cursor.execute(
                """INSERT INTO maquinas (nome_maquina, preco_compra, tempo_vida_util_anos, 
                                        valor_revenda_estimado, custo_manutencao_anual, 
                                        horas_ativas_ano, custo_minuto_maquina) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                (nome, preco, vida_util, valor_revenda, manutencao, horas_ano, custo_minuto)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'sucesso',
                'depreciacaoAnual': round(depreciacao_anual, 2),
                'custoFixoAnual': round(custo_fixo_anual, 2),
                'custoMinuto': round(custo_minuto, 4)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    cursor.execute("SELECT id, nome_maquina, custo_minuto_maquina FROM maquinas ORDER BY id DESC;")
    maquinas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(maquinas)

# ENDPOINT 3: SIMULADOR DE MARK-UP COMERCIAL (PRECIFICACAO GLOBAL)
@app.route('/api/calculo-markup', methods=['POST'])
def calcular_markup():
    data = request.get_json()
    custo_total = float(data.get('custo_total', 0))
    margem_lucro = float(data.get('margem_lucro', 0))
    impostos = float(data.get('impostos', 0))
    
    denominador = 1 - ((margem_lucro + impostos) / 100)
    if denominador <= 0:
        return jsonify({'error': 'Margem ou impostos excessivos'}), 400
        
    markup = 1 / denominador
    preco_venda = custo_total * markup
    
    return jsonify({
        'markup': round(markup, 2),
        'preco_venda': round(preco_venda, 2)
    })

# ENDPOINT 4: CONSOLE DE AUDITORIA HUMANA (HOLERITE MENSAL E 13O INDIVIDUAL)
@app.route('/api/holerite/<int:funcionario_id>/<int:mes>/<int:ano>', methods=['GET'])
def gerar_holerite(funcionario_id, mes, ano):
    conn = obter_conexao_db()
    if not conn:
        return jsonify({'error': 'Erro de conexao'}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM funcionarios WHERE id = %s", (funcionario_id,))
    func = cursor.fetchone()
    if not func:
        return jsonify({'error': 'Funcionario nao encontrado'}), 404

    cursor.execute("SELECT * FROM registro_horas_extras WHERE funcionario_id = %s AND ano_referencia = %s", (funcionario_id, ano))
    historico_he = cursor.fetchall()
    
    he_mes = [h for h in historico_he if h['mes_referencia'] == mes]
    valor_hora_comum = float(func['salario_base']) / int(func['horas_contratuais'])
    total_he_valores = 0.0
    alerta_clt = ""
    
    for he in he_mes:
        fator_dia = 1.5 if he['tipo_dia'] == 'semana' else (1.6 if he['tipo_dia'] == 'sabado' else 2.0)
        fator_noturno = 1.2 if he['eh_noturna'] else 1.0
        total_he_valores += float(he['qtd_horas']) * (valor_hora_comum * fator_dia * fator_noturno)
        
        if float(he['qtd_horas']) > 2.0:
            alerta_clt += f"Aviso: Extrapolacao do limite legal de 2h diarias em {he['data_registro']}. "

    total_he_ano_valores = 0.0
    for he in historico_he:
        fator_dia = 1.5 if he['tipo_dia'] == 'semana' else (1.6 if he['tipo_dia'] == 'sabado' else 2.0)
        fator_noturno = 1.2 if he['eh_noturna'] else 1.0
        total_he_ano_valores += float(he['qtd_horas']) * (valor_hora_comum * fator_dia * fator_noturno)
    
    media_he_13 = total_he_ano_valores / 12.0
    valor_13_integral = float(func['salario_base']) + media_he_13

    proventos = {
        'Salario Base': float(func['salario_base']),
        'Horas Extras + Adic. Noturno': round(total_he_valores, 2)
    }
    
    descontos = {
        'INSS Contribuicao': round(float(func['salario_base']) * 0.09, 2),
        'Sindicato': float(func['sindicato']) if func['sindicato'] else 0.0
    }
    
    cursor.close()
    conn.close()
    
    observacao_legal = (
        f"{alerta_clt}\n"
        f"Fundamentacoes Legais Aplicadas:\n"
        f"- Horas extras e reflexos calculados conforme Art. 142 parágrafo 5 da CLT.\n"
        f"- Adicional Noturno integrado na hora extra conforme OJ numero 97 SDI-1 TST.\n"
        f"- Media do Holerite de 13O Salario individualizado amparada na Sumula numero 45 do TST."
    )

    return jsonify({
        'funcionario': func['nome'],
        'cargo': func['departamento'],
        'mes_ano': f"{mes}/{ano}",
        'proventos': proventos,
        'descontos': descontos,
        'total_proventos': sum(proventos.values()),
        'total_descontos': sum(descontos.values()),
        'liquido': sum(proventos.values()) - sum(descontos.values()),
        'holerite_13_estimado': {
            'base_13': round(valor_13_integral, 2),
            'media_he_integrada': round(media_he_13, 2),
            'obs_13': "Calculo baseado na Sumula 45 do TST (Media duodecimal anual)."
        },
        'observacoes_fiscais': observacao_legal
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
