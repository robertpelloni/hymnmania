import os
import sys
import glob
import logging
import argparse
import json
import requests
from dotenv import load_dotenv

# Add the project root to sys.path so we can import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.midi_renderer import MidiRenderer
from src.remaker import MusicRemaker
from src.content_generator import ContentGenerator
from src.video_uploader import VideoProducer

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("hymn_remaker.log") # Commented out to avoid permission issues if run in weird places
    ]
)
logger = logging.getLogger("HymnRemaker")

def main():
    parser = argparse.ArgumentParser(description="Hymn Remaker Pipeline")
    parser.add_argument("--input-dir", default="hymn_remaker/input", help="Directory containing input MIDI files")
    parser.add_argument("--output-dir", default="hymn_remaker/output", help="Directory for output files")
    parser.add_argument("--soundfont", help="Path to custom soundfont")
    parser.add_argument("--style", default="Deep House, high quality, electronic", help="Musical style prompt for the remake")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube after generation")
    parser.add_argument("--skip-render", action="store_true", help="Skip MIDI rendering if WAV exists")
    parser.add_argument("--skip-remake", action="store_true", help="Skip music generation if output audio exists")

    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize modules
    try:
        renderer = MidiRenderer(soundfont_path=args.soundfont)
        remaker = MusicRemaker()
        content_gen = ContentGenerator()
        video_producer = VideoProducer()
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        sys.exit(1)

    # Find MIDI files
    midi_files = glob.glob(os.path.join(args.input_dir, "*.mid"))
    if not midi_files:
        logger.warning(f"No MIDI files found in {args.input_dir}")
        sys.exit(0)

    logger.info(f"Found {len(midi_files)} MIDI files to process.")

    for midi_path in midi_files:
        try:
            filename = os.path.basename(midi_path)
            name_no_ext = os.path.splitext(filename)[0]
            logger.info(f"Processing {filename}...")

            # 1. Render MIDI to Audio (WAV)
            base_audio_path = os.path.join(args.output_dir, f"{name_no_ext}_base.wav")
            if not args.skip_render or not os.path.exists(base_audio_path):
                renderer.render(midi_path, base_audio_path)
            else:
                logger.info(f"Skipping render for {filename}, {base_audio_path} exists.")

            # 2. Generate Remake (MusicGen)
            remake_audio_path = os.path.join(args.output_dir, f"{name_no_ext}_remake.wav")

            if not args.skip_remake or not os.path.exists(remake_audio_path):
                # Call Replicate
                remake_url = remaker.remake(base_audio_path, args.style)

                # Download the remake
                logger.info(f"Downloading remake from {remake_url}...")
                response = requests.get(remake_url)
                response.raise_for_status()
                with open(remake_audio_path, "wb") as f:
                    f.write(response.content)
            else:
                 logger.info(f"Skipping remake for {filename}, {remake_audio_path} exists.")

            # 3. Generate Content (Metadata & Art)
            # We can do this in parallel, but sequential is safer for now
            metadata = content_gen.generate_metadata(name_no_ext, style=args.style)

            art_prompt = f"Abstract album art for {metadata.get('title', name_no_ext)}, {args.style} style, high quality, 4k"
            art_url = content_gen.generate_art(art_prompt)

            # Save metadata to file for reference
            metadata_path = os.path.join(args.output_dir, f"{name_no_ext}_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=4)

            # 4. Create Video
            video_path = os.path.join(args.output_dir, f"{name_no_ext}.mp4")
            video_producer.create_video(remake_audio_path, art_url, video_path)

            # 5. Upload to YouTube (Optional)
            if args.upload:
                video_id = video_producer.upload_to_youtube(video_path, metadata)
                logger.info(f"Video uploaded: https://youtu.be/{video_id}")

            logger.info(f"Finished processing {filename}")

        except Exception as e:
            logger.error(f"Error processing {midi_path}: {e}")
            continue

if __name__ == "__main__":
    main()
