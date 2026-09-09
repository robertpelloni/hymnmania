"""Clean cover-generation (no capture) on the dedicated browser.
Usage: python gen_only.py <genre_key> <upload_clip_id> <hymn_name>
Prints the new clip IDs when generation completes.
"""
import sys, os, json, time, requests
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

SUNO = "https://studio-api-prod.suno.com"

GENRE_DESC = {
    "deep_house": "deep house, warm analog chords, rolling syncopated bassline, four-on-the-floor kick at 122 BPM, hypnotic groove, soulful late-night warehouse feel",
    "synthwave": "synthwave, warm analog polysynths, pulsing sidechained bassline, 100-110 BPM neon-drenched retro-future groove, 1980s nostalgia",
}

def main():
    genre = sys.argv[1]
    upload_id = sys.argv[2]
    desc = GENRE_DESC[genre]
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9333")
        # use a clean NEW page (fresh, no prior MediaElementSource)
        # first close stale suno pages to avoid conflicts
        for p in list(b.contexts[0].pages):
            if 'suno.com' in p.url:
                try:
                    p.close()
                except Exception:
                    pass
        time.sleep(1)
        page = b.contexts[0].new_page()
        page.goto("https://suno.com/song/" + upload_id, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(9000)
        # open More menu
        try:
            page.focus('button[aria-label="More menu contents"]')
            page.keyboard.press("Enter")
        except Exception:
            page.evaluate("document.querySelector('button[aria-label=\\\"More menu contents\\\"]')?.click()")
        page.wait_for_timeout(3000)
        # hover Remix to open submenu, then click Cover
        rpos = page.evaluate("""
        () => {
            var b = Array.from(document.querySelectorAll('button[data-context-menu-trigger=true]')).find(x=>{
                var it = x.closest('.context-menu-item');
                return it && (it.innerText||'').trim().toLowerCase()==='remix';
            });
            if (!b) return 'nf';
            var rr = b.getBoundingClientRect();
            return JSON.stringify({x: Math.round(rr.x+rr.width/2), y: Math.round(rr.y+rr.height/2)});
        }
        """)
        if rpos != 'nf':
            pd = json.loads(rpos)
            page.mouse.move(pd["x"], pd["y"])
            page.wait_for_timeout(3500)
            cpos = page.evaluate("""
            () => {
                var all = document.querySelectorAll('.context-menu-item, [role=menuitem], li, button, div');
                for (var e of all) {
                    var t = (e.innerText||'').trim();
                    if (t === 'Cover' && e.offsetParent) {
                        var rr = e.getBoundingClientRect();
                        if (rr.width > 5) return JSON.stringify({x: Math.round(rr.x+rr.width/2), y: Math.round(rr.y+rr.height/2)});
                    }
                }
                return 'nf';
            }
            """)
            if cpos != 'nf':
                cd = json.loads(cpos)
                page.mouse.click(cd["x"], cd["y"])
                print("cover clicked", flush=True)
            else:
                print("cover nf", flush=True)
        # wait for /create
        try:
            page.wait_for_url("**/create**", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(9000)
        print("on create:", page.url[:40], flush=True)
        # fill description
        tas = json.loads(page.evaluate("JSON.stringify(Array.from(document.querySelectorAll('textarea')).map((t,i)=>({i,ml:t.maxLength})))"))
        desc_i = next((t["i"] for t in tas if t["ml"] == 3000), 2)
        page.evaluate("(()=>{var i=" + str(desc_i) + ";var t=document.querySelectorAll('textarea')[i];var s=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;s.call(t," + json.dumps(desc) + ");t.dispatchEvent(new Event('input',{bubbles:true}));t.dispatchEvent(new Event('change',{bubbles:true}));return 'ok'})()")
        page.wait_for_timeout(2000)
        val = page.evaluate("(()=>{var t=document.querySelectorAll('textarea')[" + str(desc_i) + "];return t?t.value.slice(0,25):''})()")
        print("desc:", val, flush=True)
        # instrumental + create
        page.evaluate("(()=>{var b=Array.from(document.querySelectorAll('button,[role=switch],label')).find(x=>x.offsetParent&&/instrumental/i.test(x.innerText||x.getAttribute('aria-label')||''));if(b&&b.getAttribute('aria-pressed')!=='true'){b.click()}})()")
        page.wait_for_timeout(1000)
        trig = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        page.evaluate("(()=>{var b=Array.from(document.querySelectorAll('button')).find(x=>x.offsetParent&&((x.getAttribute('aria-label')||'').toLowerCase().includes('create'))&&!/create new workspace/i.test(x.innerText||''));if(b){b.click();return 'ok'}return 'nf'})()")
        print("Create at", trig, flush=True)
        # poll for NEW cover clips (chirp-*)
        tok = page.evaluate("async()=>{try{return await Clerk.session.getToken()}catch(e){return null}}")
        hdr = {"Authorization": "Bearer " + str(tok)}
        want = desc[:20]
        found_ids = []
        for _ in range(50):
            time.sleep(5)
            r = requests.get(SUNO + "/api/feed/?limit=15", headers=hdr, timeout=20)
            if r.status_code == 200:
                for c in (r.json() or []):
                    mn = c.get("model_name", "")
                    if not (mn.startswith("chirp-") and mn != "chirp-chirp"):
                        continue
                    md = c.get("metadata", {})
                    if md.get("cover_clip_id") != upload_id:
                        continue
                    cr = c.get("created_at", "")
                    if cr >= trig[:-5] and c.get("status") == "complete":
                        cid = c["id"]
                        if cid not in found_ids:
                            found_ids.append(cid)
                            print("NEW CLIP:", cid, mn, cr, flush=True)
                if len(found_ids) >= 2:
                    break
        print("CLIPS:" + ",".join(found_ids), flush=True)
        b.close()

if __name__ == "__main__":
    main()
