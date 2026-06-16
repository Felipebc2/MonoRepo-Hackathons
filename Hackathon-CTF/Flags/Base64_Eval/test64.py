#!/usr/bin/env python3
import base64

L = b"157/50+0+0+0"   # troque aqui pelos outros candidatos se precisar
try:
    decoded = base64.b64decode(L, validate=True)
    print("L:", L)
    print("decoded repr:", repr(decoded))
    print("decoded hex:", decoded.hex())
    try:
        print("utf8:", decoded.decode("utf-8"))
    except Exception as e:
        print("not utf8:", e)
except Exception as e:
    print("base64 decode error:", e)

