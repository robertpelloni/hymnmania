import websocket
import json
import os

ws_url = "ws://localhost:9222/devtools/page/92747F671118DC735F4D8D36394B1435"
# Some versions of Chrome/Edge require a specific header to avoid 403
try:
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    ws.send(json.dumps({'id': 1, 'method': 'Network.getCookies', 'params': {'urls': ['https://www.udio.com']}}))
    
    # Wait for the specific response
    while True:
        resp = json.loads(ws.recv())
        if resp.get('id') == 1:
            cookies = resp.get('result', {}).get('cookies', [])
            print(f"COOKIES_FOUND:{json.dumps(cookies)}")
            break
    ws.close()
except Exception as e:
    print(f"ERROR:{e}")
