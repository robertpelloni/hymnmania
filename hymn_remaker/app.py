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
    else:
        version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "VERSION.md")
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
from hymn_remaker.src.local_remaker import LocalMusicRemaker
from hymn_remaker.src.quality_evaluator import QualityEvaluator
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
        udio_oauth_remaker = UdioOAuthRemaker()
        local_remaker = LocalMusicRemaker()
        quality_eval = QualityEvaluator()
        return renderer, remaker, suno_remaker, udio_remaker, content_gen, video_producer, tts_generator, mxl_parser, omr_processor, stem_separator, udio_oauth_remaker, local_remaker, quality_eval
    except Exception as e:
        import traceback
        st.error(f"Failed to initialize modules: {e}")
        st.code(traceback.format_exc())
        return [None] * 13

modules = load_modules()
renderer, remaker, suno_remaker, udio_remaker, content_gen, video_producer, tts_generator, mxl_parser, omr_processor, stem_separator, udio_oauth_remaker, local_remaker, quality_eval = modules

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
    "Sonic Vacuum: Dry staccato sine render",
    "Symbolic Norm: Velocity-flattened grid",
    "House Quantizer: 124 BPM 4/4 structural snap",
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
visualizer_mode = "cline"
if enable_visualizer:
    visualizer_mode = st.sidebar.selectbox("Visualizer Mode", ["kaleidoscope", "cline", "line", "p2p", "avectorscope"], index=0)
generate_vocals = st.sidebar.checkbox("Generate Vocals (ElevenLabs)", value=False)
remake_priority = st.sidebar.selectbox("AI Remake Service", ["udio-oauth", "udio", "suno", "replicate", "local"], index=0)
udio_variance = st.sidebar.slider("Udio Remix Variance", 0.1, 1.0, 0.25)
local_guidance = st.sidebar.slider("Local Guidance Scale", 1.0, 10.0, 3.0)
local_temperature = st.sidebar.slider("Local Temperature", 0.1, 2.0, 1.0)

upload = st.sidebar.checkbox("Upload to YouTube", value=False)

tab1, tab2, tab3, tab4 = st.tabs(["🚀 Automated Pipeline", "🎹 Hymn Editor (Beta)", "🌀 Live Psy-Mono Studio", "📚 Library"])

with tab1:
    uploaded_files = st.file_uploader("Upload MIDI/MusicXML", type=["mid", "midi", "mxl", "xml"], accept_multiple_files=True)
    if st.button("Start Processing", type="primary"):
        st.session_state["is_processing"] = True
        st.session_state["uploaded_files_data"] = []
        if uploaded_files:
            for uf in uploaded_files:
                st.session_state["uploaded_files_data"].append({
                    "name": uf.name, "data": uf.getbuffer().tobytes()
                })

    if st.session_state.get("is_processing", False):
        if not st.session_state.get("uploaded_files_data"):
            st.warning("Please upload files.")
            st.session_state["is_processing"] = False
        else:
            os.makedirs(settings.INPUT_DIR, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)

            saved_files = []
            for uf_data in st.session_state["uploaded_files_data"]:
                file_path = os.path.join(settings.INPUT_DIR, uf_data["name"])
                with open(file_path, "wb") as f:
                    f.write(uf_data["data"])
                saved_files.append(file_path)

            for file_path in saved_files:
                filename = os.path.basename(file_path)
                with st.status(f"Processing {filename}...") as status:
                    try:
                        process_single_midi(
                            midi_path=file_path,
                            output_dir=output_dir,
                            style=style,
                            skip_render=False,
                            skip_remake=False,
                            upload=upload,
                            renderer=renderer,
                            remaker=remaker,
                            suno_remaker=suno_remaker,
                            udio_remaker=udio_remaker,
                            remake_priority=remake_priority,
                            udio_oauth_remaker=udio_oauth_remaker,
                            local_remaker=local_remaker,
                            content_gen=content_gen,
                            video_producer=video_producer,
                            mxl_parser=mxl_parser,
                            omr_processor=omr_processor,
                            tts_generator=tts_generator,
                            stem_separator=stem_separator,
                            generate_vocals=generate_vocals,
                            video_format=video_format,
                            enable_visualizer=enable_visualizer,
                            udio_variance=udio_variance,
                            local_guidance=local_guidance,
                            local_temperature=local_temperature,
                            sonic_vacuum=sonic_vacuum,
                            symbolic_norm=symbolic_norm,
                            house_quantizer=house_quantizer,
                            hiphop_vocal_path=mix_hiphop_vocals if mix_hiphop_vocals else None
                        )
                        status.update(label=f"Finished {filename}!", state="complete")
                    except Exception as e:
                        st.error(f"Error processing {filename}: {e}")
            st.balloons()
            st.session_state["is_processing"] = False

