# CFB Contrarian Predictor - Production Setup Guide

## Local Production Configuration

This guide helps you configure the CFB Contrarian Predictor for optimized local production use.

### Environment Configuration

#### 1. Production Environment Variables

Create or update your `.env` file with production settings:

```bash
# Copy production template
cp .env.example .env.production

# Edit production configuration
cat > .env.production << 'EOF'
# Production Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# API Configuration
ODDS_API_KEY=your_actual_api_key_here
ODDS_API_RATE_LIMIT=75
ESPN_API_RATE_LIMIT=45

# Performance Tuning
CACHE_TTL=7200
SESSION_CACHE_SIZE=2000
MAX_EXECUTION_TIME=12
MAX_API_CALLS_PER_PREDICTION=15

# Local Production Settings
LOCAL_PRODUCTION=true
ENABLE_FILE_LOGGING=true
LOG_ROTATION=true
EOF
```

#### 2. Load Production Configuration

```bash
# Use production environment
cp .env.production .env

# Or source it directly
export $(cat .env.production | xargs)
```

### Performance Optimization

#### 1. System Resource Limits

```bash
# Check current limits
ulimit -a

# Increase file descriptor limit if needed
ulimit -n 4096

# For persistent changes, edit ~/.bashrc or ~/.zshrc:
echo 'ulimit -n 4096' >> ~/.bashrc
```

#### 2. Python Optimization

```bash
# Use optimized Python execution
export PYTHONOPTIMIZE=1

# Disable Python assertions for production
export PYTHONDONTWRITEBYTECODE=1

# Set optimal garbage collection
export PYTHONGC=1
```

#### 3. Cache Configuration

Create cache directory with proper permissions:

```bash
# Create cache directory
sudo mkdir -p /var/cache/cfb_predictor
sudo chown $USER:$USER /var/cache/cfb_predictor
chmod 755 /var/cache/cfb_predictor

# Or use user cache directory
mkdir -p ~/.cache/cfb_predictor
export CFB_CACHE_DIR=~/.cache/cfb_predictor
```

### Logging Configuration

#### 1. Log Directory Setup

```bash
# Create logs directory
mkdir -p logs
chmod 755 logs

# Set up log rotation (if logrotate is available)
sudo tee /etc/logrotate.d/cfb_predictor << 'EOF'
/path/to/cfb-contrarian-predictor/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 user user
}
EOF
```

#### 2. Production Logging Configuration

The system automatically configures production logging when `ENVIRONMENT=production`:

- **Main log**: `logs/cfb_predictor.log` (10MB max, 5 rotations)
- **Error log**: `logs/cfb_predictor_errors.log` (5MB max, 3 rotations)
- **Log level**: WARNING and above
- **Automatic rotation**: Enabled

### Monitoring Setup

#### 1. Health Check Automation

Create a health check script:

```bash
#!/bin/bash
# healthcheck.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load production environment
export $(cat .env.production | xargs) 2>/dev/null

echo "$(date): Running health check"

# Run quick health check
python -c "
from utils.health_check import health_checker
import json
result = health_checker.quick_health_check()
issues = [k for k, v in result.items() if v not in ['healthy', 'not_configured']]
if issues:
    print(f'HEALTH ISSUES: {issues}')
    exit(1)
else:
    print('HEALTH OK')
"

if [ $? -eq 0 ]; then
    echo "$(date): Health check passed"
else
    echo "$(date): Health check failed"
    # Optional: send alert email/notification
fi
```

Make it executable and add to cron:

```bash
chmod +x healthcheck.sh

# Add to crontab (every 15 minutes)
(crontab -l 2>/dev/null; echo "*/15 * * * * /path/to/cfb-contrarian-predictor/healthcheck.sh >> logs/healthcheck.log 2>&1") | crontab -
```

#### 2. Performance Monitoring

Create a performance monitoring script:

```bash
#!/bin/bash
# performance_monitor.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export $(cat .env.production | xargs) 2>/dev/null

# Monitor prediction performance
python -c "
from utils.monitoring import system_monitor
import json
import datetime

summary = system_monitor.get_performance_summary()
timestamp = datetime.datetime.now().isoformat()

# Log performance metrics
metrics = {
    'timestamp': timestamp,
    'predictions': summary.get('total_predictions', 0),
    'avg_time': summary.get('avg_prediction_time', 0),
    'api_calls': summary.get('total_api_calls', 0),
    'errors': summary.get('total_errors', 0),
    'memory_mb': summary.get('current_memory_usage', 0)
}

print(json.dumps(metrics))

# Alert on performance issues
if metrics['avg_time'] > 10:
    print(f'ALERT: Slow performance - avg time {metrics[\"avg_time\"]:.2f}s')
if metrics['errors'] > 10:
    print(f'ALERT: High error rate - {metrics[\"errors\"]} errors')
" >> logs/performance.log
```

### Security Configuration

#### 1. File Permissions

```bash
# Secure configuration files
chmod 600 .env .env.production
chmod 644 *.py
chmod 755 . logs

# Secure log files
chmod 644 logs/*.log
```

