import requests
import json
import websocket
import time

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
        # Enable DOM
        ws.send(json.dumps({"id": 1, "method": "DOM.enable"}))
        json.loads(ws.recv())
        
        # Click Remix button if visible
        click_remix = """
        (function() {
            let clicked = false;
            let buttons = Array.from(document.querySelectorAll('button, [role="button"], span'));
            for (let el of buttons) {
                let txt = (el.textContent || '').trim().toLowerCase();
                if (txt === 'remix') {
                    // Check if it's the option button card (often has a border and no bg-remix-foreground style)
                    // Let's just click it
                    el.click();
                    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                    clicked = true;
                    return { clicked: true, html: el.outerHTML.substring(0, 150) };
                }
            }
            return { clicked: false };
        })()
        """
        payload = {
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {
                "expression": click_remix,
                "returnByValue": True,
                "awaitPromise": True
            }
        }
        ws.send(json.dumps(payload))
        click_res = json.loads(ws.recv()).get('result', {}).get('result', {}).get('value', {})
        print("Remix click action:", click_res)
        
        time.sleep(2)
        
        # Now collect everything on the page
        collect_info = """
        (function() {
            // Find all horizontal sliders or custom range controls
            let sliders = [];
            let allElements = Array.from(document.querySelectorAll('*'));
            for (let el of allElements) {
                let role = el.getAttribute('role');
                let orientation = el.getAttribute('data-orientation');
                let title = el.getAttribute('title') || '';
                
                // If it is a slider or has slider class
                if (role === 'slider' || orientation === 'horizontal' || el.className.includes('slider') || el.className.includes('thumb')) {
                    // find parent text
                    let label = '';
                    let parent = el.parentElement;
                    if (parent) {
                        label = (parent.innerText || '').substring(0, 150).replace(/\\n/g, ' ');
                    }
                    sliders.push({
                        tagName: el.tagName,
                        className: el.className,
                        role: role,
                        orientation: orientation,
                        title: title,
                        valueNow: el.getAttribute('aria-valuenow') || el.value || '',
                        labelContext: label,
                        outerHTML: el.outerHTML.substring(0, 200)
                    });
                }
            }
            
            // Find all input and select elements
            let inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                tagName: el.tagName,
                type: el.type,
                name: el.name,
                placeholder: el.placeholder || '',
                value: el.value || '',
                className: el.className,
                outerHTML: el.outerHTML.substring(0, 200)
            }));
            
            // Find all text sections in the create form
            let createForm = document.querySelector('form') || document.body;
            let formText = (createForm.innerText || '').substring(0, 3000);
            
            return {
                sliders: sliders,
                inputs: inputs,
                formText: formText
            };
        })()
        """
        payload_collect = {
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {
                "expression": collect_info,
                "returnByValue": True,
                "awaitPromise": True
            }
        }
        ws.send(json.dumps(payload_collect))
        data = json.loads(ws.recv()).get('result', {}).get('result', {}).get('value', {})
        
        print("\n=== SLIDERS ===")
        for s in data.get('sliders', []):
            print(f"- Title: '{s['title']}' | Value: {s['valueNow']} | Label Context: '{s['labelContext']}'")
            print(f"  HTML: {s['outerHTML']}")
            
        print("\n=== INPUTS ===")
        for i in data.get('inputs', []):
            print(f"- Type: {i['type']} | Placeholder: '{i['placeholder']}' | Value: '{i['value']}'")
            print(f"  HTML: {i['outerHTML']}")
            
        print("\n=== FORM TEXT ===")
        print(data.get('formText', ''))
        
    finally:
        ws.close()

if __name__ == "__main__":
    inspect()
