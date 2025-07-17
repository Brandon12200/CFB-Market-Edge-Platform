# CFB Contrarian Predictor - Streamlined Product & Technical Specification

## Executive Summary

### Product Vision
Create a command-line tool that identifies contrarian college football betting opportunities by layering "human factor" adjustments on top of existing Vegas market consensus. Rather than building statistical predictions from scratch, focus on situational and psychological factors that create 3+ point edges against sportsbook lines.

### Core Value Proposition
- **Market Enhancement**: Build on Vegas expertise rather than replacing it
- **Situational Edge Detection**: Focus on coaching, momentum, and context factors that books may underweight
- **Rapid Deployment**: Streamlined approach targeting Week 0 readiness
- **Scalable Architecture**: Modular design allows easy factor expansion post-launch

### Key Innovation
**Adjustment Layer Philosophy**: `Your Prediction = Vegas Line + Human Factor Adjustments`

---

## Product Overview

### Target User
- **Primary**: Individual sports bettors seeking systematic contrarian angles
- **Secondary**: Friend groups looking for alternative perspectives on marquee games
- **Tertiary**: Sports betting enthusiasts interested in situational analysis

### Success Metrics
- **Edge Detection**: Identify 2-3 games per week with >3 point line differences
- **Accuracy**: >55% ATS on flagged contrarian picks
- **Reliability**: <5% failure rate due to technical issues
- **Speed**: Complete analysis in <15 seconds per game

### Core User Journey
1. **Saturday Morning Check**: Run tool for weekend slate
2. **Edge Identification**: Review games with significant line differences
3. **Factor Analysis**: Understand why the edge exists via factor breakdown
4. **Betting Decision**: Use confidence levels to guide bet sizing
5. **Results Tracking**: Monitor edge detection accuracy over time

---

## Technical Architecture

### System Design Overview
```
Vegas Lines (API) → Factor Calculations → Adjustment Layer → Edge Detection → Contrarian Alerts
```

### Core Components

#### 1. Team Name Normalizer
**Purpose**: Handle flexible team name input across different data sources

```python
class TeamNameNormalizer:
    def __init__(self):
        self.espn_mappings = {
            'GEORGIA': ['georgia', 'uga', 'bulldogs'],
            'ALABAMA': ['alabama', 'bama', 'crimson tide'],
            'TEXAS': ['texas', 'ut', 'longhorns'],
            # ... 130+ FBS teams with common variations
        }
        
        self.odds_api_mappings = {
            'Georgia Bulldogs': 'GEORGIA',
            'Alabama Crimson Tide': 'ALABAMA',
            # Map odds API team names to internal format
        }
```

#### 2. Market Data Aggregator
**Purpose**: Collect real-time odds and basic team statistics

```python
class MarketDataAggregator:
    def __init__(self, odds_api_key):
        self.odds_client = OddsAPIClient(odds_api_key)
        self.espn_client = ESPNStatsClient()
        
    def get_game_context(self, home_team, away_team):
        # Get current spread from multiple books
        market_data = self.odds_client.get_spreads(home_team, away_team)
        
        # Get basic team stats for factor calculations
        team_stats = self.espn_client.get_team_data([home_team, away_team])
        
        return {
            'vegas_spread': market_data['consensus_spread'],
            'home_stats': team_stats[home_team],
            'away_stats': team_stats[away_team]
        }
```

#### 3. Three-Factor Engine
**Purpose**: Calculate coaching, situational, and momentum adjustments

#### 4. Edge Detection System
**Purpose**: Compare factor adjustments to market lines and flag significant differences

#### 5. Contrarian Alert Generator
**Purpose**: Format and present opportunities with confidence levels

---

## Three-Factor Framework

### 1. Coaching Edge Factors (Weight: 0.40)

#### A. Experience Differential (-3 to +3 points)
**Data Source**: ESPN Coach Information
**Calculation**:
```python
def calculate_experience_edge(home_coach_years, away_coach_years):
    experience_gap = home_coach_years - away_coach_years
    # Diminishing returns after 10+ years
    if experience_gap > 10:
        experience_gap = 10 + (experience_gap - 10) * 0.3
    elif experience_gap < -10:
        experience_gap = -10 + (experience_gap + 10) * 0.3
    
    return max(-3, min(3, experience_gap * 0.3))
```

**Rationale**: Experienced coaches perform better in high-pressure situations and make superior in-game adjustments.

