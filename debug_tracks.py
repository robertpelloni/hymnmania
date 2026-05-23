import json
import logging
from hymn_remaker.src.udio_browser_automation import UdioBrowserAutomation

logging.basicConfig(level=logging.INFO)
u = UdioBrowserAutomation()
tab = u._get_active_tab()
if tab:
    ws_url = tab['webSocketDebuggerUrl']
    # Script to find elements with duration-like text and button children
    script = """
    (function() {
        const all = Array.from(document.querySelectorAll('*'));
        const tracks = all.filter(el => {
            const txt = el.textContent || '';
            const hasDuration = /\\d+:\\d+/.test(txt);
            const hasPlay = !!el.querySelector('button[aria-label*="Play"]');
            return (hasDuration || hasPlay) && el.offsetHeight > 30 && el.offsetHeight < 200;
        });
        return JSON.stringify(tracks.map(el => ({
            tag: el.tagName,
            text: el.textContent.substring(0, 100).replace(/\\n/g, ' '),
            cls: el.className,
            tid: el.getAttribute('data-testid'),
            role: el.getAttribute('role'),
            h: el.offsetHeight
        })));
    })()
    """
    res = u.execute_js(ws_url, script)
    tracks = json.loads(res)
    print(f"Found {len(tracks)} potential tracks:")
    for i, t in enumerate(tracks[:10]):
        print(f"[{i}] {t}")
else:
    print("No Udio tab found.")
