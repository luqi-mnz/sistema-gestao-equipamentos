# SGE - Interface Streamlit (AC1)
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="SGE - Gestão", layout="wide")

st.sidebar.title("Navegação SGE")
menu = st.sidebar.radio("Escolha a tela:", ["🔄 Registro e Movimentação", "📊 Painel de controle"])

if menu == "🔄 Registro e Movimentação":
    st.title("🔄 Registro e Movimentação")
    
    acao = st.radio("Selecione a operação:", ["Entrada de Equipamento NOVO", "Atualizar Status de Equipamento EXISTENTE"])
    st.write("---")

    col1, col2 = st.columns(2)
    
    with col1:
        if acao == "Entrada de Equipamento NOVO":
            tipo_equipamento = st.selectbox("Tipo de Hardware", ["Terminal POS", "Pinpad", "Tablet"])
        numero_serie = st.text_input("Número de Série (S/N)")
    
    with col2:
        if acao == "Entrada de Equipamento NOVO":
            status_novo = st.selectbox("Status de Entrada", ["Ativo", "Em Estoque"])
        else:
            status_novo = st.selectbox("Novo Status:", ["Ativo", "Em Manutenção", "Em Estoque"])
            
    observacoes = st.text_area("Observações Adicionais")
    btn_salvar = st.button("Salvar no Banco de Dados", type="primary")

    if btn_salvar:
        if numero_serie == "":
            st.warning("⚠️ O Número de Série é obrigatório!")
        else:
            if acao == "Entrada de Equipamento NOVO":
                dados = {"tipo": tipo_equipamento, "numero_serie": numero_serie, "status": status_novo}
                try:
                    resposta = requests.post("http://127.0.0.1:5000/api/cadastrar", json=dados)
                    if resposta.status_code == 201:
                        st.success(f"✅ Equipamento (S/N: {numero_serie}) cadastrado com sucesso!")
                    else:
                        st.error(resposta.json().get("mensagem"))
                except:
                    st.error("⚠️ Erro de conexão com o Back-end.")
            else:
                dados = {"numero_serie": numero_serie, "status": status_novo}
                try:
                    resposta = requests.put("http://127.0.0.1:5000/api/movimentar", json=dados)
                    if resposta.status_code == 200:
                        st.success(f"✅ Status do equipamento (S/N: {numero_serie}) atualizado com sucesso!")
                    else:
                        st.error(resposta.json().get("mensagem"))
                except:
                    st.error("⚠️ Erro de conexão com o Back-end.")

elif menu == "📊 Painel de controle":
    st.title("📊 Painel de Gestão de Equipamentos")

    try:
        resposta = requests.get("http://127.0.0.1:5000/api/resumo")
        dados = resposta.json()
        df = pd.DataFrame(dados)
        
        st.subheader("Resumo Operacional")
        col1, col2, col3, col4 = st.columns(4)
        total = df["Ativos"].sum() + df["Em Manutenção"].sum() + df["Em Estoque"].sum()
        
        col1.metric("Total de Equipamentos", total)
        col2.metric("Operacionais", df["Ativos"].sum())
        col3.metric("Em Estoque", df["Em Estoque"].sum())
        col4.metric("Aguardando Manutenção", df["Em Manutenção"].sum())

        st.divider()

        col_grafico, col_tabela = st.columns([2, 1])
        with col_grafico:
            st.subheader("Status por Tipo de Hardware")
            st.bar_chart(df.set_index("Equipamento"))
        with col_tabela:
            st.subheader("Tabela de Dados")
            st.dataframe(df, use_container_width=True)
            
    except:
        st.error("⚠️ Erro de conexão com o Back-end. Rode o app.py!")