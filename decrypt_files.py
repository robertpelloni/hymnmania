import os
import json
import base64
import win32crypt
from Crypto.Cipher import AES

def get_master_key():
    local_state_path = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Local State')
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]
    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return master_key

def decrypt_v10(value, master_key):
    try:
        iv = value[3:15]
        payload = value[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_binary = cipher.decrypt(payload)[:-16]
        return decrypted_binary.decode('utf-8')
    except Exception as e:
        return f"ERROR:{e}"

master_key = get_master_key()
combined_b64 = ""
for i in [0, 1]:
    fname = f"sb-ssr-production-auth-token.{i}.bin"
    with open(fname, "rb") as f:
        encrypted_value = f.read()
    decrypted = decrypt_v10(encrypted_value, master_key)
    print(f"Decrypted {fname}, len={len(decrypted)}")
    if decrypted.startswith("base64-"):
        combined_b64 += decrypted[7:]
    else:
        combined_b64 += decrypted

# Fix padding
combined_b64 += "=" * ((4 - len(combined_b64) % 4) % 4)

try:
    decoded_json = base64.b64decode(combined_b64).decode('utf-8', errors='ignore')
    data = json.loads(decoded_json)
    token = data.get("access_token")
    if token:
        print(f"TOKEN:{token}")
        with open("hymn_remaker/.env", "w") as f:
            f.write(f"UDIO_OAUTH_TOKEN={token}\nREMAKE_PRIORITY=udio\n")
        print("Updated hymn_remaker/.env")
    else:
        print("No access_token found")
except Exception as e:
    print(f"Parse error: {e}")
