from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String, Date

Base = declarative_base()

class MatchStats(Base):
    __tablename__ = "match_stats"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    player1 = Column(String)
    player2 = Column(String)
    surface = Column(String)
    tournament = Column(String)
    court = Column(String)

    aces_p1 = Column(Integer, default=0)
    aces_p2 = Column(Integer, default=0)
    breaks_p1 = Column(Float, default=0)
    breaks_p2 = Column(Float, default=0)

    service_games_p1 = Column(Float, default=10)
    service_games_p2 = Column(Float, default=10)
    return_games_p1 = Column(Float, default=10)
    return_games_p2 = Column(Float, default=10)

    serve_points_won_p1 = Column(Float, default=0.65)
    serve_points_won_p2 = Column(Float, default=0.65)
    return_points_won_p1 = Column(Float, default=0.35)
    return_points_won_p2 = Column(Float, default=0.35)
