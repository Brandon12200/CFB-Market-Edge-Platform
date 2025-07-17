# CFB Contrarian Predictor - Troubleshooting Guide

## Common Issues and Solutions

### API-Related Issues

#### 1. "ODDS_API_KEY not found in environment variables"

**Symptoms**: Warning message during startup, no betting lines available

**Cause**: Missing or incorrectly configured Odds API key

**Solution**:
```bash
# Check if .env file exists
ls -la .env

# If missing, copy from template
cp .env.example .env

# Edit .env file and add your API key
# ODDS_API_KEY=your_actual_api_key_here
```

**Verification**:
```bash
python -c "from config import config; print('API Key configured:', bool(config.odds_api_key))"
```

#### 2. "Rate limit exceeded" or 429 errors

**Symptoms**: API calls failing with rate limit messages

**Cause**: Too many API requests in short timeframe

**Solutions**:
- **Wait**: Rate limits reset automatically (Odds API: daily, ESPN: per minute)
- **Check quota**: Verify remaining API quota
- **Adjust settings**: Reduce rate limits in config

```bash
# Check current rate limit settings
python -c "from config import config; print('Odds limit:', config.rate_limit_odds, 'ESPN limit:', config.rate_limit_espn)"

# Set lower rate limits in .env
# ODDS_API_RATE_LIMIT=50
# ESPN_API_RATE_LIMIT=30
```

#### 3. "Could not connect to API" errors

**Symptoms**: Network connection errors, timeouts

**Cause**: Network connectivity issues or API service down

**Solutions**:
1. **Check internet connection**:
   ```bash
   ping google.com
   ```

2. **Test API endpoints directly**:
   ```bash
   curl "https://api.the-odds-api.com/v4/sports?apiKey=YOUR_KEY"
   curl "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams"
   ```

3. **Check firewall/proxy settings**: Ensure ports 80/443 are open

4. **Run health check**:
   ```bash
   python -c "from utils.health_check import health_checker; print(health_checker.quick_health_check())"
   ```

### Team Name Issues

#### 4. "Invalid team names - could not normalize"

**Symptoms**: Error when entering team names

**Cause**: Team name not recognized by normalizer

**Solutions**:
1. **Try different variations**:
   - Full name: "University of Georgia" → "Georgia"
   - Common name: "Georgia Bulldogs" → "Georgia"
   - Abbreviation: "UGA" → "Georgia"

2. **Check available teams**:
   ```bash
   python -c "from normalizer import normalizer; teams = normalizer.get_all_teams(); print(f'Total teams: {len(teams)}'); print('Sample:', list(teams)[:10])"
   ```

3. **Test normalization**:
   ```bash
   python -c "from normalizer import normalizer; print(normalizer.normalize('georgia'))"
   ```

#### 5. "Home and away teams cannot be the same"

**Symptoms**: Error when both teams normalize to same value

**Cause**: Both inputs resolve to the same team

**Solution**: Use different team names or check for typos

### Performance Issues

#### 6. Predictions taking too long (>15 seconds)

**Symptoms**: Slow execution times

**Causes & Solutions**:

1. **Network latency**:
   ```bash
   # Test API response times
   time curl "https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams"
   ```

2. **Too many API calls**:
   ```bash
   # Check API call count in verbose mode
   python main.py --home georgia --away alabama --verbose
   ```

3. **Cache not working**:
   ```bash
   # Check cache directory
   ls -la /tmp/cfb_predictor_cache/ 2>/dev/null || echo "No cache directory"
   
   # Clear cache if corrupted
   rm -rf /tmp/cfb_predictor_cache/
   ```

4. **System resources**:
   ```bash
   # Check system resources
   python -c "
   import psutil
   print(f'CPU: {psutil.cpu_percent()}%')
   print(f'Memory: {psutil.virtual_memory().percent}%')
   "
   ```

#### 7. High memory usage

**Symptoms**: System slowdown, memory warnings

**Solutions**:
1. **Restart application** to clear memory
2. **Reduce cache size** in configuration
3. **Check for memory leaks**:
   ```bash
   python -c "
   from utils.monitoring import system_monitor
   summary = system_monitor.get_performance_summary()
   print('Memory usage:', summary.get('current_memory_usage', 'unknown'))
   "
   ```

### Factor Calculation Issues

#### 8. "Factor calculation failed" errors

**Symptoms**: Missing factor results, reduced confidence

**Cause**: Factor calculator encountered error

**Solutions**:
1. **Check factor registry**:
   ```bash
   python -c "
   from factors.factor_registry import factor_registry
   validation = factor_registry.validate_factor_configuration()
   print('Valid:', validation.get('valid'))
   print('Errors:', validation.get('errors', []))
   "
   ```

2. **Test individual factors**:
   ```bash
   python -c "
   from factors.factor_registry import factor_registry
   result = factor_registry.calculate_all_factors('GEORGIA', 'ALABAMA', {})
   print('Successful factors:', result['summary']['factors_successful'])
   print('Total factors:', result['summary']['factors_calculated'])
   "
   ```

3. **Check for missing data dependencies**

### Output and Display Issues

#### 9. Garbled or missing output formatting

**Symptoms**: Poor formatting, missing emojis, alignment issues