#### B. Head-to-Head Coaching Record (-2 to +4 points)
**Data Source**: ESPN Historical Game Data
**Logic**: Filter games by current coaching tenures, calculate win percentage differential
```python
def calculate_h2h_coaching_record(home_coach, away_coach, historical_games):
    relevant_games = filter_by_current_coaches(historical_games, home_coach, away_coach)
    if len(relevant_games) < 2:
        return 0  # Insufficient data
    
    home_wins = sum(1 for game in relevant_games if game['winner'] == 'home')
    win_rate = home_wins / len(relevant_games)
    
    # Convert win rate to point adjustment
    return (win_rate - 0.5) * 8  # Max 4 point swing
```

#### C. Home/Road Coaching Performance (-2 to +2 points)
**Data Source**: ESPN Coaching Records
**Calculation**: Compare each coach's home vs road win rates, calculate differential
```python
def calculate_venue_coaching_edge(home_coach_stats, away_coach_stats):
    home_coach_home_rate = home_coach_stats['home_wins'] / home_coach_stats['home_games']
    away_coach_road_rate = away_coach_stats['road_wins'] / away_coach_stats['road_games']
    
    venue_advantage = home_coach_home_rate - away_coach_road_rate
    return max(-2, min(2, venue_advantage * 4))
```

**Rationale**: Some coaches are significantly better at managing home crowd energy or handling road environments.

#### D. Coaching Pressure Index (-1 to +3 points)
**Data Source**: ESPN Performance Data + News API (optional)
**Factors**:
- Performance vs preseason expectations
- Job security indicators
- Recent contract extensions/hot seat talk

```python
def calculate_pressure_differential(home_team_record, away_team_record, preseason_expectations):
    home_pressure = calculate_pressure_score(home_team_record, preseason_expectations['home'])
    away_pressure = calculate_pressure_score(away_team_record, preseason_expectations['away'])
    
    # Higher pressure = more desperate coaching
    pressure_gap = away_pressure - home_pressure
    return max(-1, min(3, pressure_gap * 0.5))
```

### 2. Situational Context Factors (Weight: 0.40)

#### A. Desperation Index (-3 to +5 points)
**Data Source**: ESPN Standings + Remaining Schedule Analysis
**Calculation**:
```python
def calculate_desperation_differential(home_team, away_team, current_standings, remaining_schedule):
    home_desperation = calculate_team_desperation(home_team, current_standings, remaining_schedule)
    away_desperation = calculate_team_desperation(away_team, current_standings, remaining_schedule)
    
    return home_desperation - away_desperation

def calculate_team_desperation(team, standings, schedule):
    # Factors: playoff hopes, bowl eligibility, division race
    playoff_factor = get_playoff_desperation(team, standings)
    bowl_factor = get_bowl_desperation(team, standings)
    rivalry_factor = get_rivalry_game_factor(team, schedule)
    
    return playoff_factor + bowl_factor + rivalry_factor
```

**Components**:
- **Playoff/Championship Race**: Teams needing wins for conference title games
- **Bowl Eligibility**: Teams at 4-6 or 5-5 needing wins for bowl games
- **Rivalry Protection**: Historic rivalry games with extra motivation

#### B. Revenge Game Factor (0 to +4 points)
**Data Source**: ESPN Historical Results + Coaching History
**Triggers**:
- Previous season upset loss
- Coach vs former school
- Transfer portal revenge scenarios

```python
def calculate_revenge_factor(home_team, away_team, last_year_result, coaching_history):
    revenge_score = 0
    
    # Previous season result
    if last_year_result['upset_loss']:
        revenge_score += 2
    elif last_year_result['close_loss']:
        revenge_score += 1
    
    # Coaching connections
    if coaching_history['coach_vs_former_school']:
        revenge_score += 2
    
    # Transfer portal factor
    if coaching_history['key_transfers']:
        revenge_score += 1
    
    return min(4, revenge_score)
```

#### C. Sandwich Game Risk (0 to +3 points)
**Data Source**: ESPN Schedule Analysis
**Logic**: Identify teams potentially looking ahead or suffering emotional hangovers

```python
def calculate_sandwich_risk(team_schedule, current_week):
    previous_game = team_schedule[current_week - 1]
    next_game = team_schedule[current_week + 1]
    
    risk_score = 0
    
    # Looking ahead to big game
    if next_game['opponent_ranking'] <= 10:
        risk_score += 2
    elif next_game['rivalry_game']:
        risk_score += 1
    
    # Emotional hangover from big win/loss
    if previous_game['emotional_high']:
        risk_score += 1
    
    return min(3, risk_score)
```

