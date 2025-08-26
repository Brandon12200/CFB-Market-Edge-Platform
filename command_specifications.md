# Command Feature Specifications

## Overview

Two new command features designed to enhance the usability of the CFB Contrarian Predictor by providing efficient ways to view team schedules and scan weekly matchups for contrarian opportunities.

## Command 1: Team Schedule Viewer

### Command Structure
```bash
python main.py --team-schedule TEAM_NAME [--year YEAR] [--format FORMAT]
```

### Purpose
Display a comprehensive schedule view for a single team, including past results, ATS performance, and upcoming games with current betting lines.

### Implementation Architecture

#### Module Structure
```
/schedule/
    __init__.py
    schedule_viewer.py      # Main schedule viewing logic
    schedule_formatter.py   # Output formatting
    ats_calculator.py      # ATS record calculation
```

#### Core Components

**1. ScheduleViewer Class**
```python
class ScheduleViewer:
    def __init__(self, data_manager, odds_client=None):
        self.data_manager = data_manager
        self.odds_client = odds_client
        self.cfbd_client = get_cfbd_client()
        
    def get_team_schedule(self, team: str, year: int = None) -> Dict[str, Any]:
        """
        Returns:
            {
                'team': normalized_team_name,
                'year': year,
                'games': [
                    {
                        'week': int,
                        'date': str,
                        'opponent': str,
                        'location': 'home'|'away'|'neutral',
                        'result': 'W'|'L'|None,
                        'score': {'team': int, 'opponent': int},
                        'spread': float,
                        'spread_result': 'W'|'L'|'P'|None,
                        'actual_margin': float,
                        'is_completed': bool
                    }
                ],
                'ats_record': {'wins': int, 'losses': int, 'pushes': int},
                'straight_record': {'wins': int, 'losses': int}
            }
        """
```

**2. Data Sources**

- **Past Games**: CFBD `/games` endpoint with team and year filters
- **Current Lines**: The Odds API for upcoming games
- **Fallback**: ESPN API for basic schedule if CFBD unavailable

**3. ATS Calculator Module**
```python
class ATSCalculator:
    @staticmethod
    def calculate_ats_result(team_score: int, opponent_score: int, 
                            spread: float, is_home: bool) -> str:
        """
        Calculate ATS result for a game.
        
        Args:
            spread: The spread from team's perspective (negative if favored)
            
        Returns:
            'W', 'L', 'P', or None if cannot determine
        """
        
    @staticmethod
    def compile_ats_record(games: List[Dict]) -> Dict[str, int]:
        """Returns {'wins': int, 'losses': int, 'pushes': int, 'percentage': float}"""
```

**4. Schedule Formatter**
```python
class ScheduleFormatter:
    @staticmethod
    def format_table(schedule_data: Dict, format_type: str = 'table') -> str:
        """
        Formats:
        - 'table': ASCII table format
        - 'json': JSON output
        - 'csv': CSV format
        - 'compact': Single-line per game
        """
    
    @staticmethod
    def format_game_line(game: Dict, team_name: str) -> str:
        """
        Format single game line:
        'Week 3:  @ Oregon           L 32-31   (Line: +3.5, ATS: W)'
        'Week 10: @ Northwestern     (Line: -28.0)'
        """
```

### API Optimization

- **Single CFBD Call**: `/games?year={year}&team={team}` gets entire season
- **Batch Odds Request**: Get all upcoming games' lines in one call if possible
- **Caching Strategy**: Cache completed games for 7 days, upcoming games for 1 hour

### Output Format Examples

**Default Table Format:**
```
Ohio State Buckeyes - 2024 Schedule
=====================================
Record: 8-1 (5-3-1 ATS, 62.5%)

Completed Games:
Week 1:  vs Akron            W 52-6    (Line: -49.0, ATS: W +3.0)
Week 2:  vs Western Michigan W 56-0    (Line: -38.5, ATS: W +17.5)
Week 3:  @ Oregon            L 32-31   (Line: +3.5, ATS: W +4.5)
...

Upcoming Games:
Week 10: @ Northwestern      (Line: -28.0)
Week 11: vs Purdue           (Line: -38.0)
Week 13: @ Michigan          (Line: -3.5)

ATS Performance by Spread:
  As Favorite: 3-3-1 (50.0%)
  As Underdog: 2-0 (100.0%)
  Double-digit: 2-3-1 (40.0%)
```

**Compact Format (--format compact):**
```
OSU | 8-1 (5-3-1 ATS) | Next: @NW -28.0 | Last 3 ATS: W-L-L
```

### Error Handling

- Team not found → Suggest similar teams using normalizer
- No schedule data → Fallback to ESPN, then error message
- Partial data → Show what's available with warning

