import time
import json
import uuid
import streamlit as st
import os
import sys
import subprocess
import concurrent.futures
import plotly.graph_objects as go
import numpy as np
from dotenv import load_dotenv

# Load .env file from project root
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(_env_path):
    load_dotenv(_env_path)

from hymn_remaker import settings

# Load global version
VERSION = "Unknown"
try:
    version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "VERSION")
    if os.path.exists(version_path):
        with open(version_path, "r") as vf:
            VERSION = vf.read().strip()
except Exception:
    pass

st.set_page_config(page_title="Hymn Remaker UI", page_icon="🎵", layout="wide")
st.sidebar.markdown(f"**Version: {VERSION}**")
st.sidebar.markdown("---")

from hymn_remaker.src.midi_renderer import MidiRenderer
from hymn_remaker.src.remaker import MusicRemaker
from hymn_remaker.src.suno_remaker import SunoRemaker
from hymn_remaker.src.udio_remaker import UdioRemaker
from hymn_remaker.src.udio_oauth_remaker import UdioOAuthRemaker
from hymn_remaker.src.gemini_generator import GeminiContentGenerator
from hymn_remaker.src.video_uploader import VideoProducer
from hymn_remaker.src.tts_generator import TTSGenerator
from hymn_remaker.src.musicxml_parser import MusicXMLParser
from hymn_remaker.src.omr_processor import OMRProcessor
from hymn_remaker.src.stem_separator import StemSeparator
from hymn_remaker.main import process_single_midi

st.title("🎵 Hymn Remaker Pipeline")
st.write("Convert MIDI files into modern music videos with AI!")

# Initialize objects
@st.cache_resource
def load_modules():
    try:
        renderer = MidiRenderer()
        remaker = MusicRemaker()
        suno_remaker = SunoRemaker()
        udio_remaker = UdioRemaker()
        content_gen = GeminiContentGenerator()
        video_producer = VideoProducer()
        tts_generator = TTSGenerator()
        mxl_parser = MusicXMLParser()
        omr_processor = OMRProcessor()
        stem_separator = StemSeparator()
        # Create an oauth placeholder
        udio_oauth = None
        return renderer, remaker, suno_remaker, udio_remaker, content_gen, video_producer, tts_generator, mxl_parser, omr_processor, stem_separator, udio_oauth
    except Exception as e:
        import traceback
        st.error(f"Failed to initialize modules: {e}")
        st.code(traceback.format_exc())
        return None, None, None, None, None, None, None, None, None, None, None

renderer, remaker, suno_remaker, udio_remaker, content_gen, video_producer, tts_generator, mxl_parser, omr_processor, stem_separator, udio_oauth_remaker = load_modules()

st.sidebar.header("Environment & API")
missing_keys = []
if not os.environ.get("GEMINI_API_KEY") and not os.path.exists("client_secrets.json"):
    missing_keys.append("GEMINI_API_KEY / client_secrets.json")
if not os.environ.get("REPLICATE_API_TOKEN"):
    missing_keys.append("REPLICATE_API_TOKEN")
if missing_keys:
    st.sidebar.error(f"Missing Essential API Keys: {', '.join(missing_keys)}")
else:
    st.sidebar.success("Essential API Keys configured! ✅")

st.sidebar.header("Settings")
preset_styles = [
    settings.DEFAULT_STYLE,
    "Full-On Psytrance, 145 BPM, driving, psychedelic",
    "Lofi hip hop, chill, relaxing",
    "Synthwave, retro 80s",
    "Epic Orchestral",
    "Custom..."
]
selected_style = st.sidebar.selectbox("Musical Style Preset", preset_styles)
style = selected_style if selected_style != "Custom..." else st.sidebar.text_input("Custom Style", value="Your custom prompt here")

output_dir = st.sidebar.text_input("Output Directory", value=settings.OUTPUT_DIR)
max_workers = st.sidebar.slider("Concurrent Tasks", min_value=1, max_value=4, value=1)

st.sidebar.markdown("### Experimental Preprocessors")
with st.sidebar.expander("Udio/Suno Optimizers", expanded=False):
    sonic_vacuum = st.checkbox("Sonic Vacuum (Dry Render)", value=False)
    symbolic_norm = st.checkbox("Symbolic Norm (Velocity 100)", value=False)
    house_quantizer = st.checkbox("House Structural Quantizer", value=False)
    mix_hiphop_vocals = st.text_input("Hip-Hop Vocal Remix (Path/URL)")

st.sidebar.markdown("### Pipeline Options")
video_format = st.sidebar.selectbox("Video Format", ["Standard 16:9", "Vertical 9:16"])
enable_visualizer = st.sidebar.checkbox("Audio-Reactive Visualizer", value=False)
generate_vocals = st.sidebar.checkbox("Generate Vocals (ElevenLabs)", value=False)
remake_priority = st.sidebar.selectbox("AI Remake Service", ["udio-oauth", "udio", "suno", "replicate"], index=0)

tab1, tab2, tab3 = st.tabs(["🚀 Automated Pipeline", "🎹 Hymn Editor (Beta)", "🌀 Live Psy-Mono Studio"])

