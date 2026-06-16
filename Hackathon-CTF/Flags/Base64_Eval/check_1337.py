#!/usr/bin/env python3
import base64

s = b'1337'
try:
    decoded = base64.b64decode(s, validate=True)
except Exception as e:
    print("Erro ao decodificar base64:", e)
    raise SystemExit(1)

print("decoded repr:", repr(decoded))
print("decoded hex:", decoded.hex())

# tenta decodificar como UTF-8
try:
    txt = decoded.decode('utf-8')
    print("DECODED é UTF-8 VÁLIDO. decoded.decode('utf-8') ->", repr(txt))
    print("Se isto ocorrer, existe possivelmente um 's' tal que b64encode(s.encode()) == b'1337'.")
except UnicodeDecodeError as e:
    print("DECODED NÃO É UTF-8 VÁLIDO:", e)
    print("Isto significa que NÃO existe string 's' com s.encode('utf-8') = decoded, logo a condição não pode ser satisfeita.")

