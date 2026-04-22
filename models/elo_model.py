def win_probability(elo_A, elo_B):
    return 1 / (1 + 10 ** ((elo_B - elo_A) / 400.0))
