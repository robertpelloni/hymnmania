import sys
import logging
logging.basicConfig(level=logging.DEBUG)

print("Starting import tests...")

modules = [
    "hymn_remaker.settings",
    "hymn_remaker.src.midi_renderer",
    "hymn_remaker.src.remaker",
    "hymn_remaker.src.suno_remaker",
    "hymn_remaker.src.udio_remaker",
    "hymn_remaker.src.udio_oauth_remaker",
    "hymn_remaker.src.gemini_generator",
    "hymn_remaker.src.ai_video",
    "hymn_remaker.src.video_uploader",
    "hymn_remaker.src.tts_generator",
    "hymn_remaker.src.musicxml_parser",
    "hymn_remaker.src.omr_processor",
    "hymn_remaker.src.stem_separator",
    "hymn_remaker.src.radio_streamer"
]

for m in modules:
    print(f"Importing {m}...")
    try:
        __import__(m)
        print(f"  {m} ok")
    except Exception as e:
        print(f"  {m} FAILED: {e}")

print("All imports finished.")
