# CFB Contrarian Predictor

A command-line tool for analyzing college football betting opportunities through systematic factor analysis.

## Overview

Analyzes Power 4 conference games by applying "human factor" adjustments to Vegas consensus lines. The system focuses on coaching, situational, and momentum factors that may create contrarian betting opportunities.

**Approach**: `Contrarian Prediction = Vegas Line + Factor Adjustments`

## Key Features

- **Dynamic week analysis** with automatic CFB week detection
- **Power 4 focus** (SEC, Big Ten, Big 12, ACC, Independents)
- **Live betting lines** via The Odds API integration
- **Modular factor system** for systematic analysis
- **Clean terminal output** that works across screen sizes

## Installation

```bash
git clone https://github.com/yourusername/cfb-contrarian-predictor.git
cd cfb-contrarian-predictor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your Odds API key to .env file
```

**Required**: The Odds API key from [theoddsapi.com](https://theoddsapi.com) (500 free calls/month)

## Usage

```bash
# View current week Power 4 games
python main.py --analyze-week --quiet

# Analyze specific game
python main.py --home georgia --away alabama

# Detailed factor breakdown
python main.py --home uga --away bama --show-factors

# View all supported teams
python main.py --list-teams
```

## Architecture

The system uses a modular factor-based approach where new analysis components can be easily added to the `factors/` directory. Each factor inherits from `BaseFactorCalculator` and contributes weighted adjustments to the final prediction.

### Factor Categories
- **Coaching Edge** (40%) - Experience, pressure situations, venue performance
- **Situational Context** (40%) - Desperation scenarios, revenge games, lookahead spots
- **Momentum Factors** (20%) - Recent form, scoring trends, clutch performance

## Adding New Factors

Create new analysis factors by inheriting from `BaseFactorCalculator` in the `factors/` directory:

```python
class CustomFactor(BaseFactorCalculator):
    def calculate(self, home_team: str, away_team: str, context: dict) -> float:
        # Return adjustment value (-5.0 to +5.0)
        return adjustment_value
    
    def get_output_range(self) -> tuple:
        return (-3.0, 3.0)
```

The factor registry automatically loads and weights new factors based on their category.

## Configuration

Set your Odds API key in `.env`:
```bash
ODDS_API_KEY=your_key_here
```

Optional settings include logging levels, cache TTL, and factor weights (see `config.py`).

## License

MIT License
