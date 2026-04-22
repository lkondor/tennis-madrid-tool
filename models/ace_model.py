from utils.math_utils import clip
from config.settings import MADRID_ACE_FACTOR, OUTLIER_CLIP

def predict_aces(base_rate, opponent_adj, surface_factor, court_factor,
                 match_length_factor, weather_factor=1.0, is_madrid=True):
    madrid_factor = MADRID_ACE_FACTOR if is_madrid else 1.0
    expected = (
        base_rate * opponent_adj * surface_factor * madrid_factor *
        court_factor * match_length_factor * weather_factor * 10.0
    )
    return round(clip(expected, *OUTLIER_CLIP["aces"]), 2)
