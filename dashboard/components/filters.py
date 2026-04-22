import streamlit as st

def render_filters():
    st.sidebar.header("Filtri")
    surface = st.sidebar.selectbox("Superficie", ["clay", "hard", "grass"], index=0)
    return {"surface": surface}
