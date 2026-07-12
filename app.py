import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify, request, render_template_string

app = Flask(__name__)

# CONEXAO COM O BANCO DE DADOS POSTGRESQL DO RENDER
def obter_conexao_db():
    url_banco = os.environ.get('DATABASE_URL')
    if url_banco:
        if url_banco.startswith("postgres://"):
            url_banco = url_banco.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url_banco)
    return None

def inicializar_banco():
    conn = obter_conexao_db()
    if conn:
        try:
            cursor = conn.cursor()
            if os.path.exists('schema.sql'):
                with open('schema.sql', 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro na sincronizacao: {e}")

inicializar_banco()

# ROTAS MULTI-PAGINAS INICIAIS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terreno')
def pagina_terreno():
    try:
        return render_template('terreno.html')
    except Exception:
        html_terreno = """
        {% extends 'base.html' %}
        {% block title %}Instalações - TERCEIRO ADM ASSOCIADOS{% endblock %}
        {% block content %}
        <section class="card" aria-labelledby="tit-terreno">
            <h2 id="tit-terreno">Precificação de Instalações Imobiliárias</h2>
            <p>Monitore o impacto financeiro da infraestrutura física no custo minuto da planta industrial.</p>
            <div class="grid-form">
                <div class="form-group">
                    <label for="imoTerreno">Valor do Terreno (R$):</label>
                    <input type="number" id="imoTerreno" value="500000">
                    <label for="imoEdificacao">Custo do Galpão (R$):</label>
                    <input type="number" id="imoEdificacao" value="750000">
                    <label for="imoVidaUtil">Amortização (Anos):</label>
                    <input type="number" id="imoVidaUtil" value="20">
                </div>
                <div class="form-group">
                    <label for="imoImpostos">Impostos Anuais (R$):</label>
                    <input type="number" id="imoImpostos" value="15000">
                    <label for="imoHorasAno">Horas / Ano:</label>
                    <input type="number" id="imoHorasAno" value="2400">
                    <button onclick="calcularCustosImobiliarios()" class="btn-primary">Salvar Custos no Banco</button>
                </div>
            </div>
            <div id="resultadoImobiliario" class="result-box" style="display:none;"></div>
        </section>
        {% endblock %}
        """
        return render_template_string(html_terreno)
@app.route('/maquinas')
def pagina_maquinas():
    try:
        return render_template('maquinas.html')
    except Exception:
        html_maquinas = """
        {% extends 'base.html' %}
        {% block title %}Ativos Metalúrgicos - Teradmas{% endblock %}
        {% block content %}
        <section class="card" aria-labelledby="tit-maquinas">
            <h2 id="tit-maquinas">Gestão de Ativos & Eficiência Energética Metalúrgica</h2>
            <p>Cadastre os parâmetros operacionais, ciclo de manutenção preventiva e consumo elétrico em kW.</p>
            <input type="hidden" id="maquinaIdOculto" value="">
            <div class="grid-form">
                <div class="form-group">
                    <label for="maquinaNome">Nome / Identificação do Equipamento:</label>
                    <input type="text" id="maquinaNome" placeholder="Ex: Torno CNC Mazak">
                    <label for="maquinaPreco">Preço Compra (R$):</label>
                    <input type="number" id="maquinaPreco" value="250000">
                    <label for="maquinaVidaUtil">Vida Útil Estimada (Anos):</label>
                    <input type="number" id="maquinaVidaUtil" value="12">
                    <label for="maquinaValorRevenda">Valor Residual de Revenda (R$):</label>
                    <input type="number" id="maquinaValorRevenda" value="50000">
                    <label for="maquinaAquisicao">Data de Aquisição do Ativo:</label>
                    <input type="date" id="maquinaAquisicao" value="2026-01-15">
                </div>
                <div class="form-group">
                    <label for="maquinaManutencao">Custo de Manutenção Anual (R$):</label>
                    <input type="number" id="maquinaManutencao" value="18000">
                    <label for="maquinaHorasAno">Horas Operacionais por Ano:</label>
                    <input type="number" id="maquinaHorasAno" value="2400">
                    <label for="maquinaPotencia">Potência Elétrica do Motor (kW):</label>
                    <input type="number" id="maquinaPotencia" value="15.5" step="0.1">
                    <label for="maquinaTarifa">Tarifa de Energia Industrial (R$ / kWh):</label>
                    <input type="number" id="maquinaTarifa" value="0.75" step="0.0001">
                    <label for="maquinaDiametro">Diâmetro Máximo de Trabalho (mm):</label>
                    <input type="number" id="maquinaDiametro" value="350">
                </div>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label for="maquinaComprimento">Comprimento Máximo de Trabalho (mm):</label>
                <input type="number" id="maquinaComprimento" value="1000">
                <label for="maquinaPrev">Data para Próxima Manutenção Preventiva:</label>
                <input type="date" id="maquinaPrev" value="2026-12-20">
                <button onclick="adicionarMaquinaServidor()" class="btn-primary" id="btnSalvarAtivo" style="margin-top: 15px;">Salvar e Registrar Ativo</button>
            </div>
            <table class="data-table" id="tabelaMaquinas">
                <thead>
                    <tr><th>Equipamento</th><th>Capacidade Física</th><th>Potência</th><th>Próxima Preventiva</th><th>Custo / Minuto</th><th>Ações de Controle</th></tr>
                </thead>
                <tbody></tbody>
            </table>
            <div id="resultadoAtivo" class="result-box" style="display:none;"></div>
        </section>
        {% endblock %}
        """
        return render_template_string(html_maquinas)

@app.route('/processos')
def pagina_processos():
    try:
        return render_template('processos.html')
    except Exception:
        html_processos = """
        {% extends 'base.html' %}
        {% block title %}Roteiros de Fabricação - TERCEIRO ADM ASSOCIADOS{% endblock %}
        {% block content %}
        <section class="card" aria-labelledby="tit-roteiro">
            <h2 id="tit-roteiro">Engenharia de Processos & Tempo de Máquina</h2>
            <p>Monte o roteiro operacional das peças vinculando os tempos de ciclo e preparação (set-up) ao custo minuto dos ativos.</p>
            <div class="grid-form">
                <div class="form-group">
                    <label for="procSelecaoMaquina">Equipamento Industrial:</label>
                    <select id="procSelecaoMaquina"><option value="">-- Selecione uma máquina --</option></select>
                    <label for="procTempoOperacao">Tempo Ciclo por Peça (Minutos):</label>
                    <input type="number" id="procTempoOperacao" value="15">
                    <label for="procTempoSetup">Tempo Set-up / Preparação (Minutos):</label>
                    <input type="number" id="procTempoSetup" value="30">
                </div>
                <div class="form-group">
                    <label for="procSalarioMod">Salário Base Mensal do Operador (R$):</label>
                    <input type="number" id="procSalarioMod" value="3000">
                    <label for="procEncargosPercentual">Encargos Sociais + Benefícios (%):</label>
                    <input type="number" id="procEncargosPercentual" value="85">
                    <label for="procLoteTamanho">Tamanho do Lote de Produção (Peças):</label>
                    <input type="number" id="procLoteTamanho" value="100">
                    <button onclick="adicionarEtapaProcesso()" class="btn-primary" style="margin-top: 10px;">Inserir Operação no PCP</button>
                </div>
            </div>
            <table class="data-table" id="tabelaProcessos">
                <thead>
                    <tr><th>Operação / Máquina</th><th>Ciclo (Min)</th><th>Custo Minuto</th><th>Set-up Rateado</th><th>Custo MOD</th><th>Total Etapa</th><th>Ação</th></tr>
                </thead>
                <tbody></tbody>
            </table>
            <div class="total-box"><strong>Custo de Processamento da Peça: R$ <span id="totalProcessoCusto">0.00</span></strong></div>
        </section>
        {% endblock %}
        """
        return render_template_string(html_processos)

@app.route('/materiais')
def pagina_materiais(): return render_template('materiais.html')

@app.route('/precificacao')
def pagina_precificacao():
    try:
        return render_template('precificacao.html')
    except Exception:
        html_fallback = """
        {% extends 'base.html' %}
        {% block title %}Formação de Preço - TERCEIRO ADM ASSOCIADOS{% endblock %}
        {% block content %}
        <section class="card" aria-labelledby="tit-markup">
            <h2 id="tit-markup">Formação Estratégica de Preço por Canais</h2>
            <div class="grid-form">
                <div class="form-group">
                    <label for="custoTotal">Custo Industrial Acumulado (R$):</label>
                    <input type="number" id="custoTotal" value="0.00" readonly style="background-color:#f1f2f6; font-weight:bold;">
                    <label for="canalPreco">Canal de Distribuição Comercial:</label>
                    <select id="canalPreco" onchange="ajustarMargemPorCanal()">
                        <option value="varejo">Varejo (Margem Padrão)</option>
                        <option value="atacado">Atacado (Margem de Volume)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="lucro">Margem de Lucro Almejada (%):</label>
                    <input type="number" id="lucro" value="25">
                    <label for="impostosInput">Impostos sobre a Venda Faturamento (%):</label>
                    <input type="number" id="impostosInput" value="18">
                    <button onclick="calcularPrecovenda()" class="btn-primary" style="margin-top: 10px;">Processar Mark-up e Preço Final</button>
                </div>
            </div>
            <div id="resultado" class="result-box" style="display:none;"></div>
        </section>
        {% endblock %}
        """
        return render_template_string(html_fallback)

@app.route('/retorno')
def pagina_retorno(): return render_template('retorno.html')
# API ENDPOINTS DE PERSISTÊNCIA (POSTGRESQL DO RENDER)

@app.route('/api/imobiliario', methods=['POST'])
def salvar_imobiliario():
    data = request.get_json()
    v_terr = float(data.get('valor_terreno', 0))
    c_edif = float(data.get('custo_edificacao', 0))
    imp = float(data.get('impostos_anuais', 0))
    v_util = int(data.get('vida_util_anos', 20))
    h_ano = int(data.get('horas_operacionais_ano', 2400))

    amort = (v_terr + c_edif) / v_util
    c_anual = amort + imp
    minutos_ano = h_ano * 60
    c_min = c_anual / minutos_ano if minutos_ano > 0 else 0

    conn = obter_conexao_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO investimentos_iniciais (valor_terreno, custo_edificacao, impostos_transferencia) VALUES (%s, %s, %s);", (v_terr, c_edif, imp))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e: return jsonify({'error': str(e)}), 500
    return jsonify({'status':'sucesso', 'amortizacaoAnual':round(amort,2), 'custoAnualTotal':round(c_anual,2), 'custoMinutoInstalacao':round(c_min,4)})

@app.route('/api/maquinas', methods=['GET', 'POST', 'PUT'])
@app.route('/api/maquinas/<int:maquina_id>', methods=['DELETE'])
def gerenciar_maquinas(maquina_id=None):
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'DELETE' and maquina_id:
        try:
            cursor.execute("DELETE FROM maquinas WHERE id = %s;", (maquina_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    if request.method in ['POST', 'PUT']:
        data = request.get_json()
        id_m = data.get('id')
        nome = data.get('nome')
        preco = float(data.get('preco', 0))
        v_ut = int(data.get('vida_util', 1))
        v_rev = float(data.get('valor_revenda', 0))
        manut = float(data.get('manutencao', 0))
        h_an = int(data.get('horas_ano', 1))
        pot = float(data.get('potencia_kw', 0))
        tar = float(data.get('tarifa_kwh', 0))
        dt_aq = data.get('data_aquisicao') or '2026-01-15'
        dt_mn = data.get('data_manutencao') or '2026-12-20'
        diam = float(data.get('diametro_mm', 0))
        comp = float(data.get('comprimento_mm', 0))
        
        depr = (preco - v_rev) / v_ut if preco > v_rev else 0
        min_ano = h_an * 60
        c_energ = (pot * tar) / 60.0
        c_min = ((depr + manut) / min_ano) + c_energ

        try:
            if request.method == 'PUT' and id_m:
                cursor.execute(
                    """UPDATE maquinas SET nome_maquina=%s, preco_compra=%s, tempo_vida_util_anos=%s, valor_revenda_estimado=%s, 
                                          custo_manutencao_anual=%s, horas_ativas_ano=%s, potencia_kw=%s, tarifa_kwh=%s, 
                                          data_aquisicao=%s, data_manutencao_preventiva=%s, diametro_trabalho_mm=%s, comprimento_trabalho_mm=%s, custo_minuto_maquina=%s 
                       WHERE id=%s;""", (nome, preco, v_ut, v_rev, manut, h_an, pot, tar, dt_aq, dt_mn, diam, comp, c_min, id_m)
                )
            else:
                cursor.execute(
                    """INSERT INTO maquinas (nome_maquina, preco_compra, tempo_vida_util_anos, valor_revenda_estimado, custo_manutencao_anual, 
                                            horas_ativas_ano, potencia_kw, tarifa_kwh, data_aquisicao, data_manutencao_preventiva, 
                                            diametro_trabalho_mm, comprimento_trabalho_mm, custo_minuto_maquina) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", (nome, preco, v_ut, v_rev, manut, h_an, pot, tar, dt_aq, dt_mn, diam, comp, c_min)
                )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500

    cursor.execute("SELECT * FROM maquinas ORDER BY id DESC;")
    maquinas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(maquinas)

@app.route('/api/calculo-markup', methods=['POST'])
def calcular_markup():
    data = request.get_json()
    c_tot = float(data.get('custo_total', 0))
    luc = float(data.get('margem_lucro', 0))
    imp = float(data.get('impostos', 0))
    den = 1 - ((luc + imp) / 100)
    if den <= 0: return jsonify({'error': 'Erro'}), 400
    return jsonify({'markup': round(1/den, 2), 'preco_venda': round(c_tot * (1/den), 2)})

@app.route('/api/funcionarios', methods=['GET'])
def listar_funcionarios_rh():
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM funcionarios ORDER BY id DESC;")
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(res)
    except Exception: return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
