import sqlite3
import re
from flask import Flask, jsonify, request
from flasgger import Swagger
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'SGE - API de Gestão de Equipamentos',
    'uiversion': 3,
    'description': 'Documentação interativa da API REST do Sistema de Gestão de Equipamentos (AC Final).'
}
swagger = Swagger(app)


def inicializar_banco():
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            numero_serie TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_serie TEXT NOT NULL,
            status_anterior TEXT,
            status_novo TEXT NOT NULL,
            motivo TEXT NOT NULL,
            usuario TEXT DEFAULT 'Sistema',
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            perfil TEXT NOT NULL
        )
    ''')

    # Usuários padrão para acesso imediato
    usuarios_padrao = [
        ('admin', 'Supervisor Geral', generate_password_hash('admin123'), 'Supervisor'),
        ('suporte', 'Analista de Suporte', generate_password_hash('suporte123'), 'Operador')
    ]
    for username, nome, senha_hash, perfil in usuarios_padrao:
        cursor.execute('''
            INSERT OR IGNORE INTO usuarios (username, nome, senha_hash, perfil)
            VALUES (?, ?, ?, ?)
        ''', (username, nome, senha_hash, perfil))

    conexao.commit()
    conexao.close()


@app.route('/api/login', methods=['POST'])
def login():
    """
    Autentica um usuário no sistema
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: admin123
    responses:
      200:
        description: Login realizado com sucesso
      401:
        description: Usuário ou senha inválidos
    """
    dados = request.get_json() or {}
    username = dados.get('username', '').strip()
    password = dados.get('password', '')

    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT username, nome, senha_hash, perfil FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conexao.close()

    if user and check_password_hash(user[2], password):
        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "usuario": {
                "username": user[0],
                "nome": user[1],
                "perfil": user[3]
            }
        }), 200

    return jsonify({"mensagem": "Usuário ou senha inválidos."}), 401


@app.route('/api/resumo', methods=['GET'])
def resumo_inventario():
    """
    Retorna o resumo quantitativo do inventário e alertas de estoque crítico
    ---
    tags:
      - Inventário
    parameters:
      - name: minimo
        in: query
        type: integer
        required: false
        default: 5
        description: Quantidade mínima em estoque antes de disparar alerta crítico
    responses:
      200:
        description: Dados consolidados por tipo de equipamento e status
    """
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT tipo, status, numero_serie FROM equipamentos')
    equipamentos_bd = cursor.fetchall()
    conexao.close()

    resumo = {
        "Equipamento": ["Terminal POS", "Pinpad", "Tablet"],
        "Ativos": [0, 0, 0],
        "Em Manutenção": [0, 0, 0],
        "Em Estoque": [0, 0, 0]
    }

    for tipo, status, _ in equipamentos_bd:
        if tipo in resumo["Equipamento"]:
            idx = resumo["Equipamento"].index(tipo)
            if status == "Ativo":
                resumo["Ativos"][idx] += 1
            elif status == "Em Manutenção":
                resumo["Em Manutenção"][idx] += 1
            elif status == "Em Estoque":
                resumo["Em Estoque"][idx] += 1

    estoque_minimo = request.args.get('minimo', default=5, type=int)
    alertas = []
    for idx, equip in enumerate(resumo["Equipamento"]):
        qtd_estoque = resumo["Em Estoque"][idx]
        if qtd_estoque < estoque_minimo:
            alertas.append({
                "equipamento": equip,
                "quantidade_estoque": qtd_estoque,
                "minimo_recomendado": estoque_minimo
            })

    resumo["alertas_estoque_critico"] = alertas
    return jsonify(resumo), 200


@app.route('/api/equipamentos', methods=['GET'])
def listar_equipamentos():
    """
    Lista todos os equipamentos cadastrados no banco de dados
    ---
    tags:
      - Inventário
    responses:
      200:
        description: Lista completa de equipamentos com tipo, número de série e status
    """
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT tipo, numero_serie, status FROM equipamentos")
    equipamentos = cursor.fetchall()
    conexao.close()

    lista = []
    for linha in equipamentos:
        lista.append({
            'tipo': linha[0],
            'numero_serie': linha[1],
            'status': linha[2]
        })

    return jsonify(lista), 200


@app.route('/api/cadastrar', methods=['POST'])
def cadastrar_equipamento():
    """
    Cadastra um novo equipamento com validação estrita de Número de Série (Regex)
    ---
    tags:
      - Movimentações
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - tipo
            - numero_serie
            - status
          properties:
            tipo:
              type: string
              enum: [Terminal POS, Pinpad, Tablet]
              example: Terminal POS
            numero_serie:
              type: string
              example: 541-123-456
            status:
              type: string
              enum: [Ativo, Em Manutenção, Em Estoque]
              example: Em Estoque
            usuario:
              type: string
              example: admin
    responses:
      201:
        description: Equipamento cadastrado com sucesso
      400:
        description: Erro de validação de S/N ou duplicidade
    """
    dados = request.get_json() or {}
    tipo = dados.get('tipo')
    numero_serie = dados.get('numero_serie', '').upper()
    status = dados.get('status')
    usuario = dados.get('usuario', 'Sistema')

    if tipo == "Terminal POS":
        if not re.match(r'^(541|542)-\d{3}-\d{3}$', numero_serie):
            return jsonify({"mensagem": "Erro: S/N de POS deve ter o formato XXX-XXX-XXX e iniciar com 541 ou 542."}), 400

    elif tipo == "Pinpad":
        if not re.match(r'^(541|542)\d{6}$', numero_serie):
            return jsonify({"mensagem": "Erro: S/N de Pinpad deve ter exatos 9 números e iniciar com 541 ou 542."}), 400

    elif tipo == "Tablet":
        if not re.match(r'^[A-Z0-9]{11}$', numero_serie):
            return jsonify({"mensagem": "Erro: S/N de Tablet deve conter exatamente 11 caracteres alfanuméricos."}), 400

    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    try:
        cursor.execute('INSERT INTO equipamentos (tipo, numero_serie, status) VALUES (?, ?, ?)', (tipo, numero_serie, status))
        cursor.execute("""
            INSERT INTO historico_movimentacoes (numero_serie, status_anterior, status_novo, motivo, usuario, data_hora)
            VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
        """, (numero_serie, "Sem Registro", status, "Entrada inicial no sistema", usuario))
        conexao.commit()
        retorno = ({"mensagem": "Cadastrado com sucesso!"}, 201)
    except sqlite3.IntegrityError:
        retorno = ({"mensagem": "Erro: Esse Número de Série já existe no sistema."}, 400)
    finally:
        conexao.close()

    return jsonify(retorno[0]), retorno[1]


@app.route('/api/movimentar', methods=['PUT'])
def movimentar_equipamento():
    """
    Atualiza o status de um equipamento existente e grava trilha de auditoria
    ---
    tags:
      - Movimentações
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - numero_serie
            - status
            - motivo
          properties:
            numero_serie:
              type: string
              example: 541-123-456
            status:
              type: string
              enum: [Ativo, Em Manutenção, Em Estoque, Sucateado/Baixado]
              example: Em Manutenção
            motivo:
              type: string
              example: Tela danificada durante operação em campo
            usuario:
              type: string
              example: admin
            perfil:
              type: string
              example: Supervisor
    responses:
      200:
        description: Status atualizado e histórico registrado
      400:
        description: Motivo inválido ou status redundante
      403:
        description: Perfil sem permissão para sucatear equipamento
      404:
        description: Equipamento não encontrado
    """
    dados = request.get_json() or {}
    numero_serie = dados.get('numero_serie', '').upper()
    status_novo = dados.get('status')
    motivo = dados.get('motivo')
    usuario = dados.get('usuario', 'Sistema')
    perfil = dados.get('perfil', 'Supervisor')

    if perfil == "Operador" and status_novo == "Sucateado/Baixado":
        return jsonify({"mensagem": "Acesso negado: Apenas usuários com perfil Supervisor podem baixar/sucatear equipamentos."}), 403

    if not motivo or len(motivo.strip()) < 5:
        return jsonify({"mensagem": "Erro: É obrigatório informar um motivo válido (mínimo 5 caracteres) para a movimentação."}), 400

    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT status FROM equipamentos WHERE numero_serie = ?", (numero_serie,))
    resultado = cursor.fetchone()

    if not resultado:
        conexao.close()
        return jsonify({"mensagem": "Equipamento não encontrado. Verifique o Número de Série."}), 404

    status_anterior = resultado[0]

    if status_anterior == status_novo:
        conexao.close()
        return jsonify({"mensagem": f"Atenção: O equipamento já se encontra com o status '{status_novo}'."}), 400

    cursor.execute('UPDATE equipamentos SET status = ? WHERE numero_serie = ?', (status_novo, numero_serie))
    cursor.execute("""
        INSERT INTO historico_movimentacoes (numero_serie, status_anterior, status_novo, motivo, usuario, data_hora)
        VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
    """, (numero_serie, status_anterior, status_novo, motivo, usuario))

    conexao.commit()
    conexao.close()

    return jsonify({"mensagem": "Status atualizado e histórico registrado com sucesso!"}), 200


@app.route('/api/historico', methods=['GET'])
def listar_historico():
    """
    Retorna o histórico completo e imutável de movimentações
    ---
    tags:
      - Auditoria
    responses:
      200:
        description: Lista ordenada das movimentações registradas
    """
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT numero_serie, status_anterior, status_novo, motivo, usuario, data_hora FROM historico_movimentacoes ORDER BY id DESC")
    historico = cursor.fetchall()
    conexao.close()

    lista_historico = []
    for linha in historico:
        lista_historico.append({
            'numero_serie': linha[0],
            'status_anterior': linha[1],
            'status_novo': linha[2],
            'motivo': linha[3],
            'usuario': linha[4],
            'data_hora': linha[5]
        })

    return jsonify(lista_historico), 200


if __name__ == '__main__':
    inicializar_banco()
    app.run(port=5000, debug=True)