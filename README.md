# CFB Contrarian Predictor v2.0

> A command-line tool that identifies contrarian college football betting opportunities by layering "human factor" adjustments on top of Vegas market consensus.

## Overview

The CFB Contrarian Predictor uses an **Adjustment Layer** approach:

```
Your Prediction = Vegas Line + Human Factor Adjustments
```

The system analyzes college football games through three weighted factor categories:
- **Coaching Edge Factors** (40% weight) - Experience, pressure, venue performance
- **Situational Context Factors** (40% weight) - Desperation, revenge games, lookahead spots  
- **Momentum Factors** (20% weight) - ATS trends, scoring patterns, clutch performance

## Features

- 🏈 **Complete P4 Schedule Access** - List all Power 4 games by week
- 📊 **Live Betting Lines** - Integration with The Odds API
- 🎯 **Contrarian Edge Detection** - Identifies opportunities with 3+ point discrepancies
- 📈 **Factor Breakdown** - Detailed analysis of each prediction component
- ⚡ **Fast Execution** - Sub-3 second analysis per game
- 🔒 **Rate Limited** - Respects API quotas and prevents account suspension

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cfb-contrarian-predictor.git
cd cfb-contrarian-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your API keys
cp .env.example .env
# Edit .env with your API keys
```

### API Keys Required

1. **The Odds API** - Sign up at [theoddsapi.com](https://theoddsapi.com) (30 seconds, 500 free calls/month)
2. **ESPN API** - No key required (public API with rate limiting)

### Basic Usage

```bash
# Analyze a specific game
python main.py --home georgia --away alabama

# Get detailed factor breakdown
python main.py --home uga --away bama --verbose --show-factors

# List all P4 games for a week
python main.py --list-games 1

# Analyze all games in a week
python main.py --analyze-week 8 --min-edge 3.0

# See all supported teams
python main.py --list-teams
```

## Examples

### Basic Prediction
```bash
$ python main.py --home clemson --away lsu

Analyzing: LSU @ CLEMSON
--------------------------------------------------
📊 Fetching game data...
📈 Data Quality: 70.0%
💰 Vegas Spread: CLEMSON -2.5

🎯 Generating Contrarian Prediction...

📊 Prediction Results:
   Vegas Spread: CLEMSON -2.5
   Contrarian Prediction: CLEMSON -2.6
   Factor Adjustment: -0.11 points
   Edge Size: 0.11 points

🎯 Edge Analysis:
   Edge Type: No Edge
   Confidence: Medium (61.1%)
   Recommendation: PASS - No meaningful contrarian opportunity
```

### Weekly Schedule
```bash
$ python main.py --list-games 1

CFB Week 1 Schedule - P4 Games
============================================================
🏈 Found 84 P4 games for Week 1

 2. Iowa State           @ Kansas St            (Neutral: Aviva Stadium)
    Command: python main.py --home kansas-state --away iowa-state

33. Texas                @ Ohio State          
    Command: python main.py --home ohio-state --away texas

63. LSU                  @ Clemson             
    Command: python main.py --home clemson --away lsu
```

### Factor Analysis
```bash
$ python main.py --home georgia --away alabama --show-factors

📈 Factor Breakdown:
   ExperienceDifferential: +0.000 (weighted: +0.000)
      → Coaching experience levels are comparable
   VenuePerformance: +0.300 (weighted: +0.030)
      → Moderate home field advantage favors GEORGIA
   PressureSituation: -0.060 (weighted: -0.006)
      → Both teams facing similar pressure levels

📊 Category Summary:
   Coaching Edge: +0.024 points
   Situational Context: +0.005 points
   Momentum Factors: +0.000 points
