# Factor Calculations Documentation

## Overview

The CFB Contrarian Predictor uses an 11-factor system organized into three main categories to identify contrarian betting opportunities. This document provides detailed explanations of each factor's calculation methodology, weighting, and expected output ranges.

## Factor Framework

### Weight Distribution
- **Coaching Edge Factors**: 40% total weight (4 factors × 10% each)
- **Situational Context Factors**: 40% total weight (4 factors × 10% each)  
- **Momentum Factors**: 20% total weight (3 factors: 7%, 7%, 6%)

### Calculation Formula
```
Contrarian Prediction = Vegas Spread + Total Factor Adjustment

Total Factor Adjustment = Σ(Factor Value × Factor Weight)
```

---

## Coaching Edge Factors (40% Total Weight)

### 1. Experience Differential Calculator (10% Weight)

**Purpose**: Evaluates the coaching experience advantage between head coaches.

**Methodology**:
- Compares total coaching experience and tenure at current school
- Applies diminishing returns after 15 years of experience
- Includes rookie penalty for first-year coaches
- Weights tenure at current school as 30% of the calculation

**Calculation Steps**:
1. Calculate experience score: `min(total_experience, 15) / 15`
2. Calculate tenure score: `min(tenure_years, 8) / 8`
3. Composite score: `experience_score * 0.7 + tenure_score * 0.3`
4. Apply rookie penalty if total experience ≤ 1 year
5. Scale differential to output range

**Output Range**: -2.0 to +2.0 points
- Positive values favor home team (more experienced coach)
- Negative values favor away team

**Example**: Home coach with 10 years experience vs away coach with 3 years = ~+0.8 points

---

### 2. Pressure Situation Calculator (10% Weight)

**Purpose**: Assesses how coaches perform under high-pressure scenarios.

**Methodology**:
- Evaluates job security pressure based on current record
- Considers game-specific pressure (late season, rivalry games)
- Assesses performance vs expectations pressure
- Higher pressure typically hurts performance

**Pressure Factors**:
- **Job Security**: Based on win percentage (poor record = high pressure)
- **Game Pressure**: Week-dependent and home field pressure
- **Expectations Pressure**: Performance relative to preseason expectations

**Output Range**: -2.0 to +2.0 points
- Positive values indicate home team has advantage (less pressure or better under pressure)
- Negative values indicate away team has advantage

---

### 3. Venue Performance Calculator (10% Weight)

**Purpose**: Analyzes coaching performance differentials based on venue (home vs away).

**Methodology**:
- Evaluates home team's home venue advantage
- Assesses away team's road performance
- Includes base home field advantage of 0.3 points
- Considers venue familiarity and travel factors

**Calculation Components**:
- Home venue advantage: Based on home win percentage vs 50% baseline
- Road performance: Away team's road win percentage
- Base home field advantage: 0.3 points (standard CFB advantage)

**Output Range**: -1.5 to +1.5 points
- Typically positive (favoring home team) due to home field advantage
- Can be negative if away team travels exceptionally well

---

### 4. Head-to-Head Record Calculator (10% Weight)

**Purpose**: Evaluates historical performance between current coaching staffs.

**Methodology**:
- Analyzes head-to-head record filtered by current coaching tenure
- Requires minimum 3 games for statistical significance
- Weights recent games more heavily
- Only considers games involving current head coaches

**Output Range**: -1.0 to +1.0 points
- Returns 0.0 if insufficient games (< 3) for meaningful analysis
- Positive values favor home team in historical matchups

---

## Situational Context Factors (40% Total Weight)

### 5. Desperation Index Calculator (10% Weight)

**Purpose**: Measures team motivation based on playoff/bowl eligibility stakes.

**Methodology**:
- Evaluates bowl eligibility desperation (6+ wins needed)
- Assesses playoff contention desperation (≤1 loss for contention)
- Considers late-season pressure amplification
- More desperate teams often outperform expectations

**Desperation Scenarios**:
- **Elimination Game**: Must win to stay alive
- **Must Win**: Need all remaining games for goal
- **Helpful Win**: Win improves position but not critical
- **Meaningless**: Game has no impact on season goals

**Output Range**: -2.0 to +2.0 points
- Positive values indicate home team more desperate/motivated
- Peaks during weeks 10-13 when stakes are highest

---

### 6. Revenge Game Calculator (10% Weight)

**Purpose**: Identifies and weights revenge narratives and coaching connections.

**Methodology**:
- Analyzes recent losses requiring "revenge"
- Evaluates coaching connection storylines
- Considers media narrative amplification
- Includes rivalry game amplification factor

**Revenge Factors**:
- **Recent Loss Revenge**: 1-3 years with decreasing weight
- **Coaching Connections**: Former assistants vs head coaches
- **Narrative Revenge**: Media-driven storylines

**Output Range**: -1.5 to +1.5 points
- Hardcoded examples for major rivalries (e.g., Georgia vs Alabama)
- Most calculations return small values due to subjective nature

---

### 7. Lookahead/Sandwich Calculator (10% Weight)

**Purpose**: Detects schedule-based distraction factors.

**Methodology**:
- Identifies upcoming "big games" within 2 weeks (lookahead)
- Evaluates recent big games causing potential letdown
- Assesses game importance using opponent strength and stakes
- Distraction reduces focus on current game

**Analysis Components**:
- **Lookahead Distraction**: Upcoming games within 2 weeks
- **Letdown Factor**: Coming off significant wins within 1 week
- **Game Importance**: Rivalry, ranked opponent, championship implications