#### D. Statement Game Opportunity (-1 to +3 points)
**Data Source**: Rankings + National Perception Data
**Logic**: Identify breakthrough opportunities for undervalued teams

```python
def calculate_statement_opportunity(home_team, away_team, rankings, media_attention):
    opportunity_score = 0
    
    # Unranked vs ranked scenarios
    if not home_team['ranked'] and away_team['ranking'] <= 15:
        opportunity_score += 2
    
    # National TV exposure
    if media_attention['prime_time_tv']:
        opportunity_score += 1
    
    # Program trajectory
    if home_team['recruiting_momentum'] > away_team['recruiting_momentum']:
        opportunity_score += 1
    
    return max(-1, min(3, opportunity_score))
```

### 3. Basic Momentum Factors (Weight: 0.20)

#### A. Point Differential Trend (-2 to +2 points)
**Data Source**: ESPN Game Results (Last 4 Games)
**Calculation**:
```python
def calculate_momentum_trend(team_recent_games):
    recent_margins = [game['point_margin'] for game in team_recent_games[-4:]]
    season_avg_margin = calculate_season_average_margin(team_recent_games)
    
    recent_avg = sum(recent_margins) / len(recent_margins)
    trend_differential = recent_avg - season_avg_margin
    
    return max(-2, min(2, trend_differential * 0.2))
```

#### B. Close Game Performance (-1 to +3 points)
**Data Source**: ESPN Game Results
**Logic**: Teams that win close games show composure and coaching advantages

```python
def calculate_clutch_performance(team_games):
    close_games = [game for game in team_games if abs(game['margin']) <= 7]
    
    if len(close_games) < 2:
        return 0
    
    close_game_win_rate = sum(1 for game in close_games if game['won']) / len(close_games)
    
    # Convert to point adjustment
    return (close_game_win_rate - 0.5) * 6  # Max 3 point adjustment
```

#### C. Against The Spread (ATS) Recent Form (-1 to +2 points)
**Data Source**: The Odds API Historical + ESPN Results
**Calculation**:
```python
def calculate_ats_momentum(team_ats_record, recent_games=4):
    recent_ats = team_ats_record[-recent_games:]
    recent_ats_rate = sum(recent_ats) / len(recent_ats)
    season_ats_rate = sum(team_ats_record) / len(team_ats_record)
    
    ats_trend = recent_ats_rate - season_ats_rate
    return max(-1, min(2, ats_trend * 4))
```

**Rationale**: Teams performing well ATS recently may continue exceeding expectations.

---

## API Integration Strategy

### Primary Data Sources

#### The Odds API (Primary Market Data)
**Base URL**: `https://api.the-odds-api.com/v4`
**Key Endpoints**:
- `/sports/americanfootball_ncaaf/odds` - Current spreads from all major books
- `/sports/americanfootball_ncaaf/odds/history` - Historical line movement

**Rate Limiting**: 500 calls/month (free tier)
**Usage Strategy**: 
- Batch all games for the week in single API call
- Cache results for multiple factor calculations
- Use only for current week predictions

```python
class OddsAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        self.cache = {}
    
    def get_weekly_spreads(self):
        if 'weekly_odds' in self.cache:
            return self.cache['weekly_odds']
        
        url = f"{self.base_url}/sports/americanfootball_ncaaf/odds"
        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': 'spreads',
            'oddsFormat': 'decimal'
        }
        
        response = requests.get(url, params=params)
        self.cache['weekly_odds'] = response.json()
        return self.cache['weekly_odds']
    
    def get_consensus_spread(self, home_team, away_team):
        weekly_data = self.get_weekly_spreads()
        
        for game in weekly_data:
            if self.teams_match(game, home_team, away_team):
                spreads = []
                for bookmaker in game['bookmakers']:
                    for outcome in bookmaker['markets'][0]['outcomes']:
                        if outcome['name'] == home_team:
                            spreads.append(outcome['point'])
                
                return sum(spreads) / len(spreads) if spreads else None
        
        return None
```

#### ESPN College Football API (Team Statistics)
**Base URL**: `https://site.api.espn.com/apis/site/v2/sports/football/college-football`
**Key Endpoints**:
- `/teams` - Team information and coaching staff
- `/teams/{team_id}/schedule` - Season schedule and results
- `/teams/{team_id}/roster` - Player information
- `/scoreboard` - Current week games and results

**Rate Limiting**: No official limits, but implement 1 second delays
**Data Points**:
- Coaching experience and records
- Game results and point margins  
- Team standings and rankings
- Schedule strength analysis

