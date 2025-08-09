# CFB Contrarian Predictor

A command-line tool for analyzing college football betting opportunities through systematic factor analysis powered by the College Football Data API.

## Overview

Analyzes college football games by applying "human factor" adjustments to Vegas consensus lines. The system focuses on coaching experience, situational context, and momentum factors that may create contrarian betting opportunities.

**Approach**: `Contrarian Prediction = Vegas Line + Factor Adjustments`

## Key Features

- **CFBD Integration** - College Football Data API as primary source with ESPN fallback
- **Hierarchical Factor System** - Dynamic confidence-based weighting for 11 analysis factors
- **FCS Filtering** - Focuses on FBS vs FBS matchups for better analysis
- **Clean Console Output** - Technical logging sent to files, users see only results
- **Live Betting Lines** - Real-time odds via The Odds API integration
- **Automatic Team Normalization** - Handles 130+ team name variations

## Installation

```bash
git clone https://github.com/yourusername/cfb-contrarian-predictor.git
cd cfb-contrarian-predictor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## API Keys Required

Add to your `.env` file:

```bash
# Required: Betting lines (500 free calls/month)
ODDS_API_KEY=your_odds_api_key

# Optional but recommended: Enhanced coaching/stats data (5k free calls/month)
CFBD_API_KEY=your_cfbd_api_key
```

**Get API keys:**
- [The Odds API](https://theoddsapi.com) - Free tier: 500 calls/month
- [College Football Data](https://collegefootballdata.com) - Free tier: 5,000 calls/month

## Usage

```bash
# Analyze specific game
python main.py --home "Tennessee" --away "Syracuse"

# Show detailed factor breakdown
python main.py --home "Iowa State" --away "Kansas State" --show-factors

# List current week games
python main.py --list-games current

# Weekly analysis with minimum edge filter
python main.py --analyze-week --min-edge 2.0

# View all supported teams
python main.py --list-teams
```

## Data Sources

**Primary Architecture**: CFBD → ESPN → Defaults

- **College Football Data API** (Primary)
  - Coaching experience and tenure data
  - Advanced team statistics
  - Historical performance metrics
- **ESPN API** (Fallback)
  - Team information and schedules
  - Basic stats when CFBD unavailable
- **The Odds API** (Required)
  - Real-time betting lines and spreads

## Factor System

The system evaluates 11 factors across three categories with dynamic confidence-based weighting:

### Coaching Edge Factors (40% weight)
- **Experience Differential** - Head coach experience and tenure comparison
- **Pressure Situations** - Performance under high-stakes scenarios
- **Venue Performance** - Home/road coaching effectiveness
- **Head-to-Head Record** - Historical coaching matchups

### Situational Context Factors (40% weight)
- **Desperation Index** - Win-loss record and bowl eligibility pressure
- **Revenge Games** - Previous losses and coaching connections
- **Lookahead/Sandwich** - Trap game scenarios with big upcoming games
- **Statement Opportunities** - Chances for program-defining wins

### Momentum Factors (20% weight)
- **ATS Recent Form** - Against-the-spread performance trends
- **Point Differential Trends** - Scoring margin patterns
- **Close Game Performance** - Clutch situations and late-game execution

### Dynamic Weighting System

Factors use confidence-based adjustments:
- **VERY_HIGH** (0.9x) - Strong data supporting factor
- **HIGH** (0.75x) - Good data confidence
- **MEDIUM** (0.5x) - Moderate confidence
- **LOW** (0.25x) - Limited data quality
- **NONE** (0.0x) - Insufficient data

## Sample Output

```
Analyzing: KANSAS STATE @ IOWA STATE
--------------------------------------------------
📊 Fetching game data...
📈 Data Quality: 80.0%
💰 Vegas Spread: IOWA STATE +3.5

🎯 Generating Contrarian Prediction...

📊 Prediction Results:
   Vegas Spread: IOWA STATE +3.5
   Contrarian Prediction: IOWA STATE +1.2
   Factor Adjustment: +2.3 points
   Edge Size: 2.3 points

🎯 Edge Analysis:
   Edge Type: Moderate Edge
   Confidence: High (82.4%)
   Recommendation: IOWA STATE +3.5 - Contrarian value identified
```

## Architecture

### Factor Development
Each factor inherits from `BaseFactorCalculator`:

```python
class NewFactor(BaseFactorCalculator):
    def __init__(self):
        super().__init__()
        self.factor_type = FactorType.PRIMARY  # or SECONDARY, TRIGGER, MODIFIER
        self.activation_threshold = 1.0
        self.max_impact = 3.0
    
    def calculate_with_confidence(self, home_team: str, away_team: str, 
                                 context: Dict[str, Any]) -> Tuple[float, FactorConfidence, list]:
        # Analysis logic here
        return value, confidence, reasoning_list
```

### Hierarchical Factor Types
- **PRIMARY** - Strong contrarian signals (higher thresholds)
- **SECONDARY** - Supporting factors (moderate thresholds)  
- **TRIGGER** - Conditional activation factors
- **MODIFIER** - Multiplicative adjustments

## Configuration

The system automatically handles:
- **Rate Limiting** - Respects API quotas (CFBD: 150/day, Odds: 83/day, ESPN: 60/min)
- **Caching** - Reduces API calls with intelligent data caching
- **Team Normalization** - Maps 130+ team name variations
- **FCS Filtering** - Removes FCS teams from analysis
- **Logging** - Technical details in `logs/cfb_predictor.log`

## Development

### Adding New Factors
1. Create factor class in `factors/` directory
2. Register in `factor_registry.py` 
3. System automatically loads and weights new factors

### Data Requirements
Factors declare their data dependencies:

```python
def get_required_data(self) -> Dict[str, bool]:
    return {
        'team_info': True,          # Basic team information
        'coaching_data': True,      # Coaching experience data
        'team_stats': False,        # Season statistics
        'schedule_data': False,     # Game schedules
        'betting_data': False,      # Historical betting info
        'historical_data': False   # Multi-year trends
    }
```

## Troubleshooting

**No edges found**: Common for well-priced games. Try games with larger spreads or rivalry matchups.

**Missing data**: Some factors require schedule data not currently implemented. System shows which factors failed and why.

**API limits**: System automatically rate limits. Check `logs/cfb_predictor.log` for details.

## License

MIT License