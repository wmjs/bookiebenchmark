"""
Generate weekly summary video for AI prediction performance.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

from utils.database import get_connection
from utils.weekly_stats import calculate_weekly_report, format_streak_callout
from utils.tts import generate_tts_with_timing
from utils.video import generate_weekly_video
from config.prompts import WEEKLY_SCRIPT_TEMPLATE, get_random_weekly_intro

import openai


def generate_weekly_script(report: dict) -> str:
    """
    Generate a dramatic voiceover script for weekly recap using AI.

    Args:
        report: Weekly report dictionary

    Returns:
        Generated script text
    """
    # Get random intros
    project_intro, intro_hook = get_random_weekly_intro()

    # Format leaderboard for prompt
    leaderboard_text = ""
    for entry in report["overall_leaderboard"]:
        leaderboard_text += f"#{entry['rank']} {entry['model_name']}: {entry['win_rate']}% ({entry['record']})\n"

    # Format weekly stats for prompt
    weekly_text = ""
    for card in report["weekly_report_cards"]:
        indicators_str = ", ".join(card["indicators"]) if card["indicators"] else "none"
        streak_info = f"{card['streak']['count']}{card['streak']['type']}" if card["streak"]["type"] else "none"
        weekly_text += f"- {card['model_name']}: {card['weekly_record']} ({card['weekly_win_rate']}%), streak: {streak_info}, indicators: {indicators_str}\n"

    # Get streak callout
    streak_callout = format_streak_callout(report)

    prompt = WEEKLY_SCRIPT_TEMPLATE.format(
        week_start=report["week_start"],
        week_end=report["week_end"],
        total_games=report["total_games"],
        leaderboard=leaderboard_text,
        weekly_stats=weekly_text,
        streak_callout=streak_callout,
        project_intro=project_intro,
        intro_hook=intro_hook
    )

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Script generation error: {e}")
        return generate_fallback_weekly_script(report, project_intro, intro_hook)


def generate_fallback_weekly_script(report: dict, project_intro: str, intro_hook: str) -> str:
    """Generate a basic weekly script without AI."""
    lines = [project_intro, intro_hook]

    if report["overall_leaderboard"]:
        leader = report["overall_leaderboard"][0]
        lines.append(f"In first place, {leader['model_name']} with a {leader['win_rate']}% win rate!")

    if len(report["overall_leaderboard"]) > 1:
        second = report["overall_leaderboard"][1]
        lines.append(f"{second['model_name']} comes in second at {second['win_rate']}%.")

    lines.append(format_streak_callout(report))
    lines.append("Who takes the crown next week? Drop your prediction!")

    return " ".join(lines)


def generate_weekly_content(reference_date: str = None) -> dict:
    """
    Generate the weekly summary video.

    Args:
        reference_date: Reference date for determining the week (YYYY-MM-DD)

    Returns:
        Dictionary with paths to generated content
    """
    print(f"\n{'='*60}")
    print("GENERATING WEEKLY SUMMARY VIDEO")
    print(f"{'='*60}")

    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    result = {
        "script": None,
        "audio_path": None,
        "video_path": None
    }

    # Calculate weekly stats
    print("\nCalculating weekly statistics...")
    report = calculate_weekly_report(reference_date)

    print(f"Week: {report['week_start']} to {report['week_end']}")
    print(f"Total games: {report['total_games']}")

    if report["total_games"] == 0:
        print("No games found for this week - skipping video generation")
        return result

    print("\nOverall Leaderboard:")
    for entry in report["overall_leaderboard"]:
        print(f"  #{entry['rank']} {entry['model_name']}: {entry['win_rate']}% ({entry['record']})")

    # Generate script
    print("\nGenerating voiceover script...")
    script = generate_weekly_script(report)
    result["script"] = script
    print(f"Script: {script[:150]}...")

    # Generate TTS
    print("\nGenerating voiceover...")
    date_str = datetime.now().strftime("%Y%m%d")
    audio_filename = f"weekly_{date_str}.mp3"
    audio_path = str(output_dir / audio_filename)

    tts_result = generate_tts_with_timing(script, audio_path)

    if not tts_result:
        print("ERROR: TTS generation failed")
        return result

    audio_path, word_timings = tts_result
    result["audio_path"] = audio_path
    print(f"Audio generated: {audio_path}")

    # Generate video
    print("\nGenerating video...")
    video_filename = f"weekly_{date_str}.mp4"
    video_path = generate_weekly_video(
        script=script,
        audio_path=audio_path,
        word_timings=word_timings,
        report=report,
        output_filename=video_filename
    )

    if video_path:
        result["video_path"] = video_path
        print(f"Video generated: {video_path}")

        # Log to database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO content_log (game_id, video_path, script)
            VALUES (?, ?, ?)
        """, (f"weekly_{report['week_start']}_{report['week_end']}", video_path, script))
        conn.commit()
        conn.close()
    else:
        print("ERROR: Video generation failed")

    print(f"\n{'='*60}")
    print("WEEKLY VIDEO GENERATION COMPLETE")
    print(f"{'='*60}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate weekly summary video")
    parser.add_argument("--date", help="Reference date (YYYY-MM-DD)", default=None)
    args = parser.parse_args()

    result = generate_weekly_content(args.date)

    print("\nResult:")
    print(f"  Script: {'Generated' if result['script'] else 'FAILED'}")
    print(f"  Audio: {result.get('audio_path', 'FAILED')}")
    print(f"  Video: {result.get('video_path', 'FAILED')}")
