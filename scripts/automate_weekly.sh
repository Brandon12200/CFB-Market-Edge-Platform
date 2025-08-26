#!/bin/bash

# Weekly Automation Script for College Football Market Edge Platform
# 
# This script automates the weekly prediction and results checking workflow.
# Designed to be run via cron jobs or manual execution.
#
# Usage:
#   ./scripts/automate_weekly.sh [predictions|results|both]
#
# Cron job examples:
#   # Tuesday 8 AM: Generate predictions
#   0 8 * * 2 cd /path/to/project && ./scripts/automate_weekly.sh predictions
#   
#   # Monday 9 AM: Check results
#   0 9 * * 1 cd /path/to/project && ./scripts/automate_weekly.sh results

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Ensure logs directory exists
mkdir -p "$LOG_DIR"

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/automation.log"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_DIR/automation.log" >&2
}

# Function to check if virtual environment exists and is activated
check_venv() {
    if [[ ! -d "$PROJECT_DIR/venv" ]]; then
        error "Virtual environment not found at $PROJECT_DIR/venv"
        error "Please create it with: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
    
    # Activate virtual environment
    source "$PROJECT_DIR/venv/bin/activate"
    log "Virtual environment activated"
}

# Function to generate weekly predictions
run_predictions() {
    log "Starting weekly predictions generation..."
    
    local output_file="$LOG_DIR/predictions_$DATE.log"
    local error_file="$LOG_DIR/predictions_error_$DATE.log"
    
    cd "$PROJECT_DIR"
    
    # Run predictions with reasonable thresholds
    if python scripts/weekly_predictions.py --min-edge 1.0 --min-confidence 65 > "$output_file" 2> "$error_file"; then
        log "✅ Weekly predictions generated successfully"
        
        # Count predictions made
        local pred_count=$(grep -c "✅ EDGE FOUND" "$output_file" || echo "0")
        log "📊 Generated $pred_count predictions this week"
        
        # Send notification if predictions were made
        if [[ $pred_count -gt 0 ]]; then
            log "🎯 Found contrarian opportunities - check predictions file"
        else
            log "ℹ️  No contrarian opportunities found this week"
        fi
        
    else
        error "Failed to generate weekly predictions"
        error "Check logs: $output_file and $error_file"
        exit 1
    fi
}

# Function to check previous week's results
run_results_check() {
    log "Starting weekly results check..."
    
    local output_file="$LOG_DIR/results_$DATE.log"
    local error_file="$LOG_DIR/results_error_$DATE.log"
    
    cd "$PROJECT_DIR"
    
    # Run results check
    if python scripts/check_results.py --detailed-report > "$output_file" 2> "$error_file"; then
        log "✅ Weekly results check completed successfully"
        
        # Extract key metrics from output
        local win_rate=$(grep "Win Rate:" "$output_file" | head -1 | sed 's/.*Win Rate: //' || echo "N/A")
        local predictions=$(grep "Predictions:" "$output_file" | head -1 | sed 's/.*Predictions: //' || echo "0")
        
        log "📊 Week Results - Predictions: $predictions, Win Rate: $win_rate"
        
    else
        error "Failed to check weekly results"
        error "Check logs: $output_file and $error_file"
        exit 1
    fi
}

# Function to generate performance report
generate_report() {
    log "Generating performance dashboard..."
    
    local report_file="$LOG_DIR/dashboard_$DATE.txt"
    local html_report="$PROJECT_DIR/latest_performance_report.html"
    
    cd "$PROJECT_DIR"
    
    # Generate both text and HTML reports
    if python scripts/generate_report.py --save-text "$report_file" --save-html "$html_report" --quiet; then
        log "✅ Performance reports generated"
        log "📄 Text report: $report_file"
        log "🌐 HTML report: $html_report"
    else
        error "Failed to generate performance reports"
    fi
}

# Function to cleanup old log files
cleanup_logs() {
    log "Cleaning up old log files..."
    
    # Keep logs for 30 days
    find "$LOG_DIR" -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    
    log "✅ Log cleanup completed"
}

# Function to check system health
health_check() {
    log "Performing system health check..."
    
    cd "$PROJECT_DIR"
    
    # Check if main modules can be imported
    if python -c "from engine.prediction_engine import PredictionEngine; print('✅ Core system healthy')" 2>/dev/null; then
        log "✅ System health check passed"
    else
        error "System health check failed - core modules not loading"
        exit 1
    fi
    
    # Check data directory structure
    for dir in "data/predictions" "data/results" "logs"; do
        if [[ ! -d "$PROJECT_DIR/$dir" ]]; then
            error "Missing required directory: $dir"
            exit 1
        fi
    done
    
    log "✅ Directory structure verified"
}

# Function to send notifications (placeholder for future enhancement)
send_notification() {
    local message="$1"
    log "📬 Notification: $message"
    
    # Future: Could integrate with Slack, Discord, email, etc.
    # For now, just log the message
}

# Main execution function
main() {
    local mode="${1:-both}"
    
    log "=========================================="
    log "College Football Market Edge Platform"
    log "Weekly Automation Script"
    log "Mode: $mode"
    log "=========================================="
    
    # Pre-flight checks
    check_venv
    health_check
    
    case "$mode" in
        "predictions")
            run_predictions
            generate_report
            send_notification "Weekly predictions generated"
            ;;
        "results")
            run_results_check
            generate_report
            send_notification "Weekly results processed"
            ;;
        "both")
            # This mode is for manual runs - does both operations
            log "Running both predictions and results check..."
            run_predictions
            sleep 2
            run_results_check
            generate_report
            send_notification "Full weekly cycle completed"
            ;;
        *)
            error "Invalid mode: $mode"
            error "Usage: $0 [predictions|results|both]"
            exit 1
            ;;
    esac
    
    # Cleanup
    cleanup_logs
    
    log "✅ Weekly automation completed successfully"
    log "=========================================="
}

# Handle script interruption gracefully
trap 'error "Script interrupted"; exit 1' INT TERM

# Run main function with all arguments
main "$@"