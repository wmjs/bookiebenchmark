"""
Video generation utilities for creating TikTok/Reels content.
"""
import random
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont

# MoviePy imports
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip,
    CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
)
from moviepy.video.fx.all import crop, resize

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
HIGHLIGHTS_PATH = PROJECT_ROOT / "base_highlights" / "30_mins_of_highlights_1.mp4"
LOGOS_PATH = PROJECT_ROOT / "assets" / "logos"
OUTPUT_PATH = PROJECT_ROOT / "output"

# Video settings for TikTok/Reels (9:16 vertical)
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
FPS = 30

# AI logo filenames
AI_LOGOS = {
    "chatgpt": "ChatGPT.png",
    "claude": "Claude.png",
    "gemini": "Gemini.png",
    "grok": "Grok.png"
}

# Team logo mapping
TEAM_LOGO_MAP = {
    "hawks": "hawks.png", "celtics": "celtics.png", "nets": "nets.png",
    "hornets": "hornets.png", "bulls": "bulls.png", "cavaliers": "cavaliers.png",
    "mavericks": "mavericks.png", "nuggets": "nuggets.png", "pistons": "pistons.png",
    "warriors": "warriors.png", "rockets": "rockets.png", "pacers": "pacers.png",
    "clippers": "clippers.png", "lakers": "lakers.png", "grizzlies": "grizzlies.png",
    "heat": "heat.png", "bucks": "bucks.png", "timberwolves": "timberwolves.png",
    "pelicans": "pelicans.png", "knicks": "knicks.png", "thunder": "thunder.png",
    "magic": "magic.png", "76ers": "76ers.png", "suns": "suns.png",
    "trailblazers": "trailblazers.png", "kings": "kings.png", "spurs": "spurs.png",
    "raptors": "raptors.png", "jazz": "jazz.png", "wizards": "wizards.png"
}


def get_random_clip(duration: float = 30.0, source_path: Optional[str] = None) -> VideoFileClip:
    """Extract a random clip from the highlights video."""
    source = source_path or str(HIGHLIGHTS_PATH)
    video = VideoFileClip(source)
    max_start = max(0, video.duration - duration)
    start_time = random.uniform(0, max_start)
    clip = video.subclip(start_time, start_time + duration)
    return clip


def crop_to_vertical(clip: VideoFileClip) -> VideoFileClip:
    """Crop a horizontal video to 9:16 vertical format, centered."""
    w, h = clip.size
    target_ratio = 9 / 16

    if w / h > target_ratio:
        new_width = int(h * target_ratio)
        x_center = w // 2
        x1 = x_center - new_width // 2
        x2 = x_center + new_width // 2
        cropped = crop(clip, x1=x1, x2=x2)
    else:
        new_height = int(w / target_ratio)
        y_center = h // 2
        y1 = y_center - new_height // 2
        y2 = y_center + new_height // 2
        cropped = crop(clip, y1=y1, y2=y2)

    return cropped.resize((OUTPUT_WIDTH, OUTPUT_HEIGHT))


def create_logo_clip(logo_path: str, size: int = 150) -> np.ndarray:
    """Load and resize a logo to numpy array."""
    img = Image.open(logo_path).convert("RGBA")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return np.array(img)


def find_team_logo(team_name: str) -> Optional[Path]:
    """Find the logo file for a team name."""
    team_lower = team_name.lower()
    for team_key, logo_file in TEAM_LOGO_MAP.items():
        if team_key in team_lower:
            logo_path = LOGOS_PATH / logo_file
            if logo_path.exists():
                return logo_path
    return None


def find_ai_mentions(word_timings: list) -> List[dict]:
    """
    Find when each AI is mentioned in the script.
    Returns list of {ai_name, start_time, end_time} dicts.
    """
    ai_mentions = []
    ai_names = ["chatgpt", "claude", "gemini", "grok"]

    i = 0
    while i < len(word_timings):
        word = word_timings[i]["word"].lower().strip(".,!?")

        for ai_name in ai_names:
            if ai_name in word:
                # Find the end of this AI's segment (next AI mention or ~3 seconds)
                start_time = word_timings[i]["start"]
                end_time = start_time + 3.0  # Default 3 second display

                # Look for next AI mention or end of relevant content
                for j in range(i + 1, min(i + 20, len(word_timings))):
                    next_word = word_timings[j]["word"].lower().strip(".,!?")
                    # Check if another AI is mentioned
                    for other_ai in ai_names:
                        if other_ai in next_word and other_ai != ai_name:
                            end_time = word_timings[j]["start"]
                            break
                    else:
                        continue
                    break

                ai_mentions.append({
                    "ai_name": ai_name,
                    "start": start_time,
                    "end": min(end_time, start_time + 4.0)  # Cap at 4 seconds
                })
                break
        i += 1

    return ai_mentions


