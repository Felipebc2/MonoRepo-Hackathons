#!/usr/bin/env python3
# find_division_b64.py
import base64
import string
import socket
import time

HOST = "20.102.93.39"
PORT = 33472

# ajuste range de b se quiser (maior -> mais chances)
B_START = 1
B_END = 20000

BASE64_CHARS = set(string.ascii_letters + string.digits + "+/")

def is_base64_usable(s: str) -> bool:
    # must contain only base64 chars (no padding =), and length multiple of 4
    if len(s) % 4 != 0:
        return False
    return all(ch in BASE64_CHARS for ch in s)

def try_send_bytes(payload_bytes: bytes, newline=b"\n", timeout=3.0):
    try:
        with socket.create_connection((HOST, PORT), timeout=8) as s:
            # read banner
            s.settimeout(1.0)
            try:
                banner = s.recv(4096)
                if banner:
                    print("banner (utf-8 replace):")
                    print(banner.decode("utf-8", errors="replace"))
            except Exception:
                pass
            # send
            s.sendall(payload_bytes + newline)
            # read response
            s.settimeout(timeout)
            resp = b""
            try:
                while True:
                    part = s.recv(4096)
                    if not part:
                        break
                    resp += part
            except Exception:
                pass
            print("response repr:", repr(resp))
            try:
                print("response text:", resp.decode("utf-8", errors="replace"))
            except Exception:
                pass
    except Exception as e:
        print("socket/send error:", e)

def main():
    print("Searching L = 'a/b' where a = 1337*b, b in", B_START, "..", B_END)
    for b in range(B_START, B_END + 1):
        a = 1337 * b
        L = f"{a}/{b}"
        # quick filter: base64 alphabet only and length % 4 == 0
        if not is_base64_usable(L):
            continue
        # try base64 decode (validate=True)
        try:
            decoded = base64.b64decode(L, validate=True)
        except Exception:
            continue
        # must be UTF-8 decodable, since server will require inp.encode() -> this payload
        try:
            decoded.decode('utf-8')
        except Exception:
            continue

        # If we reach here, we found a candidate
        print("FOUND candidate L:", L)
        print("decoded repr:", repr(decoded))
        print("decoded hex:", decoded.hex())

        # opcional: enviar automaticamente
        do_send = True  # Mude para False se quiser só listar candidatos
        if do_send:
            print("Sending payload to server (LF and CRLF tries)...")
            try_send_bytes(decoded, newline=b"\n")
            try_send_bytes(decoded, newline=b"\r\n")
        return

    print("Search finished. No candidate found in the tested range.")

if __name__ == "__main__":
    main()

