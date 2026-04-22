from models.elo_model import win_probability

def expected_sets(p):
    return 2 + (2 * p * (1 - p))

def expected_games(hold_A, hold_B):
    avg_games_per_set = 9.5
    adjustment = max(0.85, min(1.15, (hold_A + hold_B) / 1.4))
    return avg_games_per_set * adjustment

def match_length_factor(elo_A, elo_B, hold_A, hold_B):
    p = win_probability(elo_A, elo_B)
    sets = expected_sets(p)
    games = expected_games(hold_A, hold_B)
    return round((sets * games) / 20.0, 3)
