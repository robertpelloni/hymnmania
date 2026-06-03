"""Test script: diagnose Suno create page and try different modes."""
import logging
import sys
import json
import time

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

from hymn_remaker.src.suno_browser_automation import SunoBrowserAutomation

sba = SunoBrowserAutomation()
tab = sba._get_active_tab(require_suno=True)
ws_url = tab.get("webSocketDebuggerUrl")

# Step 1: Navigate fresh to /create to reset page state
print("=== Step 1: Navigate fresh to /create ===")
sba.execute_js(ws_url, "window.location.href = 'https://suno.com/create'")
time.sleep(8)

# Step 2: Click Simple mode
print("=== Step 2: Click Simple mode ===")
simple_js = """
(function() {
    var btns = Array.from(document.querySelectorAll('button'));
    var simpleBtn = btns.find(b => b.innerText === 'Simple');
    if (simpleBtn) {
        var isActive = simpleBtn.className.includes('active');
        if (!isActive) { simpleBtn.click(); return 'clicked_simple'; }
        return 'already_simple';
    }
    return 'simple_not_found';
})()
"""
r = sba.execute_js(ws_url, simple_js)
print(f"Simple click result: {r}")
time.sleep(2)

# Step 3: Check visible textareas in Simple mode
print("=== Step 3: Check textareas ===")
diag = """
(function() {
    var tas = Array.from(document.querySelectorAll('textarea')).filter(t => t.offsetParent !== null);
    return tas.map(function(t, i) {
        return {i: i, ph: t.placeholder, val: (t.value || '').substring(0, 40)};
    });
})()
"""
tas = sba.execute_js(ws_url, diag)
print(f"Textareas: {json.dumps(tas, indent=2)}")

# Step 4: Try to inject prompt into EACH textarea and check Create button
for ta_idx, ta_info in enumerate(tas):
    print(f"\n=== Step 4.{ta_idx}: Inject prompt into textarea[{ta_idx}] ===")
    inject_js = f"""
    (function() {{
        var tas = Array.from(document.querySelectorAll('textarea')).filter(t => t.offsetParent !== null);
        var ta = tas[{ta_idx}];
        if (!ta) return 'not_found';
        
        var propsKey = Object.keys(ta).find(k => k.startsWith('__reactProps$'));
        var promptText = 'deep house remix of a hymn, four-on-the-floor beat, atmospheric pads';
        if (propsKey && ta[propsKey] && ta[propsKey].onChange) {{
            ta[propsKey].onChange({{ target: {{ value: promptText }}, persist: function() {{}} }});
        }}
        var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, promptText);
        ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
        ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return 'set_on_' + ta.placeholder;
    }})()
    """
    r = sba.execute_js(ws_url, inject_js)
    print(f"Inject result: {r}")
    time.sleep(1)

    # Check Create button
    check_js = """
    (function() {
        var btns = Array.from(document.querySelectorAll('button'));
        var createBtn = btns.find(function(b) {
            return (b.innerText || '').includes('Create') && b.offsetParent !== null;
        });
        if (createBtn) {
            return JSON.stringify({text: createBtn.innerText, disabled: createBtn.disabled});
        }
        return 'not_found';
    })()
    """
    status = sba.execute_js(ws_url, check_js)
    print(f"Create button status: {status}")
    if '"disabled":false' in str(status):
        print("*** CREATE BUTTON IS ENABLED! ***")
        # Try clicking it
        click_js = """
        (function() {
            var btns = Array.from(document.querySelectorAll('button'));
            var b = btns.find(function(el) {
                return (el.innerText || '').includes('Create') && el.offsetParent !== null && !el.disabled;
            });
            if (b) { b.click(); return 'clicked'; }
            return 'not_found_or_disabled';
        })()
        """
        click_r = sba.execute_js(ws_url, click_js)
        print(f"Click result: {click_r}")
        break
