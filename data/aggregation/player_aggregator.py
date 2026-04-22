from datetime import datetime
import numpy as np
from data.storage.db import SessionLocal
from data.storage.models import MatchStats
from data.schema import PlayerStats
from utils.decay import time_decay
from utils.math_utils import safe_div

class PlayerAggregator:
    def __init__(self):
        self.session = SessionLocal()

    def get_matches(self, player_name):
        return self.session.query(MatchStats).filter(
            ((MatchStats.player1 == player_name) | (MatchStats.player2 == player_name))
        ).all()

    def compute_stats(self, player_name, surface="clay"):
        matches = self.get_matches(player_name)
        now = datetime.now().date()

        ace_sum = service_games = 0.0
        ace_surface_sum = service_games_surface = 0.0
        ace_conceded_sum = return_games = 0.0
        spw = []
        rpw = []
        break_sum = break_conceded_sum = total_weight = 0.0

        for m in matches:
            p1 = m.player1 == player_name
            aces = m.aces_p1 if p1 else m.aces_p2
            opp_aces = m.aces_p2 if p1 else m.aces_p1
            svc_games = m.service_games_p1 if p1 else m.service_games_p2
            ret_games = m.return_games_p1 if p1 else m.return_games_p2
            serve_won = m.serve_points_won_p1 if p1 else m.serve_points_won_p2
            return_won = m.return_points_won_p1 if p1 else m.return_points_won_p2
            br = m.breaks_p1 if p1 else m.breaks_p2
            brc = m.breaks_p2 if p1 else m.breaks_p1

            months = max((now - m.date).days / 30.0, 0)
            weight = time_decay(months)

            ace_sum += aces * weight
            service_games += svc_games * weight
            if m.surface == surface:
                ace_surface_sum += aces * weight
                service_games_surface += svc_games * weight

            ace_conceded_sum += opp_aces * weight
            return_games += ret_games * weight
            spw.append(serve_won)
            rpw.append(return_won)
            break_sum += br * weight
            break_conceded_sum += brc * weight
            total_weight += weight

        return PlayerStats(
            ace_rate=safe_div(ace_sum, service_games),
            ace_rate_surface=safe_div(ace_surface_sum, service_games_surface) or safe_div(ace_sum, service_games),
            ace_conceded_rate=safe_div(ace_conceded_sum, return_games),
            first_serve_pct=0.62,
            serve_points_won=float(np.mean(spw)) if spw else 0.65,
            return_points_won=float(np.mean(rpw)) if rpw else 0.35,
            break_rate=safe_div(break_sum, total_weight) if total_weight else 1.5,
            break_conceded_rate=safe_div(break_conceded_sum, total_weight) if total_weight else 1.5,
        )
