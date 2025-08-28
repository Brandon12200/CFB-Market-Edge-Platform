#!/usr/bin/env python3
"""
Weekly Predictions Script for College Football Market Edge Platform.

Generates contrarian betting predictions for upcoming week and stores them
for later performance evaluation.

Usage:
    python scripts/weekly_predictions.py [options]

Examples:
    python scripts/weekly_predictions.py                    # Current week
    python scripts/weekly_predictions.py --week 5           # Specific week
    python scripts/weekly_predictions.py --min-edge 1.5     # Higher edge threshold
    python scripts/weekly_predictions.py --dry-run          # Don't save results
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.prediction_engine import PredictionEngine
from utils.prediction_storage import prediction_storage
from utils.normalizer import TeamNameNormalizer
from data.data_manager import data_manager

team_name_normalizer = TeamNameNormalizer()


def get_current_week() -> int:
    """
    Get the current college football week.
    
    This is a simplified version - in a real implementation you'd
    want more sophisticated week detection based on dates.
    
    Returns:
        Current week number (always >= 1, never 0)
    """
    # For now, we'll use a simple calculation based on date
    # College football typically starts first week of September
    now = datetime.now()
    
    if now.month < 8:  # Before season starts
        return 1
    elif now.month >= 12:  # After regular season
        return 15
    
    # Rough approximation - could be improved with actual calendar
    if now.month == 8:
        return 1
    elif now.month == 9:
        week_of_month = (now.day - 1) // 7 + 1
        return min(week_of_month + 1, 5)
    elif now.month == 10:
        week_of_month = (now.day - 1) // 7 + 1
        return min(week_of_month + 5, 9)
    elif now.month == 11:
        week_of_month = (now.day - 1) // 7 + 1
        return min(week_of_month + 9, 13)
    else:
        return 14


def get_games_for_week(week: int) -> list:
    """
    Get all games for the specified week.
    
    This would ideally query your data sources for upcoming games.
    For now, we'll return a sample structure.
    
    Args:
        week: Week number
        
    Returns:
        List of game dictionaries
    """
    # TODO: Implement actual game fetching from your data sources
    # For now, return empty list - this will be filled in Phase 2
    
    print(f"⚠️  Note: Game fetching not yet implemented.")
    print(f"   This script currently analyzes manually specified games.")
    print(f"   In Phase 2, this will automatically fetch all Week {week} games.")
    
    return []


def analyze_games(games: list, min_edge: float = 1.0, min_confidence: float = 60.0) -> list:
    """
    Analyze games and identify contrarian opportunities.
    
    Args:
        games: List of game dictionaries
        min_edge: Minimum edge required to include prediction
        min_confidence: Minimum confidence required to include prediction
        
    Returns:
        List of prediction dictionaries
    """
    predictions = []
    prediction_engine = PredictionEngine()
    
    print(f"Analyzing {len(games)} games for contrarian opportunities...")
    print(f"Filters: min_edge={min_edge}, min_confidence={min_confidence}")
    print()
    
    for i, game in enumerate(games, 1):
        try:
            home_team = game['home_team']
            away_team = game['away_team']
            week = game.get('week', get_current_week())
            
            print(f"[{i}/{len(games)}] Analyzing {away_team} @ {home_team}...")
            
            # Run prediction
            result = prediction_engine.generate_prediction(home_team, away_team, week=week)
            
            # Extract key metrics
            edge_size = result.get('edge_size', 0)
            confidence = result.get('confidence_score', 0) * 100
            
            print(f"    Edge: {edge_size:.1f} points, Confidence: {confidence:.1f}%")
            
            # Check if this meets our thresholds
            if edge_size >= min_edge and confidence >= min_confidence:
                # Extract recommendation and other details
                vegas_spread = result.get('vegas_spread', 'Unknown')
                recommendation = result.get('recommendation', 'No recommendation')
                
                # Create prediction entry
                prediction = prediction_storage.create_prediction_entry(
                    home_team=home_team,
                    away_team=away_team,
                    vegas_spread=vegas_spread,
                    predicted_edge=edge_size,
                    confidence=confidence,
                    recommendation=recommendation,
                    factor_breakdown=result.get('factor_breakdown', {}),
                    data_quality=result.get('data_quality', 0),
                    week=week,
                    rationale=result.get('reasoning', '')
                )
                
                predictions.append(prediction)
                print(f"    ✅ EDGE FOUND: {recommendation}")
            else:
                reasons = []
                if edge_size < min_edge:
                    reasons.append(f"edge too small ({edge_size:.1f} < {min_edge})")
                if confidence < min_confidence:
                    reasons.append(f"confidence too low ({confidence:.1f}% < {min_confidence}%)")
                print(f"    ❌ No edge: {', '.join(reasons)}")
            
            print()
            
        except Exception as e:
            print(f"    🚨 Error analyzing {away_team} @ {home_team}: {e}")
            print()
            continue
    
    return predictions


def generate_sample_games(week: int) -> list:
    """
    Generate sample games for testing purposes.
    
    This is a temporary function to demonstrate the script functionality.
    In Phase 2, this will be replaced with actual game fetching.
    
    Args:
        week: Week number
        
    Returns:
        List of sample game dictionaries
    """
    sample_games = [
        {"home_team": "Ohio State", "away_team": "Michigan", "week": week},
        {"home_team": "Alabama", "away_team": "Georgia", "week": week},
        {"home_team": "Texas", "away_team": "Oklahoma", "week": week},
        {"home_team": "Notre Dame", "away_team": "USC", "week": week},
        {"home_team": "Clemson", "away_team": "Florida State", "week": week}
    ]
    
    return sample_games


def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(
        description='Generate weekly contrarian betting predictions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        Generate predictions for current week
  %(prog)s --week 5               Generate predictions for Week 5  
  %(prog)s --min-edge 1.5         Require 1.5+ point edges
  %(prog)s --min-confidence 70    Require 70%+ confidence
  %(prog)s --dry-run              Show results without saving
  %(prog)s --sample               Use sample games for testing
        """
    )
    
    parser.add_argument('--week', type=int, 
                       help='Week number (default: current week)')
    parser.add_argument('--min-edge', type=float, default=1.0,
                       help='Minimum edge in points (default: 1.0)')
    parser.add_argument('--min-confidence', type=float, default=60.0,
                       help='Minimum confidence percentage (default: 60)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show results without saving to files')
    parser.add_argument('--sample', action='store_true',
                       help='Use sample games for testing')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Determine week (ensure it's never 0)
    week = args.week if args.week else get_current_week()
    
    if week == 0:
        print("❌ Week 0 is excluded from analysis. Using Week 1 instead.")
        week = 1
    
    print("=" * 60)
    print("College Football Market Edge Platform - Weekly Predictions")
    print("=" * 60)
    print(f"Week: {week}")
    print(f"Filters: Edge ≥ {args.min_edge}, Confidence ≥ {args.min_confidence}%")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()
    
    try:
        # Get games for analysis
        if args.sample:
            print("🧪 Using sample games for testing...")
            games = generate_sample_games(week)
        else:
            games = get_games_for_week(week)
        
        if not games:
            print("❌ No games found for analysis.")
            print("   Try using --sample flag to test with sample games.")
            return 1
        
        # Analyze games
        predictions = analyze_games(
            games, 
            min_edge=args.min_edge, 
            min_confidence=args.min_confidence
        )
        
        # Display results
        print("=" * 60)
        print("PREDICTION RESULTS")
        print("=" * 60)
        
        if predictions:
            print(f"Games with contrarian opportunities: {len(predictions)}")
            print()
            
            for i, pred in enumerate(predictions, 1):
                print(f"{i}. {pred['recommendation']}")
                print(f"   Edge: {pred['predicted_edge']} points")
                print(f"   Confidence: {pred['confidence']}%")
                print(f"   Game: {pred['away_team']} @ {pred['home_team']}")
                if pred.get('bet_rationale'):
                    print(f"   Rationale: {pred['bet_rationale']}")
                print()
        else:
            print("❌ No contrarian opportunities found.")
            print(f"   Analyzed {len(games)} games")
            print(f"   Try lowering --min-edge or --min-confidence")
        
        # Save results (unless dry run)
        if not args.dry_run and predictions:
            filepath = prediction_storage.save_weekly_predictions(predictions, week)
            print("=" * 60)
            print(f"✅ Predictions saved to: {filepath}")
            print()
            print("Next steps:")
            print(f"  1. Wait for Week {week} games to complete")
            print(f"  2. Run: python scripts/check_results.py --week {week}")
            print(f"  3. View performance in data/performance_tracker.json")
        elif args.dry_run:
            print("=" * 60)
            print("🧪 DRY RUN - Results not saved")
            print(f"   Would save {len(predictions)} predictions to Week {week} file")
        
        return 0
        
    except KeyboardInterrupt:
        print("\\n❌ Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())