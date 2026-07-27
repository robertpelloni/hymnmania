"""DAILY SOCIAL MEDIA SCHEDULER - Resurrecting Beats
Posts to Facebook using HYMNMANIA_SOCIAL_POST_TEMPLATE.

Template:
  {{HOOK_TEXT}} (rocket)

  Track: {{SONG_TITLE}}
  Vibe: {{GENRE_OR_VIBE}}
  Watch on YouTube! {{LINK_CTA_TEXT}}

  {{VISUAL_EXPERIENCE_SUMMARY}} ...

  Every track ... Hymnmania ... Bob & Lum ...

  Fixed hashtag block

Features:
- Staggered posting (no duplicate songs back-to-back)
- YouTube link posted as follow-up comment
- Fixed hashtag block on EVERY post
- Posted-video tracking to prevent repeats
"""
import os, sys, json, time, random
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTED_LOG = os.path.join(ROOT, ".social_posted.json")

# YouTube video IDs with associated genres
VIDEOS = {
    # Thy Word
    "akqa-bTXOgo": ("Thy Word", "Dubstep"),
    "VSRpZgsxfv8": ("Thy Word", "Drum and Bass"),
    "ocaP2tpbtsQ": ("Thy Word", "Drum and Bass"),
    "WLdoz_tB9eQ": ("Thy Word", "Dubstep"),
    "2qU0_cANnYQ": ("Thy Word", "Chiptune"),
    "kSgE8V6oiBM": ("Thy Word", "Deep House"),
    "dJhWAMMR8U4": ("Thy Word", "Deep House"),
    "_9lTWgYDYcU": ("Thy Word", "Detroit House"),
    "ZrxYDhktDXw": ("Thy Word", "Detroit House"),
    "xF8KrtPnSGQ": ("Thy Word", "Detroit Techno"),
    "-BWZIQ0oS_E": ("Thy Word", "Psytrance"),
    "2ShV5n5ZtHI": ("Thy Word", "Gabba"),
    "ccRWO3LkatI": ("Thy Word", "Dubstep"),
    "rUzEtoWb0SY": ("Thy Word", "Chiptune"),
    # Emmanuel
    "aCt1-SbfTh0": ("Emmanuel", "Psytrance"),
    "wkTX_nMT8Nc": ("Emmanuel", "Deep House"),
    "wG48hYrYHow": ("Emmanuel", "Drum and Bass"),
    "8zpFbORMz6s": ("Emmanuel", "Dubstep"),
    # He Leadeth Me
    "H9hQKwtjFY0": ("He Leadeth Me", "Psytrance"),
    "xyLsEJPlpFk": ("He Leadeth Me", "Deep House"),
    "Asshu12id0E": ("He Leadeth Me", "Drum and Bass"),
    # Oh For A Thousand Tongues
    "L_gXqWjCxC8": ("Oh For A Thousand Tongues", "Deep House"),
    "iZ7e5gY16PQ": ("Oh For A Thousand Tongues", "Drum and Bass"),
    # Praise Him
    "_r5pT-9FFk8": ("Praise Him Praise Him", "Deep House"),
    "RPfiWqQnGSg": ("Praise Him Praise Him", "Psytrance"),
}

FIXED_HASHTAGS = """
#ResurrectingBeats #Hymnmania #ChristianPsytrance #Psytrance #ElectronicMusic #WorshipMusic #MusicTherapy #MentalHealthAwareness"""

VISUAL_EXPERIENCES = {
    "Psytrance": "A hyper-dimensional visual journey blending sacred geometry with neon aesthetics, matching the high-energy frequency of this classic hymn.",
    "Deep House": "Warm, atmospheric visuals flow like golden-hour light through cathedral architecture, matching the smooth, soulful energy.",
    "Dubstep": "Seismic bass visualizations ripple through futuristic cathedral spaces as strobes and particle systems erupt with each drop.",
    "Drum and Bass": "Rain-soaked neon streets and cyberpunk cityscapes pulse in sync with the relentless breakbeats.",
    "Chiptune": "Pixel-perfect 8-bit cathedrals and glitching digital stained glass create a retro worship arcade experience.",
    "Gabba": "Industrial warehouse visuals with raw strobe effects and pounding kick-drum visualizations match the intensity of this hardcore worship track.",
    "Detroit Techno": "Stark warehouse shadows and light — a monochromatic journey through the birthplace of techno, reimagined for spiritual elevation.",
    "Detroit House": "Warm Motor City textures flow through cathedral architecture, blending soulful house grooves with sacred geometry.",
    "Hardstyle Trance": "Euphoric laser shows and soaring light columns match the euphoric kicks and melodies.",
    "Synthwave": "Neon-drenched retro grids stretch into infinite digital horizons as this synthwave reimagining unfolds.",
}


def load_posted():
    if os.path.exists(POSTED_LOG):
        with open(POSTED_LOG) as f:
            return set(json.load(f))
    return set()


def save_posted(posted):
    with open(POSTED_LOG, "w") as f:
        json.dump(list(posted), f)


