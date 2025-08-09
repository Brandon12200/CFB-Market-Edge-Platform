"""
Style Mismatch Amplifier - SECONDARY contrarian factor.

Identifies matchup-specific advantages based on playing style conflicts.
Public bets on team reputation/rankings, not how styles interact.
Success rate differentials and pace mismatches create hidden edges.
"""

from typing import Dict, Any, Tuple, Optional, List
import logging
from factors.base_calculator import BaseFactorCalculator, FactorType, FactorConfidence
from data.cfbd_client import get_cfbd_client


class StyleMismatchCalculator(BaseFactorCalculator):
    """
    Analyzes style conflicts that create advantages not reflected in spreads.
    
    Contrarian insight: Public focuses on overall team quality, not how
    specific strengths/weaknesses interact. Pace and explosiveness mismatches
    create scoring variance that favors underdogs.
    """
    
    def __init__(self):
        super().__init__()
        
        # SECONDARY factor: 50% of SECONDARY category's 30% = 15% total weight
        self.weight = 0.50
        self.category = "situational_context"
        self.description = "Identifies exploitable style mismatches between teams"
        
        # Output range for this factor
        self._min_output = -4.0
        self._max_output = 4.0
        
        # Hierarchical system configuration
        self.factor_type = FactorType.SECONDARY
        self.activation_threshold = 1.5
        self.max_impact = 4.0
        
        # Factor-specific parameters
        self.config = {
            'success_rate_weight': 2.0,      # Most predictive metric
            'explosiveness_weight': 1.5,     # Big play differential
            'pace_mismatch_weight': 1.2,     # Tempo conflicts
            'redzone_weight': 1.0,           # Scoring efficiency
            'havoc_weight': 0.8,             # Chaos generation
            'min_success_diff': 0.05,       # 5% success rate difference threshold
            'pace_advantage_slower': 0.3     # Slower team advantage in mismatches
        }
        
        self.cfbd_client = get_cfbd_client()
    
    def calculate(self, home_team: str, away_team: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate style mismatch adjustment.
        
        Positive values indicate home team style advantage.
        Negative values indicate away team style advantage.
        """
        if not context or not self.cfbd_client:
            self.logger.debug("No context or CFBD client available for style mismatch")
            return 0.0
        
        year = context.get('year', 2024)
        
        # Get advanced stats for both teams
        home_stats = self._get_team_advanced_stats(home_team, year)
        away_stats = self._get_team_advanced_stats(away_team, year)
        
        if not home_stats or not away_stats:
            self.logger.debug(f"Insufficient advanced stats for {home_team} vs {away_team}")
            return 0.0
        
        # Calculate individual mismatch components
        success_mismatch = self._calculate_success_rate_mismatch(home_stats, away_stats)
        explosiveness_mismatch = self._calculate_explosiveness_mismatch(home_stats, away_stats)
        pace_mismatch = self._calculate_pace_mismatch(home_stats, away_stats)
        redzone_mismatch = self._calculate_redzone_mismatch(home_stats, away_stats)
        havoc_mismatch = self._calculate_havoc_mismatch(home_stats, away_stats)
        
        # Weighted combination
        adjustment = (
            success_mismatch * self.config['success_rate_weight'] +
            explosiveness_mismatch * self.config['explosiveness_weight'] +
            pace_mismatch * self.config['pace_mismatch_weight'] +
            redzone_mismatch * self.config['redzone_weight'] +
            havoc_mismatch * self.config['havoc_weight']
        ) / 6.5  # Normalize by total weights
        
        # Log significant findings
        if abs(adjustment) > self.activation_threshold:
            self.logger.info(f"Style mismatch detected: {home_team} vs {away_team}")
            self.logger.info(f"  Success: {success_mismatch:+.2f}, Explosive: {explosiveness_mismatch:+.2f}")
            self.logger.info(f"  Pace: {pace_mismatch:+.2f}, RedZone: {redzone_mismatch:+.2f}")
            self.logger.info(f"  Total adjustment: {adjustment:+.2f}")
        
        return self.validate_output(adjustment)
    
    def _get_team_advanced_stats(self, team: str, year: int) -> Optional[Dict[str, Any]]:
        """Fetch advanced statistics for a team."""
        try:
            # Get team stats from CFBD
            stats = self.cfbd_client.get_team_stats(team, year)
            if not stats:
                return None
            
            # Extract relevant advanced metrics
            return {
                'success_rate_off': stats.get('offense', {}).get('successRate', 0.40),
                'success_rate_def': stats.get('defense', {}).get('successRate', 0.40),
                'explosiveness_off': stats.get('offense', {}).get('explosiveness', 1.0),
                'explosiveness_def': stats.get('defense', {}).get('explosiveness', 1.0),
                'plays_per_game': stats.get('offense', {}).get('playsPerGame', 70),
                'havoc_rate': stats.get('defense', {}).get('havocRate', 0.15),
                'redzone_off': stats.get('offense', {}).get('redzoneSuccess', 0.80),
                'redzone_def': stats.get('defense', {}).get('redzoneSuccess', 0.80),
                'ppa_off': stats.get('offense', {}).get('ppa', 0.0),
                'ppa_def': stats.get('defense', {}).get('ppa', 0.0)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching advanced stats for {team}: {e}")
            return None
    
    def _calculate_success_rate_mismatch(self, home_stats: Dict, away_stats: Dict) -> float:
        """
        Success rate differential is the most predictive advanced metric.
        Compare offensive success vs defensive success allowed.
        """
        # Home offense vs Away defense
        home_off_advantage = home_stats['success_rate_off'] - away_stats['success_rate_def']
        
        # Away offense vs Home defense  
        away_off_advantage = away_stats['success_rate_off'] - home_stats['success_rate_def']
        
        # Net advantage (positive favors home)
        net_advantage = home_off_advantage - away_off_advantage
        
        # Scale based on magnitude
        if abs(net_advantage) > self.config['min_success_diff']:
            return net_advantage * 10  # Convert to points scale
        return 0.0
    
    def _calculate_explosiveness_mismatch(self, home_stats: Dict, away_stats: Dict) -> float:
        """
        Explosiveness mismatches create high variance, which helps underdogs.
        Check if explosive offense faces weak explosive defense.
        """
        # Home explosive plays vs Away explosive defense
        home_explosive_edge = home_stats['explosiveness_off'] / (away_stats['explosiveness_def'] + 0.1)
        
        # Away explosive plays vs Home explosive defense
        away_explosive_edge = away_stats['explosiveness_off'] / (home_stats['explosiveness_def'] + 0.1)
        
        # High variance situations favor underdogs
        variance_factor = (home_explosive_edge + away_explosive_edge) / 2
        
        # Net advantage with variance adjustment
        if variance_factor > 1.3:  # High variance game
            # Slightly favor underdog (typically away team)
            return -0.5
        elif home_explosive_edge > away_explosive_edge * 1.2:
            return 1.0
        elif away_explosive_edge > home_explosive_edge * 1.2:
            return -1.0
        
        return 0.0
    
    def _calculate_pace_mismatch(self, home_stats: Dict, away_stats: Dict) -> float:
        """
        Pace mismatches favor slower teams (more control, less variance).
        Fast vs slow creates opportunities for time management.
        """
        home_pace = home_stats['plays_per_game']
        away_pace = away_stats['plays_per_game']
        
        pace_diff = abs(home_pace - away_pace)
        
        # Significant pace mismatch (>10 plays per game difference)
        if pace_diff > 10:
            # Slower team gets advantage
            if home_pace < away_pace:
                return self.config['pace_advantage_slower']
            else:
                return -self.config['pace_advantage_slower']
        
        return 0.0
    
    def _calculate_redzone_mismatch(self, home_stats: Dict, away_stats: Dict) -> float:
        """
        Red zone efficiency mismatches determine scoring conversion.
        Critical for close games and covering spreads.
        """
        # Home red zone offense vs Away red zone defense
        home_rz_advantage = home_stats['redzone_off'] - away_stats['redzone_def']
        
        # Away red zone offense vs Home red zone defense
        away_rz_advantage = away_stats['redzone_off'] - home_stats['redzone_def']
        
        # Net red zone advantage
        net_advantage = home_rz_advantage - away_rz_advantage
        
        # Red zone efficiency gaps are critical
        if abs(net_advantage) > 0.10:  # 10% difference
            return net_advantage * 5  # Scale to points
        
        return 0.0
    
    def _calculate_havoc_mismatch(self, home_stats: Dict, away_stats: Dict) -> float:
        """
        Havoc rate (TFL, sacks, turnovers) creates chaos that helps underdogs.
        High havoc games have more variance.
        """
        home_havoc = home_stats['havoc_rate']
        away_havoc = away_stats['havoc_rate']
        
        # Combined havoc rate
        total_havoc = (home_havoc + away_havoc) / 2
        
        # High havoc games favor underdogs
        if total_havoc > 0.20:  # Top quartile havoc
            # Slight underdog advantage (typically away)
            return -0.3
        elif home_havoc > away_havoc * 1.3:
            return 0.5
        elif away_havoc > home_havoc * 1.3:
            return -0.5
        
        return 0.0
    
    def calculate_with_confidence(self, home_team: str, away_team: str, 
                                 context: Optional[Dict[str, Any]] = None) -> Tuple[float, FactorConfidence, List[str]]:
        """Calculate with confidence scoring."""
        value = self.calculate(home_team, away_team, context)
        reasoning = []
        
        if not self.cfbd_client:
            return value, FactorConfidence.NONE, ["CFBD client unavailable"]
        
        # Determine confidence based on mismatch severity
        if abs(value) > 3.0:
            confidence = FactorConfidence.VERY_HIGH
            reasoning.append("Extreme style mismatch identified")
        elif abs(value) > 2.0:
            confidence = FactorConfidence.HIGH
            reasoning.append("Significant style conflict detected")
        elif abs(value) > 1.0:
            confidence = FactorConfidence.MEDIUM
            reasoning.append("Moderate style mismatch found")
        elif abs(value) > 0.5:
            confidence = FactorConfidence.LOW
            reasoning.append("Minor style differential present")
        else:
            confidence = FactorConfidence.NONE
            reasoning.append("No exploitable style mismatch")
        
        # Add specific mismatch type to reasoning
        if abs(value) > 1.0:
            year = context.get('year', 2024) if context else 2024
            home_stats = self._get_team_advanced_stats(home_team, year)
            away_stats = self._get_team_advanced_stats(away_team, year)
            
            if home_stats and away_stats:
                success_diff = abs(home_stats['success_rate_off'] - away_stats['success_rate_off'])
                if success_diff > 0.05:
                    reasoning.append("Success rate differential detected")
                
                pace_diff = abs(home_stats['plays_per_game'] - away_stats['plays_per_game'])
                if pace_diff > 10:
                    reasoning.append("Pace mismatch advantage")
        
        return value, confidence, reasoning
    
    def get_output_range(self) -> Tuple[float, float]:
        """Return the output range."""
        return (self._min_output, self._max_output)
    
    def get_explanation(self, home_team: str, away_team: str, value: float, 
                       context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate human-readable explanation."""
        if abs(value) < 0.1:
            return "No significant style mismatch impact"
        
        favored_team = home_team if value > 0 else away_team
        
        impact = "extreme" if abs(value) > 3.0 else "major" if abs(value) > 2.0 else "notable"
        
        # Identify primary mismatch type
        mismatch_type = "style"
        if context:
            year = context.get('year', 2024)
            home_stats = self._get_team_advanced_stats(home_team, year)
            away_stats = self._get_team_advanced_stats(away_team, year)
            
            if home_stats and away_stats:
                success_diff = abs(home_stats['success_rate_off'] - away_stats['success_rate_off'])
                pace_diff = abs(home_stats['plays_per_game'] - away_stats['plays_per_game'])
                
                if success_diff > 0.08:
                    mismatch_type = "success rate"
                elif pace_diff > 15:
                    mismatch_type = "pace"
                else:
                    mismatch_type = "explosiveness"
        
        return (f"{favored_team} has {impact} {mismatch_type} advantage "
                f"({value:+.1f} points)")
    
    def get_required_data(self) -> Dict[str, bool]:
        """Declare required data."""
        return {
            'team_stats': True,        # Required for advanced metrics
            'team_info': False,
            'coaching_data': False,
            'schedule_data': False,
            'betting_data': False,
            'historical_data': False
        }