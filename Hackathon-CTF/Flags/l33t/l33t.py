#!/usr/bin/env python3
# find_3_14.py
# Mantém a estrutura do teu script básico e adiciona geração científica + sufixos neutros

import base64
import string
import socket
import time
from fractions import Fraction
from itertools import product

HOST = "20.102.93.39"
PORT = 33693   # ajuste se a porta for outra

# limites (aumente se quiser mais busca)
B_START = 1
B_END = 2000      # aumente para 20000 se quiser (vai demorar)
E_MAX = 6         # expoente máximo (10**E)
MAX_ZERO_PAD = 4  # quantos zeros "colados" no numerador (A * 10**t)

BASE64_CHARS = set(string.ascii_letters + string.digits + "+/")

TARGET = Fraction(314, 100)   # 3.14 exato (314/100)

NEUTRAL_TAILS = ["", "/1", "+0", "e0"]  # mantêm o valor, mudam bits

def is_base64_usable(s: str) -> bool:
    if len(s) % 4 != 0:
        return False
    return all(ch in BASE64_CHARS for ch in s)

def try_send_bytes(payload_bytes: bytes, newline=b"\n", timeout=3.0):
    try:
        with socket.create_connection((HOST, PORT), timeout=8) as s:
            s.settimeout(1.0)
            try:
                banner = s.recv(4096)
                if banner:
                    print("banner (utf-8 replace):")
                    print(banner.decode("utf-8", errors="replace"))
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
            print("response repr:", repr(resp))
            try:
                print("response text:", resp.decode("utf-8", errors="replace"))
            except Exception:
                pass
    except Exception as e:
        print("socket/send error:", e)

def generate_candidates(b_start=B_START, b_end=B_END, e_max=E_MAX, zeros=MAX_ZERO_PAD):
    """Gera strings do tipo 'A/B', 'A/BeE' variando B, E e colagem de zeros no A."""
    # sementes óbvias (experimente estes primeiro)
    yield "3140/1e3"
    yield "1570/5e2"
    yield "6280/2e3"
    # geração sistemática
    for B in range(b_start, b_end + 1):
        for E in range(0, e_max + 1):
            denom = B * (10 ** E)
            num = TARGET * denom
            if num.denominator != 1:
                continue
            A_base = num.numerator
            for t in range(0, zeros + 1):
                A = A_base * (10 ** t)
                E2 = E + t
                yield f"{A}/{B}e{E2}"
                # e sem o "e" (caso seja inteiro e já curto)
                yield f"{A}/{B}"

def main():
    print("Buscando expressões para 3.14 (notação científica + sufixos neutros)...")
    tested = 0
    for seed in generate_candidates():
        tested += 1
        # para cada seed, teste variantes com 0..2 sufixos neutros concatenados
        for r in range(0, 3):
            for tails in product(NEUTRAL_TAILS, repeat=r):
                L = seed + "".join(tails)
                # filtro rápido: só alfabeto base64 e len%4==0
                if not is_base64_usable(L):
                    continue
                # tente decodificar como base64
                try:
                    decoded = base64.b64decode(L, validate=True)
                except Exception as e:
                    # comentário: se quiser debug, descomente a linha abaixo
                    # print(f"[skip] {L!r} base64 decode error: {e}")
                    continue
                # agora cheque se decoded é UTF-8 (IMPORTANTÍSSIMO)
                try:
                    txt = decoded.decode("utf-8")
                except Exception as e:
                    # não é UTF-8 -> o servidor vai falhar ao fazer inp.encode()
                    # descomente pra debug:
                    # print(f"[skip] {L!r} decoded not UTF-8: {e}  hex={decoded.hex()}")
                    continue

                # Se chegamos aqui: temos candidato válido
                print("="*40)
                print(f"[FOUND] L = {L!r}  (len={len(L)}, tested={tested})")
                print("decoded (hex):", decoded.hex())
                print("decoded (utf-8):", repr(txt))
                # envie (LF e CRLF)
                print("Enviando payload (LF)...")
                try_send_bytes(decoded, newline=b"\n")
                print("Enviando payload (CRLF)...")
                try_send_bytes(decoded, newline=b"\r\n")
                return

    print("Busca finalizada. Nenhum candidato válido encontrado nos limites testados.")

if __name__ == "__main__":
    main()
