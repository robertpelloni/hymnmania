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
                
                # Enable DOM
                self._send_cdp_cmd(ws, 10, "DOM.enable")
                
                # Get document root
                doc_resp = self._send_cdp_cmd(ws, 11, "DOM.getDocument")
                root_node_id = doc_resp['result']['root']['nodeId']
                
                # Query file input
                node_resp = self._send_cdp_cmd(ws, 12, "DOM.querySelector", {
                    "nodeId": root_node_id,
                    "selector": "input[type='file']"
                })
                if 'error' in node_resp or not node_resp.get('result', {}).get('nodeId'):
                    raise RuntimeError(f"Could not locate file input element in DOM: {node_resp}")
                input_node_id = node_resp['result']['nodeId']
                
                # Inject files
                self._send_cdp_cmd(ws, 13, "DOM.setFileInputFiles", {
                    "files": [abs_audio_path],
                    "nodeId": input_node_id
                })
                logger.info("Successfully set file input via CDP.")
            except Exception as e:
                logger.warning(f"Failed to set file input via CDP: {e}")
            finally:
                if ws:
                    try:
                        ws.close()
                    except Exception:
                        pass
            
            # Wait for upload popover options to render in DOM
            logger.info("Waiting 5 seconds for page to react to file upload and render option cards...")
            time.sleep(5)
            
            # Click Remix option button
            click_remix_js = """
            (function() {
                let buttons = Array.from(document.querySelectorAll('button, [role="button"]'));
                let remixOptionBtn = null;
                for (let el of buttons) {
                    let txt = (el.textContent || '').trim().toLowerCase();
                    if (txt === 'remix') {
                        // The option card has a border and is not the submit button (which has bg-remix-foreground)
                        if (el.className.includes('border') && !el.className.includes('bg-remix-foreground')) {
                            remixOptionBtn = el;
                            break;
                        }
                    }
                }
                if (!remixOptionBtn) {
                    // Fallback to find any remix button that is not the submit button
                    for (let el of buttons) {
                        let txt = (el.textContent || '').trim().toLowerCase();
                        if (txt === 'remix' && !el.className.includes('bg-remix-foreground')) {
                            remixOptionBtn = el;
                            break;
                        }
                    }
                }
                if (remixOptionBtn) {
                    remixOptionBtn.click();
                    remixOptionBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                    return { success: true, clicked: remixOptionBtn.outerHTML.substring(0, 120) };
                }
                return { success: false, error: "Remix option card button not found" };
            })()
            """
            logger.info("Clicking the Remix popover option card...")
            remix_result = self.execute_js(ws_url, click_remix_js)
            if not remix_result or not remix_result.get('success'):
                err = remix_result.get('error', 'Unknown option click failure') if remix_result else 'Execution returned null'
                logger.warning(f"Could not click Remix option automatically: {err}. Proceeding anyway...")
            else:
                logger.info(f"Remix option card clicked successfully: {remix_result.get('clicked')}")
                
            logger.info("Waiting 4 seconds for Remix settings and inputs to render...")
            time.sleep(4)
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

