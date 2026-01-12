"""
Text-to-speech utilities using edge-tts (free Microsoft TTS).
"""
import asyncio
import re
import edge_tts
from pathlib import Path
from typing import Optional
from mutagen.mp3 import MP3

# Good voices for dramatic sports content
VOICES = {
    "dramatic_male": "en-US-GuyNeural",
    "energetic_male": "en-US-ChristopherNeural",
    "dramatic_female": "en-US-AriaNeural",
}

DEFAULT_VOICE = "en-US-GuyNeural"


async def generate_tts_async(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+20%",
    pitch: str = "+5Hz"
) -> Optional[str]:
    """Generate TTS audio file asynchronously."""
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        print(f"TTS error: {e}")
        return None


def generate_tts(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+25%",
    pitch: str = "+5Hz"
) -> Optional[str]:
    """Synchronous wrapper for TTS generation."""
    return asyncio.run(generate_tts_async(text, output_path, voice, rate, pitch))


def estimate_word_timings(text: str, audio_duration: float) -> list:
    """
    Estimate word timings based on text and audio duration.
    Uses word length as a rough proxy for speaking time.
    """
    # Split into words, keeping punctuation attached
    words = text.split()
    if not words:
        return []

    # Calculate total "weight" based on word lengths
    # Longer words take more time to say
    weights = []
    for word in words:
        # Base weight is word length, add extra for punctuation pauses
        weight = len(word)
        if word.endswith(('.', '!', '?')):
            weight += 3  # Pause after sentences
        elif word.endswith(','):
            weight += 1  # Short pause after commas
        weights.append(weight)

    total_weight = sum(weights)
    if total_weight == 0:
        total_weight = len(words)
        weights = [1] * len(words)

    # Distribute time across words proportionally
    word_timings = []
    current_time = 0.0

    for i, word in enumerate(words):
        word_duration = (weights[i] / total_weight) * audio_duration
        word_timings.append({
            "word": word,
            "start": current_time,
            "duration": word_duration
        })
        current_time += word_duration

    return word_timings


def get_audio_duration(audio_path: str) -> float:
    """Get the duration of an audio file in seconds."""
    try:
        audio = MP3(audio_path)
        return audio.info.length
    except Exception:
        # Fallback: estimate based on file size (rough approximation)
        import os
        file_size = os.path.getsize(audio_path)
        # MP3 at ~128kbps is roughly 16KB per second
        return file_size / 16000


async def generate_tts_with_timing_async(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+20%",
    pitch: str = "+5Hz"
) -> Optional[tuple]:
    """
    Generate TTS and estimate word timings for captions.

    Returns:
        Tuple of (audio_path, word_timings) or None on failure.
    """
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_path)

        # Get audio duration and estimate word timings
        duration = get_audio_duration(output_path)
        word_timings = estimate_word_timings(text, duration)

        return output_path, word_timings

    except Exception as e:
        print(f"TTS with timing error: {e}")
        return None


def generate_tts_with_timing(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+30%",
    pitch: str = "+5Hz"
) -> Optional[tuple]:
    """
    Synchronous wrapper for TTS generation with timing.

    Returns:
        Tuple of (audio_path, word_timings) or None on failure.
    """
    return asyncio.run(generate_tts_with_timing_async(text, output_path, voice, rate, pitch))


if __name__ == "__main__":
    # Test TTS
    test_text = "ChatGPT says Lakers with 75% confidence! Claude picks Warriors. Gemini agrees with Claude. Grok is going rogue!"
    output = Path(__file__).parent.parent / "output" / "test_tts.mp3"
    output.parent.mkdir(exist_ok=True)

    result = generate_tts_with_timing(test_text, str(output))
    if result:
        print(f"Generated: {result[0]}")
        print(f"Word timings: {len(result[1])} words captured")
        for timing in result[1]:
            print(f"  {timing['start']:.2f}s: {timing['word']}")
    else:
        print("TTS generation failed")
