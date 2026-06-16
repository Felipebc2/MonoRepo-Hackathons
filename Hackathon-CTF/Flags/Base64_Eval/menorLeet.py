#!/usr/bin/env python3
# send_from_L.py
# Dado L (string que o server precisa avaliar via eval), decodifica s = b64decode(L)
# e envia s (como texto) ao servidor para que b64encode(s.encode()) == L no servidor.
#
# Ajuste L abaixo para a expressão que você encontrou (ex: "157/50+0+0+0").

import base64, socket, time

HOST = "20.102.93.39"
PORT = 33579
TIMEOUT = 3.0

# ---- EDITE AQUI: L é a string que, quando recebida dentro do eval no servidor, deve avaliar para 3.14
L = "157/50+0+0+0"
# ---- fim da edição

def validate_and_get_s(L_str: str):
    Lb = L_str.encode('ascii', errors='ignore')
    # L precisa ser base64 "válido" (comprimento múltiplo de 4) - validate=True exige isso
    try:
        decoded = base64.b64decode(Lb, validate=True)
    except Exception as e:
        print("ERROR: L não é um Base64 válido (ou padding incorreto):", e)
        return None
    # precisa ser UTF-8 decodificável (pois vamos enviar s como texto)
    try:
        s = decoded.decode('utf-8')
    except Exception as e:
        print("ERROR: bytes decodificados de L não são UTF-8:", e)
        return None
    return s

def recv_all(sock, timeout=1.0):
    sock.settimeout(0.3)
    buf = b''
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            part = sock.recv(4096)
        except socket.timeout:
            continue
        except Exception:
            break
        if not part:
            break
        buf += part
    return buf

def send_string(s: str, newline: bytes = b'\n'):
    try:
        with socket.create_connection((HOST, PORT), timeout=8) as sck:
            # banner
            try:
                banner = recv_all(sck, 0.8)
                if banner:
                    print("=== banner ===")
                    print(banner.decode('utf-8', errors='replace'))
                    print("=== end banner ===")
            except Exception:
                pass
            # enviar (servidor espera linha de texto; input() vai ler e produzir str)
            payload = s.encode('utf-8')
            print("[*] Sending payload bytes (len={}): {}".format(len(payload), repr(payload[:60])))
            sck.sendall(payload + newline)
            # ler resposta
            resp = recv_all(sck, TIMEOUT)
            print("=== response (raw repr) ===")
            print(repr(resp))
            print("=== response (utf-8 replace) ===")
            print(resp.decode('utf-8', errors='replace'))
            print("=== end response ===")
    except Exception as e:
        print("socket error:", e)

def main():
    print("[*] Using L =", repr(L))
    s = validate_and_get_s(L)
    if s is None:
        print("[!] L inválido — corrija L para uma string Base64 (len%4==0) cujo decode seja UTF-8.")
        return
    print("[*] Decoded s to send (preview):", repr(s[:120]))
    print("[*] Evaluating locally check: try to eval(L) ->", end=' ')
    try:
        # local check: eval of L itself (treating it as python expression)
        local_eval = eval(L)
        print(local_eval)
    except Exception as e:
        print("WARNING: eval(L) failed locally:", e)
        # note: eval(L) must be valid for the server; if it fails locally, server will also fail.
    # Envia com LF e CRLF (tenta os dois)
    print("[*] Sending with LF (\\n)...")
    send_string(s, newline=b'\n')
    print("[*] Sending with CRLF (\\r\\n)...")
    send_string(s, newline=b'\r\n')

if __name__ == "__main__":
    main()
