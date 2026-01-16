#!/bin/bash
# VPS Setup Script for BookieBenchmark
# Run this on a fresh Ubuntu 22.04 server

set -e

echo "=========================================="
echo "BookieBenchmark VPS Setup"
echo "=========================================="

# Update system
echo "[1/7] Updating system..."
apt update && apt upgrade -y

# Install Python and dependencies
echo "[2/7] Installing Python and system dependencies..."
apt install -y python3 python3-pip python3-venv ffmpeg git

# Create app directory
echo "[3/7] Setting up application directory..."
mkdir -p /opt/bookiebenchmark
cd /opt/bookiebenchmark

# Clone repository
echo "[4/7] Cloning repository..."
if [ -d ".git" ]; then
    git pull
else
    git clone https://github.com/wmjs/bookiebenchmark.git .
fi

# Create virtual environment and install dependencies
echo "[5/7] Installing Python dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p logs output data base_highlights config

echo "[6/7] Setup complete!"
echo ""
echo "=========================================="
echo "NEXT STEPS (run manually):"
echo "=========================================="
echo ""
echo "1. Upload your config files from your Mac:"
echo "   scp ~/Desktop/bookiebenchmark_config.tar.gz root@YOUR_SERVER_IP:/opt/bookiebenchmark/"
echo ""
echo "2. Upload your highlights video:"
echo "   scp ~/Desktop/githubpage/bookiebenchmark/base_highlights/30_mins_of_highlights_1.mp4 root@YOUR_SERVER_IP:/opt/bookiebenchmark/base_highlights/"
echo ""
echo "3. SSH back in and extract config:"
echo "   cd /opt/bookiebenchmark && tar -xzvf bookiebenchmark_config.tar.gz"
echo ""
echo "4. Test the pipeline:"
echo "   source venv/bin/activate && python3 main.py morning"
echo ""
echo "5. Set up cron (run: crontab -e) and add:"
echo "   0 5 * * * cd /opt/bookiebenchmark && /opt/bookiebenchmark/venv/bin/python3 main.py morning >> /opt/bookiebenchmark/logs/daily.log 2>&1"
echo ""
echo "=========================================="