**Output Range**: -2.0 to +2.0 points
- Requires detailed schedule data for accurate calculation
- Positive values indicate away team more distracted

---

### 8. Statement Opportunity Calculator (10% Weight)

**Purpose**: Identifies opportunities for teams to make statements against perception.

**Methodology**:
- Compares team rankings/status for statement opportunities
- Evaluates motivation to prove worthiness
- Considers "program building" opportunities
- Unranked teams vs ranked opponents provide strongest signals

**Statement Scenarios**:
- **Unranked vs Top 5**: Maximum statement opportunity
- **Lower ranked vs higher ranked**: Moderate opportunity
- **Program building**: Establishing respectability

**Output Range**: -1.5 to +1.5 points
- Positive values indicate home team has statement opportunity
- Based on estimated rankings from win percentages

---

## Momentum Factors (20% Total Weight)

### 9. ATS Recent Form Calculator (7% Weight)

**Purpose**: Analyzes recent Against The Spread (ATS) performance trends.

**Methodology**:
- Examines last 4 games' ATS performance
- Weights recent games more heavily (40%, 30%, 20%, 10%)
- Includes streak bonuses for 3+ consecutive covers/failures
- Estimates historical spreads using home field advantage

**ATS Performance Scoring**:
- **Blowout Cover** (>14 points): +1.0
- **Regular Cover**: +0.6
- **Close Miss** (≤3 points): -0.3
- **Failed Cover**: -1.0

**Output Range**: -2.0 to +2.0 points
- Positive values indicate home team has better recent ATS momentum
- Includes streak bonuses for consistent performance

---

### 10. Point Differential Trends Calculator (7% Weight)

**Purpose**: Compares recent scoring margins to season averages.

**Methodology**:
- Analyzes last 4 games vs season average point differential
- Weights recent games progressively (newest = highest weight)
- Includes consistency bonus for stable performance
- Identifies teams trending up or down

**Trend Analysis**:
- **Significant Improvement**: +10 points vs average
- **Moderate Improvement**: +5 points vs average
- **Decline**: -5 points vs average
- **Consistency Bonus**: Low standard deviation in recent games

**Output Range**: -2.0 to +2.0 points
- Positive values indicate home team trending upward
- Consistency bonus rewards predictable performance

---

### 11. Close Game Performance Calculator (6% Weight)

**Purpose**: Evaluates clutch performance in games decided by ≤7 points.

**Methodology**:
- Analyzes performance in close games (≤7 point margin)
- Requires minimum 2 close games for significance
- Weights clutch wins more heavily than blowout performance
- Includes experience bonus for teams that play close games

**Clutch Performance Scoring**:
- **Win Close Game**: +1.0
- **Lose Close Game**: -0.7
- **Blowout Win**: +0.3
- **Blowout Loss**: -0.3

**Output Range**: -1.5 to +1.5 points
- Experience multiplier (1.2x) for teams with close game history
- Minimal impact if insufficient close game sample

---

## Factor Integration

### Calculation Pipeline

1. **Data Collection**: Gather team statistics, coaching data, and betting lines
2. **Factor Calculation**: Execute all 11 factors with error handling
3. **Weight Application**: Apply category and individual factor weights
4. **Consensus Building**: Aggregate weighted factor contributions
5. **Edge Detection**: Compare total adjustment to market consensus
6. **Confidence Assessment**: Evaluate prediction reliability

### Quality Controls

- **Bounds Checking**: All factor outputs clamped to defined ranges
- **Data Validation**: Missing data handled with neutral fallbacks
- **Error Handling**: Failed calculations don't crash the system
- **Weight Normalization**: Ensures total weights sum to 1.0

### Output Interpretation

**Total Adjustment Ranges**:
- **Strong Contrarian** (≥3.0 points): Significant market disagreement
- **Moderate Contrarian** (2.0-3.0 points): Meaningful edge detected  
- **Slight Contrarian** (1.0-2.0 points): Minor edge, proceed with caution
- **Consensus** (0.5-1.0 points): Minimal edge, align with market
- **No Edge** (<0.5 points): No meaningful contrarian opportunity

---

## Implementation Notes

### Data Dependencies

**Required Data**:
- Team records and statistics
- Coaching experience and tenure
- Current betting spreads
- Schedule information (for full accuracy)

**Optional Data**:
- Historical head-to-head results
- Detailed game-by-game results
- Advanced team metrics

### Performance Characteristics

- **Execution Time**: <1 second for factor calculations
- **API Calls**: 2-4 per prediction (with caching)
- **Memory Usage**: Minimal (session-level caching only)
- **Error Rate**: <5% with graceful degradation

### Limitations

1. **Historical Data**: Limited to publicly available information
2. **Subjective Factors**: Revenge/narrative elements inherently subjective
3. **Market Efficiency**: Most effective in less efficient markets
4. **Sample Size**: Some factors require multiple games for accuracy

---

## Validation and Testing

### Unit Testing
- Each factor tested with mock data
- Boundary conditions verified
- Error handling validated

### Integration Testing  
- Full pipeline tested with real data
- Performance benchmarks validated
- Edge cases covered

### Accuracy Tracking
- Factor contribution analysis
- Historical back-testing capabilities
- Confidence correlation tracking

---

*For implementation details, see the factor calculator source code in `/factors/` directory.*