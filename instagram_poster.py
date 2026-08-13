"""Instagram Poster for Resurrecting Beats.
Posts beat videos (as Reels) to Instagram via CDP browser web uploader.
"""
import subprocess, os, json, time, random
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "pipeline_output", "instagram")
os.makedirs(OUT_DIR, exist_ok=True)

def create_instagram_clip(beat_path, duration=30, start_offset=5):
    """Create a 9:16 vertical clip for Instagram Reels (max 90s, use 30s)."""
    base = os.path.splitext(os.path.basename(beat_path))[0]
    out = os.path.join(OUT_DIR, f"{base}_ig.mp4")
    if os.path.exists(out): return out
    
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(start_offset), "-i", beat_path, "-t", str(duration),
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",
        "-c:v", "libx264", "-preset", "fast", "-crf", "28",
        "-c:a", "aac", "-b:a", "128k", out
    ]
    try:
        subprocess.run(cmd, check=True)
        if os.path.exists(out) and os.path.getsize(out) > 10000:
            return out
    except: pass
    return None

def build_instagram_caption(track_title, genre, yt_link=""):
    """Instagram caption following the brand template."""
    return f"""🌀 RESURRECTING BEATS: '{track_title}' [{genre}] ⚡

Resurrected from the vault! High-energy {genre} electronic worship.

Every track is meticulously produced using Hymnmania, engineered by Bob & Lum to fuse faith, code, and electronic music.

Full 4K visual journey link in bio! 🔗

#ResurrectingBeats #Hymnmania #SpiritualEDM #Psytrance #ElectronicMusic #WorshipMusic #MusicTherapy #MentalHealthAwareness #{genre.replace(' ', '')}"""

def post_to_instagram(video_path, caption):
    """Post a Reel to Instagram via CDP browser web uploader."""
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        
        # Find or create Instagram page
        ig = None
        for p in b.contexts[0].pages:
            if "instagram.com" in p.url:
                ig = p
                break
        if not ig:
            ig = b.contexts[0].new_page()
            ig.goto("https://www.instagram.com/")
            ig.wait_for_timeout(6000)
        
        # Click "New post" button (click parent of the svg icon)
        ig.evaluate("""(function(){
            var els = document.querySelectorAll('svg[aria-label], a[href], div[role=button]');
            for(var e of els){
                var a = (e.getAttribute('aria-label')||'').toLowerCase();
                if(a === 'new post' || a.includes('create')){
                    (e.closest('[role=button],a') || e.parentElement || e).click();
                    return;
                }
            }
        })()""")
        ig.wait_for_timeout(5000)
        
        # Upload video via file input
        abs_path = os.path.abspath(video_path)
        try:
            file_input = ig.query_selector("input[type=file]")
            if file_input:
                file_input.set_input_files(abs_path)
            else:
                with ig.expect_file_chooser(timeout=20000) as fc:
                    ig.evaluate("document.querySelector('input[type=file]')?.click()")
                fc.value.set_files(abs_path)
            print("  Instagram: video uploaded")
        except Exception as e:
            print(f"  Instagram upload error: {str(e)[:60]}")
            b.close()
            return False
        
        # Wait for processing
        ig.wait_for_timeout(20000)
        
        # Click Next (usually multiple times: crop → filter → caption)
        for _ in range(2):
            ig.evaluate("""(function(){
                var btns = document.querySelectorAll('div[role=button], button');
                for(var b of btns){
                    if((b.innerText||'').trim().toLowerCase() === 'next'){
                        b.click(); return;
                    }
                }
            })()""")
            ig.wait_for_timeout(4000)
        
        # Type caption
        ig.evaluate(f"""(function(){{
            var editors = document.querySelectorAll('[contenteditable=true], textarea, [role=textbox], .ql-editor');
            for(var e of editors){{
                if(e.offsetParent){{
                    e.focus();
                    document.execCommand('insertText', false, {json.dumps(caption)});
                    break;
                }}
            }}
        }})()""")
        ig.wait_for_timeout(3000)
        
        # Click Share
        ig.evaluate("""(function(){
            var btns = document.querySelectorAll('div[role=button], button');
            for(var b of btns){
                var t = (b.innerText||'').trim().toLowerCase();
                if(t === 'share' || t === 'post'){
                    b.click(); return;
                }
            }
        })()""")
        ig.wait_for_timeout(10000)
        print("  Instagram: Reel posted!")
        b.close()
        return True

def post_beat_to_instagram(beat_path, track_title, genre, yt_link=""):
    """Full pipeline: create clip + post to Instagram."""
    clip = create_instagram_clip(beat_path)
    if not clip:
        print("  Instagram clip creation failed")
        return False
    caption = build_instagram_caption(track_title, genre, yt_link)
    return post_to_instagram(clip, caption)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python instagram_poster.py <beat.mp4> [Track] [Genre] [YT Link]")
        sys.exit(1)
    video = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "Hymn Remix"
    genre = sys.argv[3] if len(sys.argv) > 3 else "Psytrance"
    link = sys.argv[4] if len(sys.argv) > 4 else ""
    post_beat_to_instagram(video, title, genre, link)
