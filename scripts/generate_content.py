"""
Generate video content for the most interesting matchups.
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

from utils.database import get_interesting_matchups, get_predictions_for_game, get_connection
from utils.tts import generate_tts_with_timing
from utils.video import generate_video
from config.prompts import VOICEOVER_SCRIPT_TEMPLATE, AI_MODELS, get_random_intro

# Use OpenAI for script generation (can switch to others)
import openai


def generate_voiceover_script(game: dict, predictions: list) -> str:
    """
    Generate a dramatic voiceover script using AI.

    Args:
        game: Game info dictionary
        predictions: List of prediction dictionaries

    Returns:
        Generated script text
    """
    # Format predictions for prompt
    predictions_text = ""
    for pred in predictions:
        predictions_text += f"- {pred['model_name']}: {pred['predicted_winner']} ({pred['confidence']}% confidence)\n"
        if pred.get('reasoning'):
            predictions_text += f"  Reason: {pred['reasoning']}\n"

    # Format Vegas line - only include if available
    has_vegas = game.get('vegas_favorite') and game.get('vegas_spread')
    if has_vegas:
        vegas_section = f"VEGAS LINE: {game['vegas_favorite']} -{game['vegas_spread']}"
        vegas_requirement = "- Mention the Vegas line"
    else:
        vegas_section = ""  # Don't mention Vegas at all
        vegas_requirement = "- Do NOT mention Vegas or betting lines"

    # Get a random intro hook for variety
    intro_hook = get_random_intro()

    prompt = VOICEOVER_SCRIPT_TEMPLATE.format(
        away_team=game['away_team'],
        home_team=game['home_team'],
        vegas_section=vegas_section,
        vegas_requirement=vegas_requirement,
        predictions=predictions_text,
        intro_hook=intro_hook
    )

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper model for script generation
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.9  # Higher creativity for engaging scripts
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Script generation error: {e}")
        # Fallback script
        return generate_fallback_script(game, predictions)


def generate_fallback_script(game: dict, predictions: list) -> str:
    """Generate a basic script without AI."""
    has_vegas = game.get('vegas_favorite') and game.get('vegas_spread')
    intro_hook = get_random_intro()

    if has_vegas:
        lines = [
            intro_hook,
            f"{game['away_team']} takes on {game['home_team']}.",
            f"Vegas has {game['vegas_favorite']} as the favorite.",
        ]
    else:
        lines = [
            intro_hook,
            f"{game['away_team']} takes on {game['home_team']}.",
        ]

    for pred in predictions:
        lines.append(f"{pred['model_name']} says {pred['predicted_winner']} with {pred['confidence']} percent confidence!")

    # Check for disagreement
    winners = set(p['predicted_winner'] for p in predictions)
    if len(winners) > 1:
        lines.append("THE MACHINES ARE DIVIDED! Who do YOU think takes this one?")
    else:
        lines.append("The AIs agree! But will they be right? Drop your prediction below!")

    return " ".join(lines)


def generate_content_for_game(game: dict, predictions: list, index: int) -> dict:
    """
    Generate all content (script, audio, video) for a single game.

    Args:
        game: Game info dictionary
        predictions: List of predictions for this game
        index: Index for filename uniqueness

    Returns:
        Dictionary with paths to generated content
    """
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    date_str = game['game_date'].replace("-", "")
    base_name = f"{date_str}_{game['away_team_abbrev']}_{game['home_team_abbrev']}_{index}"

    result = {
        "game_id": game['game_id'],
        "script": None,
        "audio_path": None,
        "video_path": None
    }

    # Generate script
    print(f"\n  Generating script for {game['away_team']} @ {game['home_team']}...")
    script = generate_voiceover_script(game, predictions)
    result["script"] = script
    print(f"  Script: {script[:100]}...")

    # Generate TTS audio with timing
    print("  Generating voiceover...")
    audio_path = str(output_dir / f"{base_name}.mp3")
    tts_result = generate_tts_with_timing(script, audio_path)

    if not tts_result:
        print("  ERROR: TTS generation failed")
        return result

    audio_path, word_timings = tts_result
    result["audio_path"] = audio_path
    print(f"  Audio generated: {audio_path}")

    # Generate video
    print("  Generating video...")
    video_filename = f"{base_name}.mp4"
    video_path = generate_video(
        script=script,
        audio_path=audio_path,
        word_timings=word_timings,
        game_info=game,
        predictions=predictions,
        output_filename=video_filename
    )

    if video_path:
        result["video_path"] = video_path
        print(f"  Video generated: {video_path}")

        # Log to database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO content_log (game_id, video_path, script)
            VALUES (?, ?, ?)
        """, (game['game_id'], video_path, script))
        conn.commit()
        conn.close()
    else:
        print("  ERROR: Video generation failed")

    return result


def generate_daily_content(date: str = None, limit: int = 3) -> list:
    """
    Generate content for the most interesting matchups of the day.

    Args:
        date: Date string (YYYY-MM-DD). Defaults to tomorrow.
        limit: Number of videos to generate.

    Returns:
        List of content generation results.
    """
    if date is None:
        tomorrow = datetime.now() + timedelta(days=1)
        date = tomorrow.strftime("%Y-%m-%d")

    print(f"\n{'='*60}")
    print(f"GENERATING CONTENT FOR {date}")
    print(f"{'='*60}")

    # Get interesting matchups
    matchups = get_interesting_matchups(date, limit=limit)

    if not matchups:
        print("No matchups found for content generation")
        return []

    print(f"Found {len(matchups)} interesting matchups")

    results = []
    for i, game in enumerate(matchups):
        # Get predictions for this game
        predictions = get_predictions_for_game(game['game_id'])

        if not predictions:
            print(f"No predictions for {game['away_team']} @ {game['home_team']}, skipping")
            continue

        print(f"\n[{i+1}/{len(matchups)}] Processing: {game['away_team']} @ {game['home_team']}")
        print(f"  Predictions: {len(predictions)} models")
        print(f"  Unique picks: {game.get('unique_picks', 'N/A')}")

        result = generate_content_for_game(game, predictions, i + 1)
        results.append(result)

    print(f"\n{'='*60}")
    print(f"CONTENT GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Generated {len([r for r in results if r.get('video_path')])} videos")

    return results


if __name__ == "__main__":
    results = generate_daily_content(limit=3)
    print("\nResults:")
    for r in results:
        print(f"  - {r.get('video_path', 'FAILED')}")