---

## Command 2: Weekly Contrarian Scanner

### Command Structure
```bash
python main.py --scan-week [WEEK] [--min-edge EDGE] [--conference CONF] 
               [--top N] [--lite] [--export FILE]
```

### Purpose
Efficiently scan all games in a given week to identify potential contrarian opportunities without running full analysis on every game.

### Implementation Architecture

#### Module Structure
```
/scanner/
    __init__.py
    weekly_scanner.py       # Main scanning orchestration
    lite_predictor.py       # Lightweight prediction engine
    game_filter.py          # Filtering logic
    scanner_formatter.py    # Output formatting
    batch_optimizer.py      # API call optimization
```

#### Core Components

**1. WeeklyScanner Class**
```python
class WeeklyScanner:
    def __init__(self, prediction_engine, data_manager):
        self.prediction_engine = prediction_engine
        self.data_manager = data_manager
        self.lite_predictor = LitePredictor(data_manager)
        self.batch_optimizer = BatchOptimizer()
        
    def scan_week(self, week: int = None, 
                  min_edge: float = 1.5,
                  conference: str = None,
                  lite_mode: bool = True) -> Dict[str, Any]:
        """
        Returns:
            {
                'week': int,
                'total_games': int,
                'games_with_lines': int,
                'games_analyzed': int,
                'results': [
                    {
                        'home_team': str,
                        'away_team': str,
                        'vegas_spread': float,
                        'contrarian_spread': float,
                        'edge_size': float,
                        'edge_direction': str,
                        'signal_strength': str,  # 'STRONG', 'MODERATE', 'SLIGHT', None
                        'confidence': float,
                        'key_factors': [str],  # Top 3 contributing factors
                        'rank': int  # Ranking by edge size
                    }
                ],
                'summary': {
                    'strong_signals': int,
                    'moderate_signals': int,
                    'slight_signals': int,
                    'no_edge': int
                }
            }
        """
```

**2. Lite Predictor Module**
```python
class LitePredictor:
    """
    Lightweight prediction engine that uses cached data and simplified calculations.
    Only runs PRIMARY factors and skips expensive API calls.
    """
    
    # Factors to run in lite mode (high impact, low API cost)
    LITE_FACTORS = [
        'MarketSentiment',      # Uses cached line movement
        'ExperienceDifferential', # Uses cached coaching data
        'SchedulingFatigue',    # Basic calculation
        'DesperationIndex'      # Simple record-based
    ]
    
    def quick_predict(self, home_team: str, away_team: str, 
                     vegas_spread: float, context: Dict) -> Dict:
        """
        Returns simplified prediction with minimal API calls.
        Uses cached data where possible, skips advanced stats.
        """
```

**3. Batch Optimizer**
```python
class BatchOptimizer:
    """Optimizes API calls for multiple games."""
    
    def batch_fetch_games(self, week: int) -> List[Dict]:
        """Single API call to get all games for week."""
        
    def batch_fetch_lines(self, games: List[Dict]) -> Dict[str, float]:
        """Get all betting lines in minimal API calls."""
        
    def batch_cache_coaching(self, teams: List[str]) -> None:
        """Pre-cache all coaching data in one pass."""
```

**4. Game Filter**
```python
class GameFilter:
    """Modular filtering system for games."""
    
    @staticmethod
    def filter_by_conference(games: List[Dict], conference: str) -> List[Dict]:
        """Filter to specific conference games."""
        
    @staticmethod
    def filter_by_ranking(games: List[Dict], top_25_only: bool) -> List[Dict]:
        """Filter to games involving ranked teams."""
        
    @staticmethod
    def filter_fcs(games: List[Dict]) -> List[Dict]:
        """Remove FCS matchups."""
        
    @staticmethod
    def apply_filters(games: List[Dict], filters: Dict) -> List[Dict]:
        """Apply multiple filters in sequence."""
```

### Scanning Modes

**1. LITE Mode (Default)**
- Uses cached data primarily
- Runs 4-5 key factors only
- ~2 seconds per game
- 90% accuracy vs full analysis

**2. FULL Mode (--no-lite)**
- Runs complete factor analysis
- Fresh API calls for all data
- ~5 seconds per game
- 100% accuracy

**3. HYBRID Mode (Future)**
- Lite scan first, then full on top prospects
- Optimal balance of speed and accuracy

### Output Formats