**Solutions**:
1. **Check terminal compatibility**:
   ```bash
   echo "Test emoji: 🎯 📊 ✅"
   ```

2. **Update terminal width**:
   ```bash
   python main.py --home georgia --away alabama --terminal-width 120
   ```

3. **Disable emojis if needed**:
   ```bash
   python main.py --home georgia --away alabama --no-emojis
   ```

#### 10. "No meaningful contrarian opportunity" for all games

**Symptoms**: All predictions show no edge

**Causes**:
1. **Low data quality**: Check data quality percentage in output
2. **Conservative thresholds**: Edges below minimum threshold
3. **Market efficiency**: Genuinely no edges available

**Solutions**:
1. **Lower edge threshold**:
   ```bash
   python main.py --home georgia --away alabama --min-edge 0.5
   ```

2. **Check data quality**:
   ```bash
   python main.py --home georgia --away alabama --verbose
   ```

### System Health Issues

#### 11. Running system health check

**Regular health monitoring**:
```bash
# Quick health check
python -c "from utils.health_check import health_checker; print(health_checker.quick_health_check())"

# Full health check
python -c "
from utils.health_check import health_checker
import json
result = health_checker.run_full_health_check()
print('Overall status:', result['overall_status'])
for component, status in result['components'].items():
    print(f'{component}: {status[\"status\"]} - {status[\"message\"]}')
"
```

**Interpreting health check results**:
- **Healthy**: Component working normally
- **Warning**: Component working but with issues
- **Critical**: Component not working

#### 12. Monitoring system performance

**Check performance metrics**:
```bash
python -c "
from utils.monitoring import system_monitor
summary = system_monitor.get_performance_summary()
print('Predictions:', summary.get('total_predictions'))
print('Avg time:', summary.get('avg_prediction_time'))
print('API calls:', summary.get('total_api_calls'))
print('Errors:', summary.get('total_errors'))
"
```

## Error Message Reference

### Common Error Messages and Meanings

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| `ODDS_API_KEY not found` | API key not configured | Add API key to .env file |
| `Rate limit exceeded` | Too many API calls | Wait or reduce rate limits |
| `Could not normalize teams` | Team name not recognized | Try different team name |
| `Prediction failed` | General prediction error | Check logs, run health check |
| `No betting line available` | No odds data for game | Check if game exists in current week |
| `System in recovery mode` | System operating with limitations | Wait for recovery or restart |

### Log File Locations

**Development**:
- Console output only

**Production**:
- Main log: `logs/cfb_predictor.log`
- Error log: `logs/cfb_predictor_errors.log`

```bash
# View recent logs
tail -f logs/cfb_predictor.log

# View recent errors
tail -f logs/cfb_predictor_errors.log

# Search for specific errors
grep "ERROR" logs/cfb_predictor.log
```

## Diagnostic Commands

### Quick Diagnostic Script
```bash
#!/bin/bash
echo "=== CFB Predictor Diagnostics ==="

echo "1. Configuration Check:"
python -c "from config import config; print('Odds API:', bool(config.odds_api_key)); print('Debug mode:', config.debug)"

echo "2. Health Check:"
python -c "from utils.health_check import health_checker; print(health_checker.quick_health_check())"

echo "3. Team Normalizer:"
python -c "from normalizer import normalizer; print('Test normalization:', normalizer.normalize('georgia'))"

echo "4. Basic Prediction:"
python main.py --home georgia --away alabama 2>/dev/null | head -10

echo "5. System Resources:"
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"

echo "=== Diagnostics Complete ==="
```

### Performance Profiling
```bash
# Profile prediction performance
python -m cProfile -s cumulative main.py --home georgia --away alabama

# Memory profiling (if memory_profiler installed)
python -m memory_profiler main.py --home georgia --away alabama
```

## Getting Help

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
python main.py --home georgia --away alabama --verbose
```

### Collecting Debug Information
When reporting issues, include:

1. **System information**:
   ```bash
   python --version
   pip list | grep -E "(requests|beautifulsoup4|python-dotenv)"
   uname -a
   ```

2. **Configuration (sanitized)**:
   ```bash
   python -c "from config import config; print(config)"
   ```

3. **Health check results**:
   ```bash
   python -c "from utils.health_check import health_checker; import json; print(json.dumps(health_checker.run_full_health_check(), indent=2))"
   ```

4. **Recent logs** (if available)

### Reset System State
```bash
# Clear all caches
rm -rf /tmp/cfb_predictor_cache/

# Reset error tracking
python -c "from utils.error_handler import error_handler; error_handler.reset_error_tracking()"

# Restart with fresh state
python main.py --home georgia --away alabama
```

### Emergency Recovery Mode
If system is completely non-functional:

```bash
# Minimal functionality test
python -c "
try:
    from normalizer import normalizer
    print('Normalizer working:', normalizer.normalize('georgia'))
except Exception as e:
    print('Normalizer error:', e)

try:
    from utils.error_handler import error_handler
    result = error_handler.recovery_mode_prediction('georgia', 'alabama')
    print('Recovery mode working:', result.get('prediction_type'))
except Exception as e:
    print('Recovery mode error:', e)
"
```

This troubleshooting guide should help resolve most common issues. For persistent problems, enable debug mode and collect diagnostic information for further analysis.