"""
Get predictions from all AI models for NBA games.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from utils.database import get_games_for_date, insert_prediction, get_predictions_for_game
from config.prompts import PREDICTION_PROMPT, AI_MODELS

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")


def parse_prediction_response(response_text: str, home_team: str, away_team: str) -> Optional[dict]:
    """Parse the JSON response from an AI model."""
    try:
        # Try to extract JSON from the response
        # Sometimes models add extra text before/after JSON
        text = response_text.strip()

        # Find JSON object
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            print(f"No JSON found in response: {text[:100]}")
            return None

        json_str = text[start:end]
        data = json.loads(json_str)

        # Validate required fields
        winner = data.get("winner", "")
        confidence = data.get("confidence", 50)
        reasoning = data.get("reasoning", "")

        # Normalize winner name
        winner_lower = winner.lower()
        if home_team.lower() in winner_lower or winner_lower in home_team.lower():
            winner = home_team
        elif away_team.lower() in winner_lower or winner_lower in away_team.lower():
            winner = away_team
        else:
            print(f"Could not match winner '{winner}' to teams")
            return None

        # Clamp confidence
        confidence = max(50, min(100, int(confidence)))

        return {
            "winner": winner,
            "confidence": confidence,
            "reasoning": reasoning[:500]  # Limit length
        }

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error parsing response: {e}")
        return None


def get_prediction_openai(prompt: str) -> Optional[str]:
    """Get prediction from OpenAI (ChatGPT)."""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model=AI_MODELS["ChatGPT"]["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI error: {e}")
        return None


def get_prediction_anthropic(prompt: str) -> Optional[str]:
    """Get prediction from Anthropic (Claude)."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model=AI_MODELS["Claude"]["model"],
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    except Exception as e:
        print(f"Anthropic error: {e}")
        return None


def get_prediction_google(prompt: str) -> Optional[str]:
    """Get prediction from Google (Gemini)."""
    try:
        from google import genai

        client = genai.Client(api_key=os.getenv("GOOGLE_AI_API_KEY"))
        response = client.models.generate_content(
            model=AI_MODELS["Gemini"]["model"],
            contents=prompt
        )
        return response.text

    except Exception as e:
        print(f"Google AI error: {e}")
        return None


def get_prediction_xai(prompt: str) -> Optional[str]:
    """Get prediction from xAI (Grok)."""
    try:
        import openai  # xAI uses OpenAI-compatible API
        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

        response = client.chat.completions.create(
            model=AI_MODELS["Grok"]["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"xAI error: {e}")
        return None


PREDICTION_FUNCTIONS = {
    "ChatGPT": get_prediction_openai,
    "Claude": get_prediction_anthropic,
    "Gemini": get_prediction_google,
    "Grok": get_prediction_xai
}


def get_all_predictions_for_game(game: dict) -> list:
    """Get predictions from all AI models for a single game."""
    predictions = []
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = PREDICTION_PROMPT.format(
        today_date=today,
        game_date=game["game_date"],
        home_team=game["home_team"],
        away_team=game["away_team"]
    )

    print(f"\nGetting predictions for: {game['away_team']} @ {game['home_team']}")

    for model_name, get_prediction_func in PREDICTION_FUNCTIONS.items():
        print(f"  Querying {model_name}...", end=" ")

        response = get_prediction_func(prompt)
        if not response:
            print("FAILED")
            continue

        parsed = parse_prediction_response(response, game["home_team"], game["away_team"])
        if not parsed:
            print("PARSE ERROR")
            continue

        prediction = {
            "game_id": game["game_id"],
            "model_name": model_name,
            "predicted_winner": parsed["winner"],
            "confidence": parsed["confidence"],
            "reasoning": parsed["reasoning"]
        }
        predictions.append(prediction)
        print(f"{parsed['winner']} ({parsed['confidence']}%)")

    return predictions


def get_predictions_for_date(date: Optional[str] = None) -> list:
    """Get predictions for all games on a specific date."""
    if date is None:
        tomorrow = datetime.now() + timedelta(days=1)
        date = tomorrow.strftime("%Y-%m-%d")

    games = get_games_for_date(date)
    if not games:
        print(f"No games found for {date}")
        return []

    all_predictions = []
    for game in games:
        # Check if we already have predictions for this game
        existing = get_predictions_for_game(game["game_id"])
        if len(existing) >= 4:
            print(f"Skipping {game['away_team']} @ {game['home_team']} - already have predictions")
            continue

        predictions = get_all_predictions_for_game(game)
        for pred in predictions:
            insert_prediction(pred)
            all_predictions.append(pred)

    return all_predictions


if __name__ == "__main__":
    print("Getting AI predictions for tomorrow's games...")
    predictions = get_predictions_for_date()
    print(f"\nTotal predictions collected: {len(predictions)}")
