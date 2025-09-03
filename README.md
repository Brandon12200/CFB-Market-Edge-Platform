# College Football Market Edge Platform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#testing)

Production-ready machine learning platform for identifying market inefficiencies in college football betting markets through advanced statistical analysis, market sentiment detection, and adaptive learning algorithms.

## Overview

This tool analyzes college football games by applying quantifiable "contrarian factors" to Vegas consensus lines, specifically seeking scenarios where the unfavored team has hidden advantages that the market may have overlooked. The system doesn't try to predict winners—it identifies systematic gaps between market perception and quantifiable team advantages.

## Key Features

### 🧠 **Advanced Analytics Engine**
- **Multi-Factor Analysis**: Coaching experience differentials, situational contexts, momentum indicators
- **Market Efficiency Detection**: Real-time line movement analysis and sharp money identification
- **Adaptive Calibration**: Self-improving confidence scoring based on historical performance
- **Dynamic Factor Weighting**: Automatically adjusts model weights based on predictive accuracy

### 📊 **Production-Ready Architecture**
- **Modular Design**: Clean separation of concerns with pluggable factor system
- **Comprehensive Testing**: 95%+ test coverage with unit and integration tests
- **Robust Error Handling**: Graceful degradation and detailed logging
- **Performance Monitoring**: Built-in metrics and health checking

### 🎯 **Intelligent Filtering**
- **Game Quality Assessment**: Filters high-variance and low-quality betting opportunities
- **Conference-Aware Analysis**: Specialized handling for different conference dynamics
- **Weather & Situational Context**: Environmental and temporal factor integration
- **Data Quality Validation**: Ensures predictions are based on reliable information

## Installation

```bash
git clone https://github.com/Brandon12200/CFB-Market-Edge-Platform.git
cd CFB-Market-Edge-Platform
python -m venv cfb-env
source cfb-env/bin/activate  # On Windows: cfb-env\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

## Required Configuration

Add to your `.env` file:

```bash
# Required for betting lines (500 free calls/month)
ODDS_API_KEY=your_odds_api_key

# Highly recommended for enhanced analysis (5000 free calls/month)
CFBD_API_KEY=your_cfbd_api_key

# ESPN API - No key required (public endpoints used)
```

**API Key Sources:**
- [The Odds API](https://theoddsapi.com) - Live betting lines
- [College Football Data API](https://collegefootballdata.com) - Advanced stats and coaching data
- ESPN API - No key required for basic access

## Usage

### Single Game Analysis
```bash
# Basic analysis
python main.py --home "Ohio State" --away "Michigan" --week 12

# With detailed factor breakdown
python main.py --home "Alabama" --away "Auburn" --week 13 --show-factors

# Verbose output with debugging info
python main.py --home "Texas" --away "Oklahoma" --week 6 --verbose
```

### Weekly Analysis
```bash
# Analyze current week's games
python main.py --analyze-week

# Specific week with minimum edge filter
python main.py --analyze-week 13 --min-edge 2.0

# Output as JSON or CSV
python main.py --analyze-week --format json
```

### System Utilities
```bash
# List all supported teams
python main.py --list-teams

# Validate team name
python main.py --validate-team "Ohio State"

# List games for specific week
python main.py --list-games 10

# Check system configuration
python main.py --check-config

# Clear cache
python main.py --cache-clear
```

### Factor Validation
```bash
# Validate all factors for realistic outputs
python scripts/validate_factors.py

# Validate specific factor
python scripts/validate_factors.py --factor MarketSentiment

# Generate validation report
python scripts/validate_factors.py --output json --save validation_report.json
```

## Factor System Architecture

The system employs a hierarchical factor structure with dynamic confidence-based weighting:

### Factor Categories

**Market & Style Factors** - Primary contrarian signals
- Market Sentiment (39.1%) - Betting patterns and line movements
- Style Mismatch (19.5%) - Statistical matchup advantages
- Scheduling Fatigue (12.9%) - Rest and travel advantages

**Coaching & Experience Factors** - Team leadership analysis
- Experience Differential (3.9%) - Head coach experience advantages
- Head-to-Head Record (3.9%) - Historical coaching matchups
- Pressure Situation (3.9%) - Performance under pressure

**Momentum & Situational Factors** - Game context
- Close Game Performance (2.3%) - Clutch situation execution
- Point Differential Trends (2.7%) - Recent scoring margin patterns
- Desperation Index (3.9%) - Must-win situation analysis
- Lookahead Sandwich (3.9%) - Schedule spot advantages
- Revenge Game (3.9%) - Motivation factors

Note: Weights are automatically normalized to sum to 1.0

### Confidence-Based Weighting

Each factor calculation includes a confidence assessment that adjusts its impact:
- **VERY_HIGH** (90% weight) - Strong supporting data
- **HIGH** (75% weight) - Good data quality
- **MEDIUM** (50% weight) - Moderate confidence
- **LOW** (25% weight) - Limited data
- **NONE** (0% weight) - Insufficient data

## Sample Output

### Standard Analysis
```
Analyzing: MICHIGAN @ OHIO STATE
Week: 12
--------------------------------------------------
Fetching game data...
Data Quality: 85.0%
Vegas Spread: OHIO STATE -7.5

