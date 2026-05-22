import websocket
import json
import os
import requests

def get_udio_token_from_browser():
    try:
        # 1. Get tabs from Edge debugger
        resp = requests.get('http://localhost:9222/json')
        tabs = resp.json()
        
        # 2. Find Udio tab
        udio_tab = next((t for t in tabs if 'udio.com' in t.get('url', '') and t.get('type') == 'page'), None)
        if not udio_tab:
            print("ERROR:No Udio tab found in Edge. Please open www.udio.com")
            return None
            
        ws_url = udio_tab['webSocketDebuggerUrl']
        
        # 3. Connect and get cookies
        ws = websocket.create_connection(ws_url, suppress_origin=True)
        ws.send(json.dumps({'id': 1, 'method': 'Network.getCookies', 'params': {'urls': ['https://www.udio.com']}}))
        
        cookies = []
        while True:
            r = json.loads(ws.recv())
            if r.get('id') == 1:
                cookies = r.get('result', {}).get('cookies', [])
                break
        ws.close()
        
        # 4. Extract and combine token
        cookie0 = next((c['value'] for c in cookies if c['name'] == 'sb-ssr-production-auth-token.0'), None)
        cookie1 = next((c['value'] for c in cookies if c['name'] == 'sb-ssr-production-auth-token.1'), None)
        
        if not cookie0:
            print("ERROR:sb-ssr-production-auth-token.0 not found in browser cookies.")
            return None
            
        import base64
        b64 = cookie0[7:] + (cookie1 or "")
        b64 += "=" * ((4 - len(b64) % 4) % 4)
        
        decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
        token = decoded.split('"access_token":"')[1].split('"')[0]
        
        # 5. Update .env with UTF-8
        env_path = "hymn_remaker/.env"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        new_lines = []
        keys_to_update = {
            "UDIO_OAUTH_TOKEN": token,
            "UDIO_COOKIE_0": cookie0,
            "UDIO_COOKIE_1": cookie1 or ""
        }
        
        updated_keys = set()
        for line in lines:
            matched = False
            for key in keys_to_update:
                if line.startswith(f"{key}="):
                    new_lines.append(f"{key}={keys_to_update[key]}\n")
                    updated_keys.add(key)
                    matched = True
                    break
            if not matched:
                new_lines.append(line)
        
        for key in keys_to_update:
            if key not in updated_keys:
                new_lines.append(f"{key}={keys_to_update[key]}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        print(f"SUCCESS:Fresh token extracted from Edge and saved to .env")
        return token
        
    except Exception as e:
        print(f"ERROR:Failed to extract token: {e}")
        return None

if __name__ == "__main__":
    get_udio_token_from_browser()