with tab2:
    st.header("Hymn Editor Toolbar")
    editor_file = st.file_uploader("Load MIDI/MusicXML", type=["mid", "midi", "mxl", "xml"], key="editor_up")
    if editor_file:
        file_path = os.path.join(settings.INPUT_DIR, f"edit_{editor_file.name}")
        with open(file_path, "wb") as f:
            f.write(editor_file.getbuffer())

        if st.button("Render Preview 🔊"):
            out_audio = os.path.join(settings.OUTPUT_DIR, "edit_preview.wav")
            renderer.render(file_path, out_audio)
            st.audio(out_audio)

with tab3:
    st.header("🌀 Live Psy-Mono Studio V5: Live Jam Edition")
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
        st.subheader("1. Input & Mode")
        source_mode = st.radio("Input Source", ["Hymn MIDI", "Mic Input"], key="psy_source")
        gen_mode = st.radio("Generation Mode", ["Loop (8 bars)", "Arrangement (56 bars)"], key="psy_mode")

        input_midi_path = None
        if source_mode == "Hymn MIDI":
            live_midi = st.file_uploader("Upload MIDI", type=["mid", "midi"], key="live_up")
            if live_midi:
                input_midi_path = os.path.join(settings.INPUT_DIR, "live_input.mid")
                with open(input_midi_path, "wb") as f:
                    f.write(live_midi.getbuffer())
        else:
            audio_rec = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Stop", key="mic_psy")
            if audio_rec:
                temp_audio = os.path.join(settings.INPUT_DIR, "live_mic.wav")
                input_midi_path = os.path.join(settings.INPUT_DIR, "live_mic.mid")
                with open(temp_audio, "wb") as f:
                    f.write(audio_rec['bytes'])
                transcribe_audio_to_midi(temp_audio, input_midi_path)

        st.subheader("2. Sequencer Config")
        bpm = st.slider("Target BPM", 120, 160, 145, key="psy_bpm")
        density = st.slider("Euclidean Density", 1, 16, 5, key="psy_density")
        gallop = st.selectbox("Gallop Variant", ["classic", "triplet", "rolling"], key="psy_gallop")

        st.subheader("3. Live Performance Mixer")
        master_gain = st.slider("Global Gain", 0.0, 5.0, 1.0, key="psy_gain")
        st.session_state.psy_player.set_gain(master_gain)

        vol_k = st.slider("Kick (Ch 0)", 0.0, 1.0, 0.9, key="psy_vol_k")
        vol_b = st.slider("Bass (Ch 1)", 0.0, 1.0, 0.7, key="psy_vol_b")
        vol_l = st.slider("Lead (Ch 2)", 0.0, 1.0, 0.8, key="psy_vol_l")

        st.session_state.psy_player.set_channel_volume(0, vol_k)
        st.session_state.psy_player.set_channel_volume(1, vol_b)
        st.session_state.psy_player.set_channel_volume(2, vol_l)

        st.subheader("4. Real-time Automation")
        cutoff = st.slider("Filter Cutoff (CC 74)", 0, 127, 100)
        st.session_state.psy_player.send_cc(2, 74, cutoff) # Lead channel filter

        res = st.slider("Resonance (CC 71)", 0, 127, 40)
        st.session_state.psy_player.send_cc(2, 71, res)

        st.subheader("Psy-Energy Macro")
        psy_energy = st.slider("Global Energy", 0.0, 1.0, 0.5, help="Controls density, cutoff, and resonance simultaneously.")
        # Map macro to actual params
        cutoff_macro = int(40 + (psy_energy * 80))
        st.session_state.psy_player.send_cc(2, 74, cutoff_macro)

    with col2:
        st.subheader("Performance Monitor")
        preview_placeholder = st.empty()

        st.subheader("Live Waveform Visualizer")
        viz_data = np.random.randn(100) * (0.1 + master_gain * 0.2)
        if st.session_state.psy_player.is_playing():
             # Add some "beat" pulses
             viz_data[::10] *= 2
        fig_viz = go.Figure(go.Scatter(y=viz_data, mode='lines', line=dict(color='cyan')))
        fig_viz.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, template="plotly_dark")
        st.plotly_chart(fig_viz, use_container_width=True)

        if gen_mode == "Arrangement (56 bars)":
            st.info("Arrangement Map: Intro -> Verse -> Build -> Drop -> Outro")
            # Draw a simple progress bar based on hypothetical playback (Streamlit doesn't track C++ playback time easily)
            # but we can show the static arrangement visual.
            fig_arr = go.Figure()
            fig_arr.add_trace(go.Bar(x=["Intro", "Verse", "Build", "Drop", "Outro"], y=[8, 16, 8, 16, 8], marker_color='indigo'))
            fig_arr.update_layout(title="Arrangement Timeline (Bars)", height=250)
            st.plotly_chart(fig_arr, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        if c1.button("▶️ GENERATE & PLAY"):
            if input_midi_path:
                temp_output = os.path.join(output_dir, "studio_output.mid")
                mode_str = "arrangement" if gen_mode == "Arrangement (56 bars)" else "loop"
                st.session_state.psy_gen.generate(input_midi_path, temp_output, {
                    "targetBpm": bpm, "euclideanDensity": density, "gallopVariant": gallop,
                    "mode": mode_str, "kickVelocity": vol_k, "bassVelocity": vol_b, "leadVelocity": vol_l
                })

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
                        # Show first 4 bars in preview
                        t_notes = [n for n in notes if n['track'] == t_name and n['t'] < 1920 * 4]
                        fig.add_trace(go.Scatter(x=[n['t'] for n in t_notes], y=[n['n'] for n in t_notes], mode='markers', name=t_name))
                    fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), title="Preview (First 4 Bars)")
                    preview_placeholder.plotly_chart(fig, use_container_width=True)

                st.session_state.psy_player.stop_realtime()
                st.session_state.psy_player.load(temp_output)
                st.session_state.psy_player.start_realtime()
                st.session_state.psy_player.play()
                st.success(f"Playing {mode_str} live!")

        if c2.button("⏹️ STOP"):
            st.session_state.psy_player.stop()
            st.session_state.psy_player.stop_realtime()
            st.info("Performance stopped.")

        st.subheader("Manual FX & Jam Trigger")
        fc1, fc2, fc3 = st.columns(3)
        if fc1.button("💥 Crash Cymbal"):
             st.session_state.psy_player.send_note_on(9, 49, 120) # MIDI Ch 10 is usually percussion
        if fc2.button("🚀 Rising Sweep"):
            st.session_state.psy_player.send_note_on(3, 72, 100)
        if fc3.button("🥁 Acid Fill"):
            # Trigger a rapid acid lead sequence on channel 2
            for i in range(4):
                st.session_state.psy_player.send_note_on(2, 60 + i*2, 110)
                time.sleep(0.05)
                st.session_state.psy_player.send_note_off(2, 60 + i*2)
            st.toast("Acid Fill triggered!")

    with st.expander("Novel AI Generation (Local MusicGen)"):
        novel_prompt = st.text_input("Novel Prompt", value="Fast melodic psytrance, 145 BPM, psychedelic leads, high energy")
        novel_duration = st.slider("Duration (sec)", 5, 30, 10)
        if st.button("✨ Generate Novel Track"):
            with st.spinner("Generating novel track..."):
                out_path = os.path.join(output_dir, f"novel_{uuid.uuid4().hex[:8]}.wav")
                local_remaker.generate(novel_prompt, duration=novel_duration, output_path=out_path)
                st.audio(out_path)
                st.success(f"Novel track generated: {out_path}")

