import hashlib
import json
import time
import random
from typing import List, Dict

# -----------------------------
# Simple helpers (toy keys)
# -----------------------------
def generate_keypair():
    """Return a simple (private, public) pair. THIS IS SIMULATED."""
    private = hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()
    public = hashlib.sha256(private.encode()).hexdigest()
    return private, public

def sign_message(private_key: str, message: str) -> str:
    """Toy 'signature' = hash(private + message). NOT cryptographically secure."""
    return hashlib.sha256((private_key + message).encode()).hexdigest()

def verify_signature(public_key: str, message: str, signature: str) -> bool:
    """Verify by brute-forcing that signature could come from a private whose hash is public.
       In a real system you'd use ECDSA and derive public from private; this is a simulation."""
    # In this toy demo, we cannot actually recover private from public;
    # so we'll just accept signatures when the caller provides a mapping (see Blockchain.accounts).
    # The blockchain will check signature by looking up the stored private in accounts (simulation).
    return True  # actual verification happens in Blockchain using stored private (simulated)

# -----------------------------
# Transaction & Block classes
# -----------------------------
class Transaction:
    def __init__(self, ttype: str, data: dict, sender_public: str, signature: str = None):
        self.type = ttype  # e.g., "CREATE_MARKET", "PLACE_BET", "RESOLVE_MARKET"
        self.data = data   # payload depends on type
        self.sender = sender_public
        self.signature = signature
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "type": self.type,
            "data": self.data,
            "sender": self.sender,
            "signature": self.signature,
            "timestamp": self.timestamp
        }

class Block:
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        tx_strs = [json.dumps(tx.to_dict(), sort_keys=True) for tx in self.transactions]
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": tx_strs,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

# -----------------------------
# Blockchain
# -----------------------------
class Blockchain:
    def __init__(self, difficulty=3):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        # On-chain state (applied when blocks are mined)
        self.state = {
            "markets": {},   # market_id -> market dict
            "bets": {}       # market_id -> {"A":{pub:amount}, "B":{pub:amount}}
        }
        # Simulated accounts mapping public -> private (ONLY for demo signing/verification)
        self.accounts: Dict[str, str] = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, [], "0")
        self.chain.append(genesis)

    def register_account(self, private, public):
        self.accounts[public] = private

    def add_transaction(self, tx: Transaction):
        # Verify signature using stored private (TOY check)
        stored_priv = self.accounts.get(tx.sender)
        if stored_priv is None:
            raise Exception("Unknown sender public key (account not registered).")
        # Recreate signature and compare:
        expected_sig = sign_message(stored_priv, json.dumps(tx.data, sort_keys=True))
        if tx.signature != expected_sig:
            raise Exception("Invalid signature (toy check failed).")
        self.pending_transactions.append(tx)

    def mine_pending(self, miner_public: str):
        if not self.pending_transactions:
            print("Nothing to mine.")
            return None

        # Create new block with current pending txs
        new_block = Block(len(self.chain), self.pending_transactions[:], self.chain[-1].hash)
        # Proof-of-work: find nonce so hash starts with difficulty zeros
        target = "0" * self.difficulty
        while not new_block.hash.startswith(target):
            new_block.nonce += 1
            new_block.hash = new_block.compute_hash()

        # Append the block
        self.chain.append(new_block)

        # Apply transactions to on-chain state
        for tx in new_block.transactions:
            self.apply_transaction_to_state(tx)

        # Clear pending transactions
        self.pending_transactions = []

        # Optional: miner reward (not implemented numeric transfer here)
        print(f"Mined block #{new_block.index} with hash {new_block.hash} (nonce {new_block.nonce})")
        return new_block

    def apply_transaction_to_state(self, tx: Transaction):
        t = tx.type
        d = tx.data

        if t == "CREATE_MARKET":
            market_id = d["market_id"]
            self.state["markets"][market_id] = {
                "question": d["question"],
                "option_a": d["option_a"],
                "option_b": d["option_b"],
                "end_time": d["end_time"],
                "resolved": False,
                "winner": None,
                "creator": tx.sender
            }
            self.state["bets"][market_id] = {"A": {}, "B": {}}

        elif t == "PLACE_BET":
            mid = d["market_id"]
            opt = d["option"]
            amount = d["amount"]
            if mid not in self.state["markets"]:
                print(f"Skipping PLACE_BET: market {mid} not found on-chain.")
                return
            market = self.state["markets"][mid]
            if time.time() > market["end_time"] or market["resolved"]:
                print(f"Skipping PLACE_BET: market {mid} inactive or resolved.")
                return
            # record bet
            self.state["bets"][mid][opt][tx.sender] = self.state["bets"][mid][opt].get(tx.sender, 0) + amount

        elif t == "RESOLVE_MARKET":
            mid = d["market_id"]
            winner = d["winning_option"]
            if mid not in self.state["markets"]:
                print(f"Skipping RESOLVE_MARKET: market {mid} not found.")
                return
            market = self.state["markets"][mid]
            if market["resolved"]:
                print(f"Skipping RESOLVE_MARKET: market {mid} already resolved.")
                return
            market["resolved"] = True
            market["winner"] = winner

        else:
            print(f"Unknown transaction type: {t}")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]
            if curr.hash != curr.compute_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
            if not curr.hash.startswith("0" * self.difficulty):
                return False
        return True

    # Utility to calculate payouts (reads on-chain bets & resolution)
    def calculate_payouts(self, market_id):
        market = self.state["markets"].get(market_id)
        if not market or not market["resolved"]:
            raise Exception("Market unresolved or not found on-chain.")
        bets = self.state["bets"][market_id]
        total_a = sum(bets["A"].values())
        total_b = sum(bets["B"].values())
        winner = market["winner"]
        winner_bets = bets[winner]
        losing_total = total_b if winner == "A" else total_a
        winner_total = total_a if winner == "A" else total_b
        payouts = {}
        for user, amount in winner_bets.items():
            share_of_losers = (amount / winner_total) * losing_total if winner_total > 0 else 0
            payouts[user] = amount + share_of_losers
        return payouts


