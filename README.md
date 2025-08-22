# Simple Blockchain Prediction Market

This project is a basic Python implementation of a prediction market system inspired by blockchain technology principles. It demonstrates how users can create prediction markets on future events, place bets on two possible outcomes, resolve the market based on actual results, and fairly distribute payouts automatically.

## Features

- Create prediction markets with custom questions and two betting options.
- Users place bets on their chosen option with specified amounts.
- Markets have an end time after which no new bets are accepted.
- Market resolution with declaration of the winning outcome.
- Payouts to winning bettors are calculated based on their contribution proportionally.
- Transparent and automated process inspired by blockchain smart contract logic.

## Getting Started

### Prerequisites

- Python 3.x installed on your system.
- Basic knowledge of Python programming.

### How to Run

1. Clone the repository:  
	git clone <repository_url>
	cd <repository_folder>

2. Run the main script or use the `PredictionMarket` class in your own Python scripts.

3. Example usage to create markets, place bets, resolve markets, and calculate payouts is included in the demo section of the code:
pm = PredictionMarket()
pm.create_market(“game1”, “Will Team A win the game?”, “Yes”, “No”, time.time() + 60)
pm.place_bet(“game1”, “Alice”, “A”, 100)
pm.place_bet(“game1”, “Bob”, “B”, 50)
pm.resolve_market(“game1”, “A”)
payouts = pm.calculate_payouts(“game1”) print(“Payouts:”, payouts)

## Project Structure

- `PredictionMarket` class: Core logic for market management, betting, resolution, and payouts.
- Example usage included for demonstration and testing.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
