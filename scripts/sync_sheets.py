"""
Sync predictions and results to Google Sheets for mobile access.
"""
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "config" / ".env")

from utils.database import get_connection, get_model_stats


def get_gspread_client():
    """Get authenticated gspread client using OAuth."""
    try:
        import gspread
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        config_path = Path(__file__).parent.parent / "config"
        creds_path = config_path / "credentials.json"
        token_path = config_path / "sheets_token.json"

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not creds_path.exists():
                    print("Google credentials not found. See README for setup instructions.")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), scopes)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        client = gspread.authorize(creds)
        return client

    except Exception as e:
        print(f"Error authenticating with Google: {e}")
        return None


def sync_to_sheets():
    """Sync all data to Google Sheets."""
    sheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not sheet_id:
        print("GOOGLE_SHEETS_ID not set in .env")
        return False

    client = get_gspread_client()
    if not client:
        return False

    try:
        spreadsheet = client.open_by_key(sheet_id)
    except Exception as e:
        print(f"Error opening spreadsheet: {e}")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    # --- PREDICTIONS SHEET ---
    try:
        predictions_sheet = spreadsheet.worksheet("Predictions")
    except:
        predictions_sheet = spreadsheet.add_worksheet("Predictions", rows=1000, cols=15)

    # Get all predictions with game info
    cursor.execute("""
        SELECT
            g.game_date,
            g.away_team,
            g.home_team,
            g.vegas_favorite,
            g.vegas_spread,
            g.winner as actual_winner,
            g.home_score,
            g.away_score,
            p.model_name,
            p.predicted_winner,
            p.confidence,
            p.reasoning,
            p.is_correct
        FROM predictions p
        JOIN games g ON p.game_id = g.game_id
        ORDER BY g.game_date DESC, g.game_id, p.model_name
    """)

    predictions_data = [
        ["Date", "Away Team", "Home Team", "Vegas Favorite", "Spread",
         "Actual Winner", "Home Score", "Away Score", "Model", "Prediction",
         "Confidence", "Reasoning", "Correct?"]
    ]
    for row in cursor.fetchall():
        predictions_data.append([
            row[0], row[1], row[2], row[3] or "", row[4] or "",
            row[5] or "", row[6] or "", row[7] or "", row[8], row[9],
            row[10], row[11] or "", "Yes" if row[12] == 1 else ("No" if row[12] == 0 else "")
        ])

    predictions_sheet.clear()
    if len(predictions_data) > 1:
        predictions_sheet.update(range_name="A1", values=predictions_data)
    print(f"Synced {len(predictions_data)-1} predictions")

    # --- MODEL STATS SHEET ---
    try:
        stats_sheet = spreadsheet.worksheet("Model Stats")
    except:
        stats_sheet = spreadsheet.add_worksheet("Model Stats", rows=20, cols=10)

    model_stats = get_model_stats()
    stats_data = [["Model", "Total Predictions", "Correct", "Win Rate %", "Avg Confidence"]]
    for stat in model_stats:
        stats_data.append([
            stat["model_name"],
            stat["total_predictions"],
            stat["correct_predictions"],
            stat["win_rate"],
            stat["avg_confidence"]
        ])

    stats_sheet.clear()
    stats_sheet.update(range_name="A1", values=stats_data)
    print(f"Synced stats for {len(model_stats)} models")

    # --- UPCOMING GAMES SHEET ---
    try:
        upcoming_sheet = spreadsheet.worksheet("Upcoming")
    except:
        upcoming_sheet = spreadsheet.add_worksheet("Upcoming", rows=100, cols=15)

    cursor.execute("""
        SELECT
            g.game_date,
            g.away_team,
            g.home_team,
            g.vegas_favorite,
            g.vegas_spread,
            GROUP_CONCAT(p.model_name || ': ' || p.predicted_winner || ' (' || p.confidence || '%)', ' | ') as predictions
        FROM games g
        LEFT JOIN predictions p ON g.game_id = p.game_id
        WHERE g.winner IS NULL
        GROUP BY g.game_id
        ORDER BY g.game_date
    """)

    upcoming_data = [["Date", "Away Team", "Home Team", "Vegas Favorite", "Spread", "AI Predictions"]]
    for row in cursor.fetchall():
        upcoming_data.append([row[0], row[1], row[2], row[3] or "", row[4] or "", row[5] or ""])

    upcoming_sheet.clear()
    upcoming_sheet.update(range_name="A1", values=upcoming_data)
    print(f"Synced {len(upcoming_data)-1} upcoming games")

    conn.close()
    print(f"\nGoogle Sheets synced at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True


if __name__ == "__main__":
    sync_to_sheets()
