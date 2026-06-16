#!/usr/bin/env python3
# b64_blocks_and_candidates.py
import base64
import string
import socket
import time
import math

HOST = "20.102.93.39"
PORT = 33715

# caracteres permitidos na expressão (também pertencem ao alfabeto base64)
CHARSET = "0123456789+/"
# tolerância: bytes considerados "imprimíveis" (garante UTF-8 simples)
MIN_PRINT = 0x20
MAX_PRINT = 0x7E

# se True -> envia automaticamente para o servidor quando encontrar candidato válido
DO_SEND = False

def block_to_bytes(block4: str) -> bytes:
    """Converte 4 chars base64 (usando alfabeto standard) em 3 bytes."""
    B64_ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    idx = {c: i for i, c in enumerate(B64_ALPH)}
    v = [idx[c] for c in block4]
    b0 = (v[0] << 2) | (v[1] >> 4)
    b1 = ((v[1] & 0xF) << 4) | (v[2] >> 2)
    b2 = ((v[2] & 0x3) << 6) | v[3]
    return bytes([b0, b1, b2])

def is_printable_block(block4: str) -> bool:
    try:
        b = block_to_bytes(block4)
    except Exception:
        return False
    return all(MIN_PRINT <= x <= MAX_PRINT for x in b)

def make_safe_blocks():
    """Gera todos os blocos 4-chars usando apenas CHARSET e filtra por imprimíveis."""
    safe = set()
    # 12^4 = 20736 combinações -> aceitável
    cs = CHARSET
    for c0 in cs:
        for c1 in cs:
            for c2 in cs:
                for c3 in cs:
                    blk = c0 + c1 + c2 + c3
                    if is_printable_block(blk):
                        safe.add(blk)
    return safe

def valid_blocks_for_expr(expr: str, safe_blocks: set) -> bool:
    """Verifica se expr (len %4==0) tem todos os blocos de 4 chars dentro de safe_blocks."""
    if len(expr) % 4 != 0:
        return False
    # também garante que só usemos chars do CHARSET
    if any(ch not in CHARSET for ch in expr):
        return False
    for i in range(0, len(expr), 4):
        if expr[i:i+4] not in safe_blocks:
            return False
    return True

def try_send_bytes(payload_bytes: bytes, newline=b"\n", timeout=3.0):
    try:
        with socket.create_connection((HOST, PORT), timeout=8) as s:
            s.settimeout(1.0)
            try:
                banner = s.recv(4096)
                if banner:
                    print("banner:", banner.decode('utf-8', errors='replace'))
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
            print("=== server response (repr) ===")
            print(repr(resp))
            print("=== server response (text) ===")
            try:
                print(resp.decode('utf-8', errors='replace'))
            except Exception:
                print("<could not decode as utf-8>")
    except Exception as e:
        print("socket/send error:", e)

def decode_and_test(expr: str):
    try:
        decoded = base64.b64decode(expr, validate=True)
    except Exception as e:
        return False, f"base64 decode failed: {e}", None
    # test utf-8
    try:
        txt = decoded.decode('utf-8')
        return True, txt, decoded
    except Exception:
        return False, "decoded not utf-8", decoded

