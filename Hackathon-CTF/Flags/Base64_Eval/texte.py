import argparse
import base64
import re
import socket
import sys
from typing import Tuple

def recv_until_prompt(sock: socket.socket, prompt: bytes = b">>> ", max_bytes: int = 2_000_000) -> bytes:
    """Lê o banner até ver o prompt '>>> ' (ou timeout/EOF)."""
    sock.settimeout(3)
    data = b""
    try:
        while len(data) < max_bytes:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if prompt in data:
                break
    except Exception:
        pass
    return data

def talk(host: str, port: int, payload: bytes, read_timeout: float = 4.0) -> Tuple[bytes, bytes]:
    """Abre conexão, lê banner, envia payload+\n e retorna (banner, resposta)."""
    with socket.create_connection((host, port), timeout=8) as s:
        banner = recv_until_prompt(s)
        # envia payload + newline (como faria o `echo`)
        s.sendall(payload + b"\n")
        # lê resposta até fechar/timeout
        s.settimeout(read_timeout)
        resp = b""
        try:
            while True:
                part = s.recv(4096)
                if not part:
                    break
                resp += part
        except Exception:
            pass
        return banner, resp

def main():
    ap = argparse.ArgumentParser(description="CTF base64 → eval == 1337")
    ap.add_argument("--host", default="20.102.93.39")
    ap.add_argument("--port", type=int, default=33467)
    ap.add_argument("--expr", default="1337",
                    help="Expressão Python que, após b64decode+eval no servidor, deve resultar em 1337 (default: 1337)")
    ap.add_argument("--mode", choices=["b64", "raw"], default="b64",
                    help="b64: envia base64(expr). raw: envia texto cru (ex.: MTMzNw==).")
    args = ap.parse_args()

    # payload: equivalente ao `echo -n 1337 | base64`  →  MTMzNw==
    if args.mode == "b64":
        payload = base64.b64encode(args.expr.encode("utf-8"))
    else:
        payload = args.expr.encode("utf-8")

    banner, resp = talk(args.host, args.port, payload)

    # mostre o banner opcionalmente
    if banner:
        try:
            sys.stdout.write(banner.decode("utf-8", "replace"))
        except Exception:
            pass

    text = resp.decode("utf-8", "replace")
    if text:
        print(text, end="")

    # tenta extrair a flag (IDP{...} ou variantes comuns)
    m = re.search(r'(IDP\{[^}]+\}|flag\{[^}]+\}|FLAG\{[^}]+\}|flag[^:\n]*:?[^\n]*)', text, flags=re.IGNORECASE)
    if m:
        print("\n[FLAG]", m.group(1))

if __name__ == "__main__":
    main()