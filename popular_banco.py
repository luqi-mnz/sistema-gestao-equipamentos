import sqlite3
import random
import string

def gerar_sn_pos():
    prefixo = random.choice(['541', '542'])
    meio = f"{random.randint(0, 999):03d}"
    fim = f"{random.randint(0, 999):03d}"
    return f"{prefixo}-{meio}-{fim}"

def gerar_sn_pinpad():
    prefixo = random.choice(['541', '542'])
    resto = f"{random.randint(0, 999999):06d}"
    return f"{prefixo}{resto}"

def gerar_sn_tablet():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(11))

def popular_bd():
    tipos = ["Terminal POS", "Pinpad", "Tablet"]
    status_opcoes = ["Ativo", "Em Manutenção", "Em Estoque"]
    
    conexao = sqlite3.connect('sge_banco.db')
    cursor = conexao.cursor()
    
    sucessos = 0
    
    for _ in range(50):
        tipo = random.choice(tipos)
        
        if tipo == "Terminal POS":
            sn = gerar_sn_pos()
        elif tipo == "Pinpad":
            sn = gerar_sn_pinpad()
        else:
            sn = gerar_sn_tablet()
            
        status = random.choice(status_opcoes)
        
        try:
            cursor.execute('''
                INSERT INTO equipamentos (tipo, numero_serie, status) 
                VALUES (?, ?, ?)
            ''', (tipo, sn, status))
            
            cursor.execute('''
                INSERT INTO historico_movimentacoes (numero_serie, status_anterior, status_novo, motivo, data_hora)
                VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
            ''', (sn, "Sem Registro", status, "Carga inicial de dados para testes"))
            
            sucessos += 1
        except sqlite3.IntegrityError:
            pass

    conexao.commit()
    conexao.close()
    
    print(f"✅ Banco populado! {sucessos} equipamentos foram inseridos com sucesso.")

if __name__ == "__main__":
    popular_bd()