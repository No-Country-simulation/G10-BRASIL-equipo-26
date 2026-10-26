import streamlit as st

st.set_page_config(page_title="NovaMente", page_icon="🧠", layout="wide")

st.title("🧠 Projeto NovaMente")
st.subheader("Sistema Inteligente de Adaptação e Geração de Conteúdo Educacional")

st.success("Ambiente de desenvolvimento configurado com sucesso!")

# Sidebar para parâmetros de entrada
st.sidebar.header("Configurações do Conteúdo")
perfil = st.sidebar.selectbox("Perfil do Estudante", ["Iniciante", "Pleno", "Executivo"])
formato = st.sidebar.selectbox("Formato desejado", ["Flashcards", "Resumo TL;DR", "Quiz", "Tutorial"])

st.write(f"**Perfil Selecionado:** {perfil}")
st.write(f"**Formato Selecionado:** {formato}")