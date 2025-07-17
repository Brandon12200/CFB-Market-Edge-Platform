# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CFB Contrarian Predictor v2.0 is a command-line tool that identifies contrarian college football betting opportunities by layering "human factor" adjustments on top of Vegas market consensus. The project uses an "Adjustment Layer" approach: `Your Prediction = Vegas Line + Human Factor Adjustments`

## Project Structure & File Organization

```
cfb-contrarian-predictor/
├── main.py                      # CLI entry point - start here for new features
├── config.py                    # API keys and configuration management
├── normalizer.py               # Team name standardization (130+ FBS teams)
├── data/                       # All API integration and data fetching
│   ├── odds_client.py          # The Odds API - primary betting lines source
│   ├── espn_client.py          # ESPN API - team stats and coaching data
│   ├── data_manager.py         # Unified data access with error handling
│   └── cache_manager.py        # Session-level caching (1 hour TTL)
├── factors/                    # Three-factor prediction system
│   ├── base_calculator.py      # Abstract base class - inherit from this
│   ├── coaching_edge.py        # 40% weight - experience, pressure, venue
│   ├── situational_context.py # 40% weight - desperation, revenge, lookahead
│   ├── momentum_factors.py     # 20% weight - ATS, scoring, efficiency trends
│   └── factor_registry.py     # Dynamic factor loading and weight management
├── engine/                     # Core prediction logic
│   ├── prediction_engine.py    # Main calculation orchestrator
│   ├── confidence_calculator.py # Edge confidence scoring (15-95%)
│   └── edge_detector.py       # Contrarian opportunity identification
├── output/                     # CLI presentation layer
│   ├── formatter.py           # Terminal output with emojis and tables
│   └── insights_generator.py  # Human-readable edge explanations
├── utils/                      # Supporting infrastructure
│   ├── rate_limiter.py        # API throttling (prevents 429 errors)
│   ├── error_handler.py       # Graceful API failure handling
│   └── performance_tracker.py # Execution time and accuracy monitoring
└── tests/                      # Test coverage for all components
    ├── test_factors.py        # Factor calculation validation
    ├── test_api_clients.py    # API integration testing with mocks
    └── test_integration.py    # End-to-end pipeline testing
```

## Development Setup & Environment

### Initial Setup
```bash
# Clone and navigate to project
cd cfb-contrarian-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add API keys
cp .env.example .env
# Edit .env with your API keys:
# ODDS_API_KEY=your_odds_api_key_here
```

### Required API Keys
- **The Odds API**: Sign up at theoddsapi.com (30 seconds, 500 free calls/month)
- **ESPN API**: Public API, no key required but rate limiting implemented

### Common Development Commands

```bash
# Basic prediction
python main.py --home georgia --away alabama

# Advanced options with factor breakdown
python main.py --home uga --away bama --verbose --show-factors --week 8

# Batch analysis for entire week
python main.py --analyze-week 8 --min-edge 3.0

# Test specific factor calculations
python -m pytest tests/test_factors.py::TestCoachingEdge -v

# Run with coverage to identify gaps
python -m pytest --cov=cfb_predictor --cov-report=html

# Code formatting and quality
black . && flake8 . && mypy .
```

## Core Architecture & Data Flow

### Three-Factor Framework (Key Implementation Focus)

1. **Coaching Edge Factors (40% weight)**
   - Experience differential: `calculate_experience_edge(home_years, away_years)`
   - Head-to-head record: Filter by current coaching tenure
   - Venue performance: Home/road win rate differentials
   - Pressure index: Job security and expectations vs performance

2. **Situational Context Factors (40% weight)**
   - Desperation index: Playoff/bowl eligibility stakes
   - Revenge game factor: Previous losses, coaching connections
   - Lookahead/sandwich games: Schedule position analysis
   - Statement opportunities: Ranking and perception gaps

3. **Momentum Factors (20% weight)**
   - ATS recent form: Last 4 games vs season average
   - Point differential trends: Recent margins vs season norms
   - Close game performance: Clutch situations (≤7 point games)

### Critical Data Flow Pattern
```python
# This is the core prediction pipeline - maintain this flow:
def generate_prediction(home_team, away_team):
    # 1. Normalize team names across all data sources
    home_normalized = normalizer.normalize(home_team)
    away_normalized = normalizer.normalize(away_team)
    
    # 2. Fetch market consensus (single API call for efficiency)
    vegas_spread = odds_client.get_consensus_spread(home_normalized, away_normalized)
    
    # 3. Calculate all factor adjustments
    factors = factor_registry.calculate_all_factors(home_normalized, away_normalized)
    
    # 4. Apply weights and generate adjustment
    total_adjustment = sum(factor['score'] * factor['weight'] for factor in factors.values())
    
    # 5. Create contrarian prediction and detect edges
    contrarian_prediction = vegas_spread + total_adjustment
    edge_size = abs(total_adjustment)
    confidence = confidence_calculator.calculate(factors, edge_size)
    
    # 6. Format and return results
    return format_prediction_output(vegas_spread, contrarian_prediction, factors, confidence)
```

## Key Implementation Patterns

### Factor Calculator Pattern
All factor calculators must inherit from `BaseFactorCalculator`:

```python
class NewFactorCalculator(BaseFactorCalculator):
    def __init__(self):
        super().__init__()
        self.weight = 0.05  # Assigned weight in prediction
        self.category = "situational"
        self.description = "Brief factor description"
    
    def calculate(self, home_team: str, away_team: str) -> float:
        # Always return float between defined range
        # Positive = favors home team, Negative = favors away team
        return adjustment_value
    
    def get_output_range(self) -> tuple:
        return (-3.0, 3.0)  # Define min/max possible values
```

