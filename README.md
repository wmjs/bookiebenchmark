# BookieBenchmark

AI vs Vegas: Which AI can beat the bookies? An automated system that benchmarks AI models (ChatGPT, Claude, Gemini, Grok) on NBA game predictions and generates TikTok/Instagram Reels content.

## What It Does

1. **Fetches tomorrow's NBA games** from ESPN
2. **Gets Vegas betting lines** for each game
3. **Queries 4 AI models** for their predictions and confidence levels
4. **Tracks performance** of each model over time
5. **Generates short-form video content** with dramatic voiceovers and animated captions
6. **Syncs everything to Google Sheets** for mobile access

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install ffmpeg (required for video processing)
brew install ffmpeg
```

### 2. Set Up API Keys

Copy the example config and add your API keys:

```bash
cp config/.env.example config/.env
```

Edit `config/.env` with your keys:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AI...
XAI_API_KEY=xai-...
GOOGLE_SHEETS_ID=your-sheet-id  # Optional
```

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google AI: https://makersuite.google.com/app/apikey
- xAI: https://console.x.ai/

### 3. Initialize Database

```bash
python main.py init
```

### 4. Run Your First Pipeline

```bash
# Test predictions only (no video)
python main.py predictions

# Generate one test video
python main.py content --limit 1

# Run full morning pipeline
python main.py morning
```

## Commands

```bash
python main.py morning              # Full morning pipeline (games + predictions + videos)
python main.py morning --skip-content  # Predictions only, no video generation
python main.py morning --limit 5    # Generate 5 videos instead of default 3
python main.py evening              # Update yesterday's game results
python main.py predictions          # Test AI API connections only
python main.py content --limit 1    # Generate test video only
python main.py init                 # Initialize database
```

## Automation (Cron Jobs)

To run automatically every day:

```bash
./setup_cron.sh
```

This installs:
- **8:00 AM**: Morning pipeline (fetch games, get predictions, generate videos)
- **11:00 PM**: Evening pipeline (fetch results, update stats)

## Google Sheets Setup (Optional)

To sync data to Google Sheets for mobile access:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API
4. Create a Service Account and download the JSON key
5. Save the key as `config/credentials.json`
6. Create a new Google Sheet and share it with the service account email
7. Copy the Sheet ID from the URL and add to `config/.env`

## Project Structure

```
bookiebenchmark/
├── main.py                 # Main orchestrator
├── scripts/
│   ├── fetch_games.py      # ESPN game scraper
│   ├── fetch_odds.py       # Vegas odds fetcher
│   ├── get_predictions.py  # AI model queries
│   ├── fetch_results.py    # Game results updater
│   ├── generate_content.py # Video generation
│   └── sync_sheets.py      # Google Sheets sync
├── utils/
│   ├── database.py         # SQLite database
│   ├── tts.py              # Text-to-speech (edge-tts)
│   └── video.py            # Video generation (moviepy)
├── config/
│   ├── prompts.py          # AI prompts & team mappings
│   ├── .env                # API keys (gitignored)
│   └── credentials.json    # Google credentials (gitignored)
├── assets/
│   └── logos/              # Team & AI logos (180x180 PNG)
├── base_highlights/        # Source highlight footage
├── output/                 # Generated videos
└── data/
    └── predictions.db      # SQLite database
```

## Video Output

Generated videos are saved to `output/` with naming format:
```
YYYYMMDD_AWAY_HOME_N.mp4
```

Example: `20250111_LAL_GSW_1.mp4`

Videos are:
- 9:16 vertical format (TikTok/Reels optimized)
- 1080x1920 resolution
- ~25 seconds long
- Include animated captions
- Include team logos
- No background music (add trending sounds when posting)

## Customization

### Change Voiceover Style

Edit `config/prompts.py` and modify `VOICEOVER_SCRIPT_TEMPLATE` to adjust the tone, length, or format of scripts.

### Change TTS Voice

Edit `utils/tts.py` and change `DEFAULT_VOICE`. Available voices:
- `en-US-GuyNeural` - Deep, authoritative (default)
- `en-US-ChristopherNeural` - Energetic, younger
- `en-US-AriaNeural` - Professional, clear

### Add More AI Models

1. Add the model config to `AI_MODELS` in `config/prompts.py`
2. Add the API call function in `scripts/get_predictions.py`
3. Add the logo to `assets/logos/`

## Troubleshooting

**"No games found"**: NBA might be on break, or it's past 11 PM and games haven't been scheduled yet.

**API errors**: Check that your API keys are correct in `config/.env`

**Video generation fails**: Make sure ffmpeg is installed: `brew install ffmpeg`

**Google Sheets not syncing**: Check that credentials.json exists and the sheet is shared with the service account.

## Future Ideas

- [ ] Add spread/over-under predictions
- [ ] Automated posting to TikTok/Instagram
- [ ] Weekly performance summary videos
- [ ] Support for NFL, MLB, NHL
- [ ] Leaderboard website
