# CFB Contrarian Predictor - Factor Design Document

## Project Goals & Philosophy

### Primary Objective
Create a college football arbitrage detector that makes **risky but statistically backed** predictions that diverge from Vegas lines and public perception. The goal is NOT to confirm what Vegas already knows, but to identify hidden contrarian value.

### Core Philosophy
> "Being a contrarian bettor isn't easy. It isn't sexy either. You almost never get to bet on the popular, star-studded teams that all of your Average Joe friends are rooting for."

**Success Criteria:**
- Predictions should feel "uncomfortable" and "wrong" at first glance
- Target 2-4 games per week with meaningful contrarian edges (2+ points)
- Find situations where the "worse" team has real, measurable advantages
- Create systematic factor analysis that casual bettors don't track

### Volatility Challenge
College football's extreme volatility (roster turnover, coaching changes, transfer portal) makes traditional metrics less reliable. Our contrarian approach leverages this chaos to find mispriced opportunities that emerge from:
- Schedule-induced fatigue that accumulates over weeks
- Style mismatches that public overlooks
- Market inefficiencies from recreational betting

## Factor Architecture Decisions

### Dynamic Weighting System
Each factor uses confidence-based adjustments to prevent diluting impact:
- **VERY_HIGH** (0.9x) - Strong data supporting factor
- **HIGH** (0.75x) - Good data confidence  
- **MEDIUM** (0.5x) - Moderate confidence
- **LOW** (0.25x) - Limited data quality
- **NONE** (0.0x) - Insufficient data

### Factor Categories & Weights
- **PRIMARY Factors (60% total weight)** - Direct contrarian signals
- **SECONDARY Factors (30% total weight)** - Supporting evidence
- **MODIFIER Factors (10% total weight)** - Situational adjustments

## Factors to KEEP (Proven Contrarian Value)

### 1. Head-to-Head Coaching Record ✅ KEEP
**Category:** PRIMARY (20% weight)
**Rationale:** Vegas doesn't deeply weight coaching history in individual matchups
**File:** `factors/coaching_head_to_head.py`

**Why Keep:**
- Direct historical performance data between specific coaches
- Often overlooked by public who focus on recent team performance
- Provides actual track record rather than speculation

**Implementation Notes:**
- Use CFBD `/coaches` endpoint for historical data
- Weight recent matchups more heavily (last 5 years)
- Account for different programs (coach success at current school vs previous)

### 2. Desperation Index ✅ KEEP  
**Category:** PRIMARY (20% weight)
**Rationale:** Bowl eligibility pressure creates motivation differentials undervalued by public
**File:** `factors/desperation_index.py`

**Why Keep:**
- Quantifiable pressure based on win-loss record and remaining schedule
- Public doesn't systematically track bowl eligibility math
- Creates situations where "worse" team has higher motivation

**Implementation Notes:**
- Calculate bowl eligibility scenarios for both teams
- Weight late-season games more heavily (weeks 10-12)
- Consider conference championship implications
- Factor in quality of remaining opponents

## Factors to ADD (High Contrarian Value)

### 3. Scheduling Fatigue Factor ⭐ NEW PRIMARY
**Category:** PRIMARY (20% weight)  
**Why Add:** Public doesn't track cumulative travel/rest patterns
**File:** `factors/scheduling_fatigue.py`

**Contrarian Value:**
- Teams playing 3rd+ road game in 4 weeks face hidden disadvantage
- Short rest after emotional games creates performance decline
- Away team fatigue matters more than home team advantages

**CFBD API Requirements (Tier 1):**
```python
# Required endpoints (2 API calls per game analysis)
/games - Game dates, locations, home/away status
/teams/{team}/games - Team-specific game history
```

**Calculation Logic:**
```python
stress_score = (
    road_games_in_last_4 * 0.8 +      # Cumulative travel fatigue
    short_rest_games * 1.5 +          # Recovery time deficit  
    emotional_games * 0.6             # Mental/physical toll
)
```

**Maximum Impact:** ±3.5 points

