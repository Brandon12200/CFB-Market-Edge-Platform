# CFB Contrarian Predictor

A rule-based betting model that adjusts Vegas consensus spreads using 11 quantifiable factors. Built as a forward-testing experiment to evaluate whether systematic contrarian adjustments can identify mispriced college football games.

## How It Works

The model takes the Vegas spread and applies additive and multiplicative adjustments:

```
Contrarian Spread = (Vegas Spread + Factor Adjustments) × Market Modifier
Edge = |Contrarian Spread - Vegas Spread|
```

### Factor System

11 factors organized in a fixed-weight hierarchy:

| Category | Weight | Factors |
|----------|--------|---------|
| Primary | 60% | Scheduling Fatigue (±3.5 pts), Head-to-Head Record, Desperation Index |
| Secondary | 30% | Experience Differential, Pressure Situation, Revenge Game, Lookahead Spot, Point Differential Trends, Close Game Performance, Style Mismatch |
| Modifier | 10% | Market Sentiment (0.5x–1.5x multiplier based on line movement) |

Each factor inherits from `BaseFactorCalculator` and implements:
- `calculate()` — returns a point adjustment
- `calculate_with_confidence()` — returns adjustment + confidence level + reasoning
- `get_output_range()` — defines valid output bounds for the factor

Factors have activation thresholds. Signals below threshold are zeroed out to avoid noise from weak signals affecting the prediction.

### Variance Detection

The variance detector analyzes factor agreement using coefficient of variation. When factors disagree significantly (e.g., scheduling fatigue favors Team A but market sentiment favors Team B), the game receives a reduced confidence score. This flags high-uncertainty situations where the model's signal is conflicted.

See `METHODOLOGY.md` for full algorithm documentation including the model lock verification process.

## Results

**2025 Season, Weeks 1–14**

| Metric | Value |
|--------|-------|
| Games | 300 |
| Accuracy (ATS) | 57.0% |
| ROI (at -110) | +8.82% |
| Sharpe Ratio | 0.093 |

### Experiment Integrity

The model was locked on **August 25, 2025**—before Week 1 kicked off. Since then:

- Zero modifications to prediction logic or factor weights
- No parameter tuning based on results
- Predictions generated and stored before each week's games
- Results recorded separately with actual outcomes

This separation ensures the numbers above reflect true out-of-sample performance, not backtested or curve-fit metrics.

### Data Storage

All predictions and results are stored as JSON for independent verification:

- `data/predictions/2025_week_XX.json` — Pre-game predictions with timestamps
- `data/results/2025_week_XX_results.json` — Post-game results with actual scores

Each prediction record includes: Vegas spread, contrarian spread, confidence score, factor breakdown, and data quality assessment.

## System Design

### Data Pipeline

Three external APIs with fallback chain:

| Source | Role | Data Provided |
|--------|------|---------------|
| The Odds API | Required | Live spreads from FanDuel, DraftKings, BetMGM, etc. |
| College Football Data API | Primary | Coaching records, advanced stats, historical betting lines |
| ESPN API | Fallback | Schedule and team data when CFBD is unavailable |

The `DataManager` class coordinates requests across sources:
1. Attempts CFBD first for coaching/stats data
2. Falls back to ESPN if CFBD returns incomplete data
3. If both fail, uses neutral values and penalizes prediction confidence
4. Tracks which sources contributed to each prediction via `data_sources` field

### Rate Limiting

The `RateLimiter` class implements sliding window rate limiting:
- Tracks timestamps of recent calls in a `deque`
- Enforces both per-minute and per-day limits
- Thread-safe using `threading.Lock`
- Automatically waits when limits are reached

This prevents API quota violations when running batch analyses.

### Caching

The `CacheManager` implements TTL-based caching:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Coaching data | 24 hours | Changes infrequently |
| Team stats | 1 hour | Updates after games |
| Betting lines | 30 minutes | Can move quickly |

Cache is thread-safe with automatic cleanup of expired entries. Each entry tracks access count and last access time for monitoring cache effectiveness.

### Testing

305 tests organized by component:

- **Factor tests** — Each of the 11 factors has unit tests validating output ranges, edge cases, and expected behavior for known matchups
- **API client tests** — Mock-based tests for each data source, including error handling and fallback behavior
- **Cache tests** — TTL expiration, thread safety, eviction policies
- **Integration tests** — End-to-end prediction flow from CLI input to final output

Run with: `python -m pytest tests/ -v`

## Project Structure

```
├── main.py                     # CLI entry point, argument parsing
├── config.py                   # Configuration, API keys, factor weights
├── METHODOLOGY.md              # Algorithm documentation, model lock verification
├── engine/
│   ├── prediction_engine.py    # Orchestrates factor calculation and aggregation
│   ├── edge_detector.py        # Classifies edge size and generates recommendations
│   ├── variance_detector.py    # Analyzes factor agreement/disagreement
│   └── confidence_calculator.py # Computes final confidence score
├── factors/
│   ├── base_calculator.py      # Abstract base class defining factor interface
│   ├── factor_registry.py      # Dynamic factor loading and weight normalization
│   ├── scheduling_fatigue.py   # Travel distance, rest days, emotional game hangover
│   ├── market_sentiment.py     # Line movement analysis, reverse line movement detection
│   ├── coaching_edge.py        # Experience differential, head-to-head records
│   ├── situational_context.py  # Desperation index, lookahead spots, revenge games
│   ├── momentum_factors.py     # Point differential trends, close game performance
│   └── style_mismatch.py       # Pace and efficiency matchup analysis
├── data/
│   ├── data_manager.py         # Multi-source coordinator with fallback logic
│   ├── odds_client.py          # The Odds API client
│   ├── cfbd_client.py          # College Football Data API client
│   ├── espn_client.py          # ESPN API client
│   ├── cache_manager.py        # TTL-based caching with thread safety
│   ├── predictions/            # Weekly pre-game predictions (JSON)
│   └── results/                # Weekly post-game results (JSON)
├── utils/
│   ├── rate_limiter.py         # Sliding window rate limiter
│   └── normalizer.py           # Team name normalization (handles aliases, mascots)
├── scripts/
│   ├── calculate_accuracy.py   # Computes ATS accuracy from results
│   ├── calculate_roi.py        # Computes ROI assuming -110 odds
│   └── calculate_sharpe.py     # Computes Sharpe ratio of returns
└── tests/                      # 305 tests
```

## Setup

```bash
git clone https://github.com/Brandon12200/CFB-Market-Edge-Platform.git
cd CFB-Market-Edge-Platform
pip install -r requirements.txt
```

Create `.env`:
```
ODDS_API_KEY=your_key      # Required - theoddsapi.com
CFBD_API_KEY=your_key      # Recommended - collegefootballdata.com
```

## Usage

```bash
# Single game prediction
python main.py --home "Ohio State" --away "Michigan" --week 12

# With detailed factor breakdown
python main.py --home "Ohio State" --away "Michigan" --week 12 --show-factors

# List Power 4 games for a week
python main.py --list-games 10

# Run performance analysis scripts
python scripts/calculate_accuracy.py
python scripts/calculate_roi.py
python scripts/calculate_sharpe.py
```

## License

MIT
