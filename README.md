# Blockchain Betting Simulation

This project is a **toy blockchain implementation** that simulates a prediction/betting market on-chain.  
It demonstrates the basic ideas of **blockchain, transactions, blocks, mining, and state management** with a simple prediction market use case.

⚠️ **Note:**  
This is **not secure** and is **for educational/demo purposes only**.  
It does not implement real cryptography, networking, or consensus protocols.  

---

## ✨ Features
- Simple blockchain with:
  - Blocks, transactions, proof-of-work mining
  - Chain validation
- Simulated accounts with toy signing & verification
- On-chain state for:
  - **Markets** (questions with options A/B)
  - **Bets** (users place bets on options)
  - **Market resolution** (set the winning option)
  - **Payout calculation** (based on bets)

---

## 📂 Project Structure
- **Helpers**
  - `generate_keypair()` → Creates toy (private, public) keys
  - `sign_message()` → Creates a toy signature
- **Transaction Class** → Represents a blockchain transaction
- **Block Class** → Represents a block in the chain
- **Blockchain Class**  
  - Manages chain, transactions, state, mining  
  - Applies transactions to update state  
  - Validates chain  
  - Calculates payouts for resolved markets  

---

## ▶️ Demo Flow
1. Generate accounts for Alice, Bob, Charlie, and a miner.
2. Alice creates a prediction market:  
   *"Will Team A win?"*
3. Alice, Bob, and Charlie place bets on options A or B.
4. Miner mines the transactions into a block.
5. Alice resolves the market (e.g., **Team A wins**).
6. Miner mines the resolution transaction.
7. Blockchain calculates payouts for the winners.

---

## 🖥️ Example Run (Output)
```text
Mined block #1 with hash 000f9... (nonce 2451)
Mined block #2 with hash 000ab... (nonce 1365)
Payouts (from on-chain state): {'Alice': 175.0, 'Charlie': 262.5}
Is chain valid? True
