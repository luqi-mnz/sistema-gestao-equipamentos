# SGE - Sistema de Gestão de Equipamentos (AC Final)

Repositório desenvolvido no âmbito acadêmico (ADS - Faculdade Impacta), consolidando a evolução das entregas anteriores (AC1, AC2 e AC3) em uma aplicação completa de gestão, segurança, auditoria e monitoramento de ativos de hardware.

## 🚀 Arquitetura e Tecnologias
- **Back-end:** Python, Flask (API RESTful), Flasgger (Documentação OpenAPI/Swagger), Werkzeug Security (Hash de senhas)
- **Banco de Dados:** SQLite (tabelas relacionais para equipamentos, trilha de auditoria e controle de usuários)
- **Front-end:** Streamlit (Interface web interativa com controle de sessão, RBAC e exportação em CSV)

## 📌 Funcionalidades Principais (AC Final)

1. **Autenticação e Controle de Acesso (Login & RBAC)**
   - Tela de login com validação via API (`POST /api/login`) e gerenciamento de sessão (`st.session_state`).
   - **Perfil Supervisor (`admin` / `admin123`):** Acesso total ao sistema, incluindo baixa/sucateamento de ativos e configuração do limite de estoque mínimo.
   - **Perfil Operador (`suporte` / `suporte123`):** Acesso ao painel, cadastros e movimentações operacionais (com bloqueio para sucateamento e alteração de parâmetros críticos).
   - Rastreabilidade completa identificando qual usuário realizou cada movimentação no histórico.

2. **Painel de Controle e Alertas de Estoque Crítico (`📊 Painel de controle`)**
   - Monitoramento em tempo real com disparo automático de alertas visuais caso alguma categoria (POS, Pinpad ou Tablet) fique abaixo do estoque mínimo configurado.
   - Métricas operacionais, gráficos de barras por tipo de hardware, tabela consolidada e exportação do inventário completo em CSV.

3. **Registro e Movimentação com Validação Estrita (`🔄 Registro e Movimentação`)**
   - Validação rigorosa de Número de Série via Regex (`Terminal POS`: `XXX-XXX-XXX` iniciando com 541/542; `Pinpad`: 9 dígitos iniciando com 541/542; `Tablet`: 11 caracteres alfanuméricos).
   - Bloqueio de atualizações redundantes (mesmo status) e exigência de justificativa obrigatória (mínimo de 5 caracteres).

4. **Auditoria e Histórico (`📋 Histórico e Filtros`)**
   - Trilha imutável de movimentações contendo equipamento, status anterior, novo status, motivo, usuário responsável e data/hora, com filtros dinâmicos e exportação em CSV.

5. **Documentação Interativa da API (Swagger)**
   - Especificação OpenAPI disponível em `http://127.0.0.1:5000/apidocs` para testes e consulta de todos os endpoints REST.

## ⚙️ Como Executar

Abra dois terminais na pasta do projeto e execute os comandos:

```bash
# 1. Instalar dependências (caso necessário)
pip install flask flasgger streamlit pandas requests

# 2. Executar o Servidor Back-end (Flask)
python app.py

# 3. (Opcional) Popular o Banco de Dados com Data Seeding
python popular_banco.py

# 4. Executar a Interface Front-end (Streamlit)
python -m streamlit run sistema.py