```python
class ESPNStatsClient:
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/college-football"
        self.team_cache = {}
    
    def get_team_info(self, team_name):
        if team_name in self.team_cache:
            return self.team_cache[team_name]
        
        # Get team ID first
        teams_url = f"{self.base_url}/teams"
        teams_response = requests.get(teams_url)
        team_id = self.find_team_id(teams_response.json(), team_name)
        
        # Get detailed team data
        team_url = f"{self.base_url}/teams/{team_id}"
        team_response = requests.get(team_url)
        
        self.team_cache[team_name] = team_response.json()
        time.sleep(1)  # Rate limiting
        
        return self.team_cache[team_name]
    
    def get_coaching_data(self, team_name):
        team_data = self.get_team_info(team_name)
        coaching_staff = team_data['team']['coaches']
        
        head_coach = next(coach for coach in coaching_staff if coach['position'] == 'Head Coach')
        
        return {
            'name': head_coach['displayName'],
            'experience_years': head_coach.get('experience', 0),
            'record': head_coach.get('record', {}),
            'tenure_start': head_coach.get('tenureStart', None)
        }
```

### Error Handling & Fallbacks

```python
class DataManager:
    def __init__(self, odds_api_key):
        self.odds_client = OddsAPIClient(odds_api_key)
        self.espn_client = ESPNStatsClient()
        self.fallback_data = {}
    
    def safe_data_fetch(self, fetch_function, *args, **kwargs):
        try:
            result = fetch_function(*args, **kwargs)
            # Cache successful results
            cache_key = f"{fetch_function.__name__}_{hash(str(args))}"
            self.fallback_data[cache_key] = result
            return result
        except Exception as e:
            print(f"API Error: {e}")
            # Return cached data or neutral values
            cache_key = f"{fetch_function.__name__}_{hash(str(args))}"
            if cache_key in self.fallback_data:
                print("Using cached data")
                return self.fallback_data[cache_key]
            else:
                print("Using neutral values")
                return self.get_neutral_data_structure(fetch_function.__name__)
    
    def get_neutral_data_structure(self, function_name):
        # Return neutral/zero values when no data available
        neutral_structures = {
            'get_consensus_spread': 0.0,
            'get_coaching_data': {'experience_years': 5, 'record': {'wins': 50, 'losses': 50}},
            'get_team_schedule': []
        }
        return neutral_structures.get(function_name, {})
```

---

## Prediction Engine Algorithm

### Core Adjustment Calculation

```python
class PredictionEngine:
    def __init__(self):
        self.factor_weights = {
            'coaching_edge': 0.40,
            'situational_context': 0.40,
            'momentum_factors': 0.20
        }
        
        self.factors = {
            'coaching_edge': CoachingEdgeCalculator(),
            'situational_context': SituationalContextCalculator(),
            'momentum_factors': MomentumFactorsCalculator()
        }
    
    def calculate_contrarian_prediction(self, home_team, away_team, vegas_spread):
        # Calculate factor adjustments
        factor_adjustments = {}
        total_adjustment = 0.0
        
        for factor_name, calculator in self.factors.items():
            adjustment = calculator.calculate(home_team, away_team)
            factor_adjustments[factor_name] = adjustment
            weighted_adjustment = adjustment * self.factor_weights[factor_name]
            total_adjustment += weighted_adjustment
        
        # Apply adjustment to Vegas line
        contrarian_prediction = vegas_spread + total_adjustment
        
        # Calculate edge and confidence
        edge_size = abs(total_adjustment)
        confidence = self.calculate_confidence(factor_adjustments, edge_size)
        
        return {
            'vegas_spread': vegas_spread,
            'contrarian_prediction': contrarian_prediction,
            'total_adjustment': total_adjustment,
            'edge_size': edge_size,
            'confidence': confidence,
            'factor_breakdown': factor_adjustments
        }
```

### Confidence Calculation

```python
def calculate_confidence(self, factor_adjustments, edge_size):
    # Base confidence from edge size
    edge_confidence = min(50, edge_size * 10)  # Larger edges = higher confidence
    
    # Factor alignment bonus
    positive_factors = sum(1 for adj in factor_adjustments.values() if adj > 1)
    negative_factors = sum(1 for adj in factor_adjustments.values() if adj < -1)
    total_factors = len(factor_adjustments)
    
    # Higher confidence when factors align in same direction
    alignment_ratio = max(positive_factors, negative_factors) / total_factors
    alignment_bonus = alignment_ratio * 30
    
    # Factor strength bonus
    strong_factors = sum(1 for adj in factor_adjustments.values() if abs(adj) > 2)
    strength_bonus = strong_factors * 10
    
    total_confidence = edge_confidence + alignment_bonus + strength_bonus
    return min(95, max(15, total_confidence))
```

