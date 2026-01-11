"""
Fetch Vegas odds for NBA games.
Uses ESPN's odds data (free, no API key needed).
"""
import requests
from datetime import datetime, timedelta
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.database import get_connection


ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"


def fetch_odds_for_date(date: Optional[str] = None) -> dict:
    """
    Fetch odds for NBA games on a specific date.

    Args:
        date: Date in YYYYMMDD format. If None, fetches tomorrow's games.

    Returns:
        Dictionary mapping game_id to odds info.
    """
    if date is None:
        tomorrow = datetime.now() + timedelta(days=1)
        date = tomorrow.strftime("%Y%m%d")

    url = f"{ESPN_SCOREBOARD_URL}?dates={date}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching odds: {e}")
        return {}

    odds_map = {}
    events = data.get("events", [])

    for event in events:
        try:
            game_id = event["id"]
            competition = event["competitions"][0]

            # Get odds from competition
            odds_data = competition.get("odds", [])
            if not odds_data:
                continue

            # Get the first odds provider (usually consensus)
            odds = odds_data[0]

            # Parse spread
            spread_info = odds.get("details", "")
            spread_value = odds.get("spread", 0)

            # Determine favorite
            home_team = None
            away_team = None
            for comp in competition["competitors"]:
                if comp["homeAway"] == "home":
                    home_team = comp["team"]["displayName"]
                else:
                    away_team = comp["team"]["displayName"]

            # The spread is typically shown as negative for favorite
            if spread_value and spread_value != 0:
                if spread_value < 0:
                    # Home team is favorite
                    favorite = home_team
                    spread = abs(spread_value)
                else:
                    # Away team is favorite
                    favorite = away_team
                    spread = spread_value
            else:
                # Try to parse from details string (e.g., "LAL -5.5")
                favorite = None
                spread = None
                if spread_info:
                    parts = spread_info.split()
                    if len(parts) >= 2:
                        try:
                            spread = abs(float(parts[-1]))
                            # Figure out which team is favorite
                            team_abbrev = parts[0]
                            favorite = home_team if team_abbrev in home_team.upper() else away_team
                        except ValueError:
                            pass

            odds_map[game_id] = {
                "favorite": favorite,
                "spread": spread,
                "details": spread_info
            }

        except (KeyError, IndexError) as e:
            print(f"Error parsing odds for event: {e}")
            continue

    return odds_map


def update_games_with_odds(date: Optional[str] = None):
    """Fetch odds and update games in database."""
    if date is None:
        tomorrow = datetime.now() + timedelta(days=1)
        date_db = tomorrow.strftime("%Y-%m-%d")
        date_api = tomorrow.strftime("%Y%m%d")
    else:
        date_api = date
        date_db = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")

    odds_map = fetch_odds_for_date(date_api)

    if not odds_map:
        print("No odds data found")
        return

    conn = get_connection()
    cursor = conn.cursor()

    for game_id, odds in odds_map.items():
        if odds["favorite"] and odds["spread"]:
            cursor.execute("""
                UPDATE games
                SET vegas_favorite = ?, vegas_spread = ?, updated_at = CURRENT_TIMESTAMP
                WHERE game_id = ?
            """, (odds["favorite"], odds["spread"], game_id))
            print(f"Updated odds for game {game_id}: {odds['favorite']} -{odds['spread']}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Fetching tomorrow's NBA odds...")
    update_games_with_odds()
