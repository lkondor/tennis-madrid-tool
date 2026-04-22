from models.ace_model import predict_aces
from models.break_model import predict_breaks
from models.match_length import match_length_factor
from features.feature_engineering import compute_base_ace_rate, opponent_adjustment
from features.court_model import historical_court_factor, current_tournament_court_factor, blended_court_factor
from features.weather_model import ace_weather_factor, break_weather_factor
from models.elo_system import EloSystem

def predict_match(playerA_name, playerB_name, playerA, playerB, match_obj, all_matches):
    surface_factor = 1.05 if match_obj.surface == "clay" else 1.0
    hist_cf = historical_court_factor(match_obj.court)
    curr_cf, matches_played = current_tournament_court_factor(all_matches, match_obj.court)
    court_factor = blended_court_factor(hist_cf, curr_cf, matches_played)

    temp_c = 22.0
    wind_kmh = 8.0
    ace_wf = ace_weather_factor(temp_c, wind_kmh)
    break_wf = break_weather_factor(temp_c, wind_kmh)

    elo = EloSystem({
        (playerA_name, "clay"): 1540,
        (playerB_name, "clay"): 1520,
    })
    elo_A = elo.get_elo(playerA_name, "clay")
    elo_B = elo.get_elo(playerB_name, "clay")
    match_len = match_length_factor(elo_A, elo_B, playerA.serve_points_won, playerB.serve_points_won)

    base_A = compute_base_ace_rate(playerA, playerA.ace_rate)
    base_B = compute_base_ace_rate(playerB, playerB.ace_rate)
    adj_A = opponent_adjustment(playerB.ace_conceded_rate, 0.55)
    adj_B = opponent_adjustment(playerA.ace_conceded_rate, 0.55)

    aces_A = predict_aces(base_A, adj_A, surface_factor, court_factor, match_len, ace_wf)
    aces_B = predict_aces(base_B, adj_B, surface_factor, court_factor, match_len, ace_wf)

    conversion_A = max(0.25, min(0.55, playerA.break_rate / 5.0))
    conversion_B = max(0.25, min(0.55, playerB.break_rate / 5.0))
    breaks_A = predict_breaks(playerA.return_points_won, playerB.serve_points_won, conversion_A,
                              playerA.break_rate, surface_factor, break_wf)
    breaks_B = predict_breaks(playerB.return_points_won, playerA.serve_points_won, conversion_B,
                              playerB.break_rate, surface_factor, break_wf)

    context = {
        "surface_factor": surface_factor,
        "madrid_factor": 1.15,
        "court_factor": round(court_factor, 3),
        "court_historical_factor": round(hist_cf, 3),
        "court_current_factor": round(curr_cf, 3),
        "court_matches_played": matches_played,
        "weather_temp_c": temp_c,
        "weather_wind_kmh": wind_kmh,
        "ace_weather_factor": round(ace_wf, 3),
        "break_weather_factor": round(break_wf, 3),
        "match_length": match_len,
        "elo_A": elo_A,
        "elo_B": elo_B,
    }

    return {
        "playerA": {"aces": aces_A, "breaks": breaks_A},
        "playerB": {"aces": aces_B, "breaks": breaks_B},
        "totals": {"aces": round(aces_A + aces_B, 2), "breaks": round(breaks_A + breaks_B, 2)}
    }, context
