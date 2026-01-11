"""
Prompt templates for AI predictions and content generation.
"""

PREDICTION_PROMPT = """You are a sports analyst AI making NBA game predictions.

Today's Date: {today_date}
Game Date: {game_date}

MATCHUP: {away_team} @ {home_team}

Based on your knowledge of:
- Current team records and standings
- Recent performance and momentum
- Head-to-head history
- Key player availability (injuries, rest)
- Home court advantage

Predict the winner of this game.

IMPORTANT: Respond in EXACTLY this JSON format, nothing else:
{{
    "winner": "[Team Name]",
    "confidence": [50-100],
    "reasoning": "[One sentence explanation]"
}}

Rules:
- winner must be exactly "{home_team}" or "{away_team}"
- confidence is a number 50-100 (50 = coin flip, 100 = absolute certainty)
- Keep reasoning to ONE punchy sentence
"""

VOICEOVER_SCRIPT_TEMPLATE = """Generate a dramatic, engaging voiceover script for a sports betting AI prediction video.

MATCHUP: {away_team} vs {home_team}
{vegas_section}

AI PREDICTIONS:
{predictions}

REQUIREMENTS:
1. Start with dramatic hook like "THE AIs HAVE SPOKEN" or "THE MACHINES HAVE DECIDED"
2. State the matchup dramatically
{vegas_requirement}
3. Go through each AI's pick with their confidence
4. Highlight any disagreements dramatically - this is CONTENT GOLD
5. End with a provocative question or statement to drive comments

TONE: Dramatic, slightly unhinged, rage-bait friendly. Think sports talk radio meets AI hype.

LENGTH: STRICTLY 50-70 words maximum. This is critical - the video must be under 25 seconds.

Respond with ONLY the voiceover script text, no formatting or labels. Do NOT exceed 70 words.
"""

# Team name mappings
NBA_TEAMS = {
    "ATL": {"name": "Atlanta Hawks", "short": "Hawks", "logo": "hawks.png"},
    "BOS": {"name": "Boston Celtics", "short": "Celtics", "logo": "celtics.png"},
    "BKN": {"name": "Brooklyn Nets", "short": "Nets", "logo": "nets.png"},
    "CHA": {"name": "Charlotte Hornets", "short": "Hornets", "logo": "hornets.png"},
    "CHI": {"name": "Chicago Bulls", "short": "Bulls", "logo": "bulls.png"},
    "CLE": {"name": "Cleveland Cavaliers", "short": "Cavaliers", "logo": "cavaliers.png"},
    "DAL": {"name": "Dallas Mavericks", "short": "Mavericks", "logo": "mavericks.png"},
    "DEN": {"name": "Denver Nuggets", "short": "Nuggets", "logo": "nuggets.png"},
    "DET": {"name": "Detroit Pistons", "short": "Pistons", "logo": "pistons.png"},
    "GSW": {"name": "Golden State Warriors", "short": "Warriors", "logo": "warriors.png"},
    "HOU": {"name": "Houston Rockets", "short": "Rockets", "logo": "rockets.png"},
    "IND": {"name": "Indiana Pacers", "short": "Pacers", "logo": "pacers.png"},
    "LAC": {"name": "Los Angeles Clippers", "short": "Clippers", "logo": "clippers.png"},
    "LAL": {"name": "Los Angeles Lakers", "short": "Lakers", "logo": "lakers.png"},
    "MEM": {"name": "Memphis Grizzlies", "short": "Grizzlies", "logo": "grizzlies.png"},
    "MIA": {"name": "Miami Heat", "short": "Heat", "logo": "heat.png"},
    "MIL": {"name": "Milwaukee Bucks", "short": "Bucks", "logo": "bucks.png"},
    "MIN": {"name": "Minnesota Timberwolves", "short": "Timberwolves", "logo": "timberwolves.png"},
    "NOP": {"name": "New Orleans Pelicans", "short": "Pelicans", "logo": "pelicans.png"},
    "NYK": {"name": "New York Knicks", "short": "Knicks", "logo": "knicks.png"},
    "OKC": {"name": "Oklahoma City Thunder", "short": "Thunder", "logo": "thunder.png"},
    "ORL": {"name": "Orlando Magic", "short": "Magic", "logo": "magic.png"},
    "PHI": {"name": "Philadelphia 76ers", "short": "76ers", "logo": "76ers.png"},
    "PHX": {"name": "Phoenix Suns", "short": "Suns", "logo": "suns.png"},
    "POR": {"name": "Portland Trail Blazers", "short": "Trail Blazers", "logo": "trailblazers.png"},
    "SAC": {"name": "Sacramento Kings", "short": "Kings", "logo": "kings.png"},
    "SAS": {"name": "San Antonio Spurs", "short": "Spurs", "logo": "spurs.png"},
    "TOR": {"name": "Toronto Raptors", "short": "Raptors", "logo": "raptors.png"},
    "UTA": {"name": "Utah Jazz", "short": "Jazz", "logo": "jazz.png"},
    "WAS": {"name": "Washington Wizards", "short": "Wizards", "logo": "wizards.png"},
}

# AI model configurations
AI_MODELS = {
    "ChatGPT": {
        "provider": "openai",
        "model": "gpt-4o",
        "logo": "ChatGPT.png"
    },
    "Claude": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "logo": "Claude.png"
    },
    "Gemini": {
        "provider": "google",
        "model": "gemini-2.0-flash",
        "logo": "Gemini.png"
    },
    "Grok": {
        "provider": "xai",
        "model": "grok-3",
        "logo": "Grok.png"
    }
}
