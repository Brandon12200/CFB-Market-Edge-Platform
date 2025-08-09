# CFBD API Data Mapping for Contrarian Factors

## Overview
This document maps the available CFBD API endpoints to the data needed for our three new contrarian factors.

## Key Endpoints & Data Available

### 1. `/games` - Game Information 🎯 **CRITICAL FOR SCHEDULING FATIGUE**
**Best For:** Travel patterns, scheduling stress, game timing
```python
{
    "id": 401628330,
    "season": 2024,
    "week": 1,
    "startDate": "2024-08-31T16:45:00.000Z",
    "neutralSite": false,
    "venue": "Neyland Stadium",
    "homeTeam": "Tennessee",
    "awayTeam": "Chattanooga",
    "homePoints": 69,
    "awayPoints": 3,
    "completed": true,
    "attendance": null,
    "excitementIndex": 2.0752113158
}
```
**Contrarian Value:** Track cumulative travel fatigue, short rest periods, emotional game patterns

### 2. `/stats/season/advanced` - Advanced Analytics 🎯 **PERFECT FOR STYLE MISMATCH**
**Best For:** EPA, Success Rates, Explosiveness mismatches
```python
{
    "team": "Tennessee",
    "offense": {
        "ppa": 0.23780941449577284,          # Points Per Attempt (EPA equivalent)
        "successRate": 0.47708333333333336,   # Most predictive metric!
        "explosiveness": 1.1224566084792846,  # Big play capability
        "powerSuccess": 0.8395061728395061,   # Goal line/short yardage
        "stuffRate": 0.10771992818671454,     # Negative plays
        "fieldPosition": {"averageStart": 68.4},
        "havoc": {"total": 0.129},            # Disruption rate
        "standardDowns": {
            "ppa": 0.19489819788438295,
            "successRate": 0.532258064516129,
            "explosiveness": 0.9472484685551571
        },
        "passingDowns": {
            "ppa": 0.34308081639853505,
            "successRate": 0.34172661870503596,
            "explosiveness": 1.7919361326104248
        }
    },
    "defense": {
        # Same structure for defensive metrics
    }
}
```
**Contrarian Value:** Success rate differentials, explosive vs explosive defense mismatches

### 3. `/lines` - Betting Line History 🎯 **ESSENTIAL FOR MARKET SENTIMENT**  
**Best For:** Line movement, steam moves, reverse line movement
```python
{
    "id": 401628330,
    "homeTeam": "Tennessee",
    "awayTeam": "Chattanooga", 
    "lines": [
        {
            "provider": "ESPN Bet",
            "spread": -38.5,
            "formattedSpread": "Tennessee -38.5",
            "spreadOpen": null,          # Opening line
            "overUnder": 56.5,
            "overUnderOpen": null,
            "homeMoneyline": null,
            "awayMoneyline": null
        }
    ]
}
```
**Contrarian Value:** Detect reverse line movement, sharp vs public money patterns

### 4. `/drives` - Drive-by-Drive Data 🎯 **SUPPLEMENTARY**
**Best For:** Situational performance, clutch factor analysis
```python
{
    "offense": "Tennessee",
    "defense": "Chattanooga",
    "driveResult": "TD",
    "scoring": true,
    "plays": 8,
    "yards": 75,
    "startYardline": 25,
    "startYardsToGoal": 75
}
```

### 5. `/metrics/wp` - Win Probability 🎯 **SUPPLEMENTARY**  
**Best For:** Clutch performance, momentum shifts
```python
{
    "homeWinProbability": 0.85,
    "spread": -38.5,
    "down": 3,
    "distance": 7,
    "yardLine": 35
}
```

### 6. `/recruiting/teams` - Talent Composite 🎯 **AWARENESS**
**Best For:** Understanding public perception biases
```python
{
    "year": 2024,
    "team": "Tennessee", 
    "rank": 14,
    "points": 267.26
}
```

## Factor Implementation Strategy

### 1. SchedulingFatigue (PRIMARY)
**Data Sources:**
- `/games` - Last 4-6 weeks of games per team
- Track: Away games, travel distances, rest days, emotional games

**Key Metrics to Calculate:**
```python
fatigue_score = (
    road_games_in_last_4_weeks * 0.8 +
    short_rest_penalties * 1.5 +  
    emotional_game_toll * 0.6
)
```

### 2. StyleMismatch (SECONDARY)  
**Data Sources:**
- `/stats/season/advanced` - Both teams' advanced metrics

**Key Mismatch Detection:**
```python
# Success Rate is the most predictive metric
success_rate_diff = abs(home_offense.successRate - away_defense.successRate)

# Explosiveness mismatches
explosive_mismatch = home_offense.explosiveness vs away_defense.explosiveness

# Pace and havoc mismatches  
havoc_differential = home_defense.havoc - away_offense.havoc
```

### 3. MarketSentiment (MODIFIER)
**Data Sources:**
- `/lines` - Line movement patterns
- Existing Odds API - Public betting percentages

**Detection Patterns:**
```python
# Reverse line movement
if public_bet_percentage > 70 and line_moved_opposite:
    contrarian_signal = HIGH

# Steam moves  
if line_moved > 1.5_points in < 6_hours:
    sharp_money_signal = DETECTED
```

## API Call Optimization

### Efficient Batching Strategy:
1. **SchedulingFatigue**: 2 calls per game analysis
   - `/games?team=TeamA&week=4,5,6,7`
   - `/games?team=TeamB&week=4,5,6,7`

2. **StyleMismatch**: 2 calls per game analysis
   - `/stats/season/advanced?team=TeamA` 
   - `/stats/season/advanced?team=TeamB`

3. **MarketSentiment**: 1 call per game
   - `/lines?gameId=X`

**Total: 5 API calls per game analysis** (within our 150/day budget)

## Data Quality & Caching

### High-Value Data (Cache 1 hour):
- Advanced season stats (changes infrequently)
- Team recruiting rankings (static per year)

### Medium-Value Data (Cache 30 minutes):  
- Game schedules and results (mostly static)

### Live Data (Cache 5 minutes):
- Betting line movements (dynamic)

## Contrarian Opportunities Identified

1. **Hidden Fatigue Patterns**: Public doesn't track cumulative travel stress
2. **Advanced Metric Mismatches**: Success rate differentials more predictive than rankings
3. **Market Inefficiencies**: Sharp money moving against public perception

## Implementation Priority

1. **FIRST**: Add `/games` endpoint to cfbd_client.py
2. **SECOND**: Add `/lines` endpoint to cfbd_client.py  
3. **THIRD**: Enhanced advanced stats parsing (already have basics)

The CFBD API provides exceptionally rich data that the public doesn't analyze systematically - perfect for our contrarian approach!