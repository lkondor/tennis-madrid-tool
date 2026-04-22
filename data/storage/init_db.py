import datetime as dt
from data.storage.db import engine, SessionLocal
from data.storage.models import Base, MatchStats

def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    if session.query(MatchStats).count() == 0:
        today = dt.date.today()
        demo = [
            MatchStats(date=today, player1="Jannik Sinner", player2="Carlos Alcaraz", surface="clay",
                       tournament="Madrid", court="Center", aces_p1=6, aces_p2=5, breaks_p1=2, breaks_p2=2,
                       service_games_p1=11, service_games_p2=11, return_games_p1=11, return_games_p2=11,
                       serve_points_won_p1=0.71, serve_points_won_p2=0.69,
                       return_points_won_p1=0.39, return_points_won_p2=0.38),
            MatchStats(date=today, player1="Iga Swiatek", player2="Aryna Sabalenka", surface="clay",
                       tournament="Madrid", court="Court 4", aces_p1=2, aces_p2=6, breaks_p1=4, breaks_p2=3,
                       service_games_p1=10, service_games_p2=10, return_games_p1=10, return_games_p2=10,
                       serve_points_won_p1=0.67, serve_points_won_p2=0.70,
                       return_points_won_p1=0.44, return_points_won_p2=0.37),
            MatchStats(date=today, player1="Daniil Medvedev", player2="Alexander Zverev", surface="clay",
                       tournament="Madrid", court="Court 3", aces_p1=8, aces_p2=10, breaks_p1=2, breaks_p2=1,
                       service_games_p1=12, service_games_p2=12, return_games_p1=12, return_games_p2=12,
                       serve_points_won_p1=0.73, serve_points_won_p2=0.75,
                       return_points_won_p1=0.34, return_points_won_p2=0.33)
        ]
        session.add_all(demo)
        session.commit()
    session.close()

if __name__ == "__main__":
    init_db()
