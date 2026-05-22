import websocket
import json

def inspect_udio_buttons():
    ws_url = "ws://127.0.0.1:9222/devtools/page/99D8C336B5F863B4E3401FFACB11C4D5"
    
    script = """
    Array.from(document.querySelectorAll('button, [role="button"]')).map(b => ({
        text: (b.textContent || '').trim(),
        id: b.id,
        className: b.className,
        visible: b.offsetParent !== null,
        aria: b.getAttribute('aria-label')
    }))
    """
    
    try:
        ws = websocket.create_connection(ws_url, suppress_origin=True)
        ws.send(json.dumps({
            'id': 1, 
            'method': 'Runtime.evaluate', 
            'params': {'expression': script, 'returnByValue': True}
        }))
        result = json.loads(ws.recv())
        ws.close()
        
        buttons = result.get('result', {}).get('result', {}).get('value', [])
        print(f"FOUND_BUTTONS:{json.dumps(buttons)}")
    except Exception as e:
        print(f"ERROR:{e}")

if __name__ == "__main__":
    inspect_udio_buttons()
