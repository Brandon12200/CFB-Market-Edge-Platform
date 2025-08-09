"""
Market Sentiment Divergence - MODIFIER contrarian factor.

Detects when sharp money moves against public betting patterns.
Reverse line movement and steam moves indicate informed betting
that contradicts recreational money flow.
"""

from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime, timedelta
import logging
from factors.base_calculator import BaseFactorCalculator, FactorType, FactorConfidence
from data.cfbd_client import get_cfbd_client
# from data.odds_client import get_odds_client  # TODO: Add when odds client has get_odds_client function


class MarketSentimentCalculator(BaseFactorCalculator):
    """
    Identifies sharp vs public money divergence in betting markets.
    
    Contrarian insight: When line movement opposes public betting percentages,
    sharp money is taking a position against recreational bettors. This creates
    opportunities to fade the public and follow professional money.
    """
    
    def __init__(self):
        super().__init__()
        
        # MODIFIER factor: 100% of MODIFIER category's 10% = 10% total weight
        self.weight = 1.0
        self.category = "situational_context"
        self.description = "Detects sharp money moving against public sentiment"
        
        # Output range for this factor (multiplicative modifier)
        self._min_output = 0.5   # Can reduce adjustment by 50%
        self._max_output = 1.5   # Can amplify adjustment by 50%
        
        # Hierarchical system configuration
        self.factor_type = FactorType.MODIFIER
        self.activation_threshold = 0.1  # Low threshold for modifiers
        self.max_impact = 2.5  # Maximum points impact after multiplication
        
        # Factor-specific parameters
        self.config = {
            'reverse_movement_threshold': 0.7,    # 70% public on one side
            'line_move_threshold': 0.5,          # Half point line movement
            'steam_move_threshold': 1.0,         # 1 point rapid movement
            'steam_time_window': 6,              # Hours for steam move detection
            'sharp_indicator_weight': 0.4,       # Weight for sharp indicators
            'public_fade_weight': 0.3,           # Weight for fading public
            'line_freeze_signal': 0.2            # Weight for suspicious line freezes
        }
        
        self.cfbd_client = get_cfbd_client()
        self.odds_client = None  # get_odds_client()  # TODO: Enable when available
    
    def calculate(self, home_team: str, away_team: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate market sentiment modifier.
        
        Returns a multiplier (0.5 to 1.5) that modifies other adjustments.
        1.0 = neutral, >1.0 amplifies contrarian signal, <1.0 reduces it.
        """
        if not context:
            return 1.0  # Neutral modifier if no context
        
        # Get current vegas spread from context
        vegas_spread = context.get('vegas_spread', 0)
        if not vegas_spread:
            return 1.0  # Can't analyze without spread
        
        # Analyze betting patterns
        reverse_signal = self._detect_reverse_line_movement(home_team, away_team, vegas_spread, context)
        steam_signal = self._detect_steam_moves(home_team, away_team, context)
        public_fade = self._analyze_public_betting(home_team, away_team, context)
        line_freeze = self._detect_line_freeze(vegas_spread, context)
        
        # Combine signals
        total_signal = (
            reverse_signal * self.config['sharp_indicator_weight'] +
            steam_signal * self.config['sharp_indicator_weight'] +
            public_fade * self.config['public_fade_weight'] +
            line_freeze * self.config['line_freeze_signal']
        )
        
        # Convert to modifier (centered at 1.0)
        modifier = 1.0 + (total_signal * 0.5)  # Scale to 0.5-1.5 range
        
        # Log significant market sentiment
        if abs(modifier - 1.0) > 0.2:
            self.logger.info(f"Market sentiment detected: {home_team} vs {away_team}")
            self.logger.info(f"  Reverse: {reverse_signal:.2f}, Steam: {steam_signal:.2f}")
            self.logger.info(f"  Public fade: {public_fade:.2f}, Modifier: {modifier:.2f}")
        
        # Ensure within bounds
        return max(self._min_output, min(self._max_output, modifier))
    
    def _detect_reverse_line_movement(self, home_team: str, away_team: str, 
                                     current_spread: float, context: Dict) -> float:
        """
        Detect when line moves opposite to public betting.
        Strong contrarian signal when public heavy on one side but line moves other way.
        """
        try:
            if not self.cfbd_client:
                return 0.0
            
            year = context.get('year', 2024)
            week = context.get('week', 1)
            
            # Get betting lines history
            lines = self.cfbd_client.get_betting_lines(year=year, week=week)
            
            # Find this game's lines
            game_lines = None
            for game in lines:
                if (game.get('homeTeam', '').lower() == home_team.lower() and 
                    game.get('awayTeam', '').lower() == away_team.lower()):
                    game_lines = game.get('lines', [])
                    break
            
            if not game_lines:
                return 0.0
            
            # Check for line movement
            opening_spread = None
            current_spread_from_api = None
            
            for line in game_lines:
                if line.get('spreadOpen'):
                    opening_spread = line['spreadOpen']
                if line.get('spread'):
                    current_spread_from_api = line['spread']
            
            if opening_spread is None or current_spread_from_api is None:
                return 0.0
            
            line_movement = current_spread_from_api - opening_spread
            
            # Get public betting percentage (would need odds API integration)
            public_on_favorite = self._get_public_betting_percentage(home_team, away_team, context)
            
            # Reverse line movement detection
            if public_on_favorite > self.config['reverse_movement_threshold']:
                # Public heavy on favorite but line moved toward dog
                if abs(line_movement) > self.config['line_move_threshold']:
                    if (public_on_favorite > 0.7 and line_movement > 0) or \
                       (public_on_favorite < 0.3 and line_movement < 0):
                        return 1.0  # Strong reverse signal
            
            # Moderate reverse movement
            if abs(line_movement) > self.config['line_move_threshold'] * 0.5:
                if (public_on_favorite > 0.6 and line_movement > 0) or \
                   (public_on_favorite < 0.4 and line_movement < 0):
                    return 0.5  # Moderate reverse signal
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error detecting reverse line movement: {e}")
            return 0.0
    
    def _detect_steam_moves(self, home_team: str, away_team: str, context: Dict) -> float:
        """
        Detect rapid line movement indicating sharp action.
        Steam moves show professional money hitting a number hard.
        """
        try:
            # This would require timestamp data on line movements
            # For now, we'll detect large line movements as proxy
            if not self.cfbd_client:
                return 0.0
            
            year = context.get('year', 2024)
            week = context.get('week', 1)
            
            lines = self.cfbd_client.get_betting_lines(year=year, week=week)
            
            for game in lines:
                if (game.get('homeTeam', '').lower() == home_team.lower() and 
                    game.get('awayTeam', '').lower() == away_team.lower()):
                    
                    game_lines = game.get('lines', [])
                    if not game_lines:
                        return 0.0
                    
                    # Check for significant movement across books
                    spreads = [l.get('spread') for l in game_lines if l.get('spread')]
                    if len(spreads) > 1:
                        spread_range = max(spreads) - min(spreads)
                        
                        # Large discrepancy suggests steam move in progress
                        if spread_range > self.config['steam_move_threshold']:
                            return 1.0  # Steam move detected
                        elif spread_range > self.config['steam_move_threshold'] * 0.5:
                            return 0.5  # Moderate movement
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error detecting steam moves: {e}")
            return 0.0
    
    def _analyze_public_betting(self, home_team: str, away_team: str, context: Dict) -> float:
        """
        Analyze public betting patterns to identify fade opportunities.
        Heavy public action on one side often indicates value on the other.
        """
        try:
            # Get public betting percentage
            public_pct = self._get_public_betting_percentage(home_team, away_team, context)
            
            # Extreme public betting creates fade opportunity
            if public_pct > 0.75:
                return 1.0  # Fade heavy public on favorite
            elif public_pct > 0.65:
                return 0.5  # Moderate public lean
            elif public_pct < 0.25:
                return 1.0  # Fade heavy public on underdog
            elif public_pct < 0.35:
                return 0.5  # Moderate public lean
            
            return 0.0  # Balanced public action
            
        except Exception as e:
            self.logger.error(f"Error analyzing public betting: {e}")
            return 0.0
    
    def _get_public_betting_percentage(self, home_team: str, away_team: str, context: Dict) -> float:
        """
        Get public betting percentage on the favorite.
        This would integrate with odds API or scraping service.
        """
        # Placeholder - would need real data source
        # For now, return neutral 50%
        if self.odds_client:
            try:
                # This would call the odds API for public betting data
                # public_data = self.odds_client.get_public_betting(home_team, away_team)
                # return public_data.get('favorite_percentage', 0.5)
                pass
            except:
                pass
        
        return 0.5  # Default neutral
    
    def _detect_line_freeze(self, current_spread: float, context: Dict) -> float:
        """
        Detect suspicious line freezes despite heavy action.
        When lines don't move despite lopsided betting, books may know something.
        """
        # This would require historical line movement data
        # A frozen line with heavy public action suggests trap game
        
        # Placeholder logic
        if abs(current_spread) > 14:  # Large spread
            # Large spreads that don't move are suspicious
            return 0.3
        
        return 0.0
    
    def calculate_with_confidence(self, home_team: str, away_team: str, 
                                 context: Optional[Dict[str, Any]] = None) -> Tuple[float, FactorConfidence, List[str]]:
        """Calculate with confidence scoring."""
        value = self.calculate(home_team, away_team, context)
        reasoning = []
        
        if not context:
            return value, FactorConfidence.NONE, ["No market data available"]
        
        # For modifiers, confidence based on deviation from 1.0
        deviation = abs(value - 1.0)
        
        if deviation > 0.4:
            confidence = FactorConfidence.VERY_HIGH
            reasoning.append("Strong market sentiment divergence detected")
        elif deviation > 0.25:
            confidence = FactorConfidence.HIGH
            reasoning.append("Clear sharp vs public split identified")
        elif deviation > 0.15:
            confidence = FactorConfidence.MEDIUM
            reasoning.append("Moderate betting pattern divergence")
        elif deviation > 0.05:
            confidence = FactorConfidence.LOW
            reasoning.append("Slight market sentiment signal")
        else:
            confidence = FactorConfidence.NONE
            reasoning.append("No significant market sentiment")
        
        # Add specific signals to reasoning
        if value > 1.2:
            reasoning.append("Sharp money aligned with contrarian position")
        elif value < 0.8:
            reasoning.append("Market sentiment suggests caution")
        
        return value, confidence, reasoning
    
    def get_output_range(self) -> Tuple[float, float]:
        """Return the output range (multiplicative)."""
        return (self._min_output, self._max_output)
    
    def get_explanation(self, home_team: str, away_team: str, value: float, 
                       context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate human-readable explanation."""
        if abs(value - 1.0) < 0.05:
            return "No significant market sentiment signal"
        
        if value > 1.0:
            strength = "strong" if value > 1.3 else "moderate" if value > 1.15 else "slight"
            return f"Market sentiment shows {strength} sharp money support (×{value:.2f} modifier)"
        else:
            strength = "strong" if value < 0.7 else "moderate" if value < 0.85 else "slight"
            return f"Market sentiment suggests {strength} caution (×{value:.2f} modifier)"
    
    def get_required_data(self) -> Dict[str, bool]:
        """Declare required data."""
        return {
            'betting_data': True,      # Required for line movement
            'team_info': False,
            'coaching_data': False,
            'team_stats': False,
            'schedule_data': False,
            'historical_data': False
        }