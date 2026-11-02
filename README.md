# SGE - Sistema de Gestão de Equipamentos (AC3)

Repositório desenvolvido no âmbito acadêmico, evoluindo a arquitetura em camadas da AC2 para a entrega da AC3, com foco em validações estritas de hardware, auditoria de movimentações e exportação de relatórios.

## 🚀 Arquitetura e Tecnologias
- **Back-end:** Python, Flask (API REST)
- **Banco de Dados:** SQLite (com tabelas relacionais para gestão de equipamentos e histórico de movimentações com motivo)
- **Front-end:** Streamlit (Interface web interativa com painel de controle e exportação em CSV)

## 📌 Funcionalidades Principais (AC3)

1. **Painel de Controle Operacional (`📊 Painel de controle`)**
   - Métricas em tempo real (Total de equipamentos, ativos, em estoque e em manutenção).
   - Gráficos de barras interativos segmentados por tipo de hardware.
   - Tabela consolidada do inventário atual.
   - **Exportação de Dados:** Botão para download em CSV do inventário completo de equipamentos.

2. **Registro e Movimentação (`🔄 Registro e Movimentação`)**
   - Entrada de novos equipamentos (Terminais POS, Pinpads, Tablets) com validação rigorosa de formato via Regex:
     - **Terminal POS:** Formato `XXX-XXX-XXX` (obrigatoriamente iniciando por `541` ou `542`).
     - **Pinpad:** Formato `XXXXXXXXX` com 9 dígitos numéricos (obrigatoriamente iniciando por `541` ou `542`).
     - **Tablet:** Formato alfanumérico de 11 caracteres (padrão Samsung).
   - Atualização de status de equipamentos existentes (incluindo opção de `Sucateado/Baixado`).
   - **Regra de Negócio & Auditoria:** Campo `Motivo/Observação` obrigatório (mínimo de 5 caracteres) para registrar qualquer movimentação.
   - **Validação de Segurança:** Impedimento automático de atualizações para o mesmo status atual, mantendo a auditoria limpa e sem registros redundantes.

3. **Auditoria e Histórico (`📋 Histórico e Filtros`)**
   - Registro automático e imutável de movimentações com data, hora, status anterior, novo status e motivo.
   - Filtros dinâmicos por número de série e por novo status para consulta imediata.
   - **Exportação de Relatórios:** Botão para download em CSV da trilha temporal de histórico de movimentações.

## ⚙️ Como Executar

Abra dois terminais na pasta do projeto e execute os comandos:

```bash
# 1. Executar o Servidor Back-end (Flask)
python app.py

# 2. Executar a Interface Front-end (Streamlit)
streamlit run sistema.py

# 3. (Opcional) Popular o Banco de Dados com Dados de Teste
python popular_banco.py