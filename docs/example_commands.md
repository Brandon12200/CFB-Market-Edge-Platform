# CFB Contrarian Predictor - Example Commands

## How the System Works

The CFB Contrarian Predictor fetches **current week's games** from The Odds API automatically. You don't need to specify a week - it will:

1. **Auto-detect current week** based on available games
2. **Find your specified matchup** in the current week's slate
3. **Use live betting lines** for contrarian analysis

**Best Results**: Use teams that are actually playing each other in the current week for full contrarian edge detection with real Vegas spreads.

---

## Basic Commands

### Simple Predictions
```bash
# Basic prediction
python main.py --home georgia --away alabama

# With detailed factor breakdown
python main.py --home georgia --away alabama --show-factors

# Verbose mode (shows all behind-the-scenes work)
python main.py --home georgia --away alabama --verbose

# Combined options
python main.py --home georgia --away alabama --show-factors --verbose
```

### Team Name Variations
```bash
# Common abbreviations
python main.py --home uga --away bama
python main.py --home osu --away michigan
python main.py --home fsu --away miami

# Full official names
python main.py --home "Ohio State" --away "Michigan State"
python main.py --home "Notre Dame" --away "Southern California"
python main.py --home "Texas A&M" --away "Louisiana State"

# With mascots/full names
python main.py --home "Georgia Bulldogs" --away "Alabama Crimson Tide"
python main.py --home "University of Georgia" --away "University of Alabama"

# Mixed case (system handles this)
python main.py --home GEORGIA --away alabama
python main.py --home Georgia --away ALABAMA
```

---

## Conference Matchups

### SEC (Southeastern Conference)
```bash
# Classic SEC rivalries
python main.py --home georgia --away florida --show-factors
python main.py --home alabama --away auburn --verbose
python main.py --home texas --away oklahoma --show-factors
python main.py --home lsu --away alabama --show-factors

# Other SEC matchups
python main.py --home georgia --away tennessee
python main.py --home florida --away kentucky
python main.py --home "south carolina" --away missouri
python main.py --home arkansas --away "mississippi state"
python main.py --home vanderbilt --away "ole miss"
```

### Big Ten
```bash
# The Game and other classics
python main.py --home "ohio state" --away michigan --show-factors
python main.py --home michigan --away "michigan state" --verbose
python main.py --home penn --away "ohio state" --show-factors

# Other Big Ten
python main.py --home wisconsin --away iowa
python main.py --home nebraska --away colorado
python main.py --home illinois --away northwestern
python main.py --home purdue --away indiana
python main.py --home minnesota --away maryland
```

### ACC (Atlantic Coast Conference)
```bash
# ACC rivalries
python main.py --home clemson --away "florida state" --show-factors
python main.py --home miami --away "virginia tech" --verbose
python main.py --home "north carolina" --away duke --show-factors

# Other ACC
python main.py --home "wake forest" --away "nc state"
python main.py --home virginia --away "virginia tech"
python main.py --home syracuse --away "boston college"
python main.py --home "georgia tech" --away clemson
```

### Big 12
```bash
# Big 12 classics
python main.py --home kansas --away "kansas state" --show-factors
python main.py --home "oklahoma state" --away oklahoma --verbose
python main.py --home tcu --away baylor --show-factors

# Other Big 12
python main.py --home "iowa state" --away "west virginia"
python main.py --home "texas tech" --away "texas christian"
```

### Pac-12 / West Coast
```bash
# West Coast rivalries
python main.py --home oregon --away washington --show-factors
python main.py --home stanford --away cal --verbose
python main.py --home usc --away ucla --show-factors

# Other West Coast
python main.py --home "washington state" --away oregon
python main.py --home "oregon state" --away stanford
python main.py --home arizona --away "arizona state"
```

---

## Factor-Testing Scenarios

### Coaching Experience Differentials
```bash
# Experienced vs newer coaches
python main.py --home alabama --away vanderbilt --show-factors
python main.py --home georgia --away "south carolina" --verbose
python main.py --home clemson --away "wake forest" --show-factors
python main.py --home "ohio state" --away purdue --verbose
```

### Revenge Game Scenarios
```bash
# Test revenge factor detection
python main.py --home georgia --away alabama --show-factors
python main.py --home michigan --away "ohio state" --verbose
python main.py --home auburn --away alabama --show-factors
python main.py --home "florida state" --away miami --verbose
```

### Desperation/Stakes Games
```bash
# Conference championship implications
python main.py --home michigan --away "ohio state" --show-factors
python main.py --home oregon --away washington --verbose
python main.py --home georgia --away alabama --show-factors
python main.py --home clemson --away "florida state" --verbose
```

### Home Field Advantage Testing
```bash
# Strong home field advantages
python main.py --home "penn state" --away "ohio state" --show-factors
python main.py --home clemson --away miami --verbose
python main.py --home "texas a&m" --away alabama --show-factors
python main.py --home oregon --away usc --verbose
```

---

## Weekly Analysis

### Analyze Current Week
```bash
# See all available games this week (current week)
python main.py --analyze-week

# Filter for meaningful edges only
python main.py --analyze-week --min-edge 1.5

# Filter for strong edges only
python main.py --analyze-week --min-edge 3.0

# Show all games with factor details
python main.py --analyze-week --show-factors
```

### Specific Week Analysis
```bash
# Analyze specific week (if available)
python main.py --analyze-week --week 1
python main.py --analyze-week --week 8 --min-edge 2.0
python main.py --analyze-week --week 12 --show-factors
```

