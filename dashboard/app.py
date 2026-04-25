import streamlit as st
from streamlit_autorefresh import st_autorefresh

from services.data_service import load_all_matches, get_available_dates, get_matches_by_date, load_meta
from services.model_service import run_prediction
from components.match_selector import render_match_selector
from components.prediction_view import render_prediction
from components.breakdown_view import render_breakdown
from components.filters import render_filters


def main():
    st.set_page_config(layout="wide")
    st_autorefresh(interval=15 * 60 * 1000, key="data_refresh")
    st.title("Madrid Open Predictor")

    meta = load_meta()
    all_matches = load_all_matches()

    if not all_matches:
        st.error("Nessun dato disponibile.")
        return

    st.caption(
        f"Fonte calendario: {meta.get('match_source', 'n/d')} | "
        f"Aggiornato: {meta.get('updated_at', 'n/d')}"
    )

    dates = get_available_dates(all_matches)
    selected_date = st.selectbox("Seleziona data", dates)

    matches = get_matches_by_date(selected_date)

    st.subheader("Ranking match del giorno")

    rows = []
    for m in matches:
        pred, ctx = run_prediction(m)
        rows.append({
            "Match": f"{m.player1} vs {m.player2}",
            "Court": m.court,
            "Ace totali": pred["totals"]["aces"],
            "Break totali": pred["totals"]["breaks"],
            "Confidence": ctx.get("confidence_label"),
            "Confidence score": ctx.get("confidence_score"),
            "Value": ctx.get("value_label"),
            "Value score": ctx.get("value_score"),
        })

    rows = sorted(rows, key=lambda x: x["Value score"] or 0, reverse=True)
    st.dataframe(rows, use_container_width=True)

    top_picks = [
        r for r in rows
        if (r.get("Value score") or 0) >= min_value_score
        and (r.get("Confidence score") or 0) >= min_confidence_score
    ]

    st.subheader("Top Picks")

    if not top_picks:
        st.info("Nessun match supera le soglie operative attuali.")
    else:
        for pick in top_picks[:5]:
            st.success(
                f"{pick['Match']} | "
                f"Value: {pick['Value']} ({pick['Value score']}) | "
                f"Confidence: {pick['Confidence']} ({pick['Confidence score']}) | "
                f"Ace totali: {pick['Ace totali']} | "
                f"Break totali: {pick['Break totali']}"
            )

    if not matches:
        st.warning("Nessuna partita trovata per la data selezionata.")
        return

    st.sidebar.subheader("Soglie operative")

    min_value_score = st.sidebar.slider(
        "Min Value Score",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.05
    )
    
    min_confidence_score = st.sidebar.slider(
        "Min Confidence Score",
        min_value=0.0,
        max_value=1.0,
        value=0.55,
        step=0.05
    )
    
    render_filters()
    selected_match = render_match_selector(matches)
    result, context = run_prediction(selected_match)
    
    st.metric(
        "Confidence",
        context.get("confidence_label", "-"),
        f"{context.get('confidence_score', '-')}"
    )

    st.metric(
        "Value",
        context.get("value_label", "-"),
        f"{context.get('value_score', '-')}"
    )

    render_prediction(result, selected_match.player1, selected_match.player2)
    render_breakdown(context)


if __name__ == "__main__":
    main()
