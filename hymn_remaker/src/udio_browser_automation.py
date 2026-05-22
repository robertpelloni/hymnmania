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
        if not targets:
            return None
        
        # Look for Udio tab first
        for t in targets:
            url = t.get('url', '').lower()
            if 'udio' in url:
                return t
        
        # Return first available page
        return targets[0]

    def execute_js(self, ws_url, script):
        """Evaluate arbitrary JavaScript on the target tab via CDP and return result."""
        ws_url = ws_url.replace('localhost', '127.0.0.1')
        ws = None
        try:
            ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
            
            # Send Runtime.enable
            ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            start_enable = time.time()
            while time.time() - start_enable < 5:
                try:
                    resp = json.loads(ws.recv())
                    if resp.get('id') == 1:
                        break
                except websocket.WebSocketTimeoutException:
                    break
            
            # Evaluate script
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
            
            # Recv response
            start_poll = time.time()
            while time.time() - start_poll < 10:
                try:
                    resp = json.loads(ws.recv())
                    if resp.get('id') == 2:
                        result = resp.get('result', {}).get('result', {})
                        value = result.get('value')
                        # If value is none but error is present
                        if 'exceptionDetails' in resp.get('result', {}):
                            exception = resp['result']['exceptionDetails'].get('exception', {})
                            description = exception.get('description', 'Unknown JS exception')
                            raise RuntimeError(f"JS Execution Error: {description}")
                        return value
                except websocket.WebSocketTimeoutException:
                    pass
            
            raise TimeoutError("CDP did not return evaluated JS response in time.")
        finally:
            if ws:
                try:
                    ws.close()
                except Exception:
                    pass

    def navigate_to_create(self, tab):
        """Ensure the browser tab is navigated to Udio.com/create."""
        ws_url = tab.get('webSocketDebuggerUrl')
        current_url = tab.get('url', '')
        
        if 'udio.com/create' not in current_url:
            logger.info("Browser tab not on /create. Navigating to Udio.com/create...")
            
            ws_url = ws_url.replace('localhost', '127.0.0.1')
            ws = None
            try:
                ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
                # Navigate
                ws.send(json.dumps({
                    "id": 3,
                    "method": "Page.navigate",
                    "params": {"url": f"{self.base_url}/create"}
                }))
                ws.recv()
            finally:
                if ws:
                    ws.close()
            
            # Wait for navigation to settle
            time.sleep(3)

    def _send_cdp_cmd(self, ws, msg_id, method, params=None):
        """Send a CDP command and poll until the response with the matching id is received."""
        payload = {"id": msg_id, "method": method}
        if params:
            payload["params"] = params
        ws.send(json.dumps(payload))
        
        start_time = time.time()
        while time.time() - start_time < 8:
            try:
                resp = json.loads(ws.recv())
                if resp.get("id") == msg_id:
                    return resp
            except websocket.WebSocketTimeoutException:
                pass
        raise TimeoutError(f"No response for CDP {method} (id {msg_id}) in time.")

    def _clear_udio_popups(self, ws_url):
        """Detect and clear Udio modals like 'Upload Confirmation'."""
        clear_js = """
        (async function() {
            const results = { action: null };
            
            const robustClick = (el) => {
                if (!el) return;
                console.log('Gemini: Clicking', el);
                el.click();
                ['mousedown', 'mouseup', 'click'].forEach(v => 
                    el.dispatchEvent(new MouseEvent(v, { bubbles: true, cancelable: true, view: window }))
                );
            };

            // 1. Find and check 'I understand' checkbox
            const checkbox = document.querySelector('button[role="checkbox"], input[type="checkbox"]');
            if (checkbox) {
                const isChecked = checkbox.getAttribute('aria-checked') === 'true' || checkbox.checked;
                if (!isChecked) {
                    robustClick(checkbox);
                    results.action = "checked_box";
                    await new Promise(r => setTimeout(r, 500));
                }
            }

            // 2. Find and click 'I understand and confirm' OR 'Confirm'
            const buttons = Array.from(document.querySelectorAll('button, [role="button"], div.cursor-pointer'));
            const confirmBtn = buttons.find(b => {
                const txt = b.textContent.toLowerCase();
                return txt.includes('understand and confirm') || (txt === 'confirm' && b.className.includes('bg-white'));
            });

            if (confirmBtn && !confirmBtn.className.includes('opacity-50')) {
                robustClick(confirmBtn);
                results.action = (results.action ? results.action + "+" : "") + "clicked_confirm";
                await new Promise(r => setTimeout(r, 1000));
                return results;
            }

            // 3. Find and click 'Remix' mode button (the large card in the modal)
            const remixCard = buttons.find(b => {
                const txt = b.textContent.trim();
                return txt === 'Remix' && b.className.includes('border') && !b.className.includes('bg-remix');
            });

            if (remixCard && !remixCard.className.includes('opacity-50')) {
                robustClick(remixCard);
                results.action = (results.action ? results.action + "+" : "") + "selected_remix_mode";
                return results;
            }
            
            return results;
        })()
        """
        # Try clearing sequence 8 times
        max_attempts = 8
        logger.info("Running robust Udio modal clearing sequence...")
        for i in range(max_attempts):
            res = self.execute_js(ws_url, clear_js)
            if res and res.get('action'):
                logger.info(f"  Action (attempt {i+1}): {res['action']}")
                time.sleep(2)
            else:
                time.sleep(1)
        return True

    def trigger_generation(self, prompt, audio_path=None, variance=0.85, negative_prompt="organ, classical, baroque, church organ, cathedral"):
        """Drive Edge to paste the prompt and click the Create button, optionally uploading reference audio."""
        tab = self._get_active_tab()
        if not tab:
            raise RuntimeError(f"No active Edge targets found on port {self.port}. Is Edge running?")
        
        ws_url = tab.get('webSocketDebuggerUrl')
        logger.info(f"Targeting Edge tab: {tab.get('title')} | URL: {tab.get('url')}")
        
        # Navigate if needed
        self.navigate_to_create(tab)
        
        # 1. Handle file upload if audio_path is provided
        if audio_path and os.path.exists(audio_path):
            abs_audio_path = os.path.abspath(audio_path)
            logger.info(f"Uploading reference audio via CDP: {abs_audio_path}...")
            ws_url = ws_url.replace('localhost', '127.0.0.1')
            ws = None
            try:
                ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
                self._send_cdp_cmd(ws, 10, "DOM.enable")
                doc_resp = self._send_cdp_cmd(ws, 11, "DOM.getDocument")
                root_node_id = doc_resp['result']['root']['nodeId']
                node_resp = self._send_cdp_cmd(ws, 12, "DOM.querySelector", {
                    "nodeId": root_node_id,
                    "selector": "input[type='file']"
                })
                if 'error' in node_resp or not node_resp.get('result', {}).get('nodeId'):
                    raise RuntimeError(f"Could not locate file input element in DOM: {node_resp}")
                input_node_id = node_resp['result']['nodeId']
                self._send_cdp_cmd(ws, 13, "DOM.setFileInputFiles", {
                    "files": [abs_audio_path],
                    "nodeId": input_node_id
                })
                logger.info("Successfully set file input via CDP.")
            except Exception as e:
                logger.warning(f"Failed to set file input via CDP: {e}")
            finally:
                if ws:
                    try: ws.close()
                    except: pass
            
            # Wait for upload popover options or confirmation modals to render
            logger.info("Waiting for Udio to process upload and show modal...")
            time.sleep(5) # Give it more time

            # Check for and clear any 'Upload Confirmation' modals + Select Remix
            # We call this multiple times because there are often TWO modals (Confirm then Select Mode)
            self._clear_udio_popups(ws_url)
            time.sleep(2)
            self._clear_udio_popups(ws_url)
            
            logger.info("Waiting for Remix settings and inputs to render...")
            time.sleep(3)
        elif audio_path:
            logger.warning(f"Reference audio path does not exist: {audio_path}")

        # Assemble JS snippet to enter prompt, set Variance, Style Reduction, and click create/remix
        escaped_prompt = prompt.replace('"', '\\"').replace('\n', ' ')
        escaped_neg = negative_prompt.replace('"', '\\"').replace('\n', ' ')
        
        js_snippet = f"""
        (function() {{
            // 1. Set Variance slider if present
            let varianceSlider = document.querySelector('input[type="range"][min="0.1"][max="1"]');
            if (varianceSlider) {{
                const proto = window.HTMLInputElement.prototype;
                const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
                setter.call(varianceSlider, "{variance}");
                varianceSlider.dispatchEvent(new Event('input', {{ bubbles: true }}));
                varianceSlider.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            // 2. Set Style Reduction (negative prompt) if present
            let negInput = document.querySelector('input[placeholder*="avoid"]') || document.querySelector('input[cmdk-input=""]');
            if (negInput) {{
                const proto = window.HTMLInputElement.prototype;
                const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
                setter.call(negInput, "{escaped_neg}");
                negInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                negInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            // 3. Find prompt input
            let els = Array.from(document.querySelectorAll('textarea, input[type="text"]'));
            let promptInput = null;
            for (let el of els) {{
                let placeholder = (el.placeholder || '').toLowerCase();
                if (placeholder.includes('describe') || placeholder.includes('prompt') || placeholder.includes('imagine') || placeholder.includes('track') || placeholder.includes('genre')) {{
                    promptInput = el;
                    break;
                }}
            }}
            if (!promptInput) {{
                promptInput = document.querySelector('textarea') || document.querySelector('input[type="text"]');
            }}
            if (!promptInput) {{
                return {{ success: false, error: "Prompt input field not found" }};
            }}

            // 4. Set prompt value with React support
            const prototype = promptInput.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
            const nativeSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
            nativeSetter.call(promptInput, "{escaped_prompt}");
            promptInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            promptInput.dispatchEvent(new Event('change', {{ bubbles: true }}));

            // 5. Find Create/Remix button
            let buttons = Array.from(document.querySelectorAll('button'));
            let createBtn = null;
            for (let btn of buttons) {{
                let txt = (btn.textContent || '').toLowerCase().trim();
                if (txt === 'create' || txt === 'generate' || txt === 'remix') {{
                    createBtn = btn;
                    break;
                }}
            }}
            if (!createBtn) {{
                // Fallback search
                for (let btn of Array.from(document.querySelectorAll('[role="button"], [aria-label]'))) {{
                    let txt = (btn.textContent || btn.getAttribute('aria-label') || '').toLowerCase().trim();
                    if (txt === 'create' || txt === 'generate' || txt === 'remix') {{
                        createBtn = btn;
                        break;
                    }}
                }}
            }}

            if (!createBtn) {{
                return {{ success: false, error: "Create/Generate/Remix button not found" }};
            }}

            // 6. Click the button
            createBtn.click();
            createBtn.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));

            return {{ success: true }};
        }})()
        """
        
        logger.info("Injecting JS to fill prompt and click 'Create/Remix'...")
        result = self.execute_js(ws_url, js_snippet)
        
        if not result or not result.get('success'):
            err = result.get('error', 'Unknown injection failure') if result else 'Execution returned null'
            raise RuntimeError(f"Browser automation failed: {err}")
            
        logger.info("Successfully triggered Udio generation in browser!")
        return True

    def wait_for_completion_and_download(self, timeout=300):
        """Poll the browser for the latest track's status and trigger download when ready."""
        tab = self._get_active_tab()
        if not tab:
            return False
            
        ws_url = tab.get('webSocketDebuggerUrl')
        
        # JS script to find the first 'ready' track and click its download button
        # Note: Udio's UI structure for the latest track row
        poll_script = """
        (async function() {
            // Find the most recent track row (top of the feed)
            const tracks = Array.from(document.querySelectorAll('[data-testid*="track-row"], .track-row, [data-testid="tracks-panel"] [role="row"]'));
            if (tracks.length === 0) return { status: 'none' };
            
            const latest = tracks[0];
            const isReady = latest.textContent.includes('ready') || !!latest.querySelector('button[aria-label*="Download"]');
            const isError = latest.textContent.includes('error') || latest.textContent.includes('failed');
            
            if (isError) return { status: 'error' };
            if (!isReady) return { status: 'generating' };
            
            // It's ready, trigger download
            let downloadBtn = latest.querySelector('button[aria-label*="Download"]');
            
            if (!downloadBtn) {
                const moreBtn = latest.querySelector('button[aria-label*="More"], [data-testid*="more-actions"]');
                if (moreBtn) {
                    moreBtn.click();
                    await new Promise(r => setTimeout(r, 500));
                    const menuItems = Array.from(document.querySelectorAll('[role="menuitem"]'));
                    downloadBtn = menuItems.find(i => i.textContent.toLowerCase().includes('download'));
                }
            }
            
            if (downloadBtn) {
                downloadBtn.click();
                return { status: 'downloading' };
            }
            
            return { status: 'ready_but_no_button' };
        })()
        """
        
        start_time = time.time()
        logger.info("Polling browser for track completion...")
        
        while time.time() - start_time < timeout:
            try:
                res = self.execute_js(ws_url, poll_script)
                status = res.get('status')
                
                if status == 'downloading':
                    logger.info("✅ Track completed! Triggered browser download.")
                    return True
                elif status == 'error':
                    logger.error("❌ Udio reported a generation error in the UI.")
                    return False
                elif status == 'none':
                    logger.warning("No tracks found in the Udio feed yet...")
                
                # Still generating...
                elapsed = int(time.time() - start_time)
                logger.info(f"  Status: {status} ({elapsed}s)")
                
            except Exception as e:
                logger.warning(f"Error while polling Udio UI: {e}")
                
            time.sleep(15)
            
        logger.error(f"Timed out after {timeout}s waiting for track.")
        return False
