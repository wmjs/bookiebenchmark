"""
Weekly statistics calculation module for AI model performance tracking.
"""
from datetime import datetime, timedelta
from typing import Optional

from utils.database import (
    get_model_stats,
    get_weekly_stats,
    get_model_streak,
    get_all_model_streaks,
    get_total_games_in_range
)


def get_week_date_range(reference_date: Optional[str] = None) -> tuple:
    """
    Get the start and end dates for the previous week (Mon-Sun).

    Args:
        reference_date: Reference date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Tuple of (start_date, end_date) strings
    """
    if reference_date:
        ref = datetime.strptime(reference_date, "%Y-%m-%d")
    else:
        ref = datetime.now()

    # Get previous Monday (start of last week)
    days_since_monday = ref.weekday()
    if days_since_monday == 0:
        # If today is Monday, go back to last Monday
        days_since_monday = 7

    last_monday = ref - timedelta(days=days_since_monday + 7)
    last_sunday = last_monday + timedelta(days=6)

    return last_monday.strftime("%Y-%m-%d"), last_sunday.strftime("%Y-%m-%d")


def calculate_weekly_report(reference_date: Optional[str] = None) -> dict:
    """
    Calculate comprehensive weekly stats for all models.

    Args:
        reference_date: Reference date for determining the week

    Returns:
        Dictionary with overall and weekly stats
    """
    start_date, end_date = get_week_date_range(reference_date)

    # Get overall stats (all time)
    overall_stats = get_model_stats()

    # Get weekly stats
    weekly_stats = get_weekly_stats(start_date, end_date)

    # Get streaks
    streaks = get_all_model_streaks()

    # Get total games this week
    total_games = get_total_games_in_range(start_date, end_date)

    # Build combined report
    report = {
        "week_start": start_date,
        "week_end": end_date,
        "total_games": total_games,
        "overall_leaderboard": [],
        "weekly_report_cards": []
    }

    # Overall leaderboard (sorted by win rate)
    for i, stat in enumerate(overall_stats):
        report["overall_leaderboard"].append({
            "rank": i + 1,
            "model_name": stat["model_name"],
            "win_rate": stat["win_rate"],
            "record": f"{stat['correct_predictions']}-{stat['total_predictions'] - stat['correct_predictions']}",
            "total_predictions": stat["total_predictions"],
            "correct_predictions": stat["correct_predictions"]
        })

    # Weekly report cards with indicators
    weekly_by_model = {s["model_name"]: s for s in weekly_stats}
    overall_by_model = {s["model_name"]: s for s in overall_stats}

    # Find weekly leader
    weekly_leader = weekly_stats[0]["model_name"] if weekly_stats else None

    for model_name in ["ChatGPT", "Claude", "Gemini", "Grok"]:
        weekly = weekly_by_model.get(model_name, {})
        overall = overall_by_model.get(model_name, {})
        streak = streaks.get(model_name, {"type": None, "count": 0})

        # Calculate indicators
        indicators = []

        # Hot/cold streak indicators
        if streak["type"] == "W" and streak["count"] >= 3:
            indicators.append("fire")  # Hot streak
        elif streak["type"] == "L" and streak["count"] >= 3:
            indicators.append("ice")  # Cold streak

        # Weekly leader
        if model_name == weekly_leader:
            indicators.append("crown")

        # Calculate high confidence accuracy
        high_conf_correct = weekly.get("high_conf_correct", 0)
        high_conf_total = weekly.get("high_conf_total", 0)
        high_conf_accuracy = (
            round(100 * high_conf_correct / high_conf_total, 1)
            if high_conf_total > 0 else None
        )

        report["weekly_report_cards"].append({
            "model_name": model_name,
            "weekly_record": f"{weekly.get('correct_predictions', 0)}-{weekly.get('total_predictions', 0) - weekly.get('correct_predictions', 0)}" if weekly else "0-0",
            "weekly_win_rate": weekly.get("win_rate", 0),
            "weekly_predictions": weekly.get("total_predictions", 0),
            "streak": streak,
            "indicators": indicators,
            "high_conf_accuracy": high_conf_accuracy,
            "avg_confidence": weekly.get("avg_confidence", 0)
        })

    return report


def format_streak_callout(report: dict) -> str:
    """
    Generate a dramatic callout about streaks for the script.

    Args:
        report: Weekly report dictionary

    Returns:
        String callout about noteworthy streaks
    """
    hot_models = []
    cold_models = []

    for card in report["weekly_report_cards"]:
        if "fire" in card["indicators"]:
            hot_models.append((card["model_name"], card["streak"]["count"]))
        if "ice" in card["indicators"]:
            cold_models.append((card["model_name"], card["streak"]["count"]))

    callouts = []

    if hot_models:
        for model, count in hot_models:
            callouts.append(f"{model} is ON FIRE with {count} wins in a row!")

    if cold_models:
        for model, count in cold_models:
            callouts.append(f"{model} is ICE COLD with {count} straight losses!")

    if not callouts:
        # No major streaks, find something interesting
        cards = report["weekly_report_cards"]
        if cards:
            top = max(cards, key=lambda x: x["weekly_win_rate"])
            if top["weekly_win_rate"] > 0:
                callouts.append(f"{top['model_name']} dominated this week!")

    return " ".join(callouts) if callouts else "It's anyone's game!"


def get_indicator_emoji(indicator: str) -> str:
    """Convert indicator name to emoji."""
    emoji_map = {
        "fire": "fire",
        "ice": "ice",
        "crown": "crown",
        "up": "up",
        "down": "down"
    }
    return emoji_map.get(indicator, "")


if __name__ == "__main__":
    # Test the module
    report = calculate_weekly_report()
    print(f"Week: {report['week_start']} to {report['week_end']}")
    print(f"Total games: {report['total_games']}")
    print("\nOverall Leaderboard:")
    for entry in report["overall_leaderboard"]:
        print(f"  {entry['rank']}. {entry['model_name']}: {entry['win_rate']}% ({entry['record']})")
    print("\nWeekly Report Cards:")
    for card in report["weekly_report_cards"]:
        indicators_str = ", ".join(card["indicators"]) if card["indicators"] else "none"
        print(f"  {card['model_name']}: {card['weekly_record']} ({card['weekly_win_rate']}%) - Indicators: {indicators_str}")
    print(f"\nStreak Callout: {format_streak_callout(report)}")
