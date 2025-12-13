# CFB Contrarian Predictor

Most betting models are backtested until they look good, then fail in production. This project was designed to avoid that trap—the model was frozen on August 25, 2025, before the season kicked off, and run forward with no modifications. The results below reflect genuine out-of-sample performance, not curve-fitting.

The model itself is a rule-based system that adjusts Vegas consensus spreads using 11 quantifiable factors. What makes it worth examining isn't the 57% accuracy—it's that the experiment was structured to actually know whether that number is real.

## Experiment Design

The model was locked on **August 25, 2025**—three days before Week 1. Since then:

- Zero modifications to prediction logic or factor weights
- No parameter tuning based on observed results
- Predictions generated and committed to git before each week's games
- Results recorded separately with actual outcomes

This separation ensures the numbers below reflect true out-of-sample performance. Git history provides the audit trail—`git log --oneline -- engine/prediction_engine.py` shows no changes since August 25.

## Results

**2025 Season, Weeks 1–14**

| Metric | Value |
|--------|-------|
| Games | 300 |
| Accuracy (ATS) | 57.0% |
| ROI (at -110) | +8.82% |
| Sharpe Ratio | 0.093 |

300 games provides moderate statistical confidence; the 95% confidence interval for true accuracy is approximately 51–63%. The Sharpe ratio contextualizes returns against week-to-week variance—a 0.093 Sharpe over 14 weeks suggests positive edge but acknowledges the volatility inherent in small samples.

### Data Storage

All predictions and results are stored as JSON for independent verification:

- `data/predictions/2025_week_XX.json` — Pre-game predictions with timestamps
- `data/results/2025_week_XX_results.json` — Post-game results with actual scores

Each prediction record includes: Vegas spread, contrarian spread, confidence score, factor breakdown, and data quality assessment.

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
| Primary | 60% | Scheduling Fatigue (±3.5 pts), Head-to-Head Record (±2 pts), Desperation Index (±2.5 pts) |
| Secondary | 30% | Experience Differential, Pressure Situation, Revenge Game, Lookahead Spot, Point Differential Trends, Close Game Performance, Style Mismatch |
| Modifier | 10% | Market Sentiment (0.5x–1.5x multiplier based on line movement) |

Each factor inherits from `BaseFactorCalculator` and implements `calculate()`, `calculate_with_confidence()`, and `get_output_range()`. Factors have activation thresholds—signals below threshold are zeroed out to avoid noise from weak signals.

### Why These Factors

Factors were selected based on market inefficiencies documented in betting literature and situations where public perception tends to diverge from actual game dynamics.

**Scheduling fatigue** is weighted highest because travel and rest disadvantages are quantifiable and historically underpriced by markets—a team playing its third road game in four weeks after an emotional rivalry win carries compounding fatigue that Vegas lines often underweight.

**Situational context** (desperation, lookahead, revenge) captures motivational asymmetries. A 4-5 team needing two wins for bowl eligibility plays differently than their record suggests; a team facing a cupcake before their rivalry game may underperform.

**Market sentiment** acts as a contrarian signal—when line movement diverges from betting percentages (reverse line movement), sharp money may be identifying value the public missed.

The factors deliberately exclude anything that would require subjective judgment or insider information. Everything is computable from public data.

### Variance Detection

The variance detector analyzes factor agreement using coefficient of variation. When factors disagree significantly (e.g., scheduling fatigue favors Team A but market sentiment favors Team B), the game receives a reduced confidence score.

Games with high variance scores are flagged as low-confidence; a user could filter to only bet games where factors align, trading volume for expected accuracy. This is where the model says "I don't have a strong opinion" rather than forcing a prediction.

## Design Decisions

**Why a fixed-weight hierarchy instead of learned weights?**
Learned weights require training data, which means backtesting, which means overfitting risk. Fixed weights force explicit assumptions—if scheduling fatigue should matter more than revenge games, that hypothesis is baked in before seeing any results. Wrong assumptions are exposed cleanly rather than hidden in optimized parameters.

