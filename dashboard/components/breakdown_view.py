import streamlit as st

def render_breakdown(context):
    st.subheader("Model Breakdown")

    st.json({
        "Elo A": context.get("elo_a", "-"),
        "Elo B": context.get("elo_b", "-"),
        "Win Prob A": context.get("win_prob_a", "-"),
        "Win Prob B": context.get("win_prob_b", "-"),
        "Court Factor": context.get("court_factor", "-"),
        "Madrid Factor": context.get("madrid_factor", "-"),
        "Match Length": context.get("match_length", "-"),
        "Avg Temp": context.get("avg_temp", "-"),
        "Wind km/h": context.get("wind_kmh", "-"),
        "Ace Weather Factor": context.get("ace_weather_factor", "-"),
        "Break Weather Factor": context.get("break_weather_factor", "-"),
    })