Team Information:
   OHIO STATE: Ohio State Buckeyes (Big Ten)
   MICHIGAN: Michigan Wolverines (Big Ten)

Coaching Comparison:
   OHIO STATE: Ryan Day (8 years)
   MICHIGAN: Sherrone Moore (2 years)
   Experience Edge: OHIO STATE (+6 years)

Generating Contrarian Prediction...

Prediction Results:
   Vegas Spread: OHIO STATE -7.5
   Contrarian Prediction: OHIO STATE -5.8
   Factor Adjustment: +1.7 points
   Edge Size: 1.7 points

Edge Analysis:
   Edge Type: Moderate Edge
   Confidence: High (72.4%)
   Recommendation: MICHIGAN +7.5 - Contrarian value identified
```

### Factor Breakdown Example
```
Factor Breakdown:
   MarketSentiment: x1.04 (multiplier)
      → Moderate contrarian signal in market
   StyleMismatch: +0.29 (weighted: +0.09)
      → MICHIGAN has style advantages
   SchedulingFatigue: -0.55 (weighted: -0.11)
      → OHIO STATE has rest advantage
   ExperienceDifferential: +0.84 (weighted: +0.34)
      → OHIO STATE significant experience edge
   DesperationIndex: +0.48 (weighted: +0.02)
      → OHIO STATE slightly more desperate

Category Summary:
   Situational Context: +0.02 points
   Coaching Edge: +0.34 points
   Momentum Factors: +0.09 points
   Market Modifiers: x1.04

Variance Analysis:
   Factor Agreement: MODERATE DISAGREEMENT
   Confidence Adjustment: -10% (uncertainty penalty)
   Bet Size Recommendation: 70% of normal
```

## Advanced Features

### Variance Detection System

The system analyzes factor disagreement to identify high-uncertainty games:
- **CONSENSUS** - Factors strongly agree (high confidence)
- **MILD DISAGREEMENT** - Minor variance (standard confidence)
- **MODERATE DISAGREEMENT** - Notable variance (reduce bet size)
- **STRONG DISAGREEMENT** - High uncertainty (significant caution)
- **EXTREME DISAGREEMENT** - Factors completely split (avoid)

### Trap Game Detection

Identifies suspicious betting patterns that may indicate trap games:
- Line freezes despite heavy public action
- Reverse line movement (line moves against public money)
- Key number sticking (lines frozen at 3, 7, 10, 14)
- Pattern recognition for common trap setups

### Data Quality Assessment

Each prediction includes a data quality score that impacts confidence:
- Team information availability
- Coaching data completeness
- Statistical coverage
- API response quality
- Cache freshness

## System Architecture

### Data Flow
```
User Input → CLI Parser → Prediction Engine → Factor Registry
                                    ↓
                            Data Manager ← Multi-Source APIs
                                    ↓
                            Factor Calculations
                                    ↓
                            Variance Analysis → Risk Assessment
                                    ↓
                            Final Prediction → Output Formatter
```

### Caching Strategy
- **Team Data**: 7 days (stable information)
- **Coaching Data**: 1 day (may change weekly)
- **Game Context**: 1 hour (for live updates)
- **API Responses**: Varies by endpoint volatility

### Rate Limiting
- **CFBD API**: 5000 calls/month (Tier 1)
- **Odds API**: 500 calls/month (free tier)
- **ESPN API**: 60 calls/minute (when used)

## Development

### Adding New Factors

1. Create factor class inheriting from `BaseFactorCalculator`:
```python
class NewFactor(BaseFactorCalculator):
    def __init__(self):
        super().__init__()
        self.weight = 0.15  # Factor weight within category
        self.category = "momentum_factors"
        self.activation_threshold = 0.5
        
    def calculate(self, home_team, away_team, context):
        # Implementation logic
        return adjustment_value
```

2. Place file in `factors/` directory
3. System automatically discovers and loads the factor

### Testing and Validation

Run the comprehensive validation suite:
```bash
# Full system validation
python scripts/validate_factors.py

# Check for uniform outputs
python scripts/validate_factors.py --quick

# Generate HTML report
python scripts/validate_factors.py --output html --save report.html
```

## Performance Characteristics

- **Execution Time**: 2-5 seconds per game (with caching)
- **API Efficiency**: ~10 API calls per fresh analysis
- **Cache Hit Rate**: 70-80% in typical usage
- **Memory Usage**: ~50MB baseline, ~100MB with full cache

## Troubleshooting

### Common Issues

**"No edges found"**
- Normal for efficiently priced games
- Try games with larger spreads or strong public bias
- Check data quality score

**"Factor calculation failed"**
- Usually indicates missing data
- Check API keys and rate limits
- Review logs/cfb_predictor.log for details

**"Extreme variance detected"**
- Factors strongly disagree
- System working correctly—avoid these games
- Consider waiting for more data

### Debug Mode
```bash
# Enable detailed logging
python main.py --home "Team1" --away "Team2" --week 8 --debug

# Check system health
python main.py --check-config --verbose
```

## License

MIT License - See LICENSE file for details