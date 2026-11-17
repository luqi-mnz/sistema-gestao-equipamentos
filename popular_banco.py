import requests

URL_CADASTRAR = "http://127.0.0.1:5000/api/cadastrar"
URL_MOVIMENTAR = "http://127.0.0.1:5000/api/movimentar"

equipamentos_iniciais = [
    # Terminais POS (9 dígitos com hífen, iniciando com 541 ou 542)
    {"tipo": "Terminal POS", "numero_serie": "541-100-001", "status": "Ativo", "usuario": "admin"},
    {"tipo": "Terminal POS", "numero_serie": "541-100-002", "status": "Ativo", "usuario": "admin"},
    {"tipo": "Terminal POS", "numero_serie": "542-200-003", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Terminal POS", "numero_serie": "542-200-004", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Terminal POS", "numero_serie": "541-300-005", "status": "Em Manutenção", "usuario": "admin"},
    {"tipo": "Terminal POS", "numero_serie": "542-300-006", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Terminal POS", "numero_serie": "541-400-007", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Terminal POS", "numero_serie": "542-400-008", "status": "Em Estoque", "usuario": "admin"},

    # Pinpads (9 dígitos corridos, iniciando com 541 ou 542)
    {"tipo": "Pinpad", "numero_serie": "541100001", "status": "Ativo", "usuario": "admin"},
    {"tipo": "Pinpad", "numero_serie": "541100002", "status": "Ativo", "usuario": "admin"},
    {"tipo": "Pinpad", "numero_serie": "542200003", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Pinpad", "numero_serie": "542200004", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Pinpad", "numero_serie": "541300005", "status": "Em Manutenção", "usuario": "admin"},
    {"tipo": "Pinpad", "numero_serie": "542300006", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Pinpad", "numero_serie": "541400007", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Pinpad", "numero_serie": "542400008", "status": "Em Estoque", "usuario": "admin"},

    # Tablets (11 caracteres alfanuméricos)
    {"tipo": "Tablet", "numero_serie": "RXGL304ZL01", "status": "Ativo", "usuario": "admin"},
    {"tipo": "Tablet", "numero_serie": "RXGL304ZL02", "status": "Ativo", "usuario": "admin"},
    {"tipo": "Tablet", "numero_serie": "RXGL304ZL03", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Tablet", "numero_serie": "RXGL304ZL04", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Tablet", "numero_serie": "RXGL304ZL05", "status": "Em Manutenção", "usuario": "admin"},
    {"tipo": "Tablet", "numero_serie": "RXGL304ZL06", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Tablet", "numero_serie": "RXGL304ZL07", "status": "Em Estoque", "usuario": "admin"},
    {"tipo": "Tablet", "numero_serie": "RXGL304ZL08", "status": "Em Estoque", "usuario": "admin"},
]

print("Iniciando Data Seeding...")
for item in equipamentos_iniciais:
    resp = requests.post(URL_CADASTRAR, json=item)
    print(f"{item['numero_serie']}: {resp.json().get('mensagem')}")

# Gerando histórico adicional de manutenção
movimentacoes = [
    {
        "numero_serie": "541-300-005",
        "status": "Em Manutenção",
        "motivo": "Falha na leitura de cartão com chip",
        "usuario": "admin",
        "perfil": "Supervisor"
    },
    {
        "numero_serie": "RXGL304ZL05",
        "status": "Em Manutenção",
        "motivo": "Bateria estufada e tela trincada",
        "usuario": "suporte",
        "perfil": "Operador"
    }
]

for mov in movimentacoes:
    requests.put(URL_MOVIMENTAR, json=mov)

print("Data Seeding concluído com sucesso!")