### Edge Classification

```python
def classify_edge(self, edge_size, confidence):
    if edge_size >= 6:
        return "🚨 MASSIVE EDGE"
    elif edge_size >= 4:
        return "🔥 STRONG EDGE"
    elif edge_size >= 2.5:
        return "⚡ SOLID EDGE"
    elif edge_size >= 1.5:
        return "📊 SLIGHT LEAN"
    else:
        return "➡️ NO EDGE"
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
**Week 1**:
- [x] Project setup and architecture planning
- [ ] Team name normalization system
- [ ] The Odds API integration and testing
- [ ] Basic CLI argument parsing
- [ ] ESPN API connection and team data fetching

**Week 2**:
- [ ] Coaching edge factor calculations (all 4 sub-factors)
- [ ] Basic prediction engine framework
- [ ] Error handling and fallback systems
- [ ] Unit tests for core functions

### Phase 2: Factor Implementation (Week 3-4)
**Week 3**:
- [ ] Situational context factors (4 sub-factors)
- [ ] Momentum factors (3 sub-factors)  
- [ ] Factor combination and weighting system
- [ ] Confidence calculation algorithm

**Week 4**:
- [ ] Edge detection and classification
- [ ] Output formatting and CLI presentation
- [ ] Integration testing of full pipeline
- [ ] Performance optimization for 15-second target

### Phase 3: Testing & Validation (Week 5-6)
**Week 5**:
- [ ] Backtest against 2023 season data
- [ ] Factor weight optimization based on historical performance
- [ ] Edge case handling (missing data, API failures)
- [ ] Documentation and user guide

**Week 6**:
- [ ] Live testing with preseason games
- [ ] Final CLI polish and error messaging
- [ ] Performance monitoring and logging
- [ ] Week 0 deployment preparation

### Phase 4: Week 0 Deployment & Iteration
**Week 0**:
- [ ] Live deployment for opening weekend
- [ ] Real-time monitoring of predictions
- [ ] User feedback collection
- [ ] Quick bug fixes and adjustments

**Ongoing**:
- [ ] Weekly performance tracking
- [ ] Factor weight adjustments based on results
- [ ] Additional factor development
- [ ] User experience improvements

---

## Command Line Interface Design

### Basic Usage
```bash
python cfb_predictor.py --home georgia --away alabama
```

### Advanced Options
```bash
python cfb_predictor.py --home uga --away bama --verbose --show-factors --week 8
```

### Batch Analysis
```bash
python cfb_predictor.py --analyze-week 8 --min-edge 3.0
```

### Sample Output Format
```
==================================================
CFB CONTRARIAN PREDICTOR v2.0
Georgia vs Alabama (Week 8)
==================================================

📊 MARKET CONSENSUS
Vegas Spread: Alabama -6.5 (avg of 8 books)
Implied Win Probability: Alabama 72%

🎯 CONTRARIAN ANALYSIS  
Your Prediction: Alabama -2.1
Factor Adjustment: +4.4 points toward Georgia
⚡ SOLID EDGE: 4.4 point difference
Confidence Level: 78%

📈 FACTOR BREAKDOWN
Category                Score    Impact    Reasoning
--------------------------------------------------------
Coaching Edge           +2.1     HIGH      Smart revenge game factor
                                          Experience edge to Georgia
                                          
Situational Context     +1.8     HIGH      Georgia desperate for statement win
                                          Alabama in sandwich spot vs LSU next
                                          
Momentum Factors        +0.5     LOW       Georgia trending up in close games
                                          Alabama ATS form declining

🎲 CONTRARIAN INSIGHTS
• Kirby Smart 3-1 vs Alabama since becoming Georgia coach
• Georgia needs signature win after early season struggles  
• Alabama coming off emotional Iron Bowl, LSU looming next week
• Georgia 6-1 ATS as underdog this season

