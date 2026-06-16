#!/usr/bin/env python3
# octal_hunt_314.py
import base64, binascii, socket, time
from itertools import product

HOST = "20.102.93.39"
PORT = 33716

# ===== parâmetros de busca =====
K_MAX = 200000                 # escala k para NUM=314*k, DEN=100*k
SUFFIX_OPS = ["", "+0", "+00", "/1"]   # neutros (preservam o valor)
MAX_SUFFIX_LEN = 8           # limite de caracteres extras de sufixo
SEND_FIRST_HIT = True        # envia assim que achar
PRINT_PROGRESS_EVERY = 2000

def as_oct(n: int) -> str:
    """String Python 0o... (sem sinal)"""
    return oct(n)  # e.g., '0o472'

def inv_b64_to_utf8(L: str):
    """tenta decodificar L como base64 (sem '=') retornando texto utf-8, ou None."""
    for pad in ("", "=", "=="):
        cand = L + pad
        if len(cand) % 4 != 0:
            continue
        try:
            raw = base64.b64decode(cand, validate=True)
        except binascii.Error:
            try:
                raw = base64.b64decode(cand, validate=False)
            except Exception:
                continue
        except Exception:
            continue
        try:
            txt = raw.decode("utf-8")
            return txt
        except Exception:
            pass
    return None

def send(payload_bytes: bytes, newline=b"\n", timeout=5.0):
    resp = b""
    try:
        with socket.create_connection((HOST, PORT), timeout=8) as s:
            s.settimeout(1.0)
            try:
                banner = s.recv(4096)
                if banner:
                    print("banner:", banner.decode("utf-8", errors="replace"))
            except Exception:
                pass
            s.sendall(payload_bytes + newline)
            s.settimeout(timeout)
            try:
                while True:
                    part = s.recv(4096)
                    if not part:
                        break
                    resp += part
            except Exception:
                pass
    except Exception as e:
        print("socket error:", e)
    return resp

def neutral_suffixes():
    """gera sufixos neutros de tamanho total <= MAX_SUFFIX_LEN a partir de SUFFIX_OPS"""
    base = [""]
    # fazemos breadth até atingir MAX_SUFFIX_LEN
    seen = set(base)
    frontier = list(base)
    out = set(base)
    while frontier:
        nxt = []
        for s in frontier:
            for op in SUFFIX_OPS:
                cand = s + op
                if len(cand) > MAX_SUFFIX_LEN:
                    continue
                if cand not in seen:
                    seen.add(cand)
                    nxt.append(cand)
                    out.add(cand)
        frontier = nxt
    # ordenar por comprimento (curtos primeiro)
    return sorted(out, key=len)

def main():
    t0 = time.time()
    tried = 0

    sufs = neutral_suffixes()

    # três “formas” de expressões alvo (todas avaliam 314/100):
    #   A) 0oNUM/0oDEN
    #   B) 0oNUM/DEN
    #   C) NUM/0oDEN
    def forms(n, d):
        return [
            f"{as_oct(n)}/{as_oct(d)}",
            f"{as_oct(n)}/{d}",
            f"{n}/{as_oct(d)}",
        ]

    for k in range(1, K_MAX + 1):
        NUM = 314 * k
        DEN = 100 * k

        # pular pares muito grandes pra não explodir tamanho
        if NUM > 10**9 or DEN > 10**9:
            continue

        for base_expr in forms(NUM, DEN):
            for suf in sufs:
                L = base_expr + suf
                tried += 1
                if tried % PRINT_PROGRESS_EVERY == 0:
                    dt = time.time() - t0
                    print(f"[progress] tried={tried} elapsed={dt:.1f}s last={L!r}")

                # precisa ser múltiplo de 4 e só ASCII base64 (A-Za-z0-9+/):
                if len(L) % 4 != 0:
                    continue
                if not all(('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9') or c in '+/' for c in L):
                    # contém 'o' (ok), dígitos, '+', '/', e os 'o' estão no alfabeto base64 (minúsculos) -> permitido
                    # aqui já cobrimos isso com a condição acima (a-z inclui 'o')
                    pass

                txt = inv_b64_to_utf8(L)
                if txt is None:
                    continue

                # achamos um inp!
                payload = txt.encode("utf-8")
                print("\n=== FOUND CANDIDATE ===")
                print("L:", L, f"(len={len(L)})")
                print("b64(payload):", base64.b64encode(payload).decode())
                print("payload hex:", payload.hex())
                print("payload repr:", repr(txt))

                if SEND_FIRST_HIT:
                    print("\n-> Enviando LF")
                    resp = send(payload, newline=b"\n")
                    print("resp repr:", repr(resp))
                    print("\n-> Enviando CRLF")
                    resp = send(payload, newline=b"\r\n")
                    print("resp repr:", repr(resp))
                return

    print("\nNada encontrado dentro dos limites atuais.")
    print("Sugestões: aumente K_MAX e/ou MAX_SUFFIX_LEN.")

if __name__ == "__main__":
    main()