**Why activation thresholds that zero out weak signals?**
A team that's "slightly fatigued" or in a "minor revenge spot" probably isn't mispriced—markets are efficient enough to handle small effects. Thresholds accept that not every game has an exploitable edge and reduce noise from marginal signals affecting predictions.

**Why freeze the model pre-season instead of updating weekly?**
The experiment's purpose was to test whether a static model could find edges, not to build an adaptive system. Weekly updates would introduce the same curve-fitting problem the project was designed to avoid. One season of frozen predictions produces cleaner signal on whether the underlying factors have predictive value.

**What would change for next season?**
See "What I Learned" below.

## What I Learned

**Scheduling fatigue appears to be the strongest signal.** Games where one team had significant rest/travel disadvantage showed the highest edge capture rate. This aligns with the hypothesis that physical factors are more reliably underpriced than motivational ones.

**"Revenge game" and "lookahead spot" were noisier than expected.** These situational factors produced high variance in outcomes—sometimes they mattered enormously, sometimes not at all. A v2 might reduce their weight or require additional confirming factors before activating them.

**High-confidence predictions outperformed low-confidence ones.** The variance detector's "I don't know" signal had value—filtering to only games with aligned factors would have improved accuracy at the cost of volume. This suggests the confidence scoring is capturing something real.

**What v2 would look like:**
- Reduce weight on situational/motivational factors
- Increase threshold for activation (be more selective)
- Add explicit "no bet" recommendations for low-confidence games
- Consider conference-specific adjustments (market efficiency varies)

The goal isn't to build a production betting system—it's to demonstrate that disciplined quantitative thinking can extract signal from public data, and that honest experiment design reveals what works.

## System Design

### Data Pipeline

Three external APIs with fallback chain:

| Source | Role | Data Provided |
|--------|------|---------------|
| The Odds API | Required | Live spreads from FanDuel, DraftKings, BetMGM, etc. |
| College Football Data API | Primary | Coaching records, advanced stats, historical betting lines |
| ESPN API | Fallback | Schedule and team data when CFBD is unavailable |

The `DataManager` class coordinates requests across sources. If CFBD fails, it falls back to ESPN. If both fail, it uses neutral values and penalizes prediction confidence.

### Rate Limiting & Caching

The `RateLimiter` implements sliding window rate limiting with thread-safe tracking. The `CacheManager` implements TTL-based caching (24h for coaching data, 1h for stats, 30min for lines) with automatic cleanup.

### Testing

305 tests covering factors, API clients, caching, and end-to-end prediction flow.

Run with: `python -m pytest tests/ -v`

## Project Structure

```
├── main.py                     # CLI entry point
├── config.py                   # Configuration, API keys, factor weights
├── engine/
│   ├── prediction_engine.py    # Factor calculation and aggregation
│   ├── edge_detector.py        # Edge classification and recommendations
│   ├── variance_detector.py    # Factor agreement analysis
│   └── confidence_calculator.py
├── factors/
│   ├── base_calculator.py      # Abstract base class
│   ├── factor_registry.py      # Dynamic factor loading
│   ├── scheduling_fatigue.py   # Travel, rest, emotional hangover
│   ├── market_sentiment.py     # Line movement, reverse line movement
│   ├── coaching_edge.py        # Experience, head-to-head records
│   ├── situational_context.py  # Desperation, lookahead, revenge
│   ├── momentum_factors.py     # Point differential, close games
│   └── style_mismatch.py       # Pace and efficiency matchups
├── data/
│   ├── data_manager.py         # Multi-source coordinator
│   ├── odds_client.py          # The Odds API
│   ├── cfbd_client.py          # College Football Data API
│   ├── espn_client.py          # ESPN API
│   ├── cache_manager.py        # TTL caching
│   ├── predictions/            # Weekly pre-game predictions
│   └── results/                # Weekly post-game results
├── utils/
│   ├── rate_limiter.py
│   └── normalizer.py           # Team name normalization
├── scripts/
│   ├── calculate_accuracy.py
│   ├── calculate_roi.py
│   └── calculate_sharpe.py
└── tests/
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

# Run performance analysis
python scripts/calculate_accuracy.py
python scripts/calculate_roi.py
python scripts/calculate_sharpe.py
```

## License

MIT
