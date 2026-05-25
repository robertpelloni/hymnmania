"""
Udio Browser Automation Client — Driving Udio.com via CDP (Chrome DevTools Protocol).
"""

import json
import time
import logging
import requests
import websocket
import sys
import os

logger = logging.getLogger(__name__)

class UdioBrowserAutomation:
    """Automates Udio.com generation by injecting prompts directly into the active Edge tab."""

    def __init__(self, port=9222, base_url="https://www.udio.com"):
        self.port = port
        self.base_url = base_url

    def _get_page_targets(self):
        """Fetch all debuggable targets from Edge and filter for pages."""
        try:
            res = requests.get(f"http://127.0.0.1:{self.port}/json", timeout=3)
            targets = res.json()
        except Exception:
            try:
                res = requests.get(f"http://localhost:{self.port}/json", timeout=3)
                targets = res.json()
            except Exception as e:
                logger.warning(f"Could not connect to Edge debugging port {self.port}: {e}")
                return []
        
        return [t for t in targets if t.get('type') == 'page' and 'webSocketDebuggerUrl' in t]

    def _get_active_tab(self, require_udio=False):
        """Find or prioritize the Udio tab."""
        targets = self._get_page_targets()
        udio_targets = [t for t in targets if 'udio.com' in t.get('url', '').lower()]
        if udio_targets:
            for t in udio_targets:
                if '/create' in t.get('url', '').lower(): return t
            for t in udio_targets:
                if '/library' in t.get('url', '').lower() or '/studio' in t.get('url', '').lower(): return t
            return udio_targets[0]
        
        if require_udio:
            raise RuntimeError("No Udio tab found.")
        return targets[0] if targets else None

    def execute_js(self, ws_url, script, timeout=30):
        """Evaluate arbitrary JavaScript on the target tab via CDP and return result."""
        ws_url = ws_url.replace('localhost', '127.0.0.1')
        ws = None
        try:
            ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
            ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            payload = {
                "id": 2,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": script,
                    "returnByValue": True,
                    "awaitPromise": True
                }
            }
            ws.send(json.dumps(payload))
            start_poll = time.time()
            while time.time() - start_poll < timeout:
                try:
                    resp = json.loads(ws.recv())
                    if resp.get('id') == 2:
                        result = resp.get('result', {}).get('result', {})
                        if 'exceptionDetails' in resp.get('result', {}):
                            exception = resp['result']['exceptionDetails'].get('exception', {})
                            if 'description' in exception:
                                 raise RuntimeError(f"JS Error: {exception['description']}")
                        return result.get('value')
                except websocket.WebSocketTimeoutException: pass
            raise TimeoutError(f"CDP Timeout after {timeout}s")
        finally:
            if ws: ws.close()

    def _send_cdp_cmd(self, ws, msg_id, method, params=None):
        payload = {"id": msg_id, "method": method}
        if params: payload["params"] = params
        ws.send(json.dumps(payload))
        start_time = time.time()
        while time.time() - start_time < 8:
            try:
                resp = json.loads(ws.recv())
                if resp.get("id") == msg_id: return resp
            except websocket.WebSocketTimeoutException: pass
        raise TimeoutError(f"No response for {method}")

    def navigate_to(self, tab, url):
        logger.info(f"Navigating tab to {url}...")
        ws_url = tab.get('webSocketDebuggerUrl').replace('localhost', '127.0.0.1')
        try: self.execute_js(ws_url, f"window.location.href = '{url}'")
        except: pass
        ws = None
        try:
            ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
            ws.send(json.dumps({"id": 50, "method": "Page.enable"}))
            ws.recv()
            ws.send(json.dumps({"id": 51, "method": "Page.navigate", "params": {"url": url}}))
            ws.recv()
        finally:
            if ws: ws.close()
        time.sleep(10)

    def navigate_to_create(self, tab):
        self.navigate_to(tab, f"{self.base_url}/create")

    def cdp_click(self, ws_url, selector):
        """Perform a real mouse click on the element matched by selector via CDP."""
        ws_url = ws_url.replace('localhost', '127.0.0.1')
        ws = None
        try:
            ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
            script = f"const r = document.querySelector('{selector}').getBoundingClientRect(); [r.left + r.width/2, r.top + r.height/2]"
            payload = {"id": 60, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}
            ws.send(json.dumps(payload))
            coords = None
            while True:
                resp = json.loads(ws.recv())
                if resp.get('id') == 60:
                    coords = resp.get('result', {}).get('result', {}).get('value')
                    break
            if not coords or len(coords) < 2: return False
            x, y = int(coords[0]), int(coords[1])
            
            # Hover/Move
            ws.send(json.dumps({"id": 61, "method": "Input.dispatchMouseEvent", "params": {"type": "mouseMoved", "x": x, "y": y}}))
            ws.recv()
            time.sleep(0.1)
            # Click sequence
            ws.send(json.dumps({"id": 62, "method": "Input.dispatchMouseEvent", "params": {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1}}))
            ws.recv()
            time.sleep(0.1) # Vital hold time
            ws.send(json.dumps({"id": 63, "method": "Input.dispatchMouseEvent", "params": {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1}}))
            ws.recv()
            return True
        finally:
            if ws: ws.close()

    def _clear_udio_popups(self, ws_url):
        """Detect and clear Udio modals like 'Upload Confirmation' and selection mode."""
        clear_js = """
        (function() {
            const robustClick = (el) => {
                if (!el) return;
                console.log('Gemini: Clicking', el.tagName, el.textContent, el.getAttribute('aria-label'));
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                const events = ['mouseenter', 'mouseover', 'mousedown', 'pointerdown', 'mouseup', 'pointerup', 'click'];
                events.forEach(v => {
                    const cls = v.includes('mouse') ? MouseEvent : PointerEvent;
                    el.dispatchEvent(new cls(v, { bubbles: true, cancelable: true, view: window }));
                });
                try { el.click(); } catch(e) {}
            };
            const all = Array.from(document.querySelectorAll('*'));
            
            // 1. Confirm Modals (Prioritized)
            const confirmBtn = all.find(el => {
                if (el.tagName !== 'BUTTON' || el.offsetParent === null) return false;
                const t = (el.textContent || '').toLowerCase().trim();
                return (t === 'i understand and confirm' || t === 'confirm' || t === 'i understand');
            });
            if (confirmBtn) { 
                robustClick(confirmBtn); 
                return "clicked_confirm_btn:" + (confirmBtn.textContent || 'unnamed'); 
            }

            // 2. Selection Mode
            const clearBtn = all.find(el => {
                const a = (el.getAttribute('aria-label') || '').toLowerCase();
                return (a.includes('clear selected') || a === 'clear selection') && el.offsetParent !== null;
            });
            if (clearBtn) { robustClick(clearBtn); return "cleared_selection"; }

            // 3. Close/Dismiss Modals
            const closeBtn = all.find(el => {
                if (el.tagName !== 'BUTTON' || el.offsetParent === null) return false;
                const t = (el.textContent || '').toLowerCase().trim();
                const a = (el.getAttribute('aria-label') || '').toLowerCase();
                return (t === 'close' || t === 'dismiss' || t === 'ok' || a.includes('close'));
            });
            if (closeBtn) { robustClick(closeBtn); return "closed_modal"; }

            // 4. Remix mode card
            const remixCard = all.find(el => el.textContent.trim() === 'Remix' && el.className.includes('border') && el.tagName === 'BUTTON' && el.offsetParent !== null);
            if (remixCard) {
                robustClick(remixCard);
                return "selected_remix_mode";
            }

            return null;
        })()
        """
        logger.info("Clearing Udio modals and selection mode...")
        for i in range(12):
            action = self.execute_js(ws_url, clear_js, timeout=15)
            if action:
                logger.info(f"  Action (attempt {i+1}): {action}")
                time.sleep(2.5)
                if "selected_remix_mode" in action: break
                if i >= 6: self.execute_js(ws_url, "window.location.reload()"); time.sleep(12); return True
            else: time.sleep(1)
        return True

    def trigger_generation(self, prompt, audio_path=None, variance=0.85, negative_prompt="organ, classical, baroque, church organ, cathedral"):
        tab = self._get_active_tab(require_udio=True)
        ws_url = tab.get('webSocketDebuggerUrl')
        self.navigate_to_create(tab)
        
        if audio_path and os.path.exists(audio_path):
            logger.info(f"Uploading {audio_path}...")
            ws = None
            try:
                ws = websocket.create_connection(ws_url.replace('localhost', '127.0.0.1'), suppress_origin=True, timeout=5)
                self._send_cdp_cmd(ws, 10, "DOM.enable")
                root = self._send_cdp_cmd(ws, 11, "DOM.getDocument")['result']['root']['nodeId']
                node = self._send_cdp_cmd(ws, 12, "DOM.querySelector", {"nodeId": root, "selector": "input[type='file']"})
                self._send_cdp_cmd(ws, 13, "DOM.setFileInputFiles", {"files": [os.path.abspath(audio_path)], "nodeId": node['result']['nodeId']})
            finally:
                if ws: ws.close()
            time.sleep(15)
            self._clear_udio_popups(ws_url)
            time.sleep(5)

        inj_js = """
        (function() {
            // Set Variance slider if present
            let varianceSlider = document.querySelector('input[type="range"][min="0.1"][max="1"]');
            if (varianceSlider) {
                const proto = window.HTMLInputElement.prototype;
                const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
                setter.call(varianceSlider, "%VARIANCE%");
                varianceSlider.dispatchEvent(new Event('input', { bubbles: true }));
                varianceSlider.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Set Style Reduction (negative prompt) if present
            let negInput = document.querySelector('input[placeholder*="avoid"]') || document.querySelector('input[cmdk-input=""]');
            if (negInput) {
                const proto = window.HTMLInputElement.prototype;
                const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
                setter.call(negInput, "%NEG_PROMPT%");
                negInput.dispatchEvent(new Event('input', { bubbles: true }));
                negInput.dispatchEvent(new Event('change', { bubbles: true }));
            }

            let textareas = Array.from(document.querySelectorAll('textarea'));
            let inputs = Array.from(document.querySelectorAll('input[type="text"]'));
            let els = textareas.concat(inputs);
            let inp = els.find(el => {
                let p = (el.placeholder || '').toLowerCase();
                let rect = el.getBoundingClientRect();
                let isVisible = rect.width > 0 && rect.height > 20 && el.offsetParent !== null;
                return isVisible && (p.includes('describe') || p.includes('prompt') || p.includes('imagine') || p.includes('track') || p.includes('song') || p.includes('vocals') || p.includes('revival') || p.includes('sandwich') || p === '');
            });
            if (!inp) inp = textareas.find(el => el.getBoundingClientRect().height > 40 && el.offsetParent !== null);
            if (!inp) return "no_input";
            
            const setter = Object.getOwnPropertyDescriptor(inp.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype, 'value').set;
            setter.call(inp, "%PROMPT%");
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
            if (inp.value !== "%PROMPT%") return "verify_failed:" + inp.value;
            return "ready_to_click";
        })()
        """.replace("%PROMPT%", prompt.replace('"', '\\"').replace('\n', ' ')).replace("%VARIANCE%", str(variance)).replace("%NEG_PROMPT%", negative_prompt.replace('"', '\\"').replace('\n', ' '))

        logger.info("Injecting prompt and clicking Create...")
        for i in range(12):
            res = self.execute_js(ws_url, inj_js, timeout=10)
            if res == "ready_to_click":
                logger.info("Inject success. Triggering real CDP click...")
                magenta_selector = "button.bg-brand-magenta"
                if self.cdp_click(ws_url, magenta_selector):
                    logger.info("SUCCESS: CDP Click triggered! Verifying...")
                    for j in range(8):
                        time.sleep(5)
                        verify_js = "document.body.innerText.includes('Creating') || document.body.innerText.includes('Generating') || document.body.innerText.includes('HYMNMANIA') || document.body.innerText.includes('0/4')"
                        if self.execute_js(ws_url, verify_js):
                            logger.info("SUCCESS: Generation verified.")
                            return True
                else: # Fallback to JS click
                    self.execute_js(ws_url, "document.querySelector('button.bg-brand-magenta').click()")
            
            logger.warning(f"Injection attempt {i+1} failed: {res}. Retrying...")
            self._clear_udio_popups(ws_url)
            time.sleep(5)
        raise RuntimeError("Failed to trigger generation")

    def wait_for_completion_and_download(self, timeout=300):
        """Poll the browser for the latest track's status and trigger download when ready."""
        start = time.time()
        logger.info(f"Polling browser for track completion...")
        while time.time() - start < timeout:
            try:
                tab = self._get_active_tab(require_udio=True)
                ws_url = tab.get('webSocketDebuggerUrl')
            except Exception as e:
                logger.warning(f"Waiting for Udio tab recovery: {e}")
                time.sleep(15); continue
            
            poll_js = """
            (function() {
                const clearBtn = document.querySelector('button[aria-label*="clear selected"]');
                if (clearBtn && clearBtn.offsetParent !== null) { clearBtn.click(); return "clearing_selection"; }
                const all = Array.from(document.querySelectorAll('*'));
                const tracks = all.filter(el => {
                    const txt = el.textContent || '';
                    const h = el.offsetHeight;
                    const hasTime = /\\d+:\\d+/.test(txt);
                    const isNew = /\\d+(s|m) ago/.test(txt) || /\\d+ (sec|min) ago/.test(txt) || txt.includes('000m') || txt.includes('001m') || txt.includes('002m') || txt.includes('003m');
                    const isCreating = txt.toLowerCase().includes('creating') || txt.toLowerCase().includes('generating') || txt.includes('0/4');
                    return (isNew || isCreating) && h >= 50 && h <= 150 && el.querySelector('button');
                });
                if (tracks.length === 0) {
                    const libBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.toLowerCase().includes('library') || (b.getAttribute('aria-label') || '').toLowerCase().includes('library'));
                    if (libBtn && libBtn.offsetParent !== null) { libBtn.click(); return "opening_library"; }
                    return "DIAG_no_tracks";
                }
                tracks.sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
                const latest = tracks[0];
                const text = latest.textContent.toLowerCase();
                if (text.includes('error') || text.includes('failed')) return "error_row";
                const isReady = text.includes(':') && !text.includes('creating') && !text.includes('generating');
                if (!isReady) return "generating (" + text.substring(0, 30).replace(/\\n/g, ' ') + ")";
                
                let b = latest.querySelector('button[aria-label*="Download"]');
                if (!b) {
                    let m = latest.querySelector('button[aria-label*="More"], button[aria-label*="actions"], [data-testid*="more"]');
                    if (m) { m.click(); return "waiting_menu"; }
                    b = document.querySelector('button[aria-label*="Download"]');
                }
                if (b) {
                    b.scrollIntoView({ block: 'center' }); b.click();
                    ['mousedown', 'mouseup', 'click'].forEach(v => b.dispatchEvent(new MouseEvent(v, { bubbles: true, view: window })));
                    return "downloading";
                }
                return "ready_no_btn";
            })()
            """
            try:
                res = self.execute_js(ws_url, poll_js, timeout=15)
                if not res: res = "empty_result"
                if res == "downloading": logger.info("SUCCESS: Download triggered!"); return True
                elif res == "error_row": logger.error("FAILURE: Udio reported error."); return False
                logger.info(f"  Status: {res} ({int(time.time()-start)}s)")
                if "DIAG" in res or "ready_no_btn" in res or "clearing_selection" in res:
                    self.execute_js(ws_url, "window.scrollBy(0, 200); setTimeout(()=>window.scrollBy(0,-200), 200)")
                    self._clear_udio_popups(ws_url)
            except Exception as e: logger.warning(f"Error while polling: {e}")
            time.sleep(15)
        return False
