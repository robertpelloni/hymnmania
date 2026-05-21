import requests
import json
import websocket

def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method}
    if params:
        payload["params"] = params
    ws.send(json.dumps(payload))
    
    for i in range(100):
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp
    raise TimeoutError(f"No response for {method} with id {msg_id}")

def inspect():
    res = requests.get("http://127.0.0.1:9222/json", timeout=5)
    targets = res.json()
    udio_tab = None
    for t in targets:
        if t.get('type') == 'page' and 'udio' in t.get('url', '').lower():
            udio_tab = t
            break
            
    if not udio_tab:
        print("Udio tab not found!")
        return
        
    print(f"Connecting to: {udio_tab['title']}")
    ws_url = udio_tab['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1')
    ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
    
    try:
        # Collect everything
        collect_info = """
        (function() {
            // Find all horizontal sliders or custom range controls
            let sliders = [];
            let allElements = Array.from(document.querySelectorAll('*'));
            for (let el of allElements) {
                let role = el.getAttribute('role');
                let orientation = el.getAttribute('data-orientation');
                let title = el.getAttribute('title') || '';
                let className = '';
                if (el.className) {
                    className = typeof el.className === 'string' ? el.className : (el.className.baseVal || '');
                }
                
                // If it is a slider or has slider class
                if (role === 'slider' || orientation === 'horizontal' || className.includes('slider')) {
                    // find parent text
                    let label = '';
                    let parent = el.parentElement;
                    if (parent) {
                        label = (parent.innerText || '').substring(0, 150).replace(/\\n/g, ' ');
                        if (parent.parentElement) {
                            label += " | " + (parent.parentElement.innerText || '').substring(0, 150).replace(/\\n/g, ' ');
                        }
                    }
                    sliders.push({
                        tagName: el.tagName,
                        className: className,
                        role: role,
                        orientation: orientation,
                        title: title,
                        valueNow: el.getAttribute('aria-valuenow') || el.value || '',
                        labelContext: label,
                        outerHTML: el.outerHTML.substring(0, 200)
                    });
                }
            }
            
            // Find all range inputs
            let rangeInputs = Array.from(document.querySelectorAll('input[type="range"]')).map(el => ({
                outerHTML: el.outerHTML.substring(0, 200),
                value: el.value,
                min: el.min,
                max: el.max,
                step: el.step
            }));
            
            return {
                sliders: sliders,
                rangeInputs: rangeInputs
            };
        })()
        """
        
        resp = send_cmd(ws, 1, "Runtime.evaluate", {
            "expression": collect_info,
            "returnByValue": True,
            "awaitPromise": True
        })
        
        data = resp.get('result', {}).get('result', {}).get('value', {})
        
        print("\n=== SLIDERS ===")
        for s in data.get('sliders', []):
            print(f"- Title: '{s['title']}' | Value: {s['valueNow']} | Label Context: '{s['labelContext']}'")
            print(f"  HTML: {s['outerHTML']}")
            
        print("\n=== RANGE INPUTS ===")
        for r in data.get('rangeInputs', []):
            print(f"- HTML: {r['outerHTML']}")
            print(f"  Value: {r['value']} | Min: {r['min']} | Max: {r['max']} | Step: {r['step']}")
            
    finally:
        ws.close()

if __name__ == "__main__":
    inspect()
