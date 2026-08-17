import streamlit as st

st.set_page_config(page_title="Sistema de Equipamentos", layout="wide")

st.title("Sistema de Gestão de Equipamentos (SGE)")
st.subheader("Cadastro de Máquinas com Defeito")

if 'lista_equipamentos' not in st.session_state:
    st.session_state.lista_equipamentos = []

with st.form("form_cadastro"):
    tipo_maquina = st.selectbox("Qual o tipo de equipamento?", ["POS", "Pinpad", "Tablet"])
    numero_serie = st.text_input("Número de Série do Equipamento")
    status = st.selectbox("Status", ["Disponível", "Em Manutenção", "Aguardando Troca"])
    defeito_relatado = st.text_area("Descrição do Defeito (se houver)")

    botao_salvar = st.form_submit_button("Cadastrar Equipamento")

if botao_salvar:
    if numero_serie == "":
        st.error("Aviso: O Número de Série não pode ficar vazio!")
    else:
        novo_equipamento = {
            "Tipo": tipo_maquina,
            "Série": numero_serie,
            "Status": status,
            "Defeito": defeito_relatado
        }
        st.session_state.lista_equipamentos.append(novo_equipamento)
        st.success("Equipamento cadastrado com sucesso!")

st.write("---")
st.write("### Equipamentos Cadastrados no Sistema")

if len(st.session_state.lista_equipamentos) > 0:
    st.table(st.session_state.lista_equipamentos)
else:
    st.info("Nenhum equipamento cadastrado ainda.")