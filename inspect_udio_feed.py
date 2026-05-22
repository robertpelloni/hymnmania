import websocket
import json

def inspect_udio_feed():
    ws_url = "ws://127.0.0.1:9222/devtools/page/99D8C336B5F863B4E3401FFACB11C4D5"
    
    script = """
    (function() {
        const elements = Array.from(document.querySelectorAll('*'));
        const testIds = elements.map(el => el.getAttribute('data-testid')).filter(id => id !== null);
        
        // Find everything that looks like a track row
        const possibleTracks = elements.filter(el => {
            const cls = (typeof el.className === 'string') ? el.className : (el.className?.baseVal || '');
            return cls.includes('track') || 
                   (el.textContent && el.textContent.includes('0:32')) ||
                   (el.querySelector('button[aria-label*="Play"]'));
        }).map(el => ({
            tag: el.tagName,
            class: (typeof el.className === 'string') ? el.className : (el.className?.baseVal || ''),
            text: el.textContent.substring(0, 50),
            testId: el.getAttribute('data-testid')
        }));
        
        return { testIds: [...new Set(testIds)], tracks: possibleTracks.slice(0, 10) };
    })()
    """
    
    try:
        ws = websocket.create_connection(ws_url, suppress_origin=True)
        ws.send(json.dumps({
            'id': 1, 
            'method': 'Runtime.evaluate', 
            'params': {'expression': script, 'returnByValue': True}
        }))
        while True:
            result = json.loads(ws.recv())
            if result.get('id') == 1:
                if 'exceptionDetails' in result.get('result', {}):
                    print(f"JS_ERROR:{result['result']['exceptionDetails']}")
                data = result.get('result', {}).get('result', {}).get('value', {})
                print(f"DEBUG_DATA:{json.dumps(data)}")
                break
        ws.close()
    except Exception as e:
        print(f"ERROR:{e}")

if __name__ == "__main__":
    inspect_udio_feed()
