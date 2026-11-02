import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="SGE - Gestão de Equipamentos", layout="wide")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "📊 Painel de controle"

opcoes = ["📊 Painel de controle", "🔄 Registro e Movimentação", "📋 Histórico e Filtros"]
current_index = opcoes.index(st.session_state.pagina) if st.session_state.pagina in opcoes else 0

st.sidebar.title("Navegação SGE")
escolha = st.sidebar.radio("Escolha a tela:", opcoes, index=current_index)
st.session_state.pagina = escolha

if st.session_state.pagina == "📊 Painel de controle":
    st.title("📊 Painel de controle")
    st.subheader("Resumo Operacional")
    
    try:
        resposta = requests.get("http://127.0.0.1:5000/api/resumo")
        if resposta.status_code == 200:
            dados = resposta.json()
            df_resumo = pd.DataFrame(dados)
            
            total_ativos = df_resumo['Ativos'].sum()
            total_estoque = df_resumo['Em Estoque'].sum()
            total_manutencao = df_resumo['Em Manutenção'].sum()
            total_equipamentos = total_ativos + total_estoque + total_manutencao
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de Equipamentos", int(total_equipamentos))
            col2.metric("Operacionais", int(total_ativos))
            col3.metric("Em estoque", int(total_estoque))
            col4.metric("Aguardando Manutenção", int(total_manutencao))
            
            st.markdown("---")
            
            col_grafico, col_tabela = st.columns(2)
            
            with col_grafico:
                st.subheader("Status por Tipo de Hardware")
                df_grafico = df_resumo.set_index("Equipamento")
                st.bar_chart(df_grafico)
                
            with col_tabela:
                st.subheader("Tabela de Dados")
                st.dataframe(df_resumo, use_container_width=True, hide_index=True)
                
                resposta_equipamentos = requests.get("http://127.0.0.1:5000/api/equipamentos")
                if resposta_equipamentos.status_code == 200:
                    df_completo = pd.DataFrame(resposta_equipamentos.json())
                    df_completo = df_completo[["tipo", "numero_serie", "status"]]
                    
                    csv_inventario = df_completo.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Exportar Inventário Completo para CSV",
                        data=csv_inventario,
                        file_name="inventario_completo.csv",
                        mime="text/csv",
                    )
        else:
            st.error("Erro ao carregar o resumo.")
    except requests.exceptions.ConnectionError:
        st.error("Erro de conexão com a API.")

elif st.session_state.pagina == "🔄 Registro e Movimentação":
    st.title("🔄 Registro e Movimentação")
    
    operacao = st.radio("Selecione uma operação:", ["Entrada de Equipamento NOVO", "Atualizar Status do Equipamento EXISTENTE"])
    st.markdown("---")
    
    if operacao == "Entrada de Equipamento NOVO":
        col1, col2 = st.columns(2)
        tipo = col1.selectbox("Tipo de Hardware", ["Terminal POS", "Pinpad", "Tablet"])
        status = col2.selectbox("Status de Entrada", ["Ativo", "Em Manutenção", "Em Estoque"])
        
        if tipo == "Terminal POS":
            st.info("Formato POS: XXX-XXX-XXX (Iniciando com 541 ou 542. Ex: 541-123-456)")
        elif tipo == "Pinpad":
            st.info("Formato Pinpad: 9 números corridos (Iniciando com 541 ou 542. Ex: 542123456)")
        elif tipo == "Tablet":
            st.info("Formato Tablet: 11 caracteres alfanuméricos. Ex: RXGL304ZLVR")

        sn = st.text_input("Número de Série (S/N)")
        
        if st.button("Salvar no Banco de Dados", type="primary"):
            if sn:
                dados_cadastro = {"tipo": tipo, "numero_serie": sn.upper(), "status": status}
                try:
                    resposta = requests.post("http://127.0.0.1:5000/api/cadastrar", json=dados_cadastro)
                    if resposta.status_code == 201:
                        st.success(resposta.json()["mensagem"])
                    else:
                        st.error(resposta.json()["mensagem"])
                except requests.exceptions.ConnectionError:
                    st.error("Erro de conexão com a API.")
            else:
                st.warning("Preencha o Número de Série antes de salvar.")
                
    elif operacao == "Atualizar Status do Equipamento EXISTENTE":
        sn_mov = st.text_input("Número de Série (S/N) para Movimentar")
        novo_status = st.selectbox("Novo Status", ["Ativo", "Em Manutenção", "Em Estoque", "Sucateado/Baixado"])
        motivo = st.text_area("Motivo/Observação (Obrigatório)", placeholder="Ex: Equipamento enviado para manutenção devido à tela quebrada.")
        
        if st.button("Atualizar no Banco de Dados", type="primary"):
            if sn_mov and motivo:
                dados_mov = {"numero_serie": sn_mov.upper(), "status": novo_status, "motivo": motivo}
                try:
                    resposta = requests.put("http://127.0.0.1:5000/api/movimentar", json=dados_mov)
                    if resposta.status_code == 200:
                        st.success(resposta.json()["mensagem"])
                    else:
                        st.error(resposta.json()["mensagem"])
                except requests.exceptions.ConnectionError:
                    st.error("Erro de conexão com a API.")
            else:
                st.warning("O Número de Série e o Motivo da movimentação são campos obrigatórios.")

elif st.session_state.pagina == "📋 Histórico e Filtros":
    st.title("📋 Histórico e Filtros")
    
    try:
        resposta = requests.get("http://127.0.0.1:5000/api/historico")
        if resposta.status_code == 200:
            dados_historico = resposta.json()
            
            if dados_historico:
                df_historico = pd.DataFrame(dados_historico)
                
                col1, col2 = st.columns(2)
                busca_sn = col1.text_input("Buscar por Número de Série")
                filtro_status = col2.selectbox("Filtrar por Novo Status", ["Todos", "Ativo", "Em Manutenção", "Em Estoque", "Sucateado/Baixado"])
                
                if busca_sn:
                    df_historico = df_historico[df_historico["numero_serie"].str.contains(busca_sn.upper(), case=False)]
                
                if filtro_status != "Todos":
                    df_historico = df_historico[df_historico["status_novo"] == filtro_status]
                    
                st.dataframe(df_historico, use_container_width=True, hide_index=True)
                
                csv_historico = df_historico.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Histórico para CSV",
                    data=csv_historico,
                    file_name="historico_movimentacoes.csv",
                    mime="text/csv",
                )
            else:
                st.info("Nenhuma movimentação registrada no histórico.")
        else:
            st.error("Erro ao carregar o histórico.")
    except requests.exceptions.ConnectionError:
        st.error("Erro de conexão com a API.")