def create_caption_frame(
    text: str,
    width: int = OUTPUT_WIDTH,
    height: int = 300,
    font_size: int = 100,  # Bigger text
    bg_color: tuple = (0, 0, 0, 0),  # Transparent background
    text_color: tuple = (255, 255, 255, 255),
    outline_thickness: int = 8  # Thicker outline for bigger text
):
    """Create a dramatic caption frame with text - no background, just bold outlined text."""
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to use a bold, impactful font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()

    # Handle long text by reducing font size if needed
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    while text_width > width - 60 and font_size > 35:
        font_size -= 5
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                break
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw EXTRA thick outline for visibility (no background means we need strong outline)
    outline_color = (0, 0, 0, 255)
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)

    # Draw main text in white
    draw.text((x, y), text, font=font, fill=text_color)

    return np.array(img)


def create_animated_captions(
    word_timings: list,
    duration: float,
    words_per_caption: int = 3
) -> list:
    """Create dramatically animated caption clips from word timings."""
    caption_clips = []
    chunks = []
    current_chunk = []
    current_start = 0

    for i, timing in enumerate(word_timings):
        if not current_chunk:
            current_start = timing["start"]

        current_chunk.append(timing["word"])

        # Create new chunk every N words or at punctuation
        if len(current_chunk) >= words_per_caption or timing["word"].endswith((".", "!", "?")):
            chunk_end = timing["start"] + timing["duration"]
            chunks.append({
                "text": " ".join(current_chunk),
                "start": current_start,
                "end": chunk_end
            })
            current_chunk = []

    # Add remaining words
    if current_chunk:
        chunks.append({
            "text": " ".join(current_chunk),
            "start": current_start,
            "end": duration
        })

    # Create caption clips - CENTERED on screen
    caption_y = int(OUTPUT_HEIGHT * 0.50)  # Center of screen (50%)

    # Pre-generate all caption images to avoid closure issues
    caption_data = []
    for chunk in chunks:
        caption_img = create_caption_frame(chunk["text"].upper())
        caption_data.append({
            "img": caption_img,
            "start": chunk["start"],
            "duration": chunk["end"] - chunk["start"]
        })

    # Create clips from pre-generated images
    for data in caption_data:
        clip = (
            ImageClip(data["img"])
            .set_start(data["start"])
            .set_duration(data["duration"])
            .set_position(("center", caption_y))
        )
        caption_clips.append(clip)

    print(f"    Created {len(caption_clips)} caption segments")
    return caption_clips


