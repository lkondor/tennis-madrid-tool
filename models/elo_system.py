class EloSystem:
    def __init__(self, ratings=None):
        self.ratings = ratings or {}

    def get_elo(self, player, surface="clay"):
        return self.ratings.get((player, surface), 1500)
