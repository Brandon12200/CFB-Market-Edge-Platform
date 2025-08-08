You're absolutely right - let me focus on **6 concrete, quantifiable factors** that will immediately improve your edge detection with expanded API usage.

## **6 High-Impact Quantifiable Factors**

### **3. Advanced Efficiency Metrics Differential**
**API**: Sports Reference CFB API
```python
class AdvancedEfficiencyCalculator(BaseFactorCalculator):
    def calculate(self, home_team: str, away_team: str) -> float:
        home_metrics = self.get_advanced_metrics(home_team)
        away_metrics = self.get_advanced_metrics(away_team)
        
        # Calculate key efficiency differentials
        success_rate_diff = (home_metrics.off_success_rate - home_metrics.def_success_rate) - \
                           (away_metrics.off_success_rate - away_metrics.def_success_rate)
        
        explosiveness_diff = (home_metrics.off_explosiveness - home_metrics.def_explosiveness) - \
                            (away_metrics.off_explosiveness - away_metrics.def_explosiveness)
        
        finishing_drives_diff = home_metrics.red_zone_eff - away_metrics.red_zone_eff
        
        # Weight the metrics
        composite_efficiency = (success_rate_diff * 0.4 + 
                              explosiveness_diff * 0.35 + 
                              finishing_drives_diff * 0.25)
        
        # Scale to point spread impact
        adjustment = composite_efficiency * 8.0
        
        return max(min(adjustment, 4.0), -4.0)
    
    def get_advanced_metrics(self, team: str) -> dict:
        return {
            'off_success_rate': self.api.get_offensive_success_rate(team),
            'def_success_rate': self.api.get_defensive_success_rate(team),
            'off_explosiveness': self.api.get_explosive_play_rate(team),
            'def_explosiveness': self.api.get_explosive_plays_allowed_rate(team),
            'red_zone_eff': self.api.get_red_zone_efficiency(team)
        }
```

### **4. Market Sentiment & Sharp Money Indicator**
**API**: Action Network API + Bet Labs API
```python
class MarketSentimentCalculator(BaseFactorCalculator):
    def calculate(self, home_team: str, away_team: str) -> float:
        betting_data = self.get_betting_percentages(home_team, away_team)
        line_movement = self.get_line_movement_data(home_team, away_team)
        
        # Detect reverse line movement (sharp money indicator)
        public_home_pct = betting_data.home_team_bet_percentage
        line_move_toward_home = line_movement.current_spread < line_movement.opening_spread
        
        sharp_money_indicator = 0.0
        
        # If 70%+ public money on home but line moved away from home = sharp money on away
        if public_home_pct > 0.7 and not line_move_toward_home:
            sharp_money_indicator = -1.5  # Fade the public, follow sharp money
        elif public_home_pct < 0.3 and line_move_toward_home:
            sharp_money_indicator = 1.5   # Sharp money on home team
        
        # Steam moves (rapid line movement)
        line_velocity = abs(line_movement.total_movement) / line_movement.hours_tracked
        if line_velocity > 0.3:  # Fast movement indicates information
            direction = 1 if line_movement.total_movement > 0 else -1
            sharp_money_indicator += direction * 0.8
        
        return max(min(sharp_money_indicator, 2.5), -2.5)
```

### **6. Opponent-Adjusted Performance Trends**
**API**: Advanced College Football Stats API + FEI Data
```python
class OpponentAdjustedTrendsCalculator(BaseFactorCalculator):
    def calculate(self, home_team: str, away_team: str) -> float:
        # Get last 5 games for each team with opponent adjustments
        home_trends = self.get_opponent_adjusted_trends(home_team, games=5)
        away_trends = self.get_opponent_adjusted_trends(away_team, games=5)
        
        # Calculate momentum differentials
        scoring_trend_diff = home_trends.adj_scoring_trend - away_trends.adj_scoring_trend
        defensive_trend_diff = away_trends.adj_defense_trend - home_trends.adj_defense_trend
        efficiency_trend_diff = home_trends.adj_efficiency_trend - away_trends.adj_efficiency_trend
        
        # Weight recent games more heavily
        trend_weights = [0.4, 0.25, 0.2, 0.1, 0.05]  # Last 5 games
        
        momentum_score = (scoring_trend_diff * 0.4 + 
                         defensive_trend_diff * 0.35 + 
                         efficiency_trend_diff * 0.25)
        
        return max(min(momentum_score, 2.5), -2.5)
    
    def get_opponent_adjusted_trends(self, team: str, games: int) -> dict:
        recent_games = self.api.get_recent_games(team, games)
        
        adjusted_metrics = {
            'adj_scoring_trend': 0,
            'adj_defense_trend': 0, 
            'adj_efficiency_trend': 0
        }
        
        for i, game in enumerate(recent_games):
            weight = [0.4, 0.25, 0.2, 0.1, 0.05][i]
            
            # Adjust performance by opponent strength
            opp_def_rating = self.get_opponent_defensive_rating(game.opponent)
            opp_off_rating = self.get_opponent_offensive_rating(game.opponent)
            
            adj_scoring = (game.points_scored - opp_def_rating.avg_allowed) * weight
            adj_defense = (opp_off_rating.avg_scored - game.points_allowed) * weight
            adj_efficiency = (game.total_yards - opp_def_rating.avg_yards_allowed) * weight
            
            adjusted_metrics['adj_scoring_trend'] += adj_scoring
            adjusted_metrics['adj_defense_trend'] += adj_defense
            adjusted_metrics['adj_efficiency_trend'] += adj_efficiency / 100  # Scale down
            
        return adjusted_metrics
```

