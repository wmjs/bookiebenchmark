"""
Fetch game results from ESPN and update predictions.
"""
import requests
from datetime import datetime, timedelta
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.database import get_games_needing_results, update_game_result


ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"


def fetch_results_for_date(date: Optional[str] = None) -> dict:
    """
    Fetch game results for a specific date.

    Args:
        date: Date in YYYYMMDD format. If None, fetches yesterday's games.

    Returns:
        Dictionary mapping game_id to result info.
    """
    if date is None:
        yesterday = datetime.now() - timedelta(days=1)
        date = yesterday.strftime("%Y%m%d")

    url = f"{ESPN_SCOREBOARD_URL}?dates={date}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching results: {e}")
        return {}

    results = {}
    events = data.get("events", [])

    for event in events:
        try:
            game_id = event["id"]
            competition = event["competitions"][0]

            # Check if game is finished
            status = competition.get("status", {}).get("type", {}).get("completed", False)
            if not status:
                continue

            competitors = competition["competitors"]
            home_team = None
            away_team = None
            home_score = 0
            away_score = 0

            for comp in competitors:
                score = int(comp.get("score", 0))
                team_name = comp["team"]["displayName"]

                if comp["homeAway"] == "home":
                    home_team = team_name
                    home_score = score
                else:
                    away_team = team_name
                    away_score = score

            # Determine winner
            if home_score > away_score:
                winner = home_team
            elif away_score > home_score:
                winner = away_team
            else:
                winner = "TIE"  # Shouldn't happen in NBA

            results[game_id] = {
                "winner": winner,
                "home_score": home_score,
                "away_score": away_score,
                "home_team": home_team,
                "away_team": away_team
            }

        except (KeyError, IndexError, ValueError) as e:
            print(f"Error parsing result for event: {e}")
            continue

    return results


def update_results_for_date(date: Optional[str] = None):
    """Fetch results and update database."""
    if date is None:
        yesterday = datetime.now() - timedelta(days=1)
        date_db = yesterday.strftime("%Y-%m-%d")
        date_api = yesterday.strftime("%Y%m%d")
    else:
        date_api = date
        date_db = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")

    # Get games that need results
    games_needing = get_games_needing_results(date_db)
    if not games_needing:
        print(f"No games needing results for {date_db}")
        return

    print(f"Found {len(games_needing)} games needing results")

    # Fetch results from ESPN
    results = fetch_results_for_date(date_api)

    for game in games_needing:
        game_id = game["game_id"]
        if game_id in results:
            result = results[game_id]
            update_game_result(
                game_id=game_id,
                winner=result["winner"],
                home_score=result["home_score"],
                away_score=result["away_score"]
            )
            print(f"Updated: {result['away_team']} {result['away_score']} @ {result['home_team']} {result['home_score']} - Winner: {result['winner']}")
        else:
            print(f"No result found for game {game_id}")


def update_yesterdays_results():
    """Convenience function to update yesterday's game results."""
    yesterday = datetime.now() - timedelta(days=1)
    update_results_for_date(yesterday.strftime("%Y%m%d"))


if __name__ == "__main__":
    print("Fetching yesterday's game results...")
    update_yesterdays_results()
