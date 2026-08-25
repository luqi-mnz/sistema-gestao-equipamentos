import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

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
    
    cursor.execute('SELECT COUNT(*) FROM equipamentos')
    if cursor.fetchone()[0] == 0:
        iniciais = [
            ('Terminal POS', 'POS-001', 'Ativo'),
            ('Terminal POS', 'POS-002', 'Em Manutenção'),
            ('Pinpad', 'PIN-101', 'Ativo'),
            ('Tablet', 'TAB-909', 'Em Estoque')
        ]
        cursor.executemany('INSERT OR IGNORE INTO equipamentos (tipo, numero_serie, status) VALUES (?, ?, ?)', iniciais)
        conexao.commit()
    conexao.close()

@app.route('/api/resumo', methods=['GET'])
def resumo_inventario():
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT tipo, status FROM equipamentos')
    equipamentos_bd = cursor.fetchall()
    conexao.close()
    
    resumo = {
        "Equipamento": ["Terminal POS", "Pinpad", "Tablet"],
        "Ativos": [0, 0, 0],
        "Em Manutenção": [0, 0, 0],
        "Em Estoque": [0, 0, 0]
    }
    
    for tipo, status in equipamentos_bd:
        if tipo in resumo["Equipamento"]:
            idx = resumo["Equipamento"].index(tipo)
            if status == "Ativo": resumo["Ativos"][idx] += 1
            elif status == "Em Manutenção": resumo["Em Manutenção"][idx] += 1
            elif status == "Em Estoque": resumo["Em Estoque"][idx] += 1
            
    return jsonify(resumo)

@app.route('/api/cadastrar', methods=['POST'])
def cadastrar_equipamento():
    dados = request.get_json()
    tipo = dados.get('tipo')
    numero_serie = dados.get('numero_serie')
    status = dados.get('status')
    
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    try:
        cursor.execute('INSERT INTO equipamentos (tipo, numero_serie, status) VALUES (?, ?, ?)', (tipo, numero_serie, status))
        conexao.commit()
        retorno = ({"mensagem": "Cadastrado com sucesso!"}, 201)
    except sqlite3.IntegrityError:
        retorno = ({"mensagem": "Erro: Esse Número de Série já existe no sistema."}, 400)
    conexao.close()
    
    return jsonify(retorno[0]), retorno[1]

@app.route('/api/movimentar', methods=['PUT'])
def movimentar_equipamento():
    dados = request.get_json()
    numero_serie = dados.get('numero_serie')
    status_novo = dados.get('status')
    
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute('UPDATE equipamentos SET status = ? WHERE numero_serie = ?', (status_novo, numero_serie))
    linhas = cursor.rowcount
    conexao.commit()
    conexao.close()
    
    if linhas > 0:
        return jsonify({"mensagem": "Status atualizado com sucesso!"}), 200
    else:
        return jsonify({"mensagem": "Equipamento não encontrado. Verifique o Número de Série."}), 404

if __name__ == '__main__':
    inicializar_banco()
    app.run(port=5000, debug=True)