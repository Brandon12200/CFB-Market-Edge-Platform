"""
Momentum factors for CFB Contrarian Predictor.
Implements the three momentum-based factors that comprise 20% of prediction weight.
"""

from typing import Dict, Any, Tuple, Optional, List
import logging
import statistics
from datetime import datetime, timedelta

from factors.base_calculator import BaseFactorCalculator


class ATSRecentFormCalculator(BaseFactorCalculator):
    """
    Calculate Against The Spread (ATS) recent form momentum.
    
    Analyzes team performance against betting spreads in recent games
    to identify hot/cold streaks that may not be reflected in current lines.
    """
    
    def __init__(self):
        super().__init__()
        self.weight = 0.07  # 7% of total (35% of momentum's 20%)
        self.category = "momentum_factors"
        self.description = "Against The Spread recent form analysis"
        self._min_output = -2.0
        self._max_output = 2.0
        
        # Configuration
        self.config = {
            'recent_games_window': 4,  # Number of recent games to analyze
            'ats_weights': {
                'last_game': 0.4,
                'second_last': 0.3,
                'third_last': 0.2,
                'fourth_last': 0.1
            },
            'streak_bonus': {
                'cover_streak_3': 0.5,
                'fail_streak_3': -0.5,
                'cover_streak_4': 0.8,
                'fail_streak_4': -0.8
            },
            'margin_thresholds': {
                'blowout_cover': 14,  # Points beyond spread for blowout cover
                'close_miss': 3       # Points within spread for close miss
            }
        }
    
    def calculate(self, home_team: str, away_team: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate ATS recent form factor."""
        if not context:
            return 0.0
        
        home_data = context.get('home_team_data', {})
        away_data = context.get('away_team_data', {})
        
        # Calculate ATS momentum for each team
        home_ats_momentum = self._calculate_team_ats_momentum(home_data)
        away_ats_momentum = self._calculate_team_ats_momentum(away_data)
        
        # Calculate momentum differential (positive favors home team)
        momentum_diff = home_ats_momentum - away_ats_momentum
        
        return self.validate_output(momentum_diff)
    
    def _calculate_team_ats_momentum(self, team_data: Dict) -> float:
        """Calculate ATS momentum score for a team."""
        # Get recent games from schedule
        schedule = team_data.get('schedule', [])
        if not schedule:
            return 0.0
        
        # Filter to completed games and get most recent
        completed_games = [g for g in schedule if g.get('completed', False)]
        if not completed_games:
            return 0.0
        
        # Sort by date (most recent first) and take recent games window
        completed_games.sort(key=lambda x: x.get('date', ''), reverse=True)
        recent_games = completed_games[:self.config['recent_games_window']]
        
        if len(recent_games) < 2:
            return 0.0  # Need at least 2 games for trend analysis
        
        # Calculate ATS performance for recent games
        ats_results = []
        for game in recent_games:
            ats_result = self._calculate_game_ats_performance(game, team_data)
            if ats_result is not None:
                ats_results.append(ats_result)
        
        if not ats_results:
            return 0.0
        
        # Calculate weighted ATS momentum
        momentum_score = self._calculate_weighted_ats_momentum(ats_results)
        
        # Add streak bonuses
        streak_bonus = self._calculate_streak_bonus(ats_results)
        momentum_score += streak_bonus
        
        return momentum_score
    
    def _calculate_game_ats_performance(self, game: Dict, team_data: Dict) -> Optional[float]:
        """Calculate ATS performance for a single game."""
        # This is a simplified calculation since we don't have historical spreads
        # In practice, this would compare actual margin vs betting spread
        
        team_score = game.get('team_score')
        opponent_score = game.get('opponent_score')
        is_home = game.get('is_home_game', False)
        
        if team_score is None or opponent_score is None:
            return None
        
        # Calculate actual margin
        actual_margin = team_score - opponent_score
        if not is_home:
            actual_margin = -actual_margin  # Adjust for away games
        
        # Estimate historical spread (simplified)
        estimated_spread = self._estimate_historical_spread(game, team_data)
        
        # Calculate ATS margin (actual vs spread)
        ats_margin = actual_margin - estimated_spread
        
        # Convert to ATS performance score (-1.0 to 1.0)
        if ats_margin > self.config['margin_thresholds']['blowout_cover']:
            return 1.0  # Blowout cover
        elif ats_margin > 0:
            return 0.6  # Regular cover
        elif ats_margin > -self.config['margin_thresholds']['close_miss']:
            return -0.3  # Close miss
        else:
            return -1.0  # Failed to cover
    
    def _estimate_historical_spread(self, game: Dict, team_data: Dict) -> float:
        """Estimate what the spread might have been for a historical game."""
        # Simplified estimation based on home field advantage and score differential
        is_home = game.get('is_home_game', False)
        
        # Basic home field advantage
        estimated_spread = 3.0 if is_home else -3.0
        
        # This would ideally use team strength ratings, historical spreads, etc.
        # For now, return basic home field advantage
        return estimated_spread
    
    def _calculate_weighted_ats_momentum(self, ats_results: List[float]) -> float:
        """Calculate weighted ATS momentum from recent results."""
        if not ats_results:
            return 0.0
        
        weights = list(self.config['ats_weights'].values())[:len(ats_results)]
        
        # Calculate weighted average
        weighted_sum = sum(result * weight for result, weight in zip(ats_results, weights))
        total_weight = sum(weights)
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def _calculate_streak_bonus(self, ats_results: List[float]) -> float:
        """Calculate bonus for ATS streaks."""
        if len(ats_results) < 3:
            return 0.0
        
        # Check for covering streaks (positive results)
        cover_streak = 0
        fail_streak = 0
        
        for result in ats_results:
            if result > 0:
                cover_streak += 1
                fail_streak = 0
            else:
                fail_streak += 1
                cover_streak = 0
        
        # Apply streak bonuses
        if cover_streak >= 4:
            return self.config['streak_bonus']['cover_streak_4']
        elif cover_streak >= 3:
            return self.config['streak_bonus']['cover_streak_3']
        elif fail_streak >= 4:
            return self.config['streak_bonus']['fail_streak_4']
        elif fail_streak >= 3:
            return self.config['streak_bonus']['fail_streak_3']
        
        return 0.0
    
    def get_output_range(self) -> Tuple[float, float]:
        """Get output range for ATS recent form."""
        return (self._min_output, self._max_output)
    
    def get_explanation(self, home_team: str, away_team: str, value: float, 
                       context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate explanation for ATS recent form factor."""
        if abs(value) < 0.2:
            return "Similar ATS momentum for both teams"
        
        hot_team = home_team if value > 0 else away_team
        cold_team = away_team if value > 0 else home_team
        
        if abs(value) > 1.0:
            return f"{hot_team} has strong ATS momentum vs {cold_team}"
        else:
            return f"{hot_team} has slight ATS momentum edge"
    
    def get_required_data(self) -> Dict[str, bool]:
        """ATS analysis benefits from schedule data."""
        return {
            'team_info': False,
            'coaching_data': False,
            'team_stats': False,
            'schedule_data': True,  # Required for recent game analysis
            'betting_data': False,
            'historical_data': False
        }


class PointDifferentialTrendsCalculator(BaseFactorCalculator):
    """
    Calculate point differential trends momentum.
    
    Analyzes recent scoring margins compared to season averages to identify
    teams trending up or down in performance.
    """
    
    def __init__(self):
        super().__init__()
        self.weight = 0.07  # 7% of total (35% of momentum's 20%)
        self.category = "momentum_factors"
        self.description = "Point differential trends analysis"
        self._min_output = -2.0
        self._max_output = 2.0
        
        # Configuration
        self.config = {
            'recent_games_window': 4,
            'trend_weights': {
                'last_game': 0.4,
                'second_last': 0.3,
                'third_last': 0.2,
                'fourth_last': 0.1
            },
            'improvement_thresholds': {
                'significant_improvement': 10,  # Point improvement for significant trend
                'moderate_improvement': 5,
                'decline_threshold': -5
            },
            'consistency_bonus': 0.3  # Bonus for consistent performance
        }
    
    def calculate(self, home_team: str, away_team: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate point differential trends factor."""
        if not context:
            return 0.0
        
        home_data = context.get('home_team_data', {})
        away_data = context.get('away_team_data', {})
        
        # Calculate differential trends for each team
        home_trend = self._calculate_team_differential_trend(home_data)
        away_trend = self._calculate_team_differential_trend(away_data)
        
        # Calculate trend differential (positive favors home team)
        trend_diff = home_trend - away_trend
        
        return self.validate_output(trend_diff)
    
    def _calculate_team_differential_trend(self, team_data: Dict) -> float:
        """Calculate point differential trend for a team."""
        schedule = team_data.get('schedule', [])
        if not schedule:
            return 0.0
        
        # Get completed games
        completed_games = [g for g in schedule if g.get('completed', False)]
        if len(completed_games) < 3:
            return 0.0  # Need at least 3 games for trend analysis
        
        # Sort by date and calculate point differentials
        completed_games.sort(key=lambda x: x.get('date', ''))
        
        # Calculate season average differential
        season_differentials = []
        for game in completed_games:
            differential = self._calculate_game_differential(game)
            if differential is not None:
                season_differentials.append(differential)
        
        if len(season_differentials) < 3:
            return 0.0
        
        season_avg = statistics.mean(season_differentials)
        
        # Calculate recent games trend
        recent_games = completed_games[-self.config['recent_games_window']:]
        recent_differentials = []
        
        for game in recent_games:
            differential = self._calculate_game_differential(game)
            if differential is not None:
                recent_differentials.append(differential)
        
        if not recent_differentials:
            return 0.0
        
        # Calculate weighted recent average
        recent_avg = self._calculate_weighted_recent_average(recent_differentials)
        
        # Calculate trend (recent vs season)
        trend_improvement = recent_avg - season_avg
        
        # Scale and add consistency bonus
        trend_score = self._scale_trend_improvement(trend_improvement)
        consistency_bonus = self._calculate_consistency_bonus(recent_differentials)
        
        return trend_score + consistency_bonus
    
    def _calculate_game_differential(self, game: Dict) -> Optional[float]:
        """Calculate point differential for a single game."""
        team_score = game.get('team_score')
        opponent_score = game.get('opponent_score')
        
        if team_score is None or opponent_score is None:
            return None
        
        return float(team_score - opponent_score)
    
    def _calculate_weighted_recent_average(self, differentials: List[float]) -> float:
        """Calculate weighted average of recent differentials."""
        if not differentials:
            return 0.0
        
        weights = list(self.config['trend_weights'].values())[:len(differentials)]
        
        # Reverse weights since differentials are in chronological order
        weights = weights[::-1]
        
        weighted_sum = sum(diff * weight for diff, weight in zip(differentials, weights))
        total_weight = sum(weights)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _scale_trend_improvement(self, improvement: float) -> float:
        """Scale trend improvement to factor output range."""
        if improvement >= self.config['improvement_thresholds']['significant_improvement']:
            return 1.5  # Strong positive trend
        elif improvement >= self.config['improvement_thresholds']['moderate_improvement']:
            return 1.0  # Moderate positive trend
        elif improvement <= self.config['improvement_thresholds']['decline_threshold']:
            return -1.0  # Negative trend
        else:
            # Linear scaling between thresholds
            return improvement / 10.0  # Scale to reasonable range
    
    def _calculate_consistency_bonus(self, differentials: List[float]) -> float:
        """Calculate bonus for consistent performance."""
        if len(differentials) < 3:
            return 0.0
        
        # Calculate standard deviation (lower = more consistent)
        std_dev = statistics.stdev(differentials)
        
        # Bonus for low standard deviation (consistent performance)
        if std_dev < 7:  # Very consistent
            return self.config['consistency_bonus']
        elif std_dev < 14:  # Moderately consistent
            return self.config['consistency_bonus'] * 0.5
        else:
            return 0.0  # Inconsistent performance
    
    def get_output_range(self) -> Tuple[float, float]:
        """Get output range for point differential trends."""
        return (self._min_output, self._max_output)
    
    def get_explanation(self, home_team: str, away_team: str, value: float, 
                       context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate explanation for point differential trends factor."""
        if abs(value) < 0.2:
            return "Similar scoring trends for both teams"
        
        trending_team = home_team if value > 0 else away_team
        
        if abs(value) > 1.0:
            return f"{trending_team} showing strong recent scoring improvement"
        else:
            return f"{trending_team} trending upward in point differential"
    
    def get_required_data(self) -> Dict[str, bool]:
        """Point differential trends require schedule data."""
        return {
            'team_info': False,
            'coaching_data': False,
            'team_stats': False,
            'schedule_data': True,  # Required for game-by-game analysis
            'betting_data': False,
            'historical_data': False
        }


class CloseGamePerformanceCalculator(BaseFactorCalculator):
    """
    Calculate close game performance momentum.
    
    Analyzes how teams perform in clutch situations (games decided by 7 points or less)
    to identify teams with strong/weak late-game execution.
    """
    
    def __init__(self):
        super().__init__()
        self.weight = 0.06  # 6% of total (30% of momentum's 20%)
        self.category = "momentum_factors"
        self.description = "Close game performance and clutch factor analysis"
        self._min_output = -1.5
        self._max_output = 1.5
        
        # Configuration
        self.config = {
            'close_game_threshold': 7,  # Points for close game definition
            'recent_games_window': 6,   # Look at more games for close game sample
            'clutch_weights': {
                'win_close_game': 1.0,
                'lose_close_game': -0.7,
                'blowout_win': 0.3,
                'blowout_loss': -0.3
            },
            'experience_multiplier': 1.2,  # Bonus for teams with close game experience
            'min_close_games': 2  # Minimum close games for meaningful analysis
        }
    
    def calculate(self, home_team: str, away_team: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate close game performance factor."""
        if not context:
            return 0.0
        
        home_data = context.get('home_team_data', {})
        away_data = context.get('away_team_data', {})
        
        # Calculate close game performance for each team
        home_clutch = self._calculate_team_clutch_performance(home_data)
        away_clutch = self._calculate_team_clutch_performance(away_data)
        
        # Calculate clutch differential (positive favors home team)
        clutch_diff = home_clutch - away_clutch
        
        return self.validate_output(clutch_diff)
    
    def _calculate_team_clutch_performance(self, team_data: Dict) -> float:
        """Calculate clutch performance score for a team."""
        schedule = team_data.get('schedule', [])
        if not schedule:
            return 0.0
        
        # Get completed games
        completed_games = [g for g in schedule if g.get('completed', False)]
        if not completed_games:
            return 0.0
        
        # Analyze recent games for close game performance
        recent_games = completed_games[-self.config['recent_games_window']:]
        
        close_games = []
        blowout_games = []
        
        for game in recent_games:
            game_analysis = self._analyze_game_closeness(game)
            if game_analysis:
                if game_analysis['is_close']:
                    close_games.append(game_analysis)
                else:
                    blowout_games.append(game_analysis)
        
        # Calculate clutch score
        clutch_score = 0.0
        
        # Close game performance (heavily weighted)
        if len(close_games) >= self.config['min_close_games']:
            close_game_score = self._calculate_close_game_score(close_games)
            clutch_score += close_game_score * 0.8
            
            # Experience bonus for teams that play in close games
            experience_bonus = min(len(close_games) / 4, 1.0) * 0.2
            clutch_score += experience_bonus
        
        # Blowout game context (lightly weighted)
        if blowout_games:
            blowout_score = self._calculate_blowout_score(blowout_games)
            clutch_score += blowout_score * 0.2
        
        return clutch_score
    
    def _analyze_game_closeness(self, game: Dict) -> Optional[Dict[str, Any]]:
        """Analyze whether a game was close and the outcome."""
        team_score = game.get('team_score')
        opponent_score = game.get('opponent_score')
        result = game.get('result')
        
        if team_score is None or opponent_score is None:
            return None
        
        point_differential = abs(team_score - opponent_score)
        is_close = point_differential <= self.config['close_game_threshold']
        
        return {
            'is_close': is_close,
            'point_differential': point_differential,
            'result': result,
            'team_score': team_score,
            'opponent_score': opponent_score
        }
    
    def _calculate_close_game_score(self, close_games: List[Dict]) -> float:
        """Calculate score based on close game results."""
        if not close_games:
            return 0.0
        
        total_score = 0.0
        for game in close_games:
            if game['result'] == 'W':
                total_score += self.config['clutch_weights']['win_close_game']
            elif game['result'] == 'L':
                total_score += self.config['clutch_weights']['lose_close_game']
        
        # Average score per close game
        return total_score / len(close_games)
    
    def _calculate_blowout_score(self, blowout_games: List[Dict]) -> float:
        """Calculate score based on blowout game results."""
        if not blowout_games:
            return 0.0
        
        total_score = 0.0
        for game in blowout_games:
            if game['result'] == 'W':
                total_score += self.config['clutch_weights']['blowout_win']
            elif game['result'] == 'L':
                total_score += self.config['clutch_weights']['blowout_loss']
        
        # Average score per blowout game
        return total_score / len(blowout_games)
    
    def get_output_range(self) -> Tuple[float, float]:
        """Get output range for close game performance."""
        return (self._min_output, self._max_output)
    
    def get_explanation(self, home_team: str, away_team: str, value: float, 
                       context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate explanation for close game performance factor."""
        if abs(value) < 0.1:
            return "Similar clutch performance for both teams"
        
        clutch_team = home_team if value > 0 else away_team
        
        if abs(value) > 0.8:
            return f"{clutch_team} excels in close games and clutch situations"
        else:
            return f"{clutch_team} has slight edge in close game performance"
    
    def get_required_data(self) -> Dict[str, bool]:
        """Close game performance requires schedule data."""
        return {
            'team_info': False,
            'coaching_data': False,
            'team_stats': False,
            'schedule_data': True,  # Required for game result analysis
            'betting_data': False,
            'historical_data': False
        }