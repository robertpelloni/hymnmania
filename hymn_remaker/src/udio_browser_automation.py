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

    def _get_active_tab(self):
        """Find or prioritize the Udio tab, falling back to any active page."""
        targets = self._get_page_targets()
        if not targets: return None
        for t in targets:
            if 'udio' in t.get('url', '').lower(): return t
        return targets[0]

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
                            raise RuntimeError(f"JS Error: {exception.get('description', 'Unknown')}")
                        return result.get('value')
                except websocket.WebSocketTimeoutException:
                    pass
            raise TimeoutError(f"CDP Timeout after {timeout}s")
        finally:
            if ws: ws.close()

    def navigate_to_create(self, tab):
        if 'udio.com/create' not in tab.get('url', ''):
            logger.info("Navigating to Udio.com/create...")
            ws_url = tab.get('webSocketDebuggerUrl').replace('localhost', '127.0.0.1')
            ws = None
            try:
                ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
                ws.send(json.dumps({"id": 3, "method": "Page.navigate", "params": {"url": f"{self.base_url}/create"}}))
                ws.recv()
            finally:
                if ws: ws.close()
            time.sleep(3)

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

    def _clear_udio_popups(self, ws_url):
        """Detect and clear Udio modals like 'Upload Confirmation'."""
        clear_js = """
        (function() {
            const robustClick = (el) => {
                if (!el) return;
                console.log('Gemini: Clicking', el.tagName, el.textContent);
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                ['mousedown', 'mouseup', 'click'].forEach(v => {
                    el.dispatchEvent(new MouseEvent(v, { bubbles: true, cancelable: true, view: window }));
                });
                if (el.tagName === 'LABEL' || el.getAttribute('role') === 'checkbox') {
                    el.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', bubbles: true }));
                }
                try { el.click(); } catch(e) {}
            };
            const all = Array.from(document.querySelectorAll('*'));
            const isStr = (v) => typeof v === 'string';
            
            let actions = [];
            
            // 1. Upload Confirmation Specifics
            const confirmText = all.find(el => (el.textContent || '').toLowerCase().includes('understand') && el.textContent.length < 100);
            if (confirmText) {
                const cb = all.find(el => {
                    const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                    return aria.includes('understand') && (el.getAttribute('role') === 'checkbox' || el.tagName === 'BUTTON');
                });
                if (cb && cb.getAttribute('aria-checked') !== 'true') {
                    robustClick(cb);
                    actions.push("checked_understand_box");
                }
                
                const btn = all.find(el => {
                    const t = (el.textContent || '').toLowerCase().trim();
                    return (t.includes('confirm') || t === 'i understand') && !el.className.includes('opacity-50') && el.tagName === 'BUTTON';
                });
                if (btn) {
                    robustClick(btn);
                    actions.push("clicked_confirm_button");
                }
            }

            // 2. Selection Mode: if "Selected" text is visible
            const selectedText = all.find(el => (el.textContent || '').includes('Selected') && /\\d+/.test(el.textContent));
            if (selectedText) {
                const cancel = all.find(el => (el.textContent || '').toLowerCase() === 'cancel' || (el.textContent || '').toLowerCase() === 'deselect');
                if (cancel) {
                    robustClick(cancel);
                    actions.push("cancelled_selection_mode");
                }
            }

            // 3. Remix mode selection card
            let rem = all.find(el => {
                const t = (el.textContent || '').trim();
                const cls = isStr(el.className) ? el.className : (el.className?.baseVal || '');
                return t === 'Remix' && cls.includes('border') && el.tagName === 'BUTTON';
            });
            if (rem) {
                robustClick(rem);
                actions.push("selected_remix_card");
            }

            return actions.length > 0 ? actions.join("+") : null;
        })()
        """
        logger.info("Clearing Udio modals and selection mode...")
        for i in range(12):
            action = self.execute_js(ws_url, clear_js, timeout=15)
            if action:
                logger.info(f"  Action (attempt {i+1}): {action}")
                time.sleep(2.5)
                if "selected_remix_card" in action: break
            else:
                time.sleep(1)
        return True

    def trigger_generation(self, prompt, audio_path=None, variance=0.85):
        tab = self._get_active_tab()
        if not tab: raise RuntimeError("Edge not found")
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
            time.sleep(10)
            self._clear_udio_popups(ws_url)
            time.sleep(5)

        inj_js = """
        (function() {
            let els = Array.from(document.querySelectorAll('textarea, input[type="text"]'));
            let inp = els.find(el => {
                let p = (el.placeholder || '').toLowerCase();
                let v = (el.value || '').toLowerCase();
                let isVisible = el.offsetParent !== null;
                return isVisible && (p.includes('describe') || p.includes('prompt') || p.includes('imagine') || p.includes('track') || p === '');
            });
            
            if (!inp && els.length > 0) inp = els[0];
            if (!inp) return "no_input";
            
            const setter = Object.getOwnPropertyDescriptor(inp.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype, 'value').set;
            setter.call(inp, "%PROMPT%");
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));

            let buttons = Array.from(document.querySelectorAll('button, [role="button"], div.cursor-pointer'));
            let btn = buttons.find(b => {
                let t = (b.textContent || '').toLowerCase().trim();
                let isVisible = b.offsetParent !== null;
                return isVisible && (t === 'create' || t === 'generate' || t === 'remix') && !b.disabled;
            });
            
            if (!btn) return "no_button";
            
            btn.click();
            ['mousedown', 'mouseup', 'click'].forEach(v => btn.dispatchEvent(new MouseEvent(v, { bubbles: true, cancelable: true, view: window })));
            return "success";
        })()
        """.replace("%PROMPT%", prompt.replace('"', '\\"').replace('\n', ' '))

        logger.info("Injecting prompt and clicking Create...")
        for i in range(12):
            res = self.execute_js(ws_url, inj_js, timeout=10)
            if res == "success":
                logger.info("Successfully triggered generation!")
                return True
            logger.warning(f"Injection attempt {i+1} failed: {res}. Retrying...")
            if res == "no_input": self._clear_udio_popups(ws_url)
            time.sleep(4)
        raise RuntimeError("Failed to trigger generation")

    def wait_for_completion_and_download(self, timeout=300):
        """Poll the browser for the latest track's status and trigger download when ready."""
        tab = self._get_active_tab()
        if not tab: return False
        ws_url = tab.get('webSocketDebuggerUrl')
        
        poll_js = """
        (function() {
            const all = Array.from(document.querySelectorAll('*'));
            const isStr = (v) => typeof v === 'string';
            
            const tracks = all.filter(el => {
                const txt = el.textContent || '';
                const hasDuration = /\\d+:\\d+/.test(txt);
                const hasPlay = !!el.querySelector('button[aria-label*="Play"]');
                const isCreating = txt.toLowerCase().includes('creating') || txt.toLowerCase().includes('generating');
                
                return (hasDuration || isCreating) && (hasPlay || isCreating) && 
                       el.offsetHeight > 50 && el.offsetHeight < 120 && 
                       !el.querySelector('.absolute.left-0');
            });

            if (tracks.length === 0) {
                return "DIAG: no_tracks_detected";
            }
            
            tracks.sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
            const latest = tracks[0];
            const text = latest.textContent.toLowerCase();
            
            if (text.includes('error') || text.includes('failed')) return "error_row";
            
            const isReady = (text.includes(':') && !text.includes('creating') && !text.includes('generating')) || 
                           !!latest.querySelector('button[aria-label*="Download"]');
            
            if (!isReady) return "generating (" + text.substring(0, 30).replace(/\\n/g, ' ') + ")";
            
            let b = latest.querySelector('button[aria-label*="Download"]');
            if (!b) {
                let m = latest.querySelector('button[aria-label*="More"], [data-testid*="more"]');
                if (m) { m.click(); return "waiting_menu"; }
                b = document.querySelector('button[aria-label*="Download"]');
            }
            
            if (b) {
                b.scrollIntoView({ block: 'center' });
                b.click();
                ['mousedown', 'mouseup', 'click'].forEach(v => b.dispatchEvent(new MouseEvent(v, { bubbles: true, view: window })));
                return "downloading";
            }
            
            return "ready_no_btn";
        })()
        """
        start = time.time()
        logger.info(f"Polling browser for track completion...")
        while time.time() - start < timeout:
            try:
                res = self.execute_js(ws_url, poll_js, timeout=15)
                if not res: res = "empty_result"
                
                if res in ["downloading"]:
                    logger.info("✅ Download triggered!")
                    return True
                elif res == "error_row": 
                    logger.error("❌ Udio reported failure on newest track.")
                    return False
                
                logger.info(f"  Status: {res} ({int(time.time()-start)}s)")
                
                if "DIAG" in res:
                    self.execute_js(ws_url, "window.scrollBy(0, 200); setTimeout(()=>window.scrollBy(0,-200), 200)")
                    self._clear_udio_popups(ws_url)
                         
            except Exception as e:
                logger.warning(f"Error while polling: {e}")
            time.sleep(15)
        return False
