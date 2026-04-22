def run_prediction(match):
    # Logica semplice ma stabile per far funzionare subito la dashboard
    base_aces_a = 6.5
    base_aces_b = 5.8
    base_breaks_a = 2.1
    base_breaks_b = 1.9

    court_factor = 1.08 if str(match.court).lower() == "court 4" else 1.0
    madrid_factor = 1.15
    surface_factor = 1.05
    match_length = 1.2

    aces_a = round(base_aces_a * court_factor * madrid_factor * 0.9, 1)
    aces_b = round(base_aces_b * court_factor * madrid_factor * 0.9, 1)

    breaks_a = round(base_breaks_a * surface_factor * 0.95, 1)
    breaks_b = round(base_breaks_b * surface_factor * 0.95, 1)

    result = {
        "playerA": {
            "aces": aces_a,
            "breaks": breaks_a
        },
        "playerB": {
            "aces": aces_b,
            "breaks": breaks_b
        },
        "totals": {
            "aces": round(aces_a + aces_b, 1),
            "breaks": round(breaks_a + breaks_b, 1)
        }
    }

    context = {
        "surface_factor": surface_factor,
        "madrid_factor": madrid_factor,
        "court_factor": court_factor,
        "match_length": match_length
    }

    return result, context
