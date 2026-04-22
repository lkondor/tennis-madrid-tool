from data.storage.db import SessionLocal
from data.storage.models import MatchStats

def get_upcoming_matches():
    session = SessionLocal()
    rows = session.query(MatchStats).order_by(MatchStats.date.asc(), MatchStats.id.asc()).all()
    session.close()
    return rows
