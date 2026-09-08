"""Instagram Reel post via CDP — WORKING flow (coordinate-click new post).
Usage: python ig_cdp_post.py <video_path> <caption_text>
"""
import sys, os, json, time, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

def post(video_path, caption):
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        p = b.contexts[0].new_page()
        p.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)
        p.wait_for_timeout(7000)
        # 1. Click New post svg by coordinates
        js_pos = """
        () => {
            var s = document.querySelector('svg[aria-label="New post"]');
            if (!s) return 'none';
            var r = s.getBoundingClientRect();
            return JSON.stringify({x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)});
        }
        """
        pos = json.loads(p.evaluate(js_pos))
        p.mouse.click(pos["x"], pos["y"])
        p.wait_for_timeout(3500)
        # 2. Click Post option
        p.evaluate("(function(){var els=Array.from(document.querySelectorAll('span,div,button,a'));for(var i=0;i<els.length;i++){var e=els[i];if((e.innerText||'').trim()==='Post'&&e.offsetParent){e.click();return 'ok'}}return 'nf'})()")
        p.wait_for_timeout(4000)
        # 3. Upload file
        abs_path = os.path.abspath(video_path)
        n = p.evaluate("document.querySelectorAll('input[type=file]').length")
        if n > 0:
            p.set_input_files("input[type=file]", abs_path, timeout=90000)
            print("file set OK")
        else:
            print("no file input")
            return False
        p.wait_for_timeout(25000)  # upload+process (reel can take a while)
        # 4. Click Next (crop) then Next (filter) — for reels may differ
        for step in range(3):
            clicked = p.evaluate("(function(){var els=Array.from(document.querySelectorAll('div[role=button],button,span'));for(var i=0;i<els.length;i++){var e=els[i];if((e.innerText||'').trim().toLowerCase()==='next'&&e.offsetParent){e.click();return 'next'}}var sh=els.find(e=>(e.innerText||'').trim().toLowerCase()==='share');if(sh){sh.click();return 'share'}return 'none'})()")
            print(f"  step {step}: {clicked}")
            if clicked == 'share':
                break
            p.wait_for_timeout(6000)
        # 5. Type caption if we reached the caption page
        body = p.evaluate("document.body.innerText")
        if 'share' in body.lower() or 'caption' in body.lower() or 'write a caption' in body.lower():
            # type caption
            typed = p.evaluate(f"""(function(){{
                var editors = document.querySelectorAll('[contenteditable=true], textarea, [role=textbox]');
                for(var i=0;i<editors.length;i++){{
                    var e = editors[i];
                    if(e.offsetParent && e.tagName !== 'BODY'){{
                        e.focus();
                        document.execCommand('insertText', false, {json.dumps(caption)});
                        return 'typed';
                    }}
                }}
                return 'no editor';
            }})()""")
            print("caption:", typed)
            p.wait_for_timeout(3000)
        # 6. Final Share click
        p.evaluate("(function(){var els=Array.from(document.querySelectorAll('div[role=button],button'));for(var i=0;i<els.length;i++){var e=els[i];if((e.innerText||'').trim().toLowerCase()==='share'&&e.offsetParent){e.click();return 'ok'}}return 'nf'})()")
        p.wait_for_timeout(15000)
        print("DONE - IG Reel posted")
        b.close()
        return True

if __name__ == "__main__":
    video = sys.argv[1]
    capfile = sys.argv[2]
    import io
    caption = io.open(capfile, encoding="utf-8").read()
    ok = post(video, caption)
    print("RESULT:", ok)