def generate_fraction_equivalents(a: int, b: int, max_scale_pow=4):
    """Gera versões escaladas (multiplicar num/den por 10^k) e formas reduzidas."""
    pairs = set()
    # reduzido
    g = math.gcd(a, b)
    pairs.add((a//g, b//g))
    # orig
    pairs.add((a, b))
    # escalonamentos por potencias de 10 e por 2/5
    for k in range(1, max_scale_pow+1):
        s = 10**k
        pairs.add((a*s, b*s))
        pairs.add((a*s*2, b*s*2))
        pairs.add((a*s*5, b*s*5))
    # outras formas simples (swap to common forms)
    # also include the simple reductions like 314/100 if they equal the same float roughly
    # We'll compute several small scaled rational variations around the same float
    val = a / b
    for denom in [1,10,50,100,250,500,1000,2000]:
        num = int(round(val * denom))
        pairs.add((num, denom))
    return sorted(pairs)

def make_expr_variations(a,b):
    """Gera strings de expressão a/b com variações úteis (zeros, +0, etc)."""
    base = f"{a}/{b}"
    variants = [base, base + "+0", base + "+0+0", "0"+base, base + "+00", base + "+0+00"]
    # remover duplicatas e manter ordem
    seen = set()
    out = []
    for v in variants:
        if v not in seen:
            out.append(v); seen.add(v)
    return out

def main():
    # ponto de partida: seu caso
    A = 1570
    B = 500
    print("Gerando safe blocks (4-char) usando charset:", CHARSET)
    safe_blocks = make_safe_blocks()
    print("safe blocks gerados:", len(safe_blocks))

    # gerar pares de frações equivalentes e testar
    candidates_tried = 0
    found_any = 0

    frac_pairs = generate_fraction_equivalents(A, B, max_scale_pow=3)
    print("Will test fraction pairs (examples):", frac_pairs[:20])

    for (a,b) in frac_pairs:
        exprs = make_expr_variations(a,b)
        for expr in exprs:
            candidates_tried += 1
            # só permita chars do conjunto (0-9,+,/)
            if any(ch not in CHARSET for ch in expr):
                continue
            # força comprimento múltiplo de 4: se não, tenta padear com "+0" repetidos até próximo múltiplo de 4
            if len(expr) % 4 != 0:
                # try to append "+0" until multiple of 4 (but keep only allowed chars)
                tmp = expr
                attempts = 0
                while len(tmp) % 4 != 0 and attempts < 4:
                    tmp += "+0"
                    attempts += 1
                expr_used = tmp if len(tmp) % 4 == 0 else None
            else:
                expr_used = expr

            if not expr_used:
                continue

            # agora verifica se todos os blocos de 4 estão no safe_blocks
            if not valid_blocks_for_expr(expr_used, safe_blocks):
                # rápido fallback: ainda podemos testar base64 decode mesmo que bloco não seja safe
                ok, info, decoded = decode_and_test(expr_used)
                if ok:
                    print("Found candidate (even though not all blocks safe):", expr_used)
                    print("decoded text:", info)
                    found_any += 1
                    if DO_SEND:
                        try_send_bytes(decoded, newline=b"\n")
                    else:
                        print("Set DO_SEND=True to actually send.")
                    return
                continue

            # se passou na validação por blocos, decodifica e testa UTF-8 (deveria)
            ok, info, decoded = decode_and_test(expr_used)
            if ok:
                print("\n=== ACHOU CANDIDATO VÁLIDO ===")
                print("expr:", expr_used)
                print("decoded text:", info)
                found_any += 1
                if DO_SEND:
                    print("Enviando...")
                    try_send_bytes(decoded, newline=b"\n")
                else:
                    print("DO_SEND=False -> não enviei. Ajuste DO_SEND=True para enviar.")
                return
            else:
                # report interessante pra debug
                print(f"tested {expr_used!r}: decode ok? {ok}; reason: {info}; decoded hex: {None if decoded is None else decoded.hex()}")

    print("\nFim das tentativas. candidatos testados:", candidates_tried)
    if found_any == 0:
        print("Não achamos candidato válido no conjunto gerado.")
        print("Opções seguintes recomendadas:")
        print(" - aumentar max_scale_pow em generate_fraction_equivalents()")
        print(" - gerar combinações arbitrárias de safe_blocks e tentar montar expressões que correspondam a regex '^\\d+(/\\d+)(\\+0)*$'")
        print(" - permitir blocos que produzam bytes UTF-8 válidos (não só ASCII imprimível) — alterar is_printable_block")

if __name__ == "__main__":
    main()