def pick_videos(posted, count=3):
    """Pick videos avoiding back-to-back repeats of same hymn or genre."""
    available = [(vid, hymn, genre) for vid, (hymn, genre) in VIDEOS.items() if vid not in posted]
    if not available:
        posted.clear()  # Reset if all posted
        available = list(VIDEOS.items())
        available = [(vid, hymn, genre) for vid, (hymn, genre) in available]
    
    random.shuffle(available)
    selected = []
    last_hymn = None
    last_genre = None
    
    for vid, hymn, genre in available:
        if len(selected) >= count:
            break
        if hymn != last_hymn and genre != last_genre:
            selected.append((vid, hymn, genre))
            last_hymn = hymn
            last_genre = genre
    
    return selected


def build_post(vid, hymn, genre):
    """Build a post using HYMNMANIA_SOCIAL_POST_TEMPLATE."""
    hooks = {
        "Psytrance": "Prepare your mind and spirit for a high-frequency journey through sacred geometry and neon cathedrals!",
        "Deep House": "Smooth, soulful, and deeply spiritual — warm golden-hour energy meets classic worship.",
        "Dubstep": "When sacred melody meets earth-shattering bass drops — pure electronic worship energy.",
        "Drum and Bass": "High-energy breakbeats meet timeless hymns — relentless spiritual energy through cyberpunk cathedrals.",
        "Chiptune": "Retro 8-bit worship just dropped — arcade nostalgia meets sacred melody in pixel-perfect praise.",
        "Gabba": "Industrial hardcore meets divine frequency — pure adrenaline for the spirit at 200+ BPM.",
        "Detroit Techno": "Stark industrial beauty meets rhythmic precision — Detroit Techno reimagines this hymn for the underground.",
        "Detroit House": "Deep Motor City grooves meet sacred melody — Detroit House worship for the dance floor.",
        "Hardstyle Trance": "Euphoric hardstyle kicks and soaring melodies transform this hymn into pure energy.",
        "Synthwave": "Neon-drenched retro-future worship reimagined through vintage synths and pulsing basslines.",
    }
    hook = hooks.get(genre, f"New {hymn} electronic remix just dropped!")
    visual = VISUAL_EXPERIENCES.get(genre, "Our visuals are crafted to deliver the ultimate psychedelic experience.")
    
    post = f"""{hook} 🚀

🎵 Track: {hymn}
🎹 Vibe: {genre} / Electronic Worship
📺 Watch the full visual journey on YouTube! (Full 4K visual journey on YouTube - link in top comment! 🔗)

{visual} Our visuals are crafted by our creators using multiple digital media tools to deliver the ultimate psychedelic experience.

Every track is meticulously produced using Hymnmania, a custom software automation tool engineered by Bob & Lum to fuse faith, code, and electronic music. We believe psytrance is more than music — its fast, repetitive tempos stimulate the brain's reward pathways and induce a state of deep meditation and stress relief. 🙏🧠

Head over to the Resurrecting Beats YouTube channel to stream it now! Let us know in the comments how this frequency makes you feel. 👇

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{FIXED_HASHTAGS}"""
    return post, f"https://www.youtube.com/watch?v={vid}"


def post_to_facebook(page, post_text, yt_link):
    """Post to Facebook via CDP browser, then add YouTube link as comment."""
    page.goto("https://www.facebook.com/")
    page.wait_for_timeout(5000)

    # Open composer
    page.evaluate(
        """(function(){var a=document.querySelectorAll('div[role=button],span');for(var e of a){if((e.innerText||'').trim().includes("What's on your mind")){e.click();return}}})()"""
    )
    page.wait_for_timeout(3000)

    # Type post
    page.evaluate(
        f"""(function(){{var t=document.querySelector('[role=dialog] [role=textbox], [role=dialog] div[contenteditable=true]');if(t){{t.focus();document.execCommand('insertText',false,{json.dumps(post_text)});}}}})()"""
    )
    page.wait_for_timeout(8000)

    # Click Post
    page.evaluate(
        """(function(){var a=document.querySelectorAll('[role=dialog] div[role=button], [role=dialog] span');for(var e of a){if((e.innerText||'').trim()==='Post'){e.click();return}}})()"""
    )
    page.wait_for_timeout(5000)
    
    # Add YouTube link as a follow-up comment
    time.sleep(3)
    page.evaluate(
        f"""(function(){{
            var comments = document.querySelectorAll('[role=textbox], div[contenteditable=true]');
            for(var c of comments){{
                if(c.offsetParent !== null && c.closest('[role=article]')){{
                    c.focus();
                    document.execCommand('insertText', false, {json.dumps(yt_link)});
                    c.dispatchEvent(new KeyboardEvent('keydown', {{key: 'Enter', bubbles: true}}));
                    return;
                }}
            }}
        }})()"""
    )
    page.wait_for_timeout(3000)
    return True


def run(count=3):
    """Post N videos to Facebook with staggered content."""
    posted = load_posted()
    selected = pick_videos(posted, count)

    if not selected:
        print("No videos to post!")
        return

    print(f"Posting {len(selected)} videos to Facebook...\n")

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        fb = b.contexts[0].new_page()

        for vid, hymn, genre in selected:
            post, yt_link = build_post(vid, hymn, genre)
            success = post_to_facebook(fb, post, yt_link)
            if success:
                posted.add(vid)
                save_posted(posted)
                print(f"  OK {hymn} - {genre}")
                print(f"     {yt_link}")
                print()
            time.sleep(3)

        b.close()

    print(f"Posted {len(selected)} videos!")
    print(f"Total posted: {len(posted)}/{len(VIDEOS)}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run(n)