### 4. Style Mismatch Amplifier ⭐ NEW SECONDARY
**Category:** SECONDARY (15% weight)
**Why Add:** Public bets team reputation, not matchup dynamics
**File:** `factors/style_mismatch.py`

**Contrarian Value:**
- Success rate differentials predict performance better than rankings
- Pace mismatches favor slower teams (chaos helps underdogs)
- Explosiveness vs explosiveness defense creates extreme outcomes

**CFBD API Requirements (Tier 1):**
```python
# Required endpoints (2 API calls per game analysis)  
/stats/season/advanced - EPA, success rates, explosiveness
/stats/season - Basic team statistics
```

**Key Mismatch Detection:**
- **Success Rate Differential:** Most predictive advanced metric
- **Explosiveness vs Defense:** Big play potential vs susceptibility  
- **Pace Mismatch:** Slower teams benefit in pace differential games
- **Red Zone Efficiency vs Defense:** Critical scoring situations

**Maximum Impact:** ±4.0 points

### 5. Market Sentiment Divergence ⭐ NEW MODIFIER  
**Category:** MODIFIER (10% weight)
**Why Add:** Direct contrarian signal when sharp money moves against public
**File:** `factors/market_sentiment.py`

**Contrarian Value:**
- Reverse line movement indicates sharp money disagreeing with public
- Steam moves show informed betting action
- Public betting percentages reveal recreational money flow

**API Requirements:**
```python
# CFBD Tier 1 (1 API call per game)
/betting/lines - Historical line movement

# Odds API (existing integration)  
public_betting_percentages - Where recreational money flows
```

**Detection Patterns:**
- **Reverse Movement:** Public >70% on team, line moves opposite direction
- **Steam Moves:** Rapid line movement (>1 point in <6 hours)
- **Sharp vs Public:** Betting percentages vs line movement divergence

**Maximum Impact:** ±2.5 points

## Factors to REMOVE (Confirm Vegas Lines)

### ❌ Venue Performance Factor - REMOVE
**Why Remove:** Too similar to home field advantage already priced into lines
**Problem:** Vegas already accounts for venue-specific advantages
**Replacement:** Absorbed into Scheduling Fatigue (travel component)

### ❌ ATS Recent Form - REMOVE  
**Why Remove:** Vegas adjusts lines based on recent performance
**Problem:** Following recent trends confirms rather than contradicts market
**Alternative:** Style metrics provide deeper performance indicators

### ❌ Statement Opportunities - REMOVE
**Why Remove:** Public already overvalues "big game" narratives  
**Problem:** Creates popular plays rather than contrarian value
**Focus Instead:** Desperation Index captures motivation more systematically

### ❌ All "Returning Production" Variations - REMOVE
**Why Remove:** These factors are variations of "roster quality" that confirm Vegas assessment
**Problems:**
- Returning production data is publicly tracked and priced in
- Transfer portal impact is already reflected in preseason lines
- Talent composite rankings correlate with Vegas favorites
- Creates "chalk" plays rather than contrarian opportunities

## Implementation Architecture

### File Structure
```
factors/
├── __init__.py
├── base_factor.py                    # BaseFactorCalculator class
├── coaching_head_to_head.py          # Existing - keep as-is
├── desperation_index.py              # Existing - keep as-is  
├── scheduling_fatigue.py             # NEW - primary contrarian factor
├── style_mismatch.py                 # NEW - secondary support factor
├── market_sentiment.py               # NEW - modifier factor
└── factor_registry.py                # Dynamic weighting coordinator
```

### BaseFactorCalculator Interface
```python
class BaseFactorCalculator:
    def __init__(self):
        self.factor_type = FactorType.PRIMARY | SECONDARY | MODIFIER
        self.activation_threshold = float  # Minimum value to trigger
        self.max_impact = float           # Cap on adjustment magnitude
        
    def calculate_with_confidence(self, home_team: str, away_team: str, 
                                 context: Dict[str, Any]) -> Tuple[float, FactorConfidence, List[str]]:
        """
        Returns: (adjustment_value, confidence_level, reasoning_list)
        """
        pass
        
    def get_required_data(self) -> Dict[str, bool]:
        """Declare API dependencies for data manager"""
        pass
```

