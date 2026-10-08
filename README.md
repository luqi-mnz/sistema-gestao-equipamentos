# SGE - Sistema de Gestão de Equipamentos (AC2)

Repositório desenvolvido no âmbito acadêmico, evoluindo a arquitetura em camadas da AC1 para uma aplicação completa de gestão, controle operacional e auditoria de ativos de hardware.

## 🚀 Arquitetura e Tecnologias
- **Back-end:** Python, Flask (API REST)
- **Banco de Dados:** SQLite (com tabelas relacionais para gestão de equipamentos e histórico de movimentações)
- **Front-end:** Streamlit (Interface web interativa com painel de controle)

## 📌 Funcionalidades Principais (AC2)

1. **Painel de Controle Operacional (`📊 Painel de controle`)**
   - Métricas em tempo real (Total de equipamentos, ativos, em estoque e em manutenção).
   - Gráficos de barras interativos segmentados por tipo de hardware.
   - Tabela consolidada do inventário atual.

2. **Registro e Movimentação (`🔄 Registro e Movimentação`)**
   - Entrada de novos equipamentos (Terminais POS, Pinpads, Tablets) com validação de duplicidade por número de série.
   - Atualização de status de equipamentos existentes.
   - **Validação de Segurança:** Impedimento automático de atualizações para o mesmo status atual, mantendo a auditoria limpa e sem registros redundantes.

3. **Auditoria e Histórico (`📋 Histórico e Filtros`)**
   - Registro automático de movimentações com data, hora, status anterior e novo status.
   - Filtros dinâmicos por número de série e por novo status para consulta imediata.

## ⚙️ Como Executar

Abra dois terminais na pasta do projeto e execute os comandos:

```bash
# 1. Executar o Servidor Back-end (Flask)
python app.py

# 2. Executar a Interface Front-end (Streamlit)
streamlit run sistema.py