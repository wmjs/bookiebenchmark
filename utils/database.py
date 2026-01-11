"""
Database module for storing games, predictions, and results.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "data" / "predictions.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Games table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT UNIQUE NOT NULL,
            game_date DATE NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_team_abbrev TEXT NOT NULL,
            away_team_abbrev TEXT NOT NULL,
            vegas_favorite TEXT,
            vegas_spread REAL,
            winner TEXT,
            home_score INTEGER,
            away_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            predicted_winner TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            reasoning TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_correct INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(game_id),
            UNIQUE(game_id, model_name)
        )
    """)

    # Model performance tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT UNIQUE NOT NULL,
            total_predictions INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            win_rate REAL DEFAULT 0.0,
            avg_confidence REAL DEFAULT 0.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Content generation log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            video_path TEXT,
            script TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            posted_instagram INTEGER DEFAULT 0,
            posted_tiktok INTEGER DEFAULT 0,
            posted_twitter INTEGER DEFAULT 0,
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def insert_game(game_data: dict) -> bool:
    """Insert a new game or update if exists."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO games (game_id, game_date, home_team, away_team,
                             home_team_abbrev, away_team_abbrev, vegas_favorite, vegas_spread)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(game_id) DO UPDATE SET
                vegas_favorite = excluded.vegas_favorite,
                vegas_spread = excluded.vegas_spread,
                updated_at = CURRENT_TIMESTAMP
        """, (
            game_data['game_id'],
            game_data['game_date'],
            game_data['home_team'],
            game_data['away_team'],
            game_data['home_team_abbrev'],
            game_data['away_team_abbrev'],
            game_data.get('vegas_favorite'),
            game_data.get('vegas_spread')
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting game: {e}")
        return False
    finally:
        conn.close()


def insert_prediction(prediction: dict) -> bool:
    """Insert a prediction for a game."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO predictions (game_id, model_name, predicted_winner, confidence, reasoning)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(game_id, model_name) DO UPDATE SET
                predicted_winner = excluded.predicted_winner,
                confidence = excluded.confidence,
                reasoning = excluded.reasoning
        """, (
            prediction['game_id'],
            prediction['model_name'],
            prediction['predicted_winner'],
            prediction['confidence'],
            prediction.get('reasoning', '')
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting prediction: {e}")
        return False
    finally:
        conn.close()


def update_game_result(game_id: str, winner: str, home_score: int, away_score: int) -> bool:
    """Update game with final result and mark predictions as correct/incorrect."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Update game result
        cursor.execute("""
            UPDATE games
            SET winner = ?, home_score = ?, away_score = ?, updated_at = CURRENT_TIMESTAMP
            WHERE game_id = ?
        """, (winner, home_score, away_score, game_id))

        # Update predictions as correct/incorrect
        cursor.execute("""
            UPDATE predictions
            SET is_correct = CASE WHEN predicted_winner = ? THEN 1 ELSE 0 END
            WHERE game_id = ?
        """, (winner, game_id))

        # Update model stats
        cursor.execute("""
            INSERT INTO model_stats (model_name, total_predictions, correct_predictions, win_rate, avg_confidence)
            SELECT
                model_name,
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                ROUND(100.0 * SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as rate,
                ROUND(AVG(confidence), 1) as avg_conf
            FROM predictions
            WHERE is_correct IS NOT NULL
            GROUP BY model_name
            ON CONFLICT(model_name) DO UPDATE SET
                total_predictions = excluded.total_predictions,
                correct_predictions = excluded.correct_predictions,
                win_rate = excluded.win_rate,
                avg_confidence = excluded.avg_confidence,
                updated_at = CURRENT_TIMESTAMP
        """)

        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating game result: {e}")
        return False
    finally:
        conn.close()


def get_games_for_date(date: str) -> list:
    """Get all games for a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE game_date = ?", (date,))
    games = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return games


def get_predictions_for_game(game_id: str) -> list:
    """Get all predictions for a specific game."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions WHERE game_id = ?", (game_id,))
    predictions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return predictions


def get_games_needing_results(date: str) -> list:
    """Get games from a date that don't have results yet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM games
        WHERE game_date = ? AND winner IS NULL
    """, (date,))
    games = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return games


def get_model_stats() -> list:
    """Get performance stats for all models."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM model_stats ORDER BY win_rate DESC")
    stats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return stats


def get_interesting_matchups(date: str, limit: int = 3) -> list:
    """
    Get the most interesting matchups for content creation.
    Prioritizes games where AI models disagree.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get games with prediction counts and disagreement scores
    cursor.execute("""
        SELECT
            g.*,
            COUNT(DISTINCT p.predicted_winner) as unique_picks,
            GROUP_CONCAT(p.model_name || ':' || p.predicted_winner || ':' || p.confidence) as predictions_str
        FROM games g
        LEFT JOIN predictions p ON g.game_id = p.game_id
        WHERE g.game_date = ?
        GROUP BY g.game_id
        ORDER BY unique_picks DESC, g.game_id
        LIMIT ?
    """, (date, limit))

    games = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return games


if __name__ == "__main__":
    init_db()
