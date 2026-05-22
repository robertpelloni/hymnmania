import websocket
import json
import base64
import time

def take_cdp_screenshot():
    # Udio tab ID from previous scan
    ws_url = "ws://127.0.0.1:9222/devtools/page/99D8C336B5F863B4E3401FFACB11C4D5"
    
    try:
        ws = websocket.create_connection(ws_url, suppress_origin=True)
        
        # Take screenshot
        ws.send(json.dumps({
            'id': 100, 
            'method': 'Page.captureScreenshot',
            'params': {'format': 'png'}
        }))
        
        start = time.time()
        while time.time() - start < 10:
            msg = json.loads(ws.recv())
            if msg.get('id') == 100:
                img_data = msg.get('result', {}).get('data')
                if img_data:
                    with open("cdp_debug.png", "wb") as f:
                        f.write(base64.b64decode(img_data))
                    print("SUCCESS:Screenshot saved to cdp_debug.png")
                    return True
                break
        ws.close()
    except Exception as e:
        print(f"ERROR: {e}")
    return False

if __name__ == "__main__":
    take_cdp_screenshot()
