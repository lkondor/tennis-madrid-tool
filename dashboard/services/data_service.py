from data.storage.init_db import init_db
from data.access import get_upcoming_matches

def load_matches():
    init_db()
    return get_upcoming_matches()
