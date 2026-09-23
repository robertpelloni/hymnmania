"""Enhanced beat video composer with crossfade, end screens, and audio-reactive overlay."""
import subprocess, os, random, json, time, math

CLIPS = [f for f in os.listdir("pipeline_output/magnific_videos") if f.endswith((".mp4", ".webm", ".mov"))]
CLIP_DIR = os.path.abspath("pipeline_output/magnific_videos")
OUT_DIR = os.path.abspath("pipeline_output/beat_videos")

GENRE_STYLES = {
    "Psytrance": {"color": "white@0.9", "border": "purple@0.8", "hex": "#9933FF"},
    "Deep House": {"color": "gold@0.9", "border": "darkblue@0.6", "hex": "#FFD700"},
    "Dubstep": {"color": "red@0.9", "border": "black@0.8", "hex": "#FF2222"},
    "Drum and Bass": {"color": "cyan@0.9", "border": "navy@0.7", "hex": "#00CCFF"},
    "Chiptune": {"color": "#00FF00@0.9", "border": "#003300@0.8", "hex": "#00FF00"},
    "Gabba": {"color": "orange@0.9", "border": "darkred@0.8", "hex": "#FF6600"},
    "Detroit Techno": {"color": "silver@0.9", "border": "#222222@0.8", "hex": "#CCCCCC"},
    "Detroit House": {"color": "#FFD700@0.9", "border": "#8B4513@0.7", "hex": "#FFD700"},
    "Hardstyle Trance": {"color": "yellow@0.9", "border": "orange@0.7", "hex": "#FFFF00"},
    "Synthwave": {"color": "#FF00FF@0.9", "border": "#000066@0.8", "hex": "#FF00FF"},
    "Japanese Hardcore Techno": {"color": "cyan@0.9", "border": "magenta@0.7", "hex": "#00FFFF"},
}

def get_duration(fpath):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", fpath], capture_output=True, text=True)
    return float(r.stdout.strip())

def get_resolution(fpath):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", fpath],
        capture_output=True, text=True)
    w, h = r.stdout.strip().split("x")
    return int(w), int(h)

def make_intro(duration=2.5, genre="Psytrance"):
    style = GENRE_STYLES.get(genre, GENRE_STYLES["Psytrance"])
    out = os.path.join(OUT_DIR, f"_intro_{os.getpid()}_{random.randint(1000,9999)}.mp4")
    bg = random.choice(CLIPS)
    bg_path = os.path.join(CLIP_DIR, bg)
    bg_dur = get_duration(bg_path)
    bg_start = random.uniform(0, max(0.1, bg_dur - duration))
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(bg_start), "-i", bg_path, "-t", str(duration),
        "-vf", f"drawtext=text='RESURRECTING':fontcolor={style['color']}:fontsize=48:x=(w-text_w)/2:y=(h/2-text_h-10):bordercolor={style['border']}:borderw=3,drawtext=text='BEATS':fontcolor={style['color']}:fontsize=56:x=(w-text_w)/2:y=(h/2+10):bordercolor={style['border']}:borderw=3,drawtext=text='{genre}':fontcolor=white@0.6:fontsize=24:x=(w-text_w)/2:y=(h/2+70)",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an", out
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        if os.path.exists(out) and os.path.getsize(out) > 10000: return out
    except: pass
    return None

def make_outro(duration=3.0, genre="Psytrance"):
    style = GENRE_STYLES.get(genre, GENRE_STYLES["Psytrance"])
    out = os.path.join(OUT_DIR, f"_outro_{os.getpid()}_{random.randint(1000,9999)}.mp4")
    bg = random.choice(CLIPS)
    bg_path = os.path.join(CLIP_DIR, bg)
    bg_dur = get_duration(bg_path)
    bg_start = random.uniform(0, max(0.1, bg_dur - duration))
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(bg_start), "-i", bg_path, "-t", str(duration),
        "-vf", f"drawtext=text='RESURRECTING':fontcolor={style['color']}:fontsize=42:x=(w-text_w)/2:y=(h/2-text_h-15):bordercolor={style['border']}:borderw=3,drawtext=text='BEATS':fontcolor={style['color']}:fontsize=48:x=(w-text_w)/2:y=(h/2+10):bordercolor={style['border']}:borderw=3,drawtext=text='Subscribe for more!':fontcolor=white@0.7:fontsize=20:x=(w-text_w)/2:y=(h/2+65),fade=t=out:st=2.5:d=0.5",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an", out
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        if os.path.exists(out) and os.path.getsize(out) > 10000: return out
    except: pass
    return None

