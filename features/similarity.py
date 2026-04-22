import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(player_vec, population_matrix):
    sims = cosine_similarity([player_vec], population_matrix)
    return sims[0]

def weighted_similarity_stat(similarities, stats):
    s = similarities.sum()
    if s == 0:
        return float(np.mean(stats)) if len(stats) else 0.0
    weights = similarities / s
    return float((weights * stats).sum())