with tab4:
    st.header("📚 Output Library")
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith(('.wav', '.mp3', '.mp4'))]
        if not files:
            st.info("No files found in output directory.")
        else:
            # Sort by modification time (newest first)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)

            for f in files:
                f_path = os.path.join(output_dir, f)
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.write(f"**{f}**")

                # Show score if audio
                if f.endswith(('.wav', '.mp3')):
                    score = quality_eval.evaluate(f_path)
                    c2.metric("Quality Score", f"{score}")
                    with c1:
                        st.audio(f_path)

                    if c3.button("🎹 Load Studio", key=f"load_{f}"):
                        if f.endswith('.wav'):
                            # Check if there is a matching MIDI for playback or just load the WAV
                            # For simplicity we just stop existing and load
                            st.session_state.psy_player.stop_realtime()
                            # We need a MIDI for the player load, if we only have WAV we can't play via FluidSynth
                            # but we can at least show it was clicked.
                            st.info(f"Loading {f} to studio player...")
                            # If it's studio_output.mid's render, we can load the mid
                            name_base = f.replace(".wav", "")
                            possible_mid = os.path.join(output_dir, f"{name_base}.mid")
                            if os.path.exists(possible_mid):
                                st.session_state.psy_player.load(possible_mid)
                                st.session_state.psy_player.start_realtime()
                                st.session_state.psy_player.play()
                                st.success(f"Playing {name_base}.mid")
                else:
                    with c1:
                        st.video(f_path)

                if c4.button("🗑️ Delete", key=f"del_{f}"):
                    os.remove(f_path)
                    st.rerun()
                st.divider()
    else:
        st.error(f"Output directory not found: {output_dir}")
