from data.aggregation.player_aggregator import PlayerAggregator
from pipeline.predictor import predict_match

agg = PlayerAggregator()

def run_prediction(match, all_matches):
    playerA = agg.compute_stats(match.player1, surface=match.surface)
    playerB = agg.compute_stats(match.player2, surface=match.surface)
    return predict_match(match.player1, match.player2, playerA, playerB, match, all_matches)