**Default Table:**
```
Week 13 Contrarian Scanner
==================================================
Scanning 45 games... Found 38 with valid lines.

Rank  Matchup                        Vegas   Cont.  Edge   Signal   Conf
----  -----------------------------  ------  -----  -----  -------  ----
1.    Florida @ Florida State        +2.5    +5.1   2.6    STRONG   78%
2.    Ole Miss @ Mississippi State   -10.0   -7.5   2.5    STRONG   71%
3.    Clemson @ South Carolina       -2.5    -0.5   2.0    MODERATE 65%
4.    Michigan @ Ohio State          +3.5    +5.2   1.7    MODERATE 72%
5.    Washington @ Washington State  +1.5    +3.0   1.5    SLIGHT   61%

Summary: 2 STRONG | 2 MODERATE | 1 SLIGHT | 33 NO EDGE
```

**Compact Mode:**
```
Week 13: 5/38 games with edge>=1.5 | Best: UF@FSU +2.6 | Run: python main.py --home "Florida State" --away "Florida"
```

**Export Format (JSON):**
```json
{
  "week": 13,
  "scan_date": "2024-11-20T10:30:00",
  "parameters": {
    "min_edge": 1.5,
    "mode": "lite",
    "conference": null
  },
  "results": [
    {
      "rank": 1,
      "home_team": "Florida State",
      "away_team": "Florida",
      "vegas_spread": 2.5,
      "contrarian_spread": 5.1,
      "edge_size": 2.6,
      "signal_strength": "STRONG",
      "confidence": 0.78,
      "key_factors": ["MarketSentiment", "ExperienceDifferential", "Desperation"]
    }
  ]
}
```

### Performance Optimization

**API Call Reduction Strategy:**
1. **Batch all game fetching** - 1 call instead of 45
2. **Cache coaching data** - Reuse for 24 hours
3. **Skip advanced stats** in lite mode
4. **Parallel processing** - Process games concurrently where possible

**Expected Performance:**
- Lite mode: ~60 seconds for full week (45 games)
- Full mode: ~4 minutes for full week
- API calls: ~50 (lite) vs ~500 (full)

### Signal Classification

```python
def classify_signal_strength(edge_size: float) -> str:
    """
    Classify edge into signal strength categories.
    
    >= 3.0: STRONG
    >= 2.0: MODERATE  
    >= 1.5: SLIGHT
    < 1.5:  None
    """
    if edge_size >= 3.0:
        return 'STRONG'
    elif edge_size >= 2.0:
        return 'MODERATE'
    elif edge_size >= 1.5:
        return 'SLIGHT'
    else:
        return None
```

### CLI Integration

```python
# In main.py argument parser
parser.add_argument('--scan-week', type=int, nargs='?', const='current',
                   help='Scan all games in week for contrarian opportunities')
parser.add_argument('--min-edge', type=float, default=1.5,
                   help='Minimum edge size to display (default: 1.5)')
parser.add_argument('--lite', action='store_true', default=True,
                   help='Use lite mode for faster scanning')
parser.add_argument('--conference', type=str,
                   help='Filter to specific conference')
parser.add_argument('--top', type=int,
                   help='Show only top N opportunities')
parser.add_argument('--export', type=str,
                   help='Export results to file (json/csv)')
```

### Error Handling

- **No games found** → Check week number, show available weeks
- **No lines available** → Show games without lines separately
- **API limit reached** → Gracefully degrade to cached data only
- **Partial failures** → Continue with available data, note failures

### Future Enhancements (Not for Initial Implementation)

1. **Smart Caching** - Pre-cache likely queries during off-peak
2. **Progressive Loading** - Show results as they complete
3. **Historical Tracking** - Compare to previous week's edges
4. **Alert System** - Notify when strong signals detected
5. **Confidence Threshold** - Filter by confidence not just edge
6. **Multi-week Scan** - Scan rest of season in one command

## Implementation Priority

1. **Phase 1**: Implement ScheduleViewer with basic functionality
2. **Phase 2**: Implement WeeklyScanner in LITE mode only
3. **Phase 3**: Add filtering and export capabilities
4. **Phase 4**: Optimize batch operations and caching
5. **Phase 5**: Add FULL mode option for scanner

## Testing Considerations

### Unit Tests
- Schedule parsing with various data states
- ATS calculation edge cases (pushes, missing lines)
- Filter combinations
- Lite predictor accuracy vs full predictor

### Integration Tests
- API failure handling
- Cache behavior
- Large week scanning (bowl week with 40+ games)
- Conference-only scanning

### Performance Tests
- Lite mode under 2 seconds per game
- Full week scan under 90 seconds (lite mode)
- API call count verification

## Dependencies

### New Modules Needed
- None - builds on existing infrastructure

### Existing Modules to Modify
- `main.py` - Add new argument handlers
- `data_manager.py` - Add batch fetching methods if needed

### External Dependencies
- No new package requirements
- Uses existing CFBD, ESPN, and Odds API clients