#!/bin/bash
# Setup cron jobs for BookieBenchmark
# Run this script once to install the cron jobs

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)
LOG_DIR="$SCRIPT_DIR/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "Setting up BookieBenchmark cron jobs..."
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"

# Create a temporary file with new cron entries
TEMP_CRON=$(mktemp)

# Export existing crontab
crontab -l 2>/dev/null > "$TEMP_CRON"

# Remove any existing BookieBenchmark entries
sed -i '' '/BookieBenchmark/d' "$TEMP_CRON" 2>/dev/null || sed -i '/BookieBenchmark/d' "$TEMP_CRON"

# Add new cron entries
cat >> "$TEMP_CRON" << EOF

# BookieBenchmark - Daily pipeline (5 AM)
0 5 * * * cd $SCRIPT_DIR && $PYTHON_PATH main.py morning >> $LOG_DIR/daily.log 2>&1 # BookieBenchmark
EOF

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo ""
echo "Cron jobs installed successfully!"
echo ""
echo "Schedule:"
echo "  - Daily pipeline: 5:00 AM (results + predictions + videos)"
echo ""
echo "Logs will be written to: $LOG_DIR"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove cron jobs: crontab -e (and delete the BookieBenchmark lines)"
