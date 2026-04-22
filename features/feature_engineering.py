from config.settings import WEIGHTS_ACE

def compute_base_ace_rate(player, similarity_ace_rate):
    return (
        WEIGHTS_ACE["recent"] * player.ace_rate +
        WEIGHTS_ACE["surface"] * player.ace_rate_surface +
        WEIGHTS_ACE["similarity"] * similarity_ace_rate
    )

def opponent_adjustment(opponent_ace_conceded, tour_avg):
    return 1 + max(-0.4, min(0.4, (opponent_ace_conceded - tour_avg)))