def generate_video(
    script: str,
    audio_path: str,
    word_timings: list,
    game_info: dict,
    predictions: list,
    output_filename: str
) -> Optional[str]:
    """
    Generate the full video with background, audio, logos, and captions.

    Features:
    - Team logos shown during intro (first 5 seconds)
    - AI logos shown when each AI's prediction is mentioned
    - Animated captions throughout
    """
    try:
        # Load audio to get duration
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        video_duration = audio_duration + 0.5

        # Get random background clip
        print("  Extracting background clip...")
        background = get_random_clip(duration=video_duration + 1)
        background = crop_to_vertical(background)
        background = background.subclip(0, video_duration)
        background = background.set_audio(None)

        logo_clips = []

        # === TEAM LOGOS (shown during intro, first 6 seconds) ===
        print("  Adding team logos...")
        home_logo_path = find_team_logo(game_info.get("home_team", ""))
        away_logo_path = find_team_logo(game_info.get("away_team", ""))

        # Position team logos HUGE and CENTERED vertically for maximum impact
        logo_size = 500  # Super big logos
        logo_y = int(OUTPUT_HEIGHT * 0.25)  # Centered vertically (30% down)
        intro_duration = 6.0

        # Calculate symmetric positions
        edge_padding = 10  # Minimal padding from edges

        if away_logo_path:
            away_logo_array = create_logo_clip(str(away_logo_path), size=logo_size)
            away_logo = (
                ImageClip(away_logo_array)
                .set_position((edge_padding, logo_y))
                .set_start(0)
                .set_duration(intro_duration)
            )
            logo_clips.append(away_logo)

        if home_logo_path:
            home_logo_array = create_logo_clip(str(home_logo_path), size=logo_size)
            home_logo = (
                ImageClip(home_logo_array)
                .set_position((OUTPUT_WIDTH - logo_size - edge_padding, logo_y))
                .set_start(0)
                .set_duration(intro_duration)
            )
            logo_clips.append(home_logo)

        # Add huge "VS" text between team logos - centered with logos
        vs_height = 220
        vs_img = create_caption_frame("VS", width=350, height=vs_height, font_size=130,
                                       bg_color=(0, 0, 0, 0), text_color=(255, 255, 255, 255))
        vs_y = logo_y + (logo_size - vs_height) // 2  # Center VS with logos
        vs_clip = (
            ImageClip(vs_img)
            .set_position(("center", vs_y))
            .set_start(0)
            .set_duration(intro_duration)
        )
        logo_clips.append(vs_clip)

        # === AI LOGOS (shown when each AI is mentioned) ===
        print("  Adding AI logos...")
        ai_mentions = find_ai_mentions(word_timings)

        ai_logo_size = 400  # Big AI logos
        ai_logo_y = 350  # Position below team logos area

        for mention in ai_mentions:
            ai_name = mention["ai_name"]
            logo_file = AI_LOGOS.get(ai_name)

            if logo_file:
                logo_path = LOGOS_PATH / logo_file
                if logo_path.exists():
                    ai_logo_array = create_logo_clip(str(logo_path), size=ai_logo_size)
                    # Center the AI logo
                    ai_logo_x = (OUTPUT_WIDTH - ai_logo_size) // 2
                    ai_logo = (
                        ImageClip(ai_logo_array)
                        .set_position((ai_logo_x, ai_logo_y))
                        .set_start(mention["start"])
                        .set_duration(mention["end"] - mention["start"])
                    )
                    logo_clips.append(ai_logo)
                    print(f"    {ai_name}: {mention['start']:.1f}s - {mention['end']:.1f}s")

        # === ANIMATED CAPTIONS ===
        print("  Creating animated captions...")
        caption_clips = create_animated_captions(word_timings, video_duration)

        # === COMPOSE FINAL VIDEO ===
        print("  Compositing video...")
        all_clips = [background] + logo_clips + caption_clips
        final = CompositeVideoClip(all_clips, size=(OUTPUT_WIDTH, OUTPUT_HEIGHT))

        # Set duration to match audio exactly
        final = final.set_duration(audio_duration)

        # Add audio
        audio_trimmed = audio.subclip(0, audio_duration)
        final = final.set_audio(audio_trimmed)

        # Output path
        output_path = OUTPUT_PATH / output_filename
        OUTPUT_PATH.mkdir(exist_ok=True)

        # Write video
        print("  Rendering video...")
        final.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None
        )

        # Cleanup
        background.close()
        audio.close()
        final.close()

        return str(output_path)

    except Exception as e:
        print(f"Video generation error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_leaderboard_frame(
    leaderboard: list,
    width: int = OUTPUT_WIDTH,
    height: int = 800
) -> np.ndarray:
    """Create a leaderboard display frame showing all AI rankings."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 70)
        rank_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 55)
    except:
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            rank_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
        except:
            title_font = ImageFont.load_default()
            rank_font = ImageFont.load_default()

    # Title with outline
    title = "AI LEADERBOARD"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_x = (width - (title_bbox[2] - title_bbox[0])) // 2
    title_y = 20

    # Draw title outline
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            draw.text((title_x + dx, title_y + dy), title, font=title_font, fill=(0, 0, 0, 255))
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 215, 0, 255))

    # Rank colors
    rank_colors = [
        (255, 215, 0, 255),    # Gold
        (192, 192, 192, 255),  # Silver
        (205, 127, 50, 255),   # Bronze
        (255, 255, 255, 255),  # White
    ]

    # Draw each rank
    y_offset = 130
    row_height = 160

    for i, entry in enumerate(leaderboard[:4]):
        y = y_offset + (i * row_height)
        color = rank_colors[i] if i < len(rank_colors) else (255, 255, 255, 255)

        # Rank number
        rank_text = f"#{entry['rank']}"

        # Model name and stats
        model_text = f"{entry['model_name']}"
        stats_text = f"{entry['win_rate']}% ({entry['record']})"

        # Draw rank with outline
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((60 + dx, y + dy), rank_text, font=rank_font, fill=(0, 0, 0, 255))
        draw.text((60, y), rank_text, font=rank_font, fill=color)

        # Draw model name
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((180 + dx, y + dy), model_text, font=rank_font, fill=(0, 0, 0, 255))
        draw.text((180, y), model_text, font=rank_font, fill=(255, 255, 255, 255))

        # Draw stats
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((550 + dx, y + dy), stats_text, font=rank_font, fill=(0, 0, 0, 255))
        draw.text((550, y), stats_text, font=rank_font, fill=color)

    return np.array(img)


def create_report_card_frame(
    card: dict,
    width: int = OUTPUT_WIDTH,
    height: int = 350
) -> np.ndarray:
    """Create a report card frame for a single AI model."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        name_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 65)
        stats_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 45)
        indicator_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Apple Color Emoji.ttc", 60)
    except:
        try:
            name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 65)
            stats_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
            indicator_font = stats_font
        except:
            name_font = ImageFont.load_default()
            stats_font = ImageFont.load_default()
            indicator_font = stats_font

    # Model name
    name_text = card["model_name"].upper()
    name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
    name_x = (width - (name_bbox[2] - name_bbox[0])) // 2
    name_y = 20

    # Name outline and text
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            draw.text((name_x + dx, name_y + dy), name_text, font=name_font, fill=(0, 0, 0, 255))
    draw.text((name_x, name_y), name_text, font=name_font, fill=(255, 255, 255, 255))

    # Weekly record
    record_text = f"This Week: {card['weekly_record']} ({card['weekly_win_rate']}%)"
    record_bbox = draw.textbbox((0, 0), record_text, font=stats_font)
    record_x = (width - (record_bbox[2] - record_bbox[0])) // 2
    record_y = 110

    for dx in range(-3, 4):
        for dy in range(-3, 4):
            draw.text((record_x + dx, record_y + dy), record_text, font=stats_font, fill=(0, 0, 0, 255))
    draw.text((record_x, record_y), record_text, font=stats_font, fill=(255, 255, 255, 255))

    # Streak info
    streak = card.get("streak", {})
    if streak.get("type") and streak.get("count", 0) > 0:
        streak_text = f"Streak: {streak['count']}{streak['type']}"
        streak_bbox = draw.textbbox((0, 0), streak_text, font=stats_font)
        streak_x = (width - (streak_bbox[2] - streak_bbox[0])) // 2
        streak_y = 175

        streak_color = (255, 100, 100, 255) if streak["type"] == "L" else (100, 255, 100, 255)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((streak_x + dx, streak_y + dy), streak_text, font=stats_font, fill=(0, 0, 0, 255))
        draw.text((streak_x, streak_y), streak_text, font=stats_font, fill=streak_color)

    # Indicators (emoji-like text labels)
    indicators = card.get("indicators", [])
    if indicators:
        indicator_map = {
            "fire": "HOT",
            "ice": "COLD",
            "crown": "LEADER"
        }
        indicator_text = " | ".join(indicator_map.get(i, i.upper()) for i in indicators)
        ind_bbox = draw.textbbox((0, 0), indicator_text, font=stats_font)
        ind_x = (width - (ind_bbox[2] - ind_bbox[0])) // 2
        ind_y = 260

        # Color based on indicator
        ind_color = (255, 165, 0, 255)  # Orange default
        if "fire" in indicators:
            ind_color = (255, 100, 50, 255)  # Fire orange
        elif "ice" in indicators:
            ind_color = (100, 200, 255, 255)  # Ice blue
        elif "crown" in indicators:
            ind_color = (255, 215, 0, 255)  # Gold

        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((ind_x + dx, ind_y + dy), indicator_text, font=stats_font, fill=(0, 0, 0, 255))
        draw.text((ind_x, ind_y), indicator_text, font=stats_font, fill=ind_color)

    return np.array(img)


