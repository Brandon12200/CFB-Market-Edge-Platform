#!/usr/bin/env python3
"""
CFB Contrarian Predictor - Command Line Interface

Main entry point for the college football betting analysis tool.
Identifies contrarian opportunities by layering human factor adjustments 
on top of Vegas market consensus.
"""

import sys
import argparse
import logging
import time
from typing import Optional, Dict, Any

from config import config
from normalizer import normalizer
from data.data_manager import data_manager
from data.schedule_client import CFBScheduleClient
from engine.prediction_engine import prediction_engine
from engine.confidence_calculator import confidence_calculator
from engine.edge_detector import edge_detector


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for the CFB Contrarian Predictor.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='CFB Contrarian Predictor - Find contrarian college football betting opportunities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --home georgia --away alabama
  %(prog)s --home uga --away bama --verbose --show-factors
  %(prog)s --home "Georgia Bulldogs" --away "Alabama Crimson Tide" --week 8
  %(prog)s --analyze-week 8 --min-edge 3.0
  %(prog)s --list-teams
        """
    )
    
    # Primary prediction arguments
    prediction_group = parser.add_argument_group('Prediction Options')
    prediction_group.add_argument(
        '--home',
        type=str,
        help='Home team (e.g., "georgia", "uga", "Georgia Bulldogs")'
    )
    prediction_group.add_argument(
        '--away', 
        type=str,
        help='Away team (e.g., "alabama", "bama", "Alabama Crimson Tide")'
    )
    prediction_group.add_argument(
        '--week',
        type=int,
        metavar='N',
        help='College football week number (1-17)'
    )
    
    # Batch analysis
    batch_group = parser.add_argument_group('Batch Analysis')
    batch_group.add_argument(
        '--analyze-week',
        type=int,
        metavar='N',
        nargs='?',
        const=0,
        help='Analyze all games for specified week (defaults to current week if no number provided)'
    )
    batch_group.add_argument(
        '--min-edge',
        type=float,
        default=3.0,
        metavar='POINTS',
        help='Minimum edge size to display (default: 3.0 points)'
    )
    
    # Output control
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed explanations'
    )
    output_group.add_argument(
        '--show-factors',
        action='store_true',
        help='Display factor-by-factor breakdown'
    )
    output_group.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-essential output'
    )
    output_group.add_argument(
        '--format',
        choices=['table', 'json', 'csv'],
        default='table',
        help='Output format (default: table)'
    )
    
    # Utility options
    utility_group = parser.add_argument_group('Utility Options')
    utility_group.add_argument(
        '--list-teams',
        action='store_true',
        help='List all supported team names and aliases'
    )
    utility_group.add_argument(
        '--list-games',
        type=int,
        metavar='WEEK',
        help='List all P4 games for specified week with normalized team names'
    )
    utility_group.add_argument(
        '--validate-team',
        type=str,
        metavar='TEAM',
        help='Check if team name can be normalized'
    )
    utility_group.add_argument(
        '--check-config',
        action='store_true',
        help='Validate configuration and API keys'
    )
    utility_group.add_argument(
        '--version',
        action='version',
        version='CFB Contrarian Predictor v2.0'
    )
    
    # Debug options
    debug_group = parser.add_argument_group('Debug Options')
    debug_group.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    debug_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making API calls'
    )
    debug_group.add_argument(
        '--cache-clear',
        action='store_true',
        help='Clear all cached data before running'
    )
    
    args = parser.parse_args()
    
    # Validate argument combinations
    _validate_arguments(args, parser)
    
    return args


def _validate_arguments(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """
    Validate argument combinations and requirements.
    
    Args:
        args: Parsed arguments
        parser: Argument parser for error reporting
    """
    # Check for prediction requirements
    if not any([args.home, args.analyze_week is not None, args.list_teams, args.list_games,
                args.validate_team, args.check_config]):
        parser.error("Must specify prediction teams (--home/--away) or use utility options")
    
    # Both home and away required for single prediction
    if (args.home and not args.away) or (args.away and not args.home):
        parser.error("Both --home and --away are required for single game prediction")
    
    # Week validation
    if args.week and not (1 <= args.week <= 17):
        parser.error("Week must be between 1 and 17")
    
    if args.analyze_week and args.analyze_week != 0 and not (1 <= args.analyze_week <= 17):
        parser.error("Analyze week must be between 1 and 17")
    
    # Edge threshold validation
    if args.min_edge < 0:
        parser.error("Minimum edge must be non-negative")
    
    # Conflicting options
    if args.verbose and args.quiet:
        parser.error("Cannot use --verbose and --quiet together")


def setup_logging(debug: bool = False, quiet: bool = False) -> None:
    """
    Configure logging based on command line options.
    
    Args:
        debug: Enable debug logging
        quiet: Suppress non-essential output
    """
    if debug:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    else:
        level = logging.INFO
    
    # Override config logging for CLI
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s' if not debug else '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Override any existing logging config
    )


def validate_teams(home_team: str, away_team: str) -> tuple[Optional[str], Optional[str]]:
    """
    Validate and normalize team names.
    
    Args:
        home_team: Home team input
        away_team: Away team input
        
    Returns:
        tuple: (normalized_home, normalized_away) or (None, None) if invalid
    """
    normalized_home = normalizer.normalize(home_team)
    normalized_away = normalizer.normalize(away_team)
    
    if not normalized_home:
        print(f"Error: Unknown home team '{home_team}'")
        print("Use --list-teams to see supported team names")
        return None, None
    
    if not normalized_away:
        print(f"Error: Unknown away team '{away_team}'")
        print("Use --list-teams to see supported team names")
        return None, None
    
    if normalized_home == normalized_away:
        print("Error: Home and away teams cannot be the same")
        return None, None
    
    return normalized_home, normalized_away


def list_teams() -> None:
    """Display all supported team names and aliases."""
    print("CFB Contrarian Predictor - Supported Teams")
    print("=" * 50)
    print()
    
    all_teams = sorted(normalizer.get_all_teams())
    
    # Group by conference (simplified)
    conferences = {
        'SEC': ['ALABAMA', 'ARKANSAS', 'AUBURN', 'FLORIDA', 'GEORGIA', 'KENTUCKY',
                'LSU', 'MISSISSIPPI', 'MISSISSIPPI STATE', 'MISSOURI', 'SOUTH CAROLINA',
                'TENNESSEE', 'TEXAS', 'TEXAS A&M', 'VANDERBILT', 'OKLAHOMA'],
        'BIG TEN': ['ILLINOIS', 'INDIANA', 'IOWA', 'MARYLAND', 'MICHIGAN', 'MICHIGAN STATE',
                    'MINNESOTA', 'NEBRASKA', 'NORTHWESTERN', 'OHIO STATE', 'PENN STATE',
                    'PURDUE', 'RUTGERS', 'WISCONSIN', 'OREGON', 'WASHINGTON', 'UCLA', 'USC'],
        'BIG 12': ['BAYLOR', 'IOWA STATE', 'KANSAS', 'KANSAS STATE', 'OKLAHOMA STATE',
                   'TCU', 'TEXAS TECH', 'WEST VIRGINIA', 'CINCINNATI', 'HOUSTON',
                   'UCF', 'BYU', 'COLORADO', 'UTAH', 'ARIZONA', 'ARIZONA STATE'],
        'ACC': ['BOSTON COLLEGE', 'CLEMSON', 'DUKE', 'FLORIDA STATE', 'GEORGIA TECH',
                'LOUISVILLE', 'MIAMI', 'NC STATE', 'NORTH CAROLINA', 'PITTSBURGH',
                'SYRACUSE', 'VIRGINIA', 'VIRGINIA TECH', 'WAKE FOREST', 'NOTRE DAME']
    }
    
    for conf_name, teams in conferences.items():
        print(f"{conf_name}:")
        for team in teams:
            if team in all_teams:
                aliases = normalizer.get_all_aliases(team)
                alias_str = ', '.join([a for a in aliases if a != team][:3])  # Show first 3 aliases
                if alias_str:
                    print(f"  {team:<20} (aliases: {alias_str})")
                else:
                    print(f"  {team}")
        print()
    
    print("Examples:")
    print("  --home georgia --away alabama")
    print("  --home uga --away bama")
    print("  --home 'Georgia Bulldogs' --away 'Alabama Crimson Tide'")


def validate_team_name(team_name: str) -> None:
    """Validate a single team name and show normalization."""
    normalized = normalizer.normalize(team_name)
    
    if normalized:
        print(f"✓ '{team_name}' normalizes to: {normalized}")
        
        aliases = normalizer.get_all_aliases(normalized)
        print(f"  Known aliases: {', '.join(aliases)}")
        
        espn_format = normalizer.to_espn_format(normalized)
        if espn_format:
            print(f"  ESPN format: {espn_format}")
        
        odds_format = normalizer.to_odds_format(normalized)
        if odds_format:
            print(f"  Odds API format: {odds_format}")
    else:
        print(f"✗ '{team_name}' not recognized")
        print("Use --list-teams to see supported team names")


def list_games(week: int) -> None:
    """List all P4 games for a specific week with normalized team names."""
    print(f"CFB Week {week} Schedule - P4 Games")
    print("=" * 60)
    
    try:
        # Initialize schedule client
        schedule_client = CFBScheduleClient()
        
        # Test connection first
        if not schedule_client.test_connection():
            print("❌ Cannot connect to ESPN Schedule API")
            print("   Check your internet connection and try again")
            return
        
        print(f"📊 Fetching Week {week} schedule...")
        
        # Get P4 games for the week
        p4_games = schedule_client.get_p4_games(week)
        
        if not p4_games:
            print(f"📭 No P4 games found for Week {week}")
            print("   This may be an off-season week or the data isn't available yet")
            return
        
        print(f"🏈 Found {len(p4_games)} P4 games for Week {week}")
        print()
        
        # Display each game
        for i, game in enumerate(p4_games, 1):
            away_team = game['away_team_short']
            home_team = game['home_team_short']
            venue = game['venue_name']
            
            # Add rankings if available
            away_display = away_team
            if game['away_ranking']:
                away_display = f"#{game['away_ranking']} {away_team}"
            
            home_display = home_team
            if game['home_ranking']:
                home_display = f"#{game['home_ranking']} {home_team}"
            
            # Format game line
            game_line = f"{i:2d}. {away_display:20} @ {home_display:20}"
            
            # Add venue info
            if game['neutral_site']:
                game_line += f" (Neutral: {venue})"
            
            print(game_line)
            
            # Show normalized names for easy testing
            away_norm = game['away_team_normalized']
            home_norm = game['home_team_normalized']
            
            if away_norm and home_norm:
                print(f"    Command: python main.py --home {home_norm.lower().replace(' ', '-')} --away {away_norm.lower().replace(' ', '-')}")
            else:
                print(f"    Note: Team normalization incomplete")
            
            print()
        
        print("=" * 60)
        print("💡 Tips:")
        print("   • Use the Command lines above to test individual games")
        print("   • Add --verbose --show-factors for detailed analysis")
        print(f"   • Try: python main.py --analyze-week {week} for batch analysis")
        
    except Exception as e:
        print(f"❌ Error fetching Week {week} schedule: {e}")
        print("   Check your configuration and try again")


def check_configuration() -> bool:
    """
    Check configuration and API key status.
    
    Returns:
        bool: True if configuration is valid
    """
    print("CFB Contrarian Predictor - Configuration Check")
    print("=" * 50)
    
    # Check API keys
    api_status = config.validate_api_keys()
    print(f"Odds API Key: {'✓ Configured' if api_status['odds_api'] else '✗ Missing'}")
    print(f"ESPN API Key: {'✓ Configured' if api_status['espn_api'] == True else '○ Optional' if api_status['espn_api'] == 'optional' else '✗ Missing'}")
    
    # Test API connections
    print(f"\nAPI Connection Tests:")
    try:
        connections = data_manager.test_all_connections()
        print(f"  Odds API: {'✓ Connected' if connections.get('odds_api', False) else '✗ Failed'}")
        print(f"  ESPN API: {'✓ Connected' if connections.get('espn_api', False) else '✗ Failed'}")
    except Exception as e:
        print(f"  Connection test failed: {e}")
    
    # Check configuration
    print(f"\nConfiguration:")
    print(f"  Debug mode: {config.debug}")
    print(f"  Log level: {config.log_level}")
    print(f"  Cache TTL: {config.cache_ttl}s")
    print(f"  Rate limits: Odds API {config.rate_limit_odds}/day, ESPN {config.rate_limit_espn}/min")
    
    # Check factor weights
    total_weight = config.coaching_edge_weight + config.situational_context_weight + config.momentum_factors_weight
    print(f"\nFactor Weights (total: {total_weight:.3f}):")
    print(f"  Coaching Edge: {config.coaching_edge_weight:.1%}")
    print(f"  Situational Context: {config.situational_context_weight:.1%}")
    print(f"  Momentum Factors: {config.momentum_factors_weight:.1%}")
    
    # Show cache statistics
    try:
        cache_stats = data_manager.get_cache_stats()
        print(f"\nCache Statistics:")
        print(f"  Entries: {cache_stats.get('entries', 0)}")
        print(f"  Hit rate: {cache_stats.get('hit_rate', 0):.1%}")
        print(f"  Utilization: {cache_stats.get('utilization', 0):.1%}")
    except Exception as e:
        print(f"  Cache stats unavailable: {e}")
    
    # Validation
    is_valid = api_status['odds_api'] and abs(total_weight - 1.0) < 0.001
    
    if is_valid:
        print("\n✓ Configuration valid and ready for use")
    else:
        print("\n✗ Configuration issues detected:")
        if not api_status['odds_api']:
            print("  - Odds API key required")
        if abs(total_weight - 1.0) >= 0.001:
            print(f"  - Factor weights don't sum to 1.0 (got {total_weight})")
    
    return is_valid


def run_single_prediction(home_team: str, away_team: str, week: Optional[int] = None,
                         verbose: bool = False, show_factors: bool = False) -> Dict[str, Any]:
    """
    Run prediction for a single game.
    
    Args:
        home_team: Normalized home team name
        away_team: Normalized away team name
        week: Week number (optional)
        verbose: Enable verbose output
        show_factors: Show factor breakdown
        
    Returns:
        dict: Prediction results
    """
    print(f"\nAnalyzing: {away_team} @ {home_team}")
    if week:
        print(f"Week: {week}")
    print("-" * 50)
    
    try:
        # Get comprehensive game context
        print("📊 Fetching game data...")
        context = data_manager.get_game_context(home_team, away_team, week)
        
        # Display data quality
        quality = context.get('data_quality', 0)
        quality_str = f"{quality:.1%}"
        print(f"📈 Data Quality: {quality_str}")
        
        # Get betting line
        vegas_spread = context.get('vegas_spread')
        if vegas_spread is not None:
            print(f"💰 Vegas Spread: {home_team} {vegas_spread:+.1f}")
        else:
            print("💰 Vegas Spread: Not available")
        
        # Show data availability if verbose
        if verbose:
            print(f"\n📋 Data Sources: {', '.join(context.get('data_sources', []))}")
            
            availability = data_manager.validate_data_availability(home_team, away_team)
            print("🔍 Data Availability:")
            for source, available in availability.items():
                status = "✓" if available else "✗"
                print(f"   {source}: {status}")
        
        # Show team information
        home_data = context.get('home_team_data', {})
        away_data = context.get('away_team_data', {})
        
        print(f"\n🏟️  Team Information:")
        
        # Home team info
        home_info = home_data.get('info', {})
        home_display = home_info.get('display_name', home_team)
        home_conf = home_info.get('conference', {}).get('name', 'Unknown')
        print(f"   {home_team}: {home_display} ({home_conf})")
        
        # Away team info
        away_info = away_data.get('info', {})
        away_display = away_info.get('display_name', away_team)
        away_conf = away_info.get('conference', {}).get('name', 'Unknown')
        print(f"   {away_team}: {away_display} ({away_conf})")
        
        # Show coaching comparison
        coaching_comp = context.get('coaching_comparison', {})
        if coaching_comp and show_factors:
            print(f"\n👨‍💼 Coaching Comparison:")
            
            home_coach = coaching_comp.get('home_coaching', {})
            away_coach = coaching_comp.get('away_coaching', {})
            
            home_coach_name = home_coach.get('head_coach_name', 'Unknown')
            away_coach_name = away_coach.get('head_coach_name', 'Unknown')
            
            home_exp = home_coach.get('head_coach_experience', 0)
            away_exp = away_coach.get('head_coach_experience', 0)
            
            print(f"   {home_team}: {home_coach_name} ({home_exp} years)")
            print(f"   {away_team}: {away_coach_name} ({away_exp} years)")
            
            exp_diff = coaching_comp.get('experience_differential', 0)
            if exp_diff > 0:
                print(f"   Experience Edge: {home_team} +{exp_diff} years")
            elif exp_diff < 0:
                print(f"   Experience Edge: {away_team} +{abs(exp_diff)} years")
            else:
                print(f"   Experience Edge: Even")
        
        # Generate contrarian prediction using the prediction engine
        print(f"\n🎯 Generating Contrarian Prediction...")
        prediction_result = prediction_engine.generate_prediction(home_team, away_team, week)
        
        # Calculate confidence assessment
        context_for_confidence = {
            'data_quality': quality,
            'vegas_spread': vegas_spread,
            'data_sources': context.get('data_sources', [])
        }
        
        # Get factor results for confidence calculation
        from factors.factor_registry import factor_registry
        factor_results = factor_registry.calculate_all_factors(home_team, away_team, context)
        
        confidence_assessment = confidence_calculator.calculate_confidence(
            prediction_result, factor_results, context_for_confidence
        )
        
        # Detect contrarian edges
        edge_classification = edge_detector.detect_edge(
            prediction_result, confidence_assessment, context_for_confidence
        )
        
        # Display prediction results
        print(f"\n📊 Prediction Results:")
        print(f"   Vegas Spread: {home_team} {vegas_spread:+.1f}" if vegas_spread is not None else "   Vegas Spread: Not available")
        
        if prediction_result.get('contrarian_spread') is not None:
            contrarian_spread = prediction_result['contrarian_spread']
            total_adjustment = prediction_result.get('total_adjustment', 0.0)
            edge_size = prediction_result.get('edge_size', 0.0)
            
            # Handle None values
            if contrarian_spread is None:
                contrarian_spread = 0.0
            if total_adjustment is None:
                total_adjustment = 0.0
            if edge_size is None:
                edge_size = 0.0
                
            print(f"   Contrarian Prediction: {home_team} {contrarian_spread:+.1f}")
            print(f"   Factor Adjustment: {total_adjustment:+.2f} points")
            print(f"   Edge Size: {edge_size:.2f} points")
        else:
            print("   Contrarian Prediction: Cannot calculate without betting line")
        
        print(f"\n🎯 Edge Analysis:")
        print(f"   Edge Type: {edge_classification.edge_type.value.replace('_', ' ').title()}")
        print(f"   Confidence: {confidence_assessment['confidence_level']} ({confidence_assessment['confidence_percentage']})")
        print(f"   Recommendation: {edge_classification.recommended_action}")
        
        if show_factors:
            print(f"\n📈 Factor Breakdown:")
            for factor_name, factor_result in factor_results['factors'].items():
                if factor_result['success']:
                    value = factor_result.get('value', 0.0)
                    weighted_value = factor_result.get('weighted_value', 0.0)
                    # Handle None values
                    if value is None:
                        value = 0.0
                    if weighted_value is None:
                        weighted_value = 0.0
                    print(f"   {factor_name}: {value:+.3f} (weighted: {weighted_value:+.3f})")
                    if factor_result.get('explanation'):
                        print(f"      → {factor_result['explanation']}")
                else:
                    print(f"   {factor_name}: FAILED - {factor_result.get('error', 'Unknown error')}")
            
            print(f"\n📊 Category Summary:")
            for category, adjustment in factor_results['summary'].get('category_adjustments', {}).items():
                # Handle None adjustment values
                if adjustment is None:
                    adjustment = 0.0
                print(f"   {category.replace('_', ' ').title()}: {adjustment:+.3f} points")
        
        print(f"\n💡 Explanation:")
        print(f"   {edge_classification.explanation}")
        
        # Build result structure with prediction engine results
        result = {
            'home_team': home_team,
            'away_team': away_team,
            'week': week,
            'vegas_spread': vegas_spread,
            'contrarian_prediction': prediction_result.get('contrarian_spread'),
            'edge_size': prediction_result.get('edge_size'),
            'confidence': confidence_assessment.get('confidence_score'),
            'edge_classification': edge_classification.edge_type.value,
            'data_quality': quality,
            'data_sources': context.get('data_sources', []),
            'team_data': {
                'home': home_data,
                'away': away_data
            },
            'coaching_comparison': coaching_comp,
            'recommendation': edge_classification.recommended_action,
            'timestamp': context.get('timestamp'),
            'prediction_result': prediction_result,
            'confidence_assessment': confidence_assessment,
            'edge_classification_obj': edge_classification
        }
        
        return result
        
    except Exception as e:
        print(f"❌ Error analyzing game: {e}")
        
        # Return error result
        return {
            'home_team': home_team,
            'away_team': away_team,
            'week': week,
            'error': str(e),
            'edge_classification': 'ERROR',
            'recommendation': 'Analysis failed - check configuration'
        }


def run_weekly_analysis(week: int, min_edge: float = 3.0) -> None:
    """
    Analyze all games for a specified week.
    
    Args:
        week: Week number to analyze
        min_edge: Minimum edge size to display
    """
    print(f"\nAnalyzing Week {week} Games (edges >= {min_edge} points)")
    print("=" * 60)
    
    try:
        # Check if we have odds data capability
        if not data_manager.odds_client:
            print("❌ Odds API not available - cannot fetch weekly games")
            print("   Configure ODDS_API_KEY to enable weekly analysis")
            return
        
        print("📊 Fetching weekly games...")
        weekly_data = data_manager.odds_client.get_weekly_spreads(week)
        
        games = weekly_data.get('games', [])
        if not games:
            print(f"📭 No games found for Week {week}")
            return
        
        print(f"🏈 Found {len(games)} games for Week {week}")
        print()
        
        # Analyze each game (simplified for now)
        analyzed_games = []
        
        for game in games:
            home_team = game.get('home_team')
            away_team = game.get('away_team')
            spread = game.get('consensus_spread')
            
            if home_team and away_team:
                print(f"📋 {away_team} @ {home_team}", end="")
                if spread is not None:
                    print(f" (Spread: {home_team} {spread:+.1f})")
                else:
                    print(" (No spread)")
                
                # For Week 2, just show data availability
                availability = data_manager.validate_data_availability(home_team, away_team)
                quality_score = sum(availability.values()) / len(availability)
                print(f"   Data Quality: {quality_score:.1%}")
                
                analyzed_games.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'spread': spread,
                    'quality': quality_score
                })
                print()
        
        # Summary
        print("=" * 60)
        print(f"📈 Weekly Summary:")
        print(f"   Total games: {len(analyzed_games)}")
        
        games_with_spreads = sum(1 for g in analyzed_games if g['spread'] is not None)
        print(f"   Games with spreads: {games_with_spreads}")
        
        if analyzed_games:
            avg_quality = sum(g['quality'] for g in analyzed_games) / len(analyzed_games)
            print(f"   Average data quality: {avg_quality:.1%}")
        
        print(f"\n🚧 Factor analysis will be available in Week 3-4")
        print(f"   Current implementation shows data availability only")
        
    except Exception as e:
        print(f"❌ Error in weekly analysis: {e}")
        print("   Check your API configuration and try again")


def main() -> int:
    """
    Main entry point for the CFB Contrarian Predictor CLI.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        setup_logging(args.debug, args.quiet)
        
        if args.debug:
            logging.debug(f"Arguments: {args}")
            logging.debug(f"Configuration: {config}")
        
        # Handle utility commands
        if args.list_teams:
            list_teams()
            return 0
        
        if args.list_games:
            list_games(args.list_games)
            return 0
        
        if args.validate_team:
            validate_team_name(args.validate_team)
            return 0
        
        if args.check_config:
            is_valid = check_configuration()
            return 0 if is_valid else 1
        
        # Validate configuration for prediction commands
        if not config.odds_api_key and not args.dry_run:
            logging.error("Odds API key required for predictions")
            logging.error("Set ODDS_API_KEY in environment or .env file")
            return 1
        
        start_time = time.time()
        
        # Handle prediction commands
        if args.home and args.away:
            # Validate teams
            home_normalized, away_normalized = validate_teams(args.home, args.away)
            if not home_normalized or not away_normalized:
                return 1
            
            # Run single prediction
            result = run_single_prediction(
                home_normalized, 
                away_normalized, 
                args.week,
                args.verbose, 
                args.show_factors
            )
            
            if args.format == 'json':
                import json
                # Convert EdgeClassification object to serializable format
                json_result = result.copy()
                if 'edge_classification_obj' in json_result:
                    edge_obj = json_result['edge_classification_obj']
                    json_result['edge_classification_obj'] = {
                        'edge_type': edge_obj.edge_type.value if hasattr(edge_obj.edge_type, 'value') else str(edge_obj.edge_type),
                        'recommended_action': edge_obj.recommended_action,
                        'explanation': edge_obj.explanation
                    }
                print(json.dumps(json_result, indent=2, default=str))
        
        elif args.analyze_week:
            # Run weekly analysis
            run_weekly_analysis(args.analyze_week, args.min_edge)
        
        # Performance timing
        execution_time = time.time() - start_time
        if args.debug:
            logging.debug(f"Execution time: {execution_time:.2f} seconds")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        if args.debug if 'args' in locals() else False:
            logging.exception("Unexpected error occurred")
        else:
            logging.error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())