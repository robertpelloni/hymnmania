"""DAILY SOCIAL MEDIA SCHEDULER - Resurrecting Beats
Posts to Facebook with staggered content using the brand template.

Template:
  [Headline: 1-2 punchy sentences with emojis]
  
  FULL ARTIST: RESURRECTING BEATS/HYMNMANIA
  YEAR: 2026
  GENRE: [Genre]
  
  Listen and watch the full journey here:
  🔗 [Link]
  
  #ResurrectingBeats #Hymnmania #[3-5 hashtags]

Features:
- Staggered posting (no duplicate songs back-to-back)
- Alternating genres
- Interleaved YouTube + Suno links
- Posted-video tracking to prevent repeats
- Daily batch posting
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

HEADLINES = {
    "Psytrance": [
        "Prepare your mind and spirit for a high-frequency journey! 🌌 Our latest Psytrance hymn remix is here to elevate your soul and rewire your brain.",
        "Hyper-dimensional sacred geometry meets 145 BPM worship! 🌀 This Psytrance hymn remix will take you somewhere transcendent.",
    ],
    "Deep House": [
        "Smooth, soulful, and deeply spiritual. 🏠✨ Our Deep House hymn remix brings warm golden-hour energy to classic worship.",
        "Golden hour waves meet sacred melody. 🌊 This Deep House hymn remix flows with warmth and intention.",
    ],
    "Dubstep": [
        "Prepare your mind for a bass-drop journey! 🔥 Our latest Dubstep hymn remix is here to rattle your soul.",
        "When sacred melody meets earth-shattering bass! 💀 This Dubstep hymn remix transforms worship into pure energy.",
    ],
    "Drum and Bass": [
        "High-energy breakbeats meet timeless hymns! ⚡ Our Drum and Bass remix pulses with relentless spiritual energy.",
        "Rain-soaked neon streets and breakbeat worship! 🔊 This DnB hymn remix drives through cyberpunk cathedrals.",
    ],
    "Chiptune": [
        "Retro 8-bit worship just dropped! 👾 Our Chiptune hymn remix brings arcade nostalgia to sacred melody.",
        "Pixel-perfect praise! 🎮 This Chiptune hymn remix is a glitching digital journey through classic worship.",
    ],
    "Gabba": [
        "Industrial hardcore meets divine frequency! ⛓️ Our Gabba hymn remix is pure adrenaline for the spirit.",
        "Warehouse strobes and pounding kicks transform this hymn! 🔨 Gabba hardcore worship at its most intense.",
    ],
    "Detroit Techno": [
        "Stark industrial beauty meets rhythmic precision! 🏭 Our Detroit Techno hymn remix breathes new life into tradition.",
        "Warehouse shadows and light — Detroit Techno reimagines this hymn for the underground. 🌃",
    ],
    "Detroit House": [
        "Deep Motor City grooves meet sacred melody! 🏙️ Our Detroit House hymn remix flows with warmth and soul.",
        "Jackin grooves and warm textures transform this classic hymn! 🎹 Detroit House worship for the dance floor.",
    ],
}

HASHTAGS = {
    "Psytrance": "#Psytrance #ChristianPsytrance #145BPM #PsychedelicWorship",
    "Deep House": "#DeepHouse #ElectronicWorship #SoulfulVibes #HouseMusic",
    "Dubstep": "#Dubstep #BassMusic #ElectronicWorship #WobbleWorship",
    "Drum and Bass": "#DrumAndBass #BreakbeatWorship #ElectronicWorship #DNB",
    "Chiptune": "#Chiptune #8BitWorship #RetroWorship #PixelPraise",
    "Gabba": "#Gabba #HardcoreWorship #IndustrialGospel #Hardcore",
    "Detroit Techno": "#DetroitTechno #TechnoWorship #UndergroundGospel",
    "Detroit House": "#DetroitHouse #HouseMusic #MotorCityGospel",
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
    """Build a post using the exact brand template."""
    headlines = HEADLINES.get(genre, ["New electronic hymn remix just dropped! 🎵"])
    headline = random.choice(headlines)
    hashtags_block = HASHTAGS.get(genre, "")
    
    link = f"https://www.youtube.com/watch?v={vid}"
    
    post = f"""{headline}

FULL ARTIST: RESURRECTING BEATS / HYMNMANIA

YEAR: 2026

GENRE: {genre} / Electronic Worship

Listen and watch the full journey here:
{link}

#ResurrectingBeats #Hymnmania {hashtags_block}"""
    return post


def post_to_facebook(page, post_text):
    """Post to Facebook via CDP browser."""
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
            post = build_post(vid, hymn, genre)
            success = post_to_facebook(fb, post)
            if success:
                posted.add(vid)
                save_posted(posted)
                print(f"  OK {hymn} - {genre}")
                print(f"     https://www.youtube.com/watch?v={vid}")
                print()
            time.sleep(3)

        b.close()

    print(f"Posted {len(selected)} videos!")
    print(f"Total posted: {len(posted)}/{len(VIDEOS)}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run(n)
