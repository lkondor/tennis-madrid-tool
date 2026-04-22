import streamlit as st

def render_breakdown(context):
    st.subheader("Model Breakdown")
    st.json({
        "Surface Factor": context.get("surface_factor", 1),
        "Madrid Factor": context.get("madrid_factor", 1),
        "Court Factor": context.get("court_factor", 1),
        "Court Historical Factor": context.get("court_historical_factor", 1),
        "Court Current Factor": context.get("court_current_factor", 1),
        "Court Matches Played": context.get("court_matches_played", 0),
        "Weather Temp C": context.get("weather_temp_c", 20),
        "Weather Wind km/h": context.get("weather_wind_kmh", 5),
        "Ace Weather Factor": context.get("ace_weather_factor", 1),
        "Break Weather Factor": context.get("break_weather_factor", 1),
        "Match Length": context.get("match_length", 1),
        "Elo A": context.get("elo_A", 1500),
        "Elo B": context.get("elo_B", 1500),
    })