---

## Testing & Validation Commands

### Error Handling Tests
```bash
# Invalid team names (should handle gracefully)
python main.py --home "invalid team" --away alabama
python main.py --home georgia --away "fake team"
python main.py --home "xyz" --away "abc"

# Same team for both (should reject)
python main.py --home georgia --away georgia
python main.py --home alabama --away alabama

# Empty inputs (should handle gracefully)
python main.py --home "" --away alabama
python main.py --home georgia --away ""
```

### Performance Testing
```bash
# Time execution
time python main.py --home georgia --away alabama
time python main.py --home georgia --away alabama --verbose
time python main.py --home georgia --away alabama --show-factors

# Multiple quick tests
python main.py --home georgia --away alabama && \
python main.py --home michigan --away "ohio state" && \
python main.py --home clemson --away "florida state"
```

### Team Normalizer Testing
```bash
# Test various input formats
python main.py --home "Univ of Georgia" --away "Univ of Alabama"
python main.py --home "GA Bulldogs" --away "AL Crimson Tide"
python main.py --home "UGA" --away "BAMA"
python main.py --home "georgia tech" --away "georgia state"

# Test edge cases
python main.py --home "Miami FL" --away "Miami OH"
python main.py --home "USC" --away "South Carolina"
python main.py --home "OSU" --away "Oklahoma State"
```

---

## System Diagnostics

### Health Checks
```bash
# Quick system health
python -c "from utils.health_check import health_checker; import json; print(json.dumps(health_checker.quick_health_check(), indent=2))"

# Full system health check
python -c "from utils.health_check import health_checker; import json; result = health_checker.run_full_health_check(); print('Status:', result['overall_status']); [print(f'{k}: {v[\"status\"]}') for k,v in result['components'].items()]"

# Test specific components
python -c "from normalizer import normalizer; print('Normalizer test:', normalizer.normalize('georgia'))"
python -c "from config import config; print('API configured:', bool(config.odds_api_key))"
```

### Performance Monitoring
```bash
# System performance summary
python -c "from utils.monitoring import system_monitor; summary = system_monitor.get_performance_summary(); print(f'Predictions: {summary.get(\"total_predictions\", 0)}, Avg time: {summary.get(\"avg_prediction_time\", 0):.3f}s')"

# Detailed performance metrics
python -c "from utils.monitoring import system_monitor; import json; print(json.dumps(system_monitor.get_performance_summary(), indent=2))"
```

### Factor Registry Validation
```bash
# Check factor loading
python -c "from factors.factor_registry import factor_registry; validation = factor_registry.validate_factor_configuration(); print('Factors valid:', validation.get('valid')); print('Loaded factors:', len(factor_registry.factors) if hasattr(factor_registry, 'factors') else 0)"

# Test factor calculations
python -c "from factors.factor_registry import factor_registry; result = factor_registry.calculate_all_factors('GEORGIA', 'ALABAMA', {}); print('Successful factors:', result['summary']['factors_successful'], '/', result['summary']['factors_calculated'])"
```

---

## Finding Current Games

To see what games are available for testing with real spreads:

```bash
# See all current week games
python main.py --analyze-week

# This will show output like:
# "Georgia Bulldogs vs Alabama Crimson Tide: Georgia -3.5"
# Then use: python main.py --home georgia --away alabama
```

---

## Command Line Options Reference

| Option | Description | Example |
|--------|-------------|---------|
| `--home TEAM` | Home team name (required) | `--home georgia` |
| `--away TEAM` | Away team name (required) | `--away alabama` |
| `--week N` | Specific week number | `--week 8` |
| `--show-factors` | Show detailed factor breakdown | |
| `--verbose` | Show detailed execution info | |
| `--analyze-week [N]` | Analyze all games in current week | `--analyze-week` or `--analyze-week 8` |
| `--min-edge N` | Filter results by minimum edge size | `--min-edge 2.0` |

## Important Notes

**Current Status**: The system is working great for teams that have actual Vegas spreads available this week. Some edge cases with teams that don't have current betting lines are still being refined.

**Best Results**: Use teams that are actually playing each other in the current week, as these will have real betting lines for full contrarian analysis.

**Quick Start**: Run `python main.py --analyze-week` first to see what games are available, then test with those matchups.

---

## Pro Tips

1. **Start with current week games**: Use `--analyze-week` first to see available matchups
2. **Use real matchups**: Teams actually playing each other give the best results
3. **Test different name formats**: The normalizer handles many variations
4. **Use --show-factors**: See which factors are driving the prediction
5. **Use --verbose**: Understand what data is being used
6. **Check performance**: Use `time` command to measure execution speed

## Sample Output to Expect

### Strong Contrarian Edge
```
🎯 STRONG CONTRARIAN OPPORTUNITY: GEORGIA vs ALABAMA
Vegas Spread: GEORGIA -3.5
Contrarian Prediction: GEORGIA -6.2
Edge Size: 2.7 points
Confidence: High (78.2%)
Recommendation: CONSIDER GEORGIA -6.2
```

### No Edge Detected
```
⚪ NO CLEAR EDGE: ALABAMA vs GEORGIA  
Vegas Spread: ALABAMA -4.0
Contrarian Prediction: ALABAMA -4.1
Edge Size: 0.1 points
Confidence: Medium (62.1%)
Recommendation: PASS - No meaningful opportunity
```

Happy testing! 🏈