#### 2. API Key Security

```bash
# Verify API key is not in code
grep -r "YOUR_API_KEY\|your_api_key" . --exclude-dir=.git --exclude="*.md" || echo "No hardcoded API keys found"

# Check for sensitive data in logs
grep -i "api_key\|password\|secret" logs/*.log 2>/dev/null || echo "No sensitive data in logs"
```

### System Service Setup (Optional)

For running as a system service:

#### 1. Create Service Script

```bash
# cfb_predictor_service.py
#!/usr/bin/env python3
"""
Simple HTTP service for CFB Predictor
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.prediction_engine import prediction_engine
from utils.health_check import health_checker

class CFBHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health = health_checker.quick_health_check()
            self.wfile.write(json.dumps(health).encode())
            
        elif parsed.path == '/predict':
            query = parse_qs(parsed.query)
            home = query.get('home', [''])[0]
            away = query.get('away', [''])[0]
            
            if not home or not away:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Missing home or away team')
                return
            
            try:
                result = prediction_engine.generate_prediction(home, away)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode())
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Error: {str(e)}'.encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    # Load production environment
    from dotenv import load_dotenv
    load_dotenv('.env.production')
    
    port = int(os.getenv('CFB_SERVICE_PORT', 8080))
    
    server = HTTPServer(('localhost', port), CFBHandler)
    print(f'CFB Predictor service running on port {port}')
    print(f'Health check: http://localhost:{port}/health')
    print(f'Predictions: http://localhost:{port}/predict?home=georgia&away=alabama')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        server.shutdown()
```

#### 2. Create Systemd Service (Linux)

```bash
# /etc/systemd/system/cfb-predictor.service
sudo tee /etc/systemd/system/cfb-predictor.service << 'EOF'
[Unit]
Description=CFB Contrarian Predictor Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/cfb-contrarian-predictor
Environment=CFB_SERVICE_PORT=8080
ExecStart=/usr/bin/python3 cfb_predictor_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cfb-predictor
sudo systemctl start cfb-predictor

# Check status
sudo systemctl status cfb-predictor
```

### Backup and Recovery

#### 1. Configuration Backup

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp .env.production "$BACKUP_DIR/"
cp -r docs/ "$BACKUP_DIR/"

# Backup logs (last 7 days)
find logs/ -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/" \;

# Create archive
tar -czf "cfb_predictor_backup_$(date +%Y%m%d).tar.gz" "$BACKUP_DIR"

echo "Backup created: cfb_predictor_backup_$(date +%Y%m%d).tar.gz"
```

#### 2. Recovery Procedures

```bash
#!/bin/bash
# recovery.sh

echo "CFB Predictor Recovery Mode"

# 1. Reset error tracking
python -c "from utils.error_handler import error_handler; error_handler.reset_error_tracking()"

# 2. Clear cache
rm -rf ~/.cache/cfb_predictor/* 2>/dev/null
rm -rf /tmp/cfb_predictor_cache/* 2>/dev/null

# 3. Test basic functionality
echo "Testing basic functionality..."
python -c "
try:
    from normalizer import normalizer
    print('✓ Normalizer working')
    
    from engine.prediction_engine import prediction_engine
    print('✓ Prediction engine loaded')
    
    from utils.health_check import health_checker
    health = health_checker.quick_health_check()
    print('✓ Health check:', health)
    
except Exception as e:
    print('✗ Recovery failed:', e)
    exit(1)
"

echo "Recovery complete"
```

### Production Checklist

Before going live with production configuration:

- [ ] **Environment Variables**: All production variables set
- [ ] **API Keys**: Valid and tested
- [ ] **Permissions**: Files have correct permissions
- [ ] **Logging**: Log directory created and writable
- [ ] **Monitoring**: Health checks and performance monitoring active
- [ ] **Backup**: Backup procedures tested
- [ ] **Recovery**: Recovery procedures documented and tested
- [ ] **Security**: No sensitive data in logs or code
- [ ] **Performance**: System meeting performance targets

### Maintenance Tasks

#### Daily
- Check health status
- Review error logs
- Monitor API quota usage

#### Weekly
- Review performance metrics
- Clean old cache files
- Check disk space

#### Monthly
- Backup configuration
- Review and rotate logs
- Update dependencies if needed

### Production Environment Variables Reference

| Variable | Default | Production | Description |
|----------|---------|------------|-------------|
| `ENVIRONMENT` | development | production | Environment mode |
| `DEBUG` | true | false | Debug logging |
| `LOG_LEVEL` | INFO | WARNING | Log level |
| `CACHE_TTL` | 3600 | 7200 | Cache lifetime (seconds) |
| `MAX_EXECUTION_TIME` | 15 | 12 | Max prediction time (seconds) |
| `ODDS_API_RATE_LIMIT` | 83 | 75 | Daily API call limit |
| `ESPN_API_RATE_LIMIT` | 60 | 45 | Per-minute API call limit |

This production setup provides a robust, monitored, and maintainable local production environment for the CFB Contrarian Predictor.