### API Client Error Handling Pattern
All API calls must use the safe_data_fetch pattern:

```python
def get_team_data(self, team_name):
    return self.data_manager.safe_data_fetch(
        self.espn_client.get_team_info,
        team_name
    )
    # This automatically handles:
    # - API failures with graceful degradation
    # - Rate limiting compliance
    # - Caching for repeated calls
    # - Fallback to neutral values
```

### Team Name Normalization (Critical)
Always normalize team names before any API calls:

```python
# ESPN API uses: "Georgia Bulldogs"
# Odds API uses: "Georgia" 
# User input: "uga", "georgia", "UGA"
# Internal format: "GEORGIA"

normalized_home = normalizer.normalize(user_input)
espn_name = normalizer.to_espn_format(normalized_home)
odds_name = normalizer.to_odds_format(normalized_home)
```

## Testing Strategy & Patterns

### Factor Testing Template
```python
def test_factor_calculation(self):
    calculator = YourFactorCalculator()
    
    # Test normal cases
    result = calculator.calculate("GEORGIA", "ALABAMA")
    self.assertIsInstance(result, float)
    
    # Test bounds
    min_val, max_val = calculator.get_output_range()
    self.assertTrue(min_val <= result <= max_val)
    
    # Test edge cases
    result_same_team = calculator.calculate("GEORGIA", "GEORGIA")
    self.assertEqual(result_same_team, 0.0)  # Same team should be neutral
```

### API Mocking Pattern
```python
@patch('cfb_predictor.data.espn_client.ESPNStatsClient.get_team_info')
def test_with_mock_data(self, mock_espn):
    mock_espn.return_value = {
        'coach_experience': 10,
        'home_record': {'wins': 45, 'losses': 15}
    }
    # Test your logic with controlled data
```

## Performance & Rate Limiting Guidelines

### API Call Optimization
- **Target**: <20 API calls per prediction
- **The Odds API**: 1 call per session (batch all games)
- **ESPN API**: 2-4 calls per prediction (cache aggressively)
- **Cache everything**: Session-level caching with 1-hour TTL

### Rate Limiting Implementation
```python
# Each API client must implement rate limiting:
self.rate_limiter = RateLimiter(calls_per_minute=60)  # ESPN
self.rate_limiter = RateLimiter(calls_per_minute=83)  # Odds API (500/month = ~83/day)

# Always call before API requests:
self.rate_limiter.wait_if_needed()
```

## Common Debugging Scenarios

### API Integration Issues
1. **429 Rate Limit Errors**: Check rate_limiter implementation
2. **Team Name Not Found**: Add mapping to normalizer.py
3. **Missing Data Fields**: Update get_neutral_data_structure() in data_manager.py
4. **Cache Stale Data**: Clear session cache or reduce TTL

### Factor Calculation Issues
1. **Extreme Factor Values**: Check bounds in get_output_range()
2. **Zero Adjustments**: Verify data availability and calculation logic
3. **Factor Not Loading**: Check factor_registry registration
4. **Weight Doesn't Sum to 1.0**: Use normalize_weights() method

### Output Formatting Issues
1. **Edge Classification Wrong**: Check classify_edge() thresholds
2. **Confidence Out of Range**: Verify calculate_confidence() bounds (15-95%)
3. **CLI Formatting Broken**: Test with various terminal widths

## Implementation Roadmap & Current Status

**Week 1-2: Foundation (CURRENT FOCUS)**
- [ ] Project structure setup
- [ ] Team name normalization (130+ FBS teams)
- [ ] The Odds API integration with error handling
- [ ] ESPN API client with rate limiting
- [ ] Basic CLI argument parsing

**Week 3-4: Factor Implementation**
- [ ] Coaching edge factors (4 sub-factors)
- [ ] Situational context factors (4 sub-factors)  
- [ ] Momentum factors (3 sub-factors)
- [ ] Factor registry and weight management

**Week 5-6: Testing & Deployment**
- [ ] Unit test coverage >80%
- [ ] Integration testing with live APIs
- [ ] Performance optimization (<15 second execution)
- [ ] CLI output polish and error messaging

**Success Metrics for Week 0 Launch:**
- Identify 2-3 contrarian opportunities per week (>3 point edges)
- Execution time <15 seconds per prediction
- API reliability >95%
- No crashes on invalid input

## Adding New Factors (Post-Launch)

1. Create new calculator in `factors/` inheriting from `BaseFactorCalculator`
2. Implement `calculate()` method with proper bounds checking
3. Register in `factor_registry.py` with appropriate weight
4. Add unit tests in `tests/test_factors.py`
5. Update weights to maintain balance (total should equal 1.0)

## Code Quality Standards

- **Black formatting**: 88 character line limit
- **Type hints**: All public methods must have type annotations
- **Docstrings**: Google style for all classes and public methods
- **Error handling**: Never allow unhandled exceptions to crash CLI
- **Logging**: Use print() for user output, logging for debug info
- **Constants**: Define magic numbers as named constants

## Security & API Key Management

- Store all API keys in `.env` file (never commit)
- Use `os.getenv()` with defaults for missing keys
- Implement graceful degradation when keys are invalid
- Rate limiting prevents account suspension
- No persistent storage of betting lines (licensing concerns)

This guidance should help Claude Code navigate the codebase effectively and maintain the established patterns and architecture.