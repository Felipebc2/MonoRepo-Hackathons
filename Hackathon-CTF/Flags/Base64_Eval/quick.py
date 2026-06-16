# quick_try.py
import socket, base64

HOST, PORT = "20.102.93.39", 33693

def sendL(L: str):
    raw = base64.b64decode(L, validate=True)  # bytes que precisamos enviar
    with socket.create_connection((HOST, PORT), timeout=6) as s:
        s.settimeout(1)
        try:
            print(s.recv(4096).decode("utf-8", errors="replace"))
        except Exception:
            pass
        s.sendall(raw + b"\n")               # envia os bytes + newline
        s.settimeout(2)
        resp = b""
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk: break
                resp += chunk
        except Exception:
            pass
        print(f"L='{L}' ->", resp.decode("utf-8", errors="replace"))

for L in [
    "3140/1e3", "1570/5e2", "6280/2e3",     # 3.14 com notação científica e len=8
    "314/1e2",  "157/5e1",  "628/2e2"       # versões mais curtas (len=7 -> pode falhar por não ser múltiplo de 4)
]:
    try:
        sendL(L)
    except Exception as e:
        print("erro:", L, e)

