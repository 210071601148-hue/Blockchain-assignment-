import hashlib
import time

class PredictionMarket:
    def __init__(self):
        self.markets = {}
        self.bets = {}
        self.outcomes = {}

    def create_market(self, market_id, question, option_a, option_b, end_time):
        self.markets[market_id] = {
            "question": question,
            "option_a": option_a,
            "option_b": option_b,
            "end_time": end_time,
            "resolved": False,
            "winner": None
        }
        self.bets[market_id] = {"A": {}, "B": {}}

    def place_bet(self, market_id, user, option, amount):
        market = self.markets.get(market_id)
        if not market or time.time() > market["end_time"] or market["resolved"]:
            raise Exception("Market inactive or resolved.")
        if option not in ["A", "B"]:
            raise Exception("Invalid option")
        self.bets[market_id][option][user] = self.bets[market_id][option].get(user, 0) + amount

    def resolve_market(self, market_id, winning_option):
        market = self.markets.get(market_id)
        if not market or market["resolved"]:
            raise Exception("Market already resolved or not found.")
        if winning_option not in ["A", "B"]:
            raise Exception("Invalid winning option.")
        market["resolved"] = True
        market["winner"] = winning_option
        self.outcomes[market_id] = winning_option

    def calculate_payouts(self, market_id):
        market = self.markets.get(market_id)
        if not market or not market["resolved"]:
            raise Exception("Market unresolved or not found.")

        total_a = sum(self.bets[market_id]["A"].values())
        total_b = sum(self.bets[market_id]["B"].values())
        winner = market["winner"]

        winner_bets = self.bets[market_id][winner]

        losing_total = total_b if winner == "A" else total_a
        winner_total = total_a if winner == "A" else total_b

        payouts = {}
        for user, amount in winner_bets.items():
            # User's share of the losing side proportional to their bet
            share_of_losers = (amount / winner_total) * losing_total if winner_total > 0 else 0
            payouts[user] = amount + share_of_losers

        return payouts

# --------- Demo ---------
pm = PredictionMarket()

# Market creation: Will Team A win the game? (ends in 60 seconds)
pm.create_market("game1", "Will Team A win the game?", "Yes", "No", time.time() + 60)

# Users placing bets
pm.place_bet("game1", "Alice", "A", 100)
pm.place_bet("game1", "Bob", "B", 50)
pm.place_bet("game1", "Charlie", "A", 150)

# Resolve market (Team A wins)
pm.resolve_market("game1", "A")

# Calculate payouts
payouts = pm.calculate_payouts("game1")
print("Payouts:", payouts)