with tab1:
    uploaded_files = st.file_uploader("Upload MIDI/MusicXML", type=["mid", "midi", "mxl", "xml"], accept_multiple_files=True)
    if st.button("Start Processing", type="primary"):
        if uploaded_files:
            for uf in uploaded_files:
                file_path = os.path.join(settings.INPUT_DIR, uf.name)
                with open(file_path, "wb") as f:
                    f.write(uf.getbuffer())

                with st.status(f"Processing {uf.name}...") as status:
                    process_single_midi(
                        file_path, output_dir, style, False, False, False,
                        renderer, remaker, suno_remaker, udio_remaker, remake_priority,
                        content_gen, video_producer,
                        sonic_vacuum=sonic_vacuum, symbolic_norm=symbolic_norm, house_quantizer=house_quantizer,
                        hiphop_vocal_path=mix_hiphop_vocals if mix_hiphop_vocals else None
                    )
                    status.update(label="Complete!", state="complete")
                    st.success(f"Finished {uf.name}")

with tab3:
    st.header("🌀 Live Psy-Mono Studio V3")
    st.write("Python-native algorithmic sequencing with C++ real-time mixing.")

    from streamlit_mic_recorder import mic_recorder
    from hymn_remaker.src.audio_to_midi import transcribe_audio_to_midi
    from hymn_remaker.src.psy_sequencer import PsyGenerator
    import mido

    if "psy_player" not in st.session_state:
        import hymn_player_ext
        st.session_state.psy_player = hymn_player_ext.HymnPlayer(settings.DEFAULT_SOUNDFONT_PATHS[0])
        st.session_state.psy_gen = PsyGenerator()

    col1, col2 = st.columns([1, 2])

    with col1:
        source_mode = st.radio("Input Source", ["Hymn MIDI", "Mic Input"])
        input_midi_path = None

        if source_mode == "Hymn MIDI":
            live_midi = st.file_uploader("Upload Hymn MIDI", type=["mid", "midi"], key="live_psy_uploader")
            if live_midi:
                input_midi_path = os.path.join(settings.INPUT_DIR, "live_input.mid")
                with open(input_midi_path, "wb") as f:
                    f.write(live_midi.getbuffer())
        else:
            audio_rec = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Stop", key="mic")
            if audio_rec:
                temp_audio = os.path.join(settings.INPUT_DIR, "live_mic.wav")
                input_midi_path = os.path.join(settings.INPUT_DIR, "live_input_mic.mid")
                with open(temp_audio, "wb") as f:
                    f.write(audio_rec['bytes'])
                transcribe_audio_to_midi(temp_audio, input_midi_path)

        st.subheader("Sequencer Config")
        bpm = st.slider("Target BPM", 120, 160, 145)
        density = st.slider("Euclidean Density", 1, 16, 5)
        gallop = st.selectbox("Gallop Variant", ["classic", "triplet", "rolling"])

        st.subheader("Master Gain")
        master_gain = st.slider("Global Gain", 0.0, 5.0, 1.0)
        st.session_state.psy_player.set_gain(master_gain)

        st.subheader("Track Mixer")
        vol_k = st.slider("Kick (Ch 0)", 0.0, 1.0, 0.9)
        vol_b = st.slider("Bass (Ch 1)", 0.0, 1.0, 0.7)
        vol_l = st.slider("Lead (Ch 2)", 0.0, 1.0, 0.8)

        st.session_state.psy_player.set_channel_volume(0, vol_k)
        st.session_state.psy_player.set_channel_volume(1, vol_b)
        st.session_state.psy_player.set_channel_volume(2, vol_l)

    with col2:
        st.subheader("Pattern Preview")
        preview_placeholder = st.empty()

        c1, c2, c3 = st.columns(3)
        if c1.button("▶️ Generate & Play"):
            if input_midi_path:
                temp_output = os.path.join(output_dir, "studio_output.mid")
                config = {
                    "targetBpm": bpm, "euclideanDensity": density, "gallopVariant": gallop,
                    "kickVelocity": vol_k, "bassVelocity": vol_b, "leadVelocity": vol_l
                }
                st.session_state.psy_gen.generate(input_midi_path, temp_output, config)

                # Plotly Piano Roll
                mid = mido.MidiFile(temp_output)
                notes = []
                for track in mid.tracks:
                    time = 0
                    for msg in track:
                        time += msg.time
                        if msg.type == 'note_on' and msg.velocity > 0:
                            notes.append({'t': time, 'n': msg.note, 'track': track.name})

                if notes:
                    fig = go.Figure()
                    for t_name in ['Kick', 'Bass', 'Lead']:
                        t_notes = [n for n in notes if n['track'] == t_name and n['t'] < 1920 * 2] # Show 2 bars
                        fig.add_trace(go.Scatter(
                            x=[n['t'] for n in t_notes], y=[n['n'] for n in t_notes],
                            mode='markers', name=t_name, marker=dict(size=10)
                        ))
                    fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_title="Ticks", yaxis_title="MIDI Note")
                    preview_placeholder.plotly_chart(fig, use_container_width=True)

                st.session_state.psy_player.stop_realtime()
                st.session_state.psy_player.load(temp_output)
                st.session_state.psy_player.start_realtime()
                st.session_state.psy_player.play()
                st.success("Playing live!")

        if c2.button("⏹️ Stop"):
            st.session_state.psy_player.stop()
            st.session_state.psy_player.stop_realtime()
            st.info("Stopped.")

        if c3.button("💾 Export Stems"):
            st.info("Stem export triggered. Check output directory.")
