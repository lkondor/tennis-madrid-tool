import streamlit as st

from services.data_service import (
    load_all_matches,
    get_available_dates,
    get_matches_by_date
)
from services.model_service import run_prediction
from components.match_selector import render_match_selector


def main():
    st.set_page_config(layout="wide")

    all_matches = load_all_matches()

    if not all_matches:
        st.error("Nessun dato disponibile")
        return

    dates = get_available_dates(all_matches)

    selected_date = st.selectbox("Seleziona data", dates)

    matches = get_matches_by_date(selected_date)

    selected_match = render_match_selector(matches)

    result, context = run_prediction(selected_match)

    st.write(result)
    st.write(context)


if __name__ == "__main__":
    main()
