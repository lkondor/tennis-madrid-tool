from collections import defaultdict

def historical_court_factor(court_name):
    base = {"Center": 1.00, "Court 3": 1.03, "Court 4": 1.08}
    return base.get(court_name, 1.00)

def current_tournament_court_factor(matches, court_name):
    grouped = defaultdict(list)
    for m in matches:
        grouped[m.court].append((m.aces_p1 + m.aces_p2, m.breaks_p1 + m.breaks_p2))
    if not grouped:
        return 1.0, 0
    avg_all = sum(sum(a for a, _ in vals)/len(vals) for vals in grouped.values()) / len(grouped)
    vals = grouped.get(court_name, [])
    if not vals:
        return 1.0, 0
    avg_this = sum(a for a, _ in vals) / len(vals)
    return avg_this / avg_all if avg_all else 1.0, len(vals)

def blended_court_factor(historical, current, matches_played):
    weight_current = min(0.5, matches_played / 50.0)
    weight_hist = 1 - weight_current
    return weight_hist * historical + weight_current * current
