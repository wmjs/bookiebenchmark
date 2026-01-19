"""
Prompt templates for AI predictions and content generation.
"""
import random

# Varied intro hooks to avoid repetition
INTRO_HOOKS = [
    "VEGAS VS AI",
    "AI VS THE BOOK",
    "THE AIs HAVE SPOKEN!",
    "THE MACHINES HAVE DECIDED!",
    "SILICON VERSUS SWEAT!",
    "FOUR AIs, ONE WINNER!",
    "THE BOTS ARE BETTING!",
    "ARTIFICIAL INTELLIGENCE PICKS!",
    "AI VERSUS AI!",
    "FOUR MODELS, FOUR OPINIONS!",
]

def get_random_intro():
    """Get a random intro hook for variety."""
    return random.choice(INTRO_HOOKS)


# Weekly video project intro hooks
WEEKLY_PROJECT_INTROS = [
    "Welcome to the AI Prediction Benchmark!",
    "Which AI is BEST at sports predictions?",
    "Four AIs battle to prove who's the smartest!",
    "We're testing AI on the hardest game: sports betting.",
    "The ultimate AI showdown continues!",
    "Can AI beat the spread? Let's find out!",
    "Four models. One goal. Beat the odds.",
]

# Weekly video intro hooks
WEEKLY_INTRO_HOOKS = [
    "It's time for the WEEKLY RECAP!",
    "THE RESULTS ARE IN!",
    "WEEKLY SHOWDOWN UPDATE!",
    "HERE'S HOW THE AIs DID!",
    "THE MACHINES HAVE BEEN TESTED!",
    "WEEKLY LEADERBOARD DROP!",
    "TIME TO CROWN A WINNER!",
    "THE WEEKLY BATTLE RESULTS!",
]


def get_random_weekly_intro():
    """Get random project intro and weekly intro hook."""
    return random.choice(WEEKLY_PROJECT_INTROS), random.choice(WEEKLY_INTRO_HOOKS)

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
1. Start EXACTLY with this hook: "{intro_hook}"
2. State the matchup dramatically
{vegas_requirement}
3. Go through each AI's pick with their confidence
4. Highlight any disagreements dramatically - this is CONTENT GOLD
5. End with a provocative question or statement to drive comments

TONE: Dramatic, slightly unhinged, rage-bait friendly. Think sports talk radio meets AI hype.

LENGTH: STRICTLY 50-70 words maximum. This is critical - the video must be under 25 seconds.

Respond with ONLY the voiceover script text, no formatting or labels. Do NOT exceed 70 words.
"""

WEEKLY_SCRIPT_TEMPLATE = """Generate a dramatic voiceover script for a weekly AI prediction recap video.

PROJECT CONTEXT: We're benchmarking AI models to see which one is best at predicting NBA games.

WEEKLY STATS:
- Week: {week_start} to {week_end}
- Total games: {total_games}

OVERALL LEADERBOARD (all-time):
{leaderboard}

WEEKLY PERFORMANCE:
{weekly_stats}

STREAK INFO:
{streak_callout}

REQUIREMENTS:
1. Start with: "{project_intro}"
2. Then: "{intro_hook}"
3. Announce the overall leader dramatically
4. Highlight any hot/cold streaks
5. End with engagement hook (question or challenge)

TONE: Hype, dramatic, sports broadcaster energy. Make it engaging!

LENGTH: STRICTLY 60-80 words. This is critical for video timing.

Respond with ONLY the voiceover script text, no formatting or labels.
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
