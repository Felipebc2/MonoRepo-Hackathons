#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, re, time, argparse
from fractions import Fraction
from collections import defaultdict

HOST_DEFAULT = "172.203.251.252"
PORT_DEFAULT = 23131
MAX_LEN = 100

# ----------- GERADOR (com limite de 100 chars) -----------
def generate_expr_len_constrained(target:int, digit:str, max_digits:int,
                                  max_magnitude=10000, max_len=100):
    D = digit
    T = Fraction(target, 1)

    if target == 0:
        s = f"{D}-{D}"
        return s if len(s) <= max_len else None

    sets = [defaultdict(str) for _ in range(max_digits+1)]

    # concatenações puras
    for k in range(1, max_digits+1):
        tok = D * k
        sets[k][Fraction(int(tok),1)] = tok

    # já bateu?
    for k in range(1, max_digits+1):
        if T in sets[k] and len(sets[k][T]) <= max_len:
            return sets[k][T]

    for total in range(1, max_digits+1):
        if T in sets[total] and len(sets[total][T]) <= max_len:
            return sets[total][T]

        for a in range(1, total):
            b = total - a
            LA, LB = sets[a], sets[b]
            if not LA or not LB: 
                continue

            def put(val, s):
                if len(s) > max_len: 
                    return
                cur = sets[total].get(val)
                if not cur or len(s) < len(cur):
                    sets[total][val] = s

            for lv, ls in LA.items():
                if abs(lv) > max_magnitude: 
                    continue
                for rv, rs in LB.items():
                    if abs(rv) > max_magnitude: 
                        continue
                    put(lv + rv, f"({ls}+{rs})")
                    put(lv - rv, f"({ls}-{rs})")
                    put(lv * rv, f"({ls}*{rs})")
                    if rv != 0:
                        put(lv / rv, f"({ls}/{rs})")
                    if lv.denominator == 1 and rv.denominator == 1 and rv != 0:
                        put(Fraction(int(lv) % int(rv),1), f"({ls}%{rs})")

        if T in sets[total] and len(sets[total][T]) <= max_len:
            return sets[total][T]

    return None

def find_expression_with_autoscale(target:int, digit:str, start_digits=7, max_digits_cap=12, max_len=MAX_LEN):
    for md in range(start_digits, max_digits_cap+1):
        expr = generate_expr_len_constrained(target, digit, md, max_len=max_len)
        if expr is not None:
            return expr
    return None

# ----------- REGEX / PARSER -----------
RE_READY   = re.compile(r"\bpronto\b", re.I)
RE_CHALL   = re.compile(r"n(?:ú|u)mero\s+([+-]?\d+).+d[ií]gito\s+([0-9])", re.I)
RE_COR_OK  = re.compile(r"(correto|correta|\[\+\]|acertou|ok)", re.I)
RE_COR_BAD = re.compile(r"(incorreto|errado|\[-\])", re.I)
RE_FLAG    = re.compile(r"(flag\{.*?\}|FLAG\{.*?\}|IDP\{.*?\})", re.I)  # <- linha corrigida

def parse_target_digit(text:str):
    m = RE_CHALL.search(text)
    if not m: 
        return None, None
    return int(m.group(1)), m.group(2)

# ----------- SOCKET HELPERS -----------
def recv_until(sock, patterns, total_timeout=60.0, per_recv_timeout=2.5):
    sock.settimeout(per_recv_timeout)
    buf = ""
    t0 = time.time()
    while True:
        for i, p in enumerate(patterns):
            if p.search(buf):
                return i, buf
        if time.time() - t0 > total_timeout:
            return None, buf
        try:
            data = sock.recv(8192)
            if not data:
                return None, buf
            buf += data.decode(errors="ignore")
        except socket.timeout:
            continue
        except Exception:
            return None, buf

# ----------- LOOP PRINCIPAL -----------
def solve(host, port, start_digits=7, cap_digits=12, max_len=MAX_LEN):
    print(f"[+] Conectando a {host}:{port} ...")
    with socket.create_connection((host, port), timeout=15) as s:
        peer = s.getpeername()
        print(f"[+] Conectado a {peer[0]}:{peer[1]}")
        sent_ready = False

        while True:
            idx, buf = recv_until(s, [RE_READY, RE_CHALL, RE_FLAG], total_timeout=120.0)
            if idx is None:
                if not buf:
                    print("[!] Servidor fechou a conexão.")
                    break
                fm = RE_FLAG.search(buf)
                if fm:
                    print("[FLAG]", fm.group(0))
                else:
                    print("[!] Timeout aguardando enunciado…")
                continue

            if idx == 0 and not sent_ready:
                print("[>] Enviando: pronto")
                s.sendall(b"pronto\n")
                sent_ready = True
                continue

            target, digit = parse_target_digit(buf)
            if target is None or digit is None:
                idx2, buf2 = recv_until(s, [RE_CHALL, RE_FLAG], total_timeout=30.0)
                if idx2 is None:
                    print("[!] Não consegui extrair target/digit.")
                    continue
                target, digit = parse_target_digit(buf + buf2)

            print(f"[DESAFIO] target={target} digit={digit}")

            expr = find_expression_with_autoscale(target, digit, start_digits, cap_digits, max_len)
            if expr is None:
                d = int(digit)
                if d != 0 and target % d == 0:
                    n = abs(target) // d
                    candidate = "+".join([digit]*n)
                    expr = candidate if (len(candidate) <= max_len and target >= 0) else None
            if expr is None:
                print(f"[!] Não encontrei expressão <= {max_len} chars. Enviando dígito isolado (vai errar).")
                expr = digit

            print(f"[>] Enviando expressão ({len(expr)} chars): {expr}")
            s.sendall((expr + "\n").encode())

            idxc, conf = recv_until(s, [RE_COR_OK, RE_COR_BAD, RE_FLAG, RE_CHALL], total_timeout=45.0)
            print("[<] Confirmação/Next:\n", (conf[-400:] if conf else ""))
            if conf and RE_FLAG.search(conf):
                print("[FLAG]", RE_FLAG.search(conf).group(0))
                break

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=HOST_DEFAULT)
    ap.add_argument("--port", default=PORT_DEFAULT, type=int)
    ap.add_argument("--start-digits", default=7, type=int)
    ap.add_argument("--cap-digits", default=12, type=int)
    ap.add_argument("--max-len", default=MAX_LEN, type=int)
    args = ap.parse_args()
    try:
        solve(args.host, args.port, args.start_digits, args.cap_digits, args.max_len)
    except KeyboardInterrupt:
        print("\n[!] Interrompido pelo usuário")

if __name__ == "__main__":
    main()
