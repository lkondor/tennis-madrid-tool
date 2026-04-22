import streamlit as st

def render_prediction(result, playerA, playerB):
    st.title(f"{playerA} vs {playerB}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(playerA)
        st.metric("Ace previsti", result["playerA"]["aces"])
        st.metric("Break previsti", result["playerA"]["breaks"])
    with c2:
        st.subheader(playerB)
        st.metric("Ace previsti", result["playerB"]["aces"])
        st.metric("Break previsti", result["playerB"]["breaks"])

    st.divider()
    c3, c4 = st.columns(2)
    with c3:
        st.metric("Ace totali", result["totals"]["aces"])
    with c4:
        st.metric("Break totali", result["totals"]["breaks"])
