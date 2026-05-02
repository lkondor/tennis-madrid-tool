import json
from pathlib import Path
from types import SimpleNamespace

import streamlit as st

from services.model_service import run_prediction


HISTORICAL_MATCHES_PATH = Path("data/raw/historical_matches.json")


def load_json(path, default):
    if not path.exists():
        return default

    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return default
        return json.loads(text)
    except Exception:
        return default


def to_match_object(row):
    return SimpleNamespace(
        player1=row.get("player1", ""),
        player2=row.get("player2", ""),
        date=row.get("date", ""),
        court=row.get("court", ""),
    )


def main():
    st.set_page_config(layout="wide")
    st.title("Model Validation")

    matches = load_json(HISTORICAL_MATCHES_PATH, [])

    if not matches:
        st.error("historical_matches.json è vuoto.")
        return

    st.sidebar.subheader("Filtri")

    tours = sorted(set(str(m.get("tour", "unknown")) for m in matches))
    seasons = sorted(set(str(m.get("season", "unknown")) for m in matches), reverse=True)
    surfaces = sorted(set(str(m.get("surface", "unknown")) for m in matches))

    selected_tour = st.sidebar.selectbox("Tour", tours, index=tours.index("atp") if "atp" in tours else 0)
    selected_season = st.sidebar.selectbox("Season", seasons)
    selected_surface = st.sidebar.selectbox("Surface", surfaces)

    filtered = [
        m for m in matches
        if str(m.get("tour")) == selected_tour
        and str(m.get("season")) == selected_season
        and str(m.get("surface")) == selected_surface
        and m.get("player1")
        and m.get("player2")
    ]

    st.metric("Match filtrati", len(filtered))

    if not filtered:
        st.warning("Nessun match trovato con questi filtri.")
        return

    options = {
        f"{m.get('date')} | {m.get('tournament_slug')} | {m.get('player1')} vs {m.get('player2')}": m
        for m in filtered[:1000]
    }

    selected_label = st.selectbox("Seleziona match storico", list(options.keys()))
    selected_row = options[selected_label]

    match = to_match_object(selected_row)
    result, context = run_prediction(match)

    st.subheader("Prediction Output")
    st.json(result)

    st.subheader("Model Context")
    st.json(context)

    st.subheader("Historical Match Row")
    st.json(selected_row)


if __name__ == "__main__":
    main()
