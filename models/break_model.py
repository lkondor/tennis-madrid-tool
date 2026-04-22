from utils.math_utils import clip
from config.settings import MADRID_BREAK_FACTOR, BREAK_STABILIZATION, OUTLIER_CLIP

def predict_breaks(return_points_won, opponent_serve_points_won, conversion_rate,
                   historical_avg, surface_factor, weather_factor=1.0, is_madrid=True):
    madrid_factor = MADRID_BREAK_FACTOR if is_madrid else 1.0
    creation = max(0.05, return_points_won * max(0.05, (1 - opponent_serve_points_won)))
    raw_breaks = creation * conversion_rate * surface_factor * madrid_factor * weather_factor * 12.0
    stabilized = BREAK_STABILIZATION * raw_breaks + (1 - BREAK_STABILIZATION) * historical_avg
    return round(clip(stabilized, *OUTLIER_CLIP["breaks"]), 2)
