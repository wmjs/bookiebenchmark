"""
Fetch upcoming NBA games from ESPN.
"""
import requests
from datetime import datetime, timedelta
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.database import insert_game, get_games_for_date
from config.prompts import NBA_TEAMS


ESPN_SCHEDULE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"


def get_team_abbrev(espn_abbrev: str) -> str:
    """Convert ESPN abbreviation to our standard abbreviation."""
    # ESPN uses some different abbreviations
    mapping = {
        "GS": "GSW",
        "NY": "NYK",
        "NO": "NOP",
        "SA": "SAS",
        "UTAH": "UTA",
        "WSH": "WAS",
        "PHO": "PHX",
        "PHOE": "PHX",
    }
    return mapping.get(espn_abbrev, espn_abbrev)


def fetch_games_for_date(date: Optional[str] = None) -> list:
    """
    Fetch NBA games for a specific date.

    Args:
        date: Date in YYYYMMDD format. If None, fetches tomorrow's games.

    Returns:
        List of game dictionaries.
    """
    if date is None:
        tomorrow = datetime.now() + timedelta(days=1)
        date = tomorrow.strftime("%Y%m%d")

    url = f"{ESPN_SCHEDULE_URL}?dates={date}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching games: {e}")
        return []

    games = []
    events = data.get("events", [])

    for event in events:
        try:
            competition = event["competitions"][0]
            competitors = competition["competitors"]

            # ESPN lists home team first, away team second
            home_team = None
            away_team = None
            for comp in competitors:
                if comp["homeAway"] == "home":
                    home_team = comp
                else:
                    away_team = comp

            if not home_team or not away_team:
                continue

            home_abbrev = get_team_abbrev(home_team["team"]["abbreviation"])
            away_abbrev = get_team_abbrev(away_team["team"]["abbreviation"])

            # Get team info from our mapping
            home_info = NBA_TEAMS.get(home_abbrev, {})
            away_info = NBA_TEAMS.get(away_abbrev, {})

            game_data = {
                "game_id": event["id"],
                "game_date": datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d"),
                "home_team": home_info.get("name", home_team["team"]["displayName"]),
                "away_team": away_info.get("name", away_team["team"]["displayName"]),
                "home_team_abbrev": home_abbrev,
                "away_team_abbrev": away_abbrev,
            }
            games.append(game_data)

        except (KeyError, IndexError) as e:
            print(f"Error parsing event: {e}")
            continue

    return games


def fetch_and_store_games(date: Optional[str] = None) -> list:
    """Fetch games and store them in the database."""
    games = fetch_games_for_date(date)

    for game in games:
        insert_game(game)
        print(f"Stored: {game['away_team']} @ {game['home_team']}")

    return games


if __name__ == "__main__":
    print("Fetching tomorrow's NBA games...")
    tomorrow = datetime.now() + timedelta(days=1)
    games = fetch_and_store_games(tomorrow.strftime("%Y%m%d"))
    print(f"\nFound {len(games)} games for tomorrow:")
    for game in games:
        print(f"  {game['away_team']} @ {game['home_team']}")
