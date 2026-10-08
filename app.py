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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_serie TEXT NOT NULL,
            status_anterior TEXT,
            status_novo TEXT NOT NULL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
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
        INSERT INTO historico_movimentacoes (numero_serie, status_anterior, status_novo, data_hora)
        VALUES (?, ?, ?, datetime('now', 'localtime'))
    """, (numero_serie, status_anterior, status_novo))
    
    conexao.commit()
    conexao.close()
    
    return jsonify({"mensagem": "Status atualizado e histórico registrado com sucesso!"}), 200

@app.route('/api/historico', methods=['GET'])
def listar_historico():
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT numero_serie, status_anterior, status_novo, data_hora FROM historico_movimentacoes ORDER BY id DESC")
    historico = cursor.fetchall()
    conexao.close()
    
    lista_historico = []
    for linha in historico:
        lista_historico.append({
            'numero_serie': linha[0],
            'status_anterior': linha[1],
            'status_novo': linha[2],
            'data_hora': linha[3]
        })
        
    return jsonify(lista_historico), 200

if __name__ == '__main__':
    inicializar_banco()
    app.run(port=5000, debug=True)
    