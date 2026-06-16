#!/usr/bin/env python3
# verbose_search_3_14.py
import base64, string, socket, sys, time
from fractions import Fraction
from itertools import product

HOST = "20.102.93.39"
PORT = 33693

TARGET = Fraction(314, 100)   # 3.14 exato
BASE64_CHARS = set(string.ascii_letters + string.digits + "+/")

def is_b64_alphabet(s: str) -> bool:
    return all(ch in BASE64_CHARS for ch in s)

def try_send_bytes(payload_bytes: bytes, newline=b"\n", timeout=3.0):
    try:
        with socket.create_connection((HOST, PORT), timeout=8) as s:
            s.settimeout(1.0)
            try:
                banner = s.recv(4096)
                if banner:
                    print("banner:", banner.decode("utf-8", "replace"))
            except Exception:
                pass
            s.sendall(payload_bytes + newline)
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
            print("=== RESPONSE (repr) ===")
            print(repr(resp))
            print("=== RESPONSE (text) ===")
            print(resp.decode("utf-8", "replace"))
    except Exception as e:
        print("socket/send error:", e)

def b64_decode_validate_utf8(L: str):
    """Retorna (raw_bytes, reason) onde raw_bytes é bytes se OK, caso contrário None e reason string."""
    # length %4
    if len(L) % 4 != 0:
        return None, "len%4 != 0"
    if not is_b64_alphabet(L):
        return None, "contains non-base64 chars"
    try:
        raw = base64.b64decode(L, validate=True)
    except Exception as e:
        return None, f"b64decode error: {e}"
    # check utf-8
    try:
        raw.decode("utf-8")
        return raw, "OK-utf8"
    except Exception as e:
        return None, f"not-utf8: {e}"

def generate_scientific_seeds(e_max=6, b_max=2000, zeros=6):
    # seeds óbvios (experimente primeiro)
    yield "3140/1e3"
    yield "1570/5e2"
    yield "6280/2e3"
    # gerar outros: A / (B * 10^E) => string "A/BeE"
    for E in range(0, e_max+1):
        for B in range(1, b_max+1):
            denom = B * (10**E)
            num = TARGET * denom
            if num.denominator != 1:
                continue
            A_base = num.numerator
            for t in range(0, zeros+1):
                A = A_base * (10**t)
                E2 = E + t
                yield f"{A}/{B}e{E2}"

def neutral_tails():
    # sufixos neutros que não alteram o valor: /1, +0, e0
    return ["", "/1", "+0", "e0", "/1+0", "/1e0", "+0e0"]

def main():
    tested = 0
    found = 0
    t0 = time.time()
    for seed in generate_scientific_seeds(e_max=8, b_max=3000, zeros=8):
        tested += 1
        # print progresso a cada 2000 seeds
        if tested % 2000 == 0:
            print(f"[progress] tested={tested}, found={found}, elapsed={int(time.time()-t0)}s")
            sys.stdout.flush()
        # algumas seeds podem já conter chars inválidos; testar variações com tails
        for tail_count in range(0, 3):  # tente 0,1,2 sufixos combinados
            for tails in product(neutral_tails(), repeat=tail_count):
                L = seed + "".join(tails)
                raw, reason = b64_decode_validate_utf8(L)
                if raw is None:
                    # comente a linha abaixo se gerar muito log
                    # print(f"[bad] {L!r} -> {reason}")
                    continue
                # se chegamos aqui: raw é bytes e decodifica em UTF-8
                found += 1
                print("="*40)
                print(f"[FOUND] L={L!r}  len={len(L)}  tested={tested}")
                print("decoded hex:", raw.hex())
                try:
                    print("decoded text repr:", raw.decode("utf-8"))
                except Exception:
                    print("decoded text: <not printable>")
                # envia (LF / CRLF)
                print("-> Enviando ao servidor (LF)")
                try_send_bytes(raw, newline=b"\n")
                print("-> Também enviando (CRLF)")
                try_send_bytes(raw, newline=b"\r\n")
                return
    print("Fim da busca. Nenhum candidato UTF-8 encontrado.")
    print(f"total tested={tested}, found={found}, elapsed={int(time.time()-t0)}s")

if __name__ == "__main__":
    main()