def generate_weekly_video(
    script: str,
    audio_path: str,
    word_timings: list,
    report: dict,
    output_filename: str
) -> Optional[str]:
    """
    Generate a weekly recap video with leaderboard and report cards.

    Args:
        script: Voiceover script text
        audio_path: Path to audio file
        word_timings: Word timing data from TTS
        report: Weekly report dictionary from calculate_weekly_report()
        output_filename: Output filename

    Returns:
        Path to generated video or None if failed
    """
    try:
        # Load audio to get duration
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        video_duration = audio_duration + 0.5

        # Get random background clip
        print("  Extracting background clip...")
        background = get_random_clip(duration=video_duration + 1)
        background = crop_to_vertical(background)
        background = background.subclip(0, video_duration)
        background = background.set_audio(None)

        overlay_clips = []

        # === LEADERBOARD (first 12 seconds or so) ===
        print("  Creating leaderboard...")
        leaderboard = report.get("overall_leaderboard", [])
        if leaderboard:
            leaderboard_img = create_leaderboard_frame(leaderboard)
            leaderboard_y = int(OUTPUT_HEIGHT * 0.15)
            leaderboard_duration = min(12.0, video_duration * 0.5)

            leaderboard_clip = (
                ImageClip(leaderboard_img)
                .set_position(("center", leaderboard_y))
                .set_start(0)
                .set_duration(leaderboard_duration)
            )
            overlay_clips.append(leaderboard_clip)

        # === REPORT CARDS (cycle through them after leaderboard) ===
        print("  Creating report cards...")
        report_cards = report.get("weekly_report_cards", [])
        card_start_time = min(12.0, video_duration * 0.5)
        remaining_time = video_duration - card_start_time - 1.0  # Leave 1s at end
        card_duration = remaining_time / max(len(report_cards), 1)
        card_duration = min(card_duration, 4.0)  # Cap at 4 seconds each

        for i, card in enumerate(report_cards):
            card_img = create_report_card_frame(card)
            card_y = int(OUTPUT_HEIGHT * 0.20)
            start = card_start_time + (i * card_duration)

            if start >= video_duration - 0.5:
                break

            card_clip = (
                ImageClip(card_img)
                .set_position(("center", card_y))
                .set_start(start)
                .set_duration(min(card_duration, video_duration - start - 0.1))
            )
            overlay_clips.append(card_clip)
            print(f"    {card['model_name']}: {start:.1f}s - {start + card_duration:.1f}s")

        # === AI LOGOS alongside report cards ===
        print("  Adding AI logos...")
        for i, card in enumerate(report_cards):
            model_name = card["model_name"].lower()
            logo_file = AI_LOGOS.get(model_name)

            if logo_file:
                logo_path = LOGOS_PATH / logo_file
                if logo_path.exists():
                    start = card_start_time + (i * card_duration)
                    if start >= video_duration - 0.5:
                        break

                    ai_logo_array = create_logo_clip(str(logo_path), size=250)
                    ai_logo_x = (OUTPUT_WIDTH - 250) // 2
                    ai_logo_y = int(OUTPUT_HEIGHT * 0.55)

                    ai_logo = (
                        ImageClip(ai_logo_array)
                        .set_position((ai_logo_x, ai_logo_y))
                        .set_start(start)
                        .set_duration(min(card_duration, video_duration - start - 0.1))
                    )
                    overlay_clips.append(ai_logo)

        # === ANIMATED CAPTIONS ===
        print("  Creating animated captions...")
        caption_clips = create_animated_captions(word_timings, video_duration)

        # === COMPOSE FINAL VIDEO ===
        print("  Compositing video...")
        all_clips = [background] + overlay_clips + caption_clips
        final = CompositeVideoClip(all_clips, size=(OUTPUT_WIDTH, OUTPUT_HEIGHT))
        final = final.set_duration(audio_duration)

        # Add audio
        audio_trimmed = audio.subclip(0, audio_duration)
        final = final.set_audio(audio_trimmed)

        # Output path
        output_path = OUTPUT_PATH / output_filename
        OUTPUT_PATH.mkdir(exist_ok=True)

        # Write video
        print("  Rendering video...")
        final.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None
        )

        # Cleanup
        background.close()
        audio.close()
        final.close()

        return str(output_path)

    except Exception as e:
        print(f"Weekly video generation error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("Testing video utilities...")
    try:
        clip = get_random_clip(duration=5)
        print(f"Extracted {clip.duration}s clip")
        clip.close()
    except Exception as e:
        print(f"Error: {e}")
