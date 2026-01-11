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

# BookieBenchmark - Morning pipeline (8 AM daily)
0 8 * * * cd $SCRIPT_DIR && $PYTHON_PATH main.py morning >> $LOG_DIR/morning.log 2>&1 # BookieBenchmark

# BookieBenchmark - Evening results update (11 PM daily)
0 23 * * * cd $SCRIPT_DIR && $PYTHON_PATH main.py evening >> $LOG_DIR/evening.log 2>&1 # BookieBenchmark
EOF

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo ""
echo "Cron jobs installed successfully!"
echo ""
echo "Schedule:"
echo "  - Morning pipeline: 8:00 AM daily"
echo "  - Evening results:  11:00 PM daily"
echo ""
echo "Logs will be written to: $LOG_DIR"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove cron jobs: crontab -e (and delete the BookieBenchmark lines)"
