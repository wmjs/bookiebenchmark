#!/bin/bash
# VPS Setup Script for BookieBenchmark
# Run this on a fresh Ubuntu 22.04 server (e.g., Hetzner CX22)

set -e

echo "=========================================="
echo "BookieBenchmark VPS Setup"
echo "=========================================="

# Update system
echo "[1/8] Updating system..."
apt update && apt upgrade -y

# Install Python and dependencies
echo "[2/8] Installing Python and system dependencies..."
apt install -y python3 python3-pip python3-venv ffmpeg git

# Set timezone to EST for 5 AM cron jobs
echo "[3/8] Setting timezone to America/New_York..."
timedatectl set-timezone America/New_York

# Create app directory
echo "[4/8] Setting up application directory..."
mkdir -p /opt/bookiebenchmark
cd /opt/bookiebenchmark

# Create virtual environment and install dependencies
echo "[5/8] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Create directories
mkdir -p logs output data base_highlights config

echo "[6/8] Setup complete!"
echo ""
echo "=========================================="
echo "NEXT STEPS (run manually):"
echo "=========================================="
echo ""
echo "1. Upload project files from your Mac:"
echo "   rsync -avz -e 'ssh -i ~/.ssh/hetzner' --exclude '.git' --exclude '__pycache__' --exclude 'output' --exclude 'data' --exclude 'venv' ~/Desktop/githubpage/bookiebenchmark/ root@YOUR_SERVER_IP:/opt/bookiebenchmark/"
echo ""
echo "2. Upload your highlights video (1.2GB):"
echo "   scp -i ~/.ssh/hetzner ~/Desktop/githubpage/bookiebenchmark/base_highlights/30_mins_of_highlights_1.mp4 root@YOUR_SERVER_IP:/opt/bookiebenchmark/base_highlights/"
echo ""
echo "3. SSH in and install Python dependencies:"
echo "   ssh -i ~/.ssh/hetzner root@YOUR_SERVER_IP"
echo "   cd /opt/bookiebenchmark && source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Apply moviepy Pillow compatibility patch:"
echo "   sed -i 's/Image.ANTIALIAS/Image.Resampling.LANCZOS/g' /opt/bookiebenchmark/venv/lib/python3.*/site-packages/moviepy/video/fx/resize.py"
echo ""
echo "5. Upload config files (API keys, tokens):"
echo "   scp -i ~/.ssh/hetzner ~/Desktop/githubpage/bookiebenchmark/config/.env root@YOUR_SERVER_IP:/opt/bookiebenchmark/config/"
echo "   scp -i ~/.ssh/hetzner ~/Desktop/githubpage/bookiebenchmark/config/credentials.json root@YOUR_SERVER_IP:/opt/bookiebenchmark/config/"
echo "   scp -i ~/.ssh/hetzner ~/Desktop/githubpage/bookiebenchmark/config/drive_token.json root@YOUR_SERVER_IP:/opt/bookiebenchmark/config/"
echo "   scp -i ~/.ssh/hetzner ~/Desktop/githubpage/bookiebenchmark/config/sheets_token.json root@YOUR_SERVER_IP:/opt/bookiebenchmark/config/"
echo ""
echo "6. Copy your local database (to preserve history):"
echo "   scp -i ~/.ssh/hetzner ~/Desktop/githubpage/bookiebenchmark/data/predictions.db root@YOUR_SERVER_IP:/opt/bookiebenchmark/data/"
echo ""
echo "7. Test the pipeline:"
echo "   source venv/bin/activate && python3 main.py morning --skip-content"
echo ""
echo "8. Set up cron jobs (run: crontab -e) and add:"
echo "   # Daily pipeline at 5 AM EST"
echo "   0 5 * * * cd /opt/bookiebenchmark && /opt/bookiebenchmark/venv/bin/python3 main.py morning >> /opt/bookiebenchmark/logs/daily.log 2>&1"
echo "   # Weekly summary at 6 AM EST on Sundays"
echo "   0 6 * * 0 cd /opt/bookiebenchmark && /opt/bookiebenchmark/venv/bin/python3 main.py weekly >> /opt/bookiebenchmark/logs/weekly.log 2>&1"
echo ""
echo "=========================================="
