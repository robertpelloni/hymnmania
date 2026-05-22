import requests
import json
import websocket

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
        
    ws_url = udio_tab['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1')
    ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=5)
    try:
        script = """
        (function() {
            let inputs = Array.from(document.querySelectorAll('input[type="range"]'));
            let results = [];
            for (let input of inputs) {
                let info = {
                    outerHTML: input.outerHTML.substring(0, 250),
                    value: input.value,
                    min: input.min,
                    max: input.max,
                    step: input.step,
                    parentsText: []
                };
                let current = input.parentElement;
                for (let i = 0; i < 4; i++) {
                    if (current) {
                        // Get direct text content of parent
                        let clone = current.cloneNode(true);
                        // remove children to get direct text
                        while (clone.firstElementChild) {
                            clone.removeChild(clone.firstElementChild);
                        }
                        let text = clone.innerText || clone.textContent || '';
                        info.parentsText.push({
                            tagName: current.tagName,
                            className: current.className,
                            directText: text.trim(),
                            fullText: (current.innerText || '').substring(0, 200).trim()
                        });
                        current = current.parentElement;
                    }
                }
                results.push(info);
            }
            return results;
        })()
        """
        payload = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": script,
                "returnByValue": True,
                "awaitPromise": True
            }
        }
        ws.send(json.dumps(payload))
        resp = json.loads(ws.recv())
        result = resp.get('result', {}).get('result', {}).get('value')
        print(json.dumps(result, indent=2))
    finally:
        ws.close()

if __name__ == "__main__":
    inspect()