💰 RECOMMENDED ACTION
STRONG PLAY: Georgia +6.5
Kelly Criterion Bet Size: 2.1% of bankroll
```

---

## Data Architecture & Storage

### Stateless Design Philosophy
- **No Persistent Storage**: All data fetched fresh per execution
- **Session-Based Caching**: Cache API responses only during single run
- **API-Dependent**: Relies on external sources for all data
- **Ephemeral Results**: Output exists only in terminal session

### Memory Management
```python
class DataCache:
    def __init__(self):
        self.session_cache = {}
        self.cache_timestamps = {}
        self.max_cache_age = 3600  # 1 hour
    
    def get_cached_data(self, key):
        if key in self.session_cache:
            if time.time() - self.cache_timestamps[key] < self.max_cache_age:
                return self.session_cache[key]
        return None
    
    def cache_data(self, key, data):
        self.session_cache[key] = data
        self.cache_timestamps[key] = time.time()
    
    def clear_expired_cache(self):
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.cache_timestamps.items()
            if current_time - timestamp > self.max_cache_age
        ]
        for key in expired_keys:
            del self.session_cache[key]
            del self.cache_timestamps[key]
```

### API Call Optimization
**Target**: <20 API calls per prediction
- **The Odds API**: 1 call per session (all games)
- **ESPN API**: 2-4 calls per game (team data)
- **Batch Processing**: When analyzing multiple games
- **Smart Caching**: Reuse team data across multiple predictions

---

## Modular Factor System

### Factor Registration Architecture
```python
class FactorRegistry:
    def __init__(self):
        self.factors = {}
        self.weights = {}
        self.total_weight = 0.0
    
    def register_factor(self, name, calculator_class, weight, category):
        self.factors[name] = {
            'calculator': calculator_class(),
            'weight': weight,
            'category': category
        }
        self.weights[name] = weight
        self.total_weight += weight
    
    def calculate_all_factors(self, home_team, away_team):
        results = {}
        for name, factor_info in self.factors.items():
            try:
                score = factor_info['calculator'].calculate(home_team, away_team)
                results[name] = {
                    'score': score,
                    'weight': factor_info['weight'],
                    'category': factor_info['category']
                }
            except Exception as e:
                print(f"Factor {name} failed: {e}")
                results[name] = {'score': 0, 'weight': factor_info['weight'], 'category': factor_info['category']}
        
        return results
    
    def get_weighted_adjustment(self, factor_results):
        total_adjustment = 0.0
        for factor_name, result in factor_results.items():
            weighted_score = result['score'] * result['weight']
            total_adjustment += weighted_score
        
        return total_adjustment
```

### Adding New Factors (Post-Launch)
```python
# Example: Adding new "Weather Impact" factor
class WeatherImpactCalculator:
    def calculate(self, home_team, away_team):
        # Weather calculation logic
        return weather_adjustment_score

# Register new factor
factor_registry.register_factor(
    name="weather_impact",
    calculator_class=WeatherImpactCalculator,
    weight=0.05,
    category="environmental"
)

# Automatically rebalance weights
factor_registry.normalize_weights()
```

---

## Quality Assurance & Testing Strategy

### Unit Testing Framework
```python
import unittest
from unittest.mock import Mock, patch

class TestCoachingEdgeCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = CoachingEdgeCalculator()
        self.mock_data_manager = Mock()
    
    def test_experience_differential_calculation(self):
        # Test normal experience gap
        result = self.calculator.calculate_experience_edge(15, 5)
        self.assertAlmostEqual(result, 3.0)  # Max cap
        
        # Test reverse gap
        result = self.calculator.calculate_experience_edge(2, 12)
        self.assertAlmostEqual(result, -3.0)  # Min cap
        
        # Test equal experience
        result = self.calculator.calculate_experience_edge(8, 8)
        self.assertEqual(result, 0.0)
    
    @patch('cfb_predictor.data_manager.ESPNStatsClient')
    def test_coaching_data_integration(self, mock_espn):
        # Mock API response
        mock_espn.get_coaching_data.return_value = {
            'experience_years': 10,
            'record': {'wins': 85, 'losses': 25}
        }
        
        result = self.calculator.calculate_with_real_data('georgia', 'alabama')
        self.assertIsInstance(result, float)
        self.assertTrue(-10 <= result <= 10)  # Reasonable bounds
```

### Integration Testing
```python
class TestFullPipeline(unittest.TestCase):
    def setUp(self):
        self.predictor = CFBPredictor(test_mode=True)
    
    def test_end_to_end_prediction(self):
        # Test complete prediction flow
        result = self.predictor.generate_prediction('georgia', 'alabama')
        
        # Verify output structure
        required_fields = ['vegas_spread', 'contrarian_prediction', 'confidence', 'edge_size']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Verify reasonable ranges
        self.assertTrue(0 <= result['confidence'] <= 100)
        self.assertTrue(-21 <= result['contrarian_prediction'] <= 21)
    
    def test_api_failure_graceful_degradation(self):
        # Test behavior when APIs fail
        with patch('cfb_predictor.odds_api.get_consensus_spread', side_effect=Exception("API Error")):
            result = self.predictor.generate_prediction('georgia', 'alabama')
            self.assertIsNotNone(result)  # Should not crash
