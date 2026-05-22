import json
import logging
from hymn_remaker.src.udio_browser_automation import UdioBrowserAutomation

logging.basicConfig(level=logging.INFO)
u = UdioBrowserAutomation()
tab = u._get_active_tab()
if tab:
    ws_url = tab['webSocketDebuggerUrl']
    script = 'JSON.stringify(Array.from(document.querySelectorAll("button, [role=\'button\'], div.cursor-pointer")).map(b => ({t: (b.textContent || "").trim(), c: (typeof b.className === "string") ? b.className : ""})))'
    res = u.execute_js(ws_url, script)
    buttons = json.loads(res)
    for b in buttons:
        if b['t'] in ['Create', 'Remix', 'Generate']:
            print(f"FOUND: {b}")
        elif 'create' in b['t'].lower() or 'remix' in b['t'].lower():
             print(f"POTENTIAL: {b}")
else:
    print("No Udio tab found.")