### Dynamic Weighting in factor_registry.py
```python
# Weight factors by type and confidence
weighted_adjustment = raw_adjustment * confidence_multiplier * category_weight

# Category weights (must sum to 1.0)
PRIMARY_WEIGHT = 0.60      # Direct contrarian signals
SECONDARY_WEIGHT = 0.30    # Supporting evidence  
MODIFIER_WEIGHT = 0.10     # Situational adjustments

# Individual factor weights within categories
primary_factors = {
    'coaching_head_to_head': 0.33,    # 20% of total
    'desperation_index': 0.33,        # 20% of total  
    'scheduling_fatigue': 0.34        # 20% of total
}
```

## API Usage Strategy (CFBD Tier 1 - 5,000 calls/month)

### Call Budget Allocation
- **Per Game Analysis:** 6 API calls maximum
- **Monthly Capacity:** ~800 game analyses
- **Aggressive Caching:** Season-long stats cached 1 hour
- **Batch Requests:** Multiple weeks in single call when possible

### API Call Distribution per Game:
```python
# Scheduling Fatigue: 2 calls (recent games for each team)
GET /games?year=2024&team=TeamA&week=4,5,6,7
GET /games?year=2024&team=TeamB&week=4,5,6,7

# Style Mismatch: 2 calls (advanced stats for each team)  
GET /stats/season/advanced?year=2024&team=TeamA
GET /stats/season/advanced?year=2024&team=TeamB

# Market Sentiment: 1-2 calls (betting lines + public data)
GET /betting/lines?gameId=12345
GET odds_api/public_percentages (external)
```

### Caching Strategy
```python
# Cache keys by data volatility
SEASON_STATS_TTL = 3600      # 1 hour (changes infrequently)
GAME_RESULTS_TTL = 86400     # 24 hours (historical data)
BETTING_LINES_TTL = 300      # 5 minutes (live data)
```

## Expected Contrarian Outcomes

### Target Results
- **2-4 contrarian games per week** with 2+ point edges
- **Uncomfortable predictions** that feel wrong initially
- **Hidden advantages** for unfavored teams based on:
  - Accumulated schedule stress differentials
  - Overlooked stylistic matchup advantages  
  - Sharp money moving against public perception

### Success Metrics
1. **Divergence from Vegas:** Predictions differ from consensus by 2+ points
2. **Contrarian Nature:** Recommendations favor underdogs/unpopular sides
3. **Statistical Backing:** Each factor supported by quantifiable data
4. **Market Inefficiency:** Exploits gaps in public analysis

### Risk Profile
- **High Variance:** Contrarian plays inherently riskier than consensus
- **Low Volume:** Focus on quality opportunities rather than quantity
- **Systematic Edge:** Consistent methodology rather than gut feelings

## Code Implementation Guidelines

### For Future Development
1. **Factor Isolation:** Each factor in separate file with clear interface
2. **Confidence Weighting:** Always multiply raw adjustment by confidence level
3. **API Efficiency:** Cache aggressively, batch requests, track call limits
4. **Reasoning Transparency:** Every adjustment includes human-readable explanation
5. **Validation Logic:** Handle missing data gracefully with appropriate confidence reduction

### Error Handling
```python
# Graceful degradation when API calls fail
try:
    factor_result = calculate_factor(team_a, team_b)
except APIException:
    factor_result = (0.0, FactorConfidence.NONE, ["API unavailable"])
```

### Testing Strategy
- **Historical Backtesting:** Validate factors against known outcomes
- **API Mocking:** Test without consuming API quota
- **Edge Cases:** Handle missing data, extreme values, new teams

## Conclusion

This factor redesign transforms the predictor from a "Vegas confirmation tool" into a true contrarian analyzer. By focusing on hidden fatigue patterns, overlooked style mismatches, and market sentiment divergence, we create systematic opportunities to identify mispriced games where the "wrong" team has real advantages.

The key insight: **College football's volatility creates inefficiencies that systematic analysis can exploit, but only if we look where others don't.**