```

### Manual Testing Checklist

**Factor Accuracy**:
- [ ] Coaching experience calculations match ESPN data
- [ ] Situational factors trigger correctly for known scenarios
- [ ] Momentum calculations align with recent game results

**API Integration**:
- [ ] The Odds API returns reasonable spreads for current games
- [ ] ESPN API provides complete team data
- [ ] Error handling works when APIs are down

**Output Quality**:
- [ ] CLI output is readable and actionable
- [ ] Factor breakdowns help understand edge reasoning
- [ ] Confidence levels correlate with factor strength

**Edge Cases**:
- [ ] New/rebuilt programs with limited coaching history
- [ ] Teams with interim coaches
- [ ] Games with extreme weather conditions
- [ ] Neutral site games

---

## Performance Monitoring & Success Metrics

### Real-Time Performance Tracking
```python
class PerformanceTracker:
    def __init__(self):
        self.predictions = []
        self.api_call_times = []
        self.total_execution_times = []
    
    def log_prediction(self, prediction_data, execution_time):
        self.predictions.append({
            'timestamp': datetime.now(),
            'home_team': prediction_data['home_team'],
            'away_team': prediction_data['away_team'],
            'vegas_spread': prediction_data['vegas_spread'],
            'contrarian_prediction': prediction_data['contrarian_prediction'],
            'edge_size': prediction_data['edge_size'],
            'confidence': prediction_data['confidence'],
            'execution_time': execution_time
        })
        
        self.total_execution_times.append(execution_time)
    
    def get_performance_summary(self):
        return {
            'avg_execution_time': sum(self.total_execution_times) / len(self.total_execution_times),
            'total_predictions': len(self.predictions),
            'avg_edge_size': sum(p['edge_size'] for p in self.predictions) / len(self.predictions),
            'high_confidence_predictions': len([p for p in self.predictions if p['confidence'] > 75])
        }
```

### Success Metrics Dashboard
**Weekly Tracking**:
- Number of contrarian edges identified (target: 2-3 per week)
- Average edge size on flagged games (target: >3 points)
- Execution time performance (target: <15 seconds)
- API reliability rate (target: >95%)

**Season-Long Validation**:
- ATS performance on high-confidence picks (target: >55%)
- Confidence calibration accuracy
- Factor performance attribution
- User adoption and retention

### Continuous Improvement Process
```python
def analyze_weekly_performance():
    # Collect results from completed games
    completed_predictions = get_games_with_results()
    
    # Calculate accuracy metrics
    high_confidence_accuracy = calculate_ats_accuracy(
        [p for p in completed_predictions if p['confidence'] > 75]
    )
    
    # Factor performance analysis
    factor_performance = analyze_factor_contribution(completed_predictions)
    
    # Weight adjustment recommendations
    weight_adjustments = recommend_weight_changes(factor_performance)
    
    return {
        'accuracy_report': high_confidence_accuracy,
        'factor_analysis': factor_performance,
        'recommended_adjustments': weight_adjustments
    }
```

---

## Project Structure

```
cfb-contrarian-predictor/
├── main.py                      # CLI entry point and orchestration
├── config.py                    # Configuration and API keys
├── normalizer.py               # Team name standardization
├── data/
│   ├── __init__.py
│   ├── odds_client.py          # The Odds API integration
│   ├── espn_client.py          # ESPN API client
│   ├── data_manager.py         # Unified data access layer
│   └── cache_manager.py        # Session caching system
├── factors/
│   ├── __init__.py
│   ├── base_calculator.py      # Abstract base class for factors
│   ├── coaching_edge.py        # Coaching-related calculations
│   ├── situational_context.py # Game situation factors
│   ├── momentum_factors.py     # Recent performance trends
│   └── factor_registry.py     # Factor registration system
├── engine/
│   ├── __init__.py
│   ├── prediction_engine.py    # Core prediction logic
│   ├── confidence_calculator.py # Confidence scoring
│   └── edge_detector.py       # Edge identification and classification
├── output/
│   ├── __init__.py
│   ├── formatter.py           # CLI output formatting
│   └── insights_generator.py  # Contrarian insight explanations
├── utils/
│   ├── __init__.py
│   ├── rate_limiter.py        # API rate limiting
│   ├── error_handler.py       # Exception management
│   └── performance_tracker.py # Monitoring and metrics
├── tests/
│   ├── __init__.py
│   ├── test_factors.py        # Unit tests for factor calculations
│   ├── test_api_clients.py    # API integration tests
│   ├── test_prediction_engine.py # Core logic tests
│   └── test_integration.py    # End-to-end testing
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # Setup and usage instructions
```

## Technical Dependencies

### Core Dependencies
```txt
requests>=2.31.0          # HTTP API calls
argparse                  # CLI argument parsing (built-in)
datetime                  # Date/time handling (built-in)
time                      # Rate limiting and delays (built-in)
json                      # API response parsing (built-in)
statistics                # Mathematical calculations (built-in)
unittest                  # Testing framework (built-in)
```

### Development Dependencies
```txt
pytest>=7.4.0            # Enhanced testing framework
pytest-mock>=3.11.0      # Mocking for tests
black>=23.7.0            # Code formatting
flake8>=6.0.0            # Code linting
mypy>=1.5.0              # Type checking
```

### Environment Configuration
```bash
# API Keys (stored in .env file)
ODDS_API_KEY=your_odds_api_key_here
ESPN_API_KEY=optional_if_required
```

## Core Classes and Interfaces

### Base Factor Calculator Interface
```python
from abc import ABC, abstractmethod

class BaseFactorCalculator(ABC):
    def __init__(self):
        self.weight = 0.0
        self.category = ""
        self.description = ""
    
    @abstractmethod
    def calculate(self, home_team: str, away_team: str) -> float:
        """
        Calculate factor adjustment for given teams.
        
        Args:
            home_team: Normalized home team name
            away_team: Normalized away team name
            
        Returns:
            Float adjustment value (negative favors away, positive favors home)
        """
        pass
    
    def validate_input(self, home_team: str, away_team: str) -> bool:
        """Validate team names and required data availability."""
        return home_team and away_team and home_team != away_team
    
    def get_factor_info(self) -> dict:
        """Return metadata about this factor."""
        return {
            'weight': self.weight,
            'category': self.category,
            'description': self.description,
            'range': self.get_output_range()
        }
    
    @abstractmethod
    def get_output_range(self) -> tuple:
        """Return (min_value, max_value) for this factor."""
        pass
```

### Data Client Interface
```python
from abc import ABC, abstractmethod

class BaseDataClient(ABC):
    def __init__(self):
        self.rate_limiter = None
        self.cache = {}
    
    @abstractmethod
    def get_team_data(self, team_name: str) -> dict:
        """Fetch team information from data source."""
        pass
    
    def cache_result(self, key: str, data: dict, ttl: int = 3600):
        """Cache API response with time-to-live."""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl
        }
    
    def get_cached_result(self, key: str) -> dict:
        """Retrieve cached data if still valid."""
        if key in self.cache:
            cached = self.cache[key]
            if time.time() - cached['timestamp'] < cached['ttl']:
                return cached['data']
        return None
```

## Additional Factors for Future Development

### Environmental Factors
- **Weather Impact**: Rain, wind, temperature effects on gameplay
- **Altitude Adjustment**: High-altitude venue impacts
- **Travel Distance**: Miles traveled and time zone changes

### Personnel Factors  
- **Key Injury Impact**: Star player availability adjustments
- **Depth Chart Analysis**: Backup quality vs starters
- **Transfer Portal Newcomers**: New player integration success

### Advanced Situational Factors
- **Conference Championship Implications**: Stakes-based motivation
- **Bowl Game Positioning**: December motivation factors
- **Recruiting Weekend Pressure**: High-profile visitor impacts
- **Academic Calendar Stress**: Midterms, finals period effects

### Market-Based Factors
- **Line Movement Patterns**: Sharp vs public money indicators
- **Betting Volume Analysis**: Handle and ticket count disparities
- **Historical Market Inefficiencies**: Books' blind spots by team/situation

### Media & Perception Factors
- **National TV Exposure**: Prime time performance history
- **Social Media Sentiment**: Fan base confidence indicators
- **Preseason Hype vs Reality**: Expectation gap analysis
- **Coach Media Pressure**: Press conference tone and content

This comprehensive specification provides all the technical details needed to build and deploy the CFB Contrarian Predictor v2.0 by Week 0 of the college football season.