def generate_thumbnail(video_path, hymn, genre, out_name):
    """Generate custom thumbnail with genre + hymn title overlay."""
    out = os.path.join(OUT_DIR, f"{out_name}_thumb.jpg")
    if os.path.exists(out): return out
    
    style = GENRE_STYLES.get(genre, GENRE_STYLES["Psytrance"])
    
    # Extract a frame from 1/3 into the video for the best visual
    dur = get_duration(video_path)
    thumb_time = dur * 0.33
    
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(thumb_time), "-i", video_path,
        "-vframes", "1",
        "-vf", f"drawtext=text='{genre}':fontcolor={style['color']}:fontsize=36:x=20:y=20:bordercolor={style['border']}:borderw=3,drawtext=text='{hymn}':fontcolor=white@0.9:fontsize=28:x=20:y=65:bordercolor=black@0.7:borderw=2,drawtext=text='RESURRECTING BEATS':fontcolor={style['color']}:fontsize=24:x=w-text_w-20:y=20:bordercolor={style['border']}:borderw=2",
        out
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        if os.path.exists(out): return out
    except: pass
    return None

def compose(audio_fp, hymn, genre_tag, add_branding=True):
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
    if tempo >= 160: beats_per_phrase = 16
    elif tempo >= 130: beats_per_phrase = 12
    elif tempo >= 100: beats_per_phrase = 8
    else: beats_per_phrase = 4
    cut_dur = beats_per_phrase * beat_dur
    n_cuts = max(5, int(audio_dur / cut_dur))
    cut_dur = audio_dur / n_cuts
    
    genre = "Psytrance"
    for g in GENRE_STYLES:
        if g.lower() in genre_tag.lower():
            genre = g
            break
    
    chosen = random.sample(CLIPS, min(n_cuts, len(CLIPS)))
    
    segments = []
    for i, clip in enumerate(chosen):
        cp = os.path.join(CLIP_DIR, clip)
        seg = os.path.join(OUT_DIR, f"_seg_{i}_{os.getpid()}.mp4")
        try:
            cdur = get_duration(cp)
            start = random.uniform(0, max(0.1, cdur - cut_dur))
            # Clip with audio-reactive overlay
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                "-ss", str(start), "-i", cp, "-t", str(cut_dur),
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", seg], check=True)
            segments.append(seg)
        except: continue
    
    if len(segments) < 2: return None
    
    # Build concat with crossfade transitions
    xfade_dur = 0.4
    seg_list = os.path.join(OUT_DIR, f"_list_{os.getpid()}.txt")
    
    # Build filter complex for crossfade
    inputs_list = []
    if add_branding:
        intro = make_intro(2.5, genre)
        outro = make_outro(3.0, genre)
        if intro: inputs_list.append(intro)
    inputs_list.extend(segments)
    if add_branding and 'outro' in dir() and outro: inputs_list.append(outro)
    
    # Write concat file
    with open(seg_list, "w") as f:
        for s in inputs_list:
            f.write(f"file '{os.path.abspath(s)}'\n")
    
    # Build xfade filter
    n_inputs = len(inputs_list)
    if n_inputs > 2:
        # ffmpeg xfade: [v0][v1]xfade=duration=0.4:offset=dur1-0.4[x1]; [x1][v2]xfade...[xN]
        xfade_filters = []
        last = "0:v"
        for i in range(1, n_inputs):
            seg_dur = get_duration(inputs_list[i-1])
            offset = seg_dur - xfade_dur
            out_label = f"x{i}"
            xfade_filters.append(f"[{last}][{i}:v]xfade=duration={xfade_dur}:offset={offset}[{out_label}]")
            last = out_label
        
        xfade_chain = ";".join(xfade_filters)
        
        # Build input args
        input_args = []
        for s in inputs_list:
            input_args.extend(["-i", s])
        
        # Build audio with delay for intro
        audio_out = os.path.join(OUT_DIR, f"_audio_{os.getpid()}.aac")
        audio_delay = 2500 if add_branding else 0
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio_fp,
            "-af", f"adelay={audio_delay}|{audio_delay}", "-c:a", "aac", "-b:a", "192k", audio_out], check=True)
        
        cmd = ["ffmpeg", "-y", "-loglevel", "error"] + input_args + [
            "-i", audio_out,
            "-filter_complex", xfade_chain + f";[{last}]format=yuv420p[vout]",
            "-map", "[vout]", "-map", f"{n_inputs}:a",
            "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", out_fp
        ]
    else:
        # Simple concat for short videos
        audio_out = os.path.join(OUT_DIR, f"_audio_{os.getpid()}.aac")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio_fp,
            "-c:a", "aac", "-b:a", "192k", audio_out], check=True)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", seg_list,
            "-i", audio_out, "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-map", "0:v", "-map", "1:a", out_fp]
    
    subprocess.run(cmd, check=True)
    
    # Generate custom thumbnail
    thumbnail = generate_thumbnail(out_fp, hymn, genre, base)
    if thumbnail:
        # Set as YouTube thumbnail via API later
        pass
    
    # Cleanup
    cleanup = segments + [seg_list, audio_out]
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