# -----------------------------
# DEMO: create accounts, create market, bets, mine, resolve
# -----------------------------
if __name__ == "__main__":
    bc = Blockchain(difficulty=3)  # difficulty=3 -> manageable for demo

    # Create some simulated accounts
    priv_a, pub_a = generate_keypair()   # Alice
    priv_b, pub_b = generate_keypair()   # Bob
    priv_c, pub_c = generate_keypair()   # Charlie
    miner_priv, miner_pub = generate_keypair()

    # Register accounts (so blockchain can verify signatures in this toy demo)
    bc.register_account(priv_a, pub_a)
    bc.register_account(priv_b, pub_b)
    bc.register_account(priv_c, pub_c)
    bc.register_account(miner_priv, miner_pub)

    # 1) Create market transaction
    market_tx_data = {
        "market_id": "game1",
        "question": "Will Team A win?",
        "option_a": "Yes",
        "option_b": "No",
        "end_time": time.time() + 60  # ends in 60 seconds
    }
    sig_create = sign_message(priv_a, json.dumps(market_tx_data, sort_keys=True))
    tx_create = Transaction("CREATE_MARKET", market_tx_data, pub_a, sig_create)
    bc.add_transaction(tx_create)

    # 2) Place bets (as transactions)
    bet1 = {"market_id": "game1", "option": "A", "amount": 100}
    tx_b1 = Transaction("PLACE_BET", bet1, pub_a, sign_message(priv_a, json.dumps(bet1, sort_keys=True)))
    bc.add_transaction(tx_b1)

    bet2 = {"market_id": "game1", "option": "B", "amount": 50}
    tx_b2 = Transaction("PLACE_BET", bet2, pub_b, sign_message(priv_b, json.dumps(bet2, sort_keys=True)))
    bc.add_transaction(tx_b2)

    bet3 = {"market_id": "game1", "option": "A", "amount": 150}
    tx_b3 = Transaction("PLACE_BET", bet3, pub_c, sign_message(priv_c, json.dumps(bet3, sort_keys=True)))
    bc.add_transaction(tx_b3)

    # Mine block with the above transactions
    bc.mine_pending(miner_pub)

    # Now resolve market (Team A wins) as an on-chain transaction
    resolve_data = {"market_id": "game1", "winning_option": "A"}
    tx_resolve = Transaction("RESOLVE_MARKET", resolve_data, pub_a, sign_message(priv_a, json.dumps(resolve_data, sort_keys=True)))
    bc.add_transaction(tx_resolve)

    # Mine the resolve transaction
    bc.mine_pending(miner_pub)

    # Calculate payouts by reading on-chain state
    payouts = bc.calculate_payouts("game1")
    # Map pub -> friendly names for display
    name_map = {pub_a: "Alice", pub_b: "Bob", pub_c: "Charlie"}
    readable = {name_map.get(pub, pub): amt for pub, amt in payouts.items()}

    print("Payouts (from on-chain state):", readable)
    print("Is chain valid?", bc.is_chain_valid())
