import streamlit as st

def render_match_selector(matches):
    options = [f"{m.player1} vs {m.player2} ({m.court})" for m in matches]
    idx = st.sidebar.selectbox("Scegli partita", range(len(options)), format_func=lambda i: options[i])
    return matches[idx]
