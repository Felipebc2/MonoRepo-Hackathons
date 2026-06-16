#!/usr/bin/env python3
# bruteforce_b64_short.py
# Tenta strings base64 curtas (len=4) compostas de digits + '+' + '/'
# e verifica se eval(L) == 1337 and base64.b64decode(L) é UTF-8 válido.
# Se sim, envia o payload decodificado ao host/port e imprime resposta.

import itertools, base64, socket, time

HOST = "20.102.93.39"
PORT = 33472
TIMEOUT = 3.0

CHARS = "0123456789+/"   # 12 chars -> 12**4 = 20736 combos
LENGTH = 4

def is_utf8(b):
    try:
        b.decode('utf-8')
        return True
    except Exception:
        return False

def recv_all(sock, timeout=1.0):
    sock.settimeout(0.3)
    buf = b""
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

def try_candidate(L):
    # L is bytes
    try:
        # eval on the ascii string (unsafe but local script)
        val = eval(L.decode('ascii'))
    except Exception:
        return False, None
    if val != 1337:
        return False, None

    # check base64 decode -> UTF-8 valid
    try:
        decoded = base64.b64decode(L, validate=True)
    except Exception:
        return False, None
    if not is_utf8(decoded):
        return False, None

    # looks promising: send to server
    out = {}
    for newline_name, newline in (("LF", b"\n"), ("CRLF", b"\r\n")):
        try:
            with socket.create_connection((HOST, PORT), timeout=6) as s:
                # read banner
                banner = recv_all(s, timeout=0.8)
                out['banner'] = banner
                s.sendall(decoded + newline)
                resp = recv_all(s, timeout=TIMEOUT)
                out['resp_'+newline_name] = resp
                text = ""
                try:
                    text = resp.decode('utf-8', errors='ignore')
                except Exception:
                    text = repr(resp)
                if "IDP{" in text or "flag" in text.lower():
                    return True, out
        except Exception as e:
            out['error'] = str(e)
            return False, out
    return False, out

def main():
    print("Trying candidates length", LENGTH, "over", len(CHARS), "chars => total", len(CHARS)**LENGTH)
    tried = 0
    for tup in itertools.product(CHARS, repeat=LENGTH):
        s = "".join(tup)
        L = s.encode('ascii')
        tried += 1
        ok, out = try_candidate(L)
        if ok:
            print("FOUND candidate:", L)
            print("banner (repr):", repr(out.get('banner')))
            print("resp LF repr:", repr(out.get('resp_LF')))
            print("resp CRLF repr:", repr(out.get('resp_CRLF')))
            return
        # show some progress occasionally
        if tried % 2000 == 0:
            print("tried", tried, "candidates...")
    print("done. none found in space length", LENGTH)

if __name__ == "__main__":
    main()

