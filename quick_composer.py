"""Enhanced beat-synced video composer with RESURRECTING BEATS intro/outro.
Uses ffmpeg drawtext for flashy artistic branding matched to each genre.
Each video starts with a different random clip for unique YouTube previews.
"""
import subprocess, os, random, json, time

CLIPS = [f for f in os.listdir("pipeline_output/magnific_videos") if f.endswith((".mp4", ".webm", ".mov"))]
CLIP_DIR = os.path.abspath("pipeline_output/magnific_videos")
OUT_DIR = os.path.abspath("pipeline_output/beat_videos")

# Genre-matched text styles for intro/outro
GENRE_STYLES = {
    "Psytrance": {"color": "white@0.9", "border": "purple@0.8", "font": "Arial", "effect": "neon glow"},
    "Deep House": {"color": "gold@0.9", "border": "darkblue@0.6", "font": "Arial", "effect": "warm fade"},
    "Dubstep": {"color": "red@0.9", "border": "black@0.8", "font": "Impact", "effect": "bass shake"},
    "Drum and Bass": {"color": "cyan@0.9", "border": "navy@0.7", "font": "Arial", "effect": "fast pulse"},
    "Chiptune": {"color": "#00FF00@0.9", "border": "#003300@0.8", "font": "Courier", "effect": "pixel glitch"},
    "Gabba": {"color": "orange@0.9", "border": "darkred@0.8", "font": "Impact", "effect": "hardcore flash"},
    "Detroit Techno": {"color": "silver@0.9", "border": "#222222@0.8", "font": "Arial", "effect": "industrial"},
    "Detroit House": {"color": "#FFD700@0.9", "border": "#8B4513@0.7", "font": "Arial", "effect": "smooth"},
    "Hardstyle Trance": {"color": "yellow@0.9", "border": "orange@0.7", "font": "Impact", "effect": "laser blast"},
    "Synthwave": {"color": "#FF00FF@0.9", "border": "#000066@0.8", "font": "Arial", "effect": "neon grid"},
    "Japanese Hardcore Techno": {"color": "cyan@0.9", "border": "magenta@0.7", "font": "Impact", "effect": "kawaii rave"},
    "Chiptune": {"color": "#00FF00@0.9", "border": "#003300@0.8", "font": "Courier", "effect": "pixel glitch"},
}

def get_duration(fpath):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", fpath], capture_output=True, text=True)
    return float(r.stdout.strip())

def make_intro(duration=3.0, genre="Psytrance"):
    """Create an intro clip with RESURRECTING BEATS text."""
    style = GENRE_STYLES.get(genre, GENRE_STYLES["Psytrance"])
    out = os.path.join(OUT_DIR, f"_intro_{os.getpid()}_{random.randint(1000,9999)}.mp4")
    
    # Pick a random Magnific clip for the intro background
    bg = random.choice(CLIPS)
    bg_path = os.path.join(CLIP_DIR, bg)
    bg_dur = get_duration(bg_path)
    bg_start = random.uniform(0, max(0.1, bg_dur - duration))
    
    # Create intro: clip background + RESURRECTING BEATS text overlay
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(bg_start), "-i", bg_path, "-t", str(duration),
        "-vf", f"drawtext=text='RESURRECTING':fontcolor={style['color']}:fontsize=48:fontfile=/Windows/Fonts/impact.ttf:x=(w-text_w)/2:y=(h/2-text_h-10):bordercolor={style['border']}:borderw=3,drawtext=text='BEATS':fontcolor={style['color']}:fontsize=56:fontfile=/Windows/Fonts/impact.ttf:x=(w-text_w)/2:y=(h/2+10):bordercolor={style['border']}:borderw=3,drawtext=text='{genre}':fontcolor=white@0.6:fontsize=24:fontfile=/Windows/Fonts/arial.ttf:x=(w-text_w)/2:y=(h/2+70)",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an", out
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        if os.path.exists(out) and os.path.getsize(out) > 10000:
            return out
    except:
        pass
    return None

def make_outro(duration=3.0, genre="Psytrance"):
    """Create an outro clip with RESURRECTING BEATS + subscribe text."""
    style = GENRE_STYLES.get(genre, GENRE_STYLES["Psytrance"])
    out = os.path.join(OUT_DIR, f"_outro_{os.getpid()}_{random.randint(1000,9999)}.mp4")
    
    bg = random.choice(CLIPS)
    bg_path = os.path.join(CLIP_DIR, bg)
    bg_dur = get_duration(bg_path)
    bg_start = random.uniform(0, max(0.1, bg_dur - duration))
    
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(bg_start), "-i", bg_path, "-t", str(duration),
        "-vf", f"drawtext=text='RESURRECTING':fontcolor={style['color']}:fontsize=42:fontfile=/Windows/Fonts/impact.ttf:x=(w-text_w)/2:y=(h/2-text_h-15):bordercolor={style['border']}:borderw=3,drawtext=text='BEATS':fontcolor={style['color']}:fontsize=48:fontfile=/Windows/Fonts/impact.ttf:x=(w-text_w)/2:y=(h/2+10):bordercolor={style['border']}:borderw=3,drawtext=text='Subscribe for more!':fontcolor=white@0.7:fontsize=20:fontfile=/Windows/Fonts/arial.ttf:x=(w-text_w)/2:y=(h/2+65),fade=t=out:st=2.5:d=0.5",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an", out
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        if os.path.exists(out) and os.path.getsize(out) > 10000:
            return out
    except:
        pass
    return None