### **1. Recruiting Talent Differential**
**API**: 247Sports Composite API
```python
class RecruitingTalentCalculator(BaseFactorCalculator):
    def calculate(self, home_team: str, away_team: str) -> float:
        home_talent = self.get_247_composite_score(home_team)
        away_talent = self.get_247_composite_score(away_team)
        
        # Normalize talent scores (0-100 scale)
        talent_differential = (home_talent - away_talent) / 10
        
        # Convert to point spread impact
        # Every 10 points of talent = ~0.5 point spread advantage
        adjustment = talent_differential * 0.05
        
        return max(min(adjustment, 2.0), -2.0)
    
    def get_247_composite_score(self, team: str) -> float:
        # 4-year rolling average of recruiting classes
        scores = []
        for year in range(2021, 2025):
            class_score = self.api_client.get_recruiting_class_score(team, year)
            scores.append(class_score)
        return sum(scores) / len(scores)
```

### **2. Key Player Injury Impact**
**API**: ESPN Injury Report + Pro Football Focus API
```python
class InjuryImpactCalculator(BaseFactorCalculator):
    def calculate(self, home_team: str, away_team: str) -> float:
        home_injuries = self.get_key_injuries(home_team)
        away_injuries = self.get_key_injuries(away_team)
        
        home_impact = self.calculate_team_injury_impact(home_injuries)
        away_impact = self.calculate_team_injury_impact(away_injuries)
        
        # Net injury impact (positive = home team advantage)
        net_impact = away_impact - home_impact
        
        return max(min(net_impact, 3.0), -3.0)
    
    def calculate_team_injury_impact(self, injuries: list) -> float:
        total_impact = 0.0
        
        for injury in injuries:
            position_weight = {
                'QB': 2.5, 'RB': 0.8, 'WR': 0.6, 'TE': 0.4,
                'OL': 0.7, 'DL': 0.6, 'LB': 0.5, 'DB': 0.5,
                'K': 0.2, 'P': 0.1
            }
            
            player_importance = self.get_player_pff_grade(injury.player_id) / 100
            position_multiplier = position_weight.get(injury.position, 0.3)
            
            injury_severity = {
                'out': 1.0, 'doubtful': 0.7, 'questionable': 0.3, 'probable': 0.1
            }
            
            impact = (player_importance * position_multiplier * 
                     injury_severity.get(injury.status, 0))
            total_impact += impact
            
        return total_impact
```

### **5. Venue-Specific Performance Metrics**
**API**: ESPN Venue API + Custom Venue Database
```python
class VenueSpecificCalculator(BaseFactorCalculator):
    def calculate(self, home_team: str, away_team: str) -> float:
        venue = self.get_game_venue(home_team)
        
        # Home team venue-specific performance
        home_venue_record = self.get_venue_record(home_team, venue.name, years=3)
        home_venue_ats = self.get_venue_ats_record(home_team, venue.name, years=3)
        
        # Away team performance at similar venues
        similar_venues = self.get_similar_venues(venue)
        away_similar_venue_record = self.get_performance_at_similar_venues(away_team, similar_venues)
        
        adjustment = 0.0
        
        # Home team venue mastery bonus
        if home_venue_record.games > 10:
            venue_win_rate = home_venue_record.wins / home_venue_record.games
            venue_ats_rate = home_venue_ats.covers / home_venue_ats.games
            
            if venue_win_rate > 0.75 and venue_ats_rate > 0.55:
                adjustment += 1.2  # Strong venue performer
            elif venue_win_rate < 0.4 or venue_ats_rate < 0.45:
                adjustment -= 0.8  # Struggles at home venue
        
        # Venue-specific factors
        venue_factors = {
            'altitude': self.calculate_altitude_impact(venue, away_team),
            'surface': self.calculate_surface_impact(venue, away_team),
            'crowd_noise': self.calculate_crowd_impact(venue, away_team),
            'travel_difficulty': self.calculate_venue_access_difficulty(venue, away_team)
        }
        
        adjustment += sum(venue_factors.values())
        
        return max(min(adjustment, 3.0), -3.0)
```