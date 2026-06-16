#!/usr/bin/env python3
# decrypt_response.py
import base64
from hashlib import md5
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def derive_key(tb):
    # md5(str(tb) + "idp") -> 16 bytes
    return md5((str(tb) + "idp").encode()).digest()

def decrypt_response(data_b64, iv_b64, tb):
    key = derive_key(tb)
    ct = base64.b64decode(data_b64)
    iv = base64.b64decode(iv_b64)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    try:
        pt = unpad(pt, AES.block_size)
    except ValueError:
        # se padding falhar, mostra raw bytes (possível timestamp errado)
        return None, pt
    try:
        s = pt.decode('utf-8')
    except UnicodeDecodeError:
        s = pt.decode('latin-1', errors='replace')
    return s, pt

if __name__ == "__main__":
    examples = [
        # coloque aqui as tripas que o probe imprimiu
        # (data, iv, timestamp)
        ("GgDnG4xUPx4kctynhu8JNgGcZiyeJYPafVyQZIrkPVQ=",
         "LogDGwN2cKGxjjQgLMedMQ==",
         352516328),
        ("822jgOG2lUvZs/N3NBvlc4Uo7/LKq5m2S52y6Fcx3X4=",
         "lDwQxFWWJJVFjWKL+utlFQ==",
         352516329),
        ("x9BjoQpSOfxtSj9hM9QmYUFUnQfcxyMun+6PlgpxxCM=",
         "P1dn3yAi9dhtRJspqeAWkQ==",
         352516329),
        ("GkzpTJ5LaY9yb1Y7/NLU3uUHWw+byAz4itHXrPfoUoS8xkh/MyMZ3e4Qh8Tdfebz",
         "yXrWc1pXlmokG1yKMNbohg==",
         352516329),
        # adicione outras linhas se quiser
    ]

    for data_b64, iv_b64, tb in examples:
        s, raw = decrypt_response(data_b64, iv_b64, tb)
        print("---- decrypt (tb:", tb, ") ----")
        if s is None:
            print("Padding/decoding parece falhar; raw bytes:")
            print(raw)
        else:
            print(s)
        print("-------------------------------\n")

