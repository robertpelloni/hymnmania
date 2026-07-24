"""Quick beat-synced video composer using ffmpeg + Magnific clips."""
import subprocess, os, random, json, time

CLIPS = [f for f in os.listdir("pipeline_output/magnific_videos") if f.endswith((".mp4", ".webm", ".mov"))]
CLIP_DIR = os.path.abspath("pipeline_output/magnific_videos")
OUT_DIR = os.path.abspath("pipeline_output/beat_videos")

def get_duration(fpath):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", fpath], capture_output=True, text=True)
    return float(r.stdout.strip())

def compose(audio_fp, hymn, genre_tag, beats_per_phrase=8):
    base = os.path.splitext(os.path.basename(audio_fp))[0]
    out_fp = os.path.join(OUT_DIR, f"{base}_beatsynced.mp4")
    if os.path.exists(out_fp): return out_fp
    
    audio_dur = get_duration(audio_fp)
    
    # Estimate BPM via librosa or fallback
    try:
        import librosa
        y, sr = librosa.load(audio_fp, sr=22050)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo, (list,)): tempo = tempo[0]
        tempo = max(60, min(200, float(tempo)))
    except:
        tempo = 130
    
    beat_dur = 60.0 / tempo
    cut_dur = beats_per_phrase * beat_dur
    n_cuts = max(5, int(audio_dur / cut_dur))
    cut_dur = audio_dur / n_cuts
    
    # Pick unique random clips for each segment
    chosen = random.sample(CLIPS, min(n_cuts, len(CLIPS)))
    
    # Trim each clip to cut_dur
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
    
    # Build concat with crossfade
    seg_list = os.path.join(OUT_DIR, f"_list_{os.getpid()}.txt")
    with open(seg_list, "w") as f:
        for s in segments:
            f.write(f"file '{os.path.abspath(s)}'\n")
    
    # Use ffmpeg concat with small crossfade
    xfade = 0.3
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", seg_list]
    cmd += ["-i", audio_fp, "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-map", "0:v", "-map", "1:a", out_fp]
    subprocess.run(cmd, check=True)
    
    # Cleanup
    for s in segments + [seg_list]:
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