```

## Project Structure

```
cfb-contrarian-predictor/
├── main.py                      # CLI entry point
├── config.py                    # Configuration management
├── normalizer.py               # Team name standardization
├── data/                       # API integration
│   ├── odds_client.py          # The Odds API client
│   ├── espn_client.py          # ESPN API client
│   ├── schedule_client.py      # Weekly schedule fetching
│   ├── data_manager.py         # Unified data access
│   └── cache_manager.py        # Session-level caching
├── factors/                    # Three-factor prediction system
│   ├── base_calculator.py      # Abstract base class
│   ├── coaching_edge.py        # Coaching factors (40% weight)
│   ├── situational_context.py # Situational factors (40% weight)
│   ├── momentum_factors.py     # Momentum factors (20% weight)
│   └── factor_registry.py     # Dynamic factor loading
├── engine/                     # Core prediction logic
│   ├── prediction_engine.py    # Main calculation orchestrator
│   ├── confidence_calculator.py # Edge confidence scoring
│   └── edge_detector.py       # Contrarian opportunity detection
├── output/                     # CLI presentation
│   ├── formatter.py           # Terminal output formatting
│   └── insights_generator.py  # Human-readable explanations
├── utils/                      # Supporting infrastructure
│   ├── rate_limiter.py        # API throttling
│   ├── error_handler.py       # Graceful failure handling
│   └── performance_tracker.py # Execution monitoring
└── tests/                      # Test coverage
    ├── test_factors.py        # Factor validation
    ├── test_api_clients.py    # API integration tests
    └── test_integration.py    # End-to-end testing
```

## CLI Reference

### Core Commands
```bash
# Single game prediction
--home TEAM --away TEAM [--week N] [--verbose] [--show-factors]

# Batch analysis
--analyze-week N [--min-edge POINTS]

# Utility commands
--list-teams                    # Show all supported teams
--list-games WEEK              # Show P4 games for week
--validate-team TEAM           # Check team normalization
--check-config                 # Validate API configuration

# Output formats
--format {table,json,csv}      # Change output format
--quiet                        # Minimal output
--debug                        # Detailed logging
```

### Team Name Flexibility
The system accepts multiple formats for team names:
```bash
# All of these work for Georgia:
python main.py --home georgia --away alabama
python main.py --home uga --away bama  
python main.py --home "Georgia Bulldogs" --away "Alabama Crimson Tide"
```

## Adding Custom Factors

To add new prediction factors:

1. **Create factor calculator** in `factors/` inheriting from `BaseFactorCalculator`
2. **Implement required methods**:
   ```python
   class CustomFactor(BaseFactorCalculator):
       def calculate(self, home_team: str, away_team: str) -> float:
           # Return adjustment value (-5.0 to +5.0)
           return adjustment_value
       
       def get_output_range(self) -> tuple:
           return (-3.0, 3.0)  # Define bounds
   ```
3. **Register in factor_registry.py** with appropriate weight
4. **Add unit tests** in `tests/test_factors.py`

## Configuration

### Environment Variables
```bash
# Required
ODDS_API_KEY=your_odds_api_key_here

# Optional  
LOG_LEVEL=INFO
CACHE_TTL=3600
RATE_LIMIT_ODDS=83
RATE_LIMIT_ESPN=60
```

### Factor Weights
Default weights in `config.py`:
```python
coaching_edge_weight = 0.4      # 40%
situational_context_weight = 0.4  # 40%  
momentum_factors_weight = 0.2   # 20%
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cfb_predictor --cov-report=html

# Test specific factor
pytest tests/test_factors.py::TestCoachingEdge -v

# Test API integration (requires keys)
pytest tests/test_api_clients.py
```

## Performance

- **Target execution time**: <15 seconds per prediction
- **API call efficiency**: <20 calls per prediction
- **Rate limiting**: Compliant with all API quotas
- **Cache hit rate**: >80% for repeated team lookups

## Supported Conferences

- **SEC** (16 teams)
- **Big Ten** (18 teams) 
- **Big 12** (16 teams)
- **ACC** (15 teams)
- **Notre Dame** (Independent)

130+ total FBS teams supported with comprehensive alias mapping.

### Development Guidelines
- Follow Black formatting (88 character limit)
- Add type hints to all public methods
- Include unit tests for new factors
- Update CLAUDE.md with implementation notes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
