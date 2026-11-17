import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="SGE - Gestão de Equipamentos", layout="wide")

# Controle de sessão de autenticação
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'usuario_info' not in st.session_state:
    st.session_state.usuario_info = None
if 'pagina' not in st.session_state:
    st.session_state.pagina = "📊 Painel de controle"

# TELA DE LOGIN
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("🔐 SGE - Acesso ao Sistema")
        st.markdown("Informe suas credenciais para gerenciar o inventário de hardware.")

        with st.form("form_login"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar", type="primary", use_container_width=True)

            if submit:
                if username and password:
                    try:
                        resp = requests.post(
                            "http://127.0.0.1:5000/api/login",
                            json={"username": username, "password": password}
                        )
                        if resp.status_code == 200:
                            st.session_state.logado = True
                            st.session_state.usuario_info = resp.json()["usuario"]
                            st.rerun()
                        else:
                            st.error(resp.json().get("mensagem", "Erro ao autenticar."))
                    except requests.exceptions.ConnectionError:
                        st.error("Erro de conexão com a API Flask (porta 5000).")
                else:
                    st.warning("Preencha usuário e senha.")

        st.info("**Credenciais de Demonstração:**\n- **Supervisor:** `admin` / `admin123`\n- **Operador:** `suporte` / `suporte123`")

# APLICAÇÃO AUTENTICADA
else:
    user = st.session_state.usuario_info
    eh_supervisor = user["perfil"] == "Supervisor"
    opcoes = ["📊 Painel de controle", "🔄 Registro e Movimentação", "📋 Histórico e Filtros"]
    current_index = opcoes.index(st.session_state.pagina) if st.session_state.pagina in opcoes else 0

    st.sidebar.title("Navegação SGE")
    st.sidebar.markdown(f"👤 **{user['nome']}**\n\n🛡️ Perfil: `{user['perfil']}`")
    st.sidebar.markdown("---")

    escolha = st.sidebar.radio("Escolha a tela:", opcoes, index=current_index)
    st.session_state.pagina = escolha

    st.sidebar.markdown("---")
    st.sidebar.caption("📄 Documentação API (Swagger):\nhttp://127.0.0.1:5000/apidocs")

    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.usuario_info = None
        st.rerun()

    # TELA 1: PAINEL DE CONTROLE
    if st.session_state.pagina == "📊 Painel de controle":
        col_tit, col_cfg = st.columns([3, 1])
        col_tit.title("📊 Painel de controle")
        minimo_estoque = col_cfg.number_input(
            "Estoque Mínimo (Alerta)",
            min_value=1,
            max_value=100,
            value=5,
            disabled=not eh_supervisor,
            help="Apenas usuários com perfil Supervisor podem alterar o parâmetro de estoque mínimo."
        )

        st.subheader("Resumo Operacional")

        try:
            resposta = requests.get("http://127.0.0.1:5000/api/resumo", params={"minimo": minimo_estoque})
            if resposta.status_code == 200:
                dados = resposta.json()
                alertas = dados.pop("alertas_estoque_critico", [])
                df_resumo = pd.DataFrame(dados)

                # ALERTAS DE ESTOQUE CRÍTICO
                if alertas:
                    for alerta in alertas:
                        st.error(
                            f"🚨 **ALERTA DE ESTOQUE CRÍTICO:** **{alerta['equipamento']}** possui apenas "
                            f"**{alerta['quantidade_estoque']}** unidade(s) em estoque "
                            f"(mínimo recomendado: {alerta['minimo_recomendado']})."
                        )
                else:
                    st.success(f"✅ Níveis de estoque dentro da normalidade (mínimo de {minimo_estoque} unidades por categoria).")

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
                        if not df_completo.empty:
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

    # TELA 2: REGISTRO E MOVIMENTAÇÃO
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
                    dados_cadastro = {
                        "tipo": tipo,
                        "numero_serie": sn.upper(),
                        "status": status,
                        "usuario": user["username"]
                    }
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

            if eh_supervisor:
                opcoes_status = ["Ativo", "Em Manutenção", "Em Estoque", "Sucateado/Baixado"]
            else:
                opcoes_status = ["Ativo", "Em Manutenção", "Em Estoque"]
                st.caption("ℹ️ Perfil Operador: A baixa/sucateamento de equipamentos é restrita ao perfil Supervisor.")

            novo_status = st.selectbox("Novo Status", opcoes_status)
            motivo = st.text_area("Motivo/Observação (Obrigatório)", placeholder="Ex: Equipamento enviado para manutenção devido à tela quebrada.")

            if st.button("Atualizar no Banco de Dados", type="primary"):
                if sn_mov and motivo:
                    dados_mov = {
                        "numero_serie": sn_mov.upper(),
                        "status": novo_status,
                        "motivo": motivo,
                        "usuario": user["username"],
                        "perfil": user["perfil"]
                    }
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

    # TELA 3: HISTÓRICO E FILTROS
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