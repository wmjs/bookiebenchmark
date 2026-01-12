#!/usr/bin/env python3
"""
BookieBenchmark - AI Sports Prediction Content Generator

Main orchestrator script that runs the full pipeline:
1. Fetch tomorrow's NBA games
2. Get Vegas odds
3. Query AI models for predictions
4. Generate content for interesting matchups
5. Update results from yesterday's games
6. Sync everything to Google Sheets
"""
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import init_db


def run_morning_pipeline(skip_content: bool = False, content_limit: int = 3):
    """
    Run the full daily pipeline (once per day at 5 AM).

    1. Initialize database
    2. Fetch yesterday's results (update accuracy)
    3. Fetch tomorrow's games
    4. Fetch Vegas odds
    5. Get AI predictions for all games
    6. Generate content for top matchups
    7. Upload videos to Google Drive
    8. Sync to Google Sheets
    """
    from scripts.fetch_games import fetch_and_store_games
    from scripts.fetch_odds import update_games_with_odds
    from scripts.get_predictions import get_predictions_for_date
    from scripts.generate_content import generate_daily_content
    from scripts.fetch_results import update_yesterdays_results
    from scripts.upload_drive import upload_todays_videos
    from scripts.sync_sheets import sync_to_sheets

    print("\n" + "="*60)
    print("BOOKIEBENCHMARK - DAILY PIPELINE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Initialize database
    print("\n[1/8] Initializing database...")
    init_db()

    # Fetch yesterday's results first
    print("\n[2/8] Fetching yesterday's results...")
    update_yesterdays_results()

    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    date_api = tomorrow.strftime("%Y%m%d")
    date_db = tomorrow.strftime("%Y-%m-%d")

    # Fetch games
    print(f"\n[3/8] Fetching games for {date_db}...")
    games = fetch_and_store_games(date_api)
    print(f"Found {len(games)} games")

    if not games:
        print("No games tomorrow. Skipping predictions and content.")
        print("\n[8/8] Syncing to Google Sheets...")
        sync_to_sheets()
        print("\n" + "="*60)
        print("DAILY PIPELINE COMPLETE")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        return

    # Fetch odds
    print(f"\n[4/8] Fetching Vegas odds...")
    update_games_with_odds(date_api)

    # Get predictions
    print(f"\n[5/8] Getting AI predictions...")
    predictions = get_predictions_for_date(date_db)
    print(f"Collected {len(predictions)} predictions")

    # Generate content
    videos_created = 0
    if not skip_content:
        print(f"\n[6/8] Generating content (top {content_limit} matchups)...")
        content_results = generate_daily_content(date_db, limit=content_limit)
        videos_created = len([r for r in content_results if r.get('video_path')])
        print(f"Created {videos_created} videos")
    else:
        print("\n[6/8] Skipping content generation (--skip-content flag)")

    # Upload videos to Google Drive
    if videos_created > 0:
        print("\n[7/8] Uploading videos to Google Drive...")
        upload_todays_videos()
    else:
        print("\n[7/8] No videos to upload")

    # Sync to sheets
    print("\n[8/8] Syncing to Google Sheets...")
    sync_to_sheets()

    print("\n" + "="*60)
    print("DAILY PIPELINE COMPLETE")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


def run_evening_pipeline():
    """
    Run the evening results update pipeline.

    1. Fetch yesterday's game results
    2. Update prediction accuracy
    3. Sync updated stats to Google Sheets
    """
    from scripts.fetch_results import update_yesterdays_results
    from scripts.sync_sheets import sync_to_sheets

    print("\n" + "="*60)
    print("BOOKIEBENCHMARK - EVENING PIPELINE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Initialize database (in case it doesn't exist)
    init_db()

    # Fetch results
    print("\n[1/2] Fetching yesterday's results...")
    update_yesterdays_results()

    # Sync to sheets
    print("\n[2/2] Syncing to Google Sheets...")
    sync_to_sheets()

    print("\n" + "="*60)
    print("EVENING PIPELINE COMPLETE")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


def run_predictions_only():
    """Run just the predictions part (for testing API connections)."""
    from scripts.fetch_games import fetch_and_store_games
    from scripts.get_predictions import get_predictions_for_date

    init_db()

    tomorrow = datetime.now() + timedelta(days=1)
    date_api = tomorrow.strftime("%Y%m%d")
    date_db = tomorrow.strftime("%Y-%m-%d")

    print("Fetching games...")
    games = fetch_and_store_games(date_api)
    print(f"Found {len(games)} games")

    if games:
        print("\nGetting predictions...")
        predictions = get_predictions_for_date(date_db)
        print(f"Got {len(predictions)} predictions")


def run_content_only(limit: int = 1):
    """Run just the content generation (for testing video pipeline)."""
    from scripts.generate_content import generate_daily_content

    tomorrow = datetime.now() + timedelta(days=1)
    date_db = tomorrow.strftime("%Y-%m-%d")

    print(f"Generating content for {date_db}...")
    generate_daily_content(date_db, limit=limit)


def main():
    parser = argparse.ArgumentParser(
        description="BookieBenchmark - AI Sports Prediction Content Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py morning              # Run full morning pipeline
  python main.py evening              # Update yesterday's results
  python main.py morning --skip-content  # Predictions only, no videos
  python main.py predictions          # Test AI API connections
  python main.py content --limit 1    # Generate 1 test video
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Morning command
    morning_parser = subparsers.add_parser("morning", help="Run morning content generation pipeline")
    morning_parser.add_argument("--skip-content", action="store_true", help="Skip video generation")
    morning_parser.add_argument("--limit", type=int, default=3, help="Number of videos to generate")

    # Evening command
    subparsers.add_parser("evening", help="Run evening results update pipeline")

    # Test commands
    subparsers.add_parser("predictions", help="Test predictions only (no content)")
    content_parser = subparsers.add_parser("content", help="Test content generation only")
    content_parser.add_argument("--limit", type=int, default=1, help="Number of videos to generate")

    # Init command
    subparsers.add_parser("init", help="Initialize database only")

    args = parser.parse_args()

    if args.command == "morning":
        run_morning_pipeline(skip_content=args.skip_content, content_limit=args.limit)
    elif args.command == "evening":
        run_evening_pipeline()
    elif args.command == "predictions":
        run_predictions_only()
    elif args.command == "content":
        run_content_only(limit=args.limit)
    elif args.command == "init":
        init_db()
        print("Database initialized successfully!")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