def compose(audio_fp, hymn, genre_tag, beats_per_phrase=8, add_branding=True):
    base = os.path.splitext(os.path.basename(audio_fp))[0]
    out_fp = os.path.join(OUT_DIR, f"{base}_beatsynced.mp4")
    if os.path.exists(out_fp): return out_fp
    
    audio_dur = get_duration(audio_fp)
    
    try:
        import librosa
        y, sr = librosa.load(audio_fp, sr=22050)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo, (list,)): tempo = tempo[0]
        tempo = max(60, min(200, float(tempo)))
    except:
        tempo = 130
    
    beat_dur = 60.0 / tempo
    # Scale beats_per_phrase with tempo to keep clip duration in 3-6s range
    if tempo >= 160:      # Gabba, fast DnB — 16 beats per phrase
        beats_per_phrase = 16
    elif tempo >= 130:    # Psytrance, Hardstyle — 12 beats
        beats_per_phrase = 12
    elif tempo >= 100:    # Deep House, Detroit — 8 beats
        beats_per_phrase = 8
    else:                 # Half-speed, ambient — 4 beats
        beats_per_phrase = 4
    cut_dur = beats_per_phrase * beat_dur
    n_cuts = max(5, int(audio_dur / cut_dur))
    cut_dur = audio_dur / n_cuts
    
    # Determine genre for styling
    genre = "Psytrance"
    for g in GENRE_STYLES:
        if g.lower() in genre_tag.lower():
            genre = g
            break
    
    # Pick UNIQUE random clips — no duplicates within this video
    chosen = random.sample(CLIPS, min(n_cuts, len(CLIPS)))
    
    # Trim each clip to cut_dur with RANDOM start positions
    segments = []
    for i, clip in enumerate(chosen):
        cp = os.path.join(CLIP_DIR, clip)
        seg = os.path.join(OUT_DIR, f"_seg_{i}_{os.getpid()}.mp4")
        try:
            cdur = get_duration(cp)
            start = random.uniform(0, max(0.1, cdur - cut_dur))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                "-ss", str(start), "-i", cp, "-t", str(cut_dur),
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", seg], check=True)
            segments.append(seg)
        except:
            continue
    
    if len(segments) < 2:
        return None
    
    # Build intro and outro
    intro = None
    outro = None
    if add_branding:
        try:
            intro = make_intro(2.5, genre)
            outro = make_outro(3.0, genre)
        except:
            pass
    
    # Build final concat list: intro + segments + outro
    seg_list = os.path.join(OUT_DIR, f"_list_{os.getpid()}.txt")
    with open(seg_list, "w") as f:
        if intro:
            f.write(f"file '{os.path.abspath(intro)}'\n")
        for s in segments:
            f.write(f"file '{os.path.abspath(s)}'\n")
        if outro:
            f.write(f"file '{os.path.abspath(outro)}'\n")
    
    # Adjust audio — pad with silence at start/end for intro/outro
    audio_cmd = ["ffmpeg", "-y", "-loglevel", "error",
        "-i", audio_fp,
        "-af", f"adelay={'2500' if add_branding else '0'}|{'2500' if add_branding else '0'}",
        "-c:a", "aac", "-b:a", "192k",
        os.path.join(OUT_DIR, f"_audio_{os.getpid()}.aac")]
    audio_out = os.path.join(OUT_DIR, f"_audio_{os.getpid()}.aac")
    subprocess.run(audio_cmd, check=True)
    
    # Combine video + audio
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", seg_list]
    cmd += ["-i", audio_out, "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-map", "0:v", "-map", "1:a", out_fp]
    subprocess.run(cmd, check=True)
    
    # Cleanup
    cleanup = segments + [seg_list, audio_out]
    if intro: cleanup.append(intro)
    if outro: cleanup.append(outro)
    for s in cleanup:
        try: os.remove(s)
        except: pass
    
    sz = os.path.getsize(out_fp)//1024//1024
    print(f"  {hymn[:20]} - {genre_tag[:30]:30s} {sz:4d}MB")
    return out_fp

if __name__ == "__main__":
    import sys
    audio = sys.argv[1] if len(sys.argv) > 1 else None
    hymn = sys.argv[2] if len(sys.argv) > 2 else "Track"
    genre = sys.argv[3] if len(sys.argv) > 3 else "Electronic"
    if audio:
        compose(audio, hymn, genre)
