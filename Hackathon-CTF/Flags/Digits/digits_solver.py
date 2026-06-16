#!/usr/bin/env python3
"""
digits_solver_wait.py

Versão robusta: conecta, envia 'pronto' quando solicitado, gera expressão e
AGUARDA confirmação do servidor + próximo enunciado antes de prosseguir.

Uso:
  python digits_solver_wait.py
  python digits_solver_wait.py --host 172.203.251.252 --port 23099 --max-digits 8
"""

import socket, re, time, argparse
from fractions import Fraction
from collections import defaultdict

HOST_DEFAULT = "172.203.251.252"
PORT_DEFAULT = 23099

# ------------------ GERADOR (mesma lógica do anterior) ------------------ #
def generate_expression(target:int, digit:str, max_digits=12, max_magnitude=10000):
    D = digit
    targetF = Fraction(target,1)
    if target == 0:
        return f"{D}-{D}"
    sets = [defaultdict(str) for _ in range(max_digits+1)]
    for k in range(1, max_digits+1):
        s = D * k
        sets[k][Fraction(int(s),1)] = s
    for total in range(1, max_digits+1):
        if targetF in sets[total]:
            return sets[total][targetF]
        for a in range(1, total):
            b = total - a
            for lv, ls in list(sets[a].items()):
                for rv, rs in list(sets[b].items()):
                    # + - * / %
                    try:
                        # plus
                        v = lv + rv
                        if abs(v) <= max_magnitude:
                            s = f"({ls}+{rs})"
                            if v not in sets[total] or len(s) < len(sets[total][v]):
                                sets[total][v] = s
                                if v == targetF: return s
                        # minus
                        v = lv - rv
                        if abs(v) <= max_magnitude:
                            s = f"({ls}-{rs})"
                            if v not in sets[total] or len(s) < len(sets[total][v]):
                                sets[total][v] = s
                                if v == targetF: return s
                        # multiply
                        v = lv * rv
                        if abs(v) <= max_magnitude:
                            s = f"({ls}*{rs})"
                            if v not in sets[total] or len(s) < len(sets[total][v]):
                                sets[total][v] = s
                                if v == targetF: return s
                        # division
                        if rv != 0:
                            v = lv / rv
                            if abs(v) <= max_magnitude:
                                s = f"({ls}/{rs})"
                                if v not in sets[total] or len(s) < len(sets[total][v]):
                                    sets[total][v] = s
                                    if v == targetF: return s
                        # modulus (inteiros apenas)
                        if lv.denominator == 1 and rv.denominator == 1 and rv != 0:
                            iv = int(lv)
                            ir = int(rv)
                            m = iv % ir
                            v = Fraction(m,1)
                            s = f"({ls}%{rs})"
                            if v not in sets[total] or len(s) < len(sets[total][v]):
                                sets[total][v] = s
                                if v == targetF: return s
                    except Exception:
                        pass
    # fallback simples
    d = int(D)
    if d != 0 and target % d == 0:
        times = abs(target) // d
        sign = "-" if target < 0 else ""
        return sign + "+".join([D]*times) if times <= 20 else None
    return None

# ------------------ regexes para parsing ------------------ #
RE_CHALL = re.compile(r"n(?:ú|u)mero\s+([+-]?\d+)\s+utiliz", re.I)
RE_DIGIT = re.compile(r"d[ií]gito\s+([0-9])", re.I)
RE_READY = re.compile(r"\bpronto\b", re.I)
RE_CORRECT = re.compile(r"(correto|correta|\[\+\]|\bOK\b|\bAcertou\b)", re.I)
RE_INCORRECT = re.compile(r"(errado|incorreto|\[-\])", re.I)
RE_FLAG = re.compile(r"(flag\{.*?\}|FLAG\{.*?\}|IDP\{.*?\})", re.I)

def parse_target_digit(text: str):
    # tentamos capturar target + digit em conjunto (quando possível)
    m1 = RE_CHALL.search(text)
    m2 = RE_DIGIT.search(text)
    if m1 and m2:
        try:
            return int(m1.group(1)), m2.group(1)
        except:
            return None, None
    return None, None

# ------------------ função utilitária de leitura aguardando padrões ------------------ #
def recv_until_patterns(sock, patterns, total_timeout=20.0, per_recv_timeout=2.0):
    """
    Lê do socket até encontrar algum dos regex em `patterns` ou até total_timeout.
    Retorna (matched_pattern, full_text).
    matched_pattern = index do pattern que bateu ou None se timeout.
    """
    sock.settimeout(per_recv_timeout)
    buf = ""
    start = time.time()
    while True:
        # checar se já bate sem fazer recv
        for i, p in enumerate(patterns):
            if p.search(buf):
                return i, buf
        # timeout total
        if time.time() - start > total_timeout:
            return None, buf
        try:
            data = sock.recv(8192)
            if not data:  # conexão fechada
                return None, buf
            buf += data.decode(errors="ignore")
        except socket.timeout:
            # continua tentando até total_timeout
            continue
        except Exception as e:
            return None, buf

# ------------------ loop principal melhorado ------------------ #
def solve_over_nc(host, port, max_digits=7, expect_count=None):
    print(f"[+] Conectando a {host}:{port} ...")
    with socket.create_connection((host, port), timeout=15) as s:
        print("[+] Conectado. aguardando prompt...")
        s.settimeout(2.0)
        buffer = ""
        sent_ready = False
        solved = 0

        while True:
            # primeiro, leia o que houver no socket e acumule no buffer
            idx, buffer = recv_until_patterns(s, [RE_READY, RE_CHALL, RE_FLAG], total_timeout=60.0)
            # se nada veio, servidor provavelmente fechou ou demorou demais
            if idx is None:
                # veja se buffer contém algo útil
                if not buffer:
                    print("[!] Sem dados e sem buffer — encerrando.")
                    break
                # se temos flag no buffer, mostramos e saímos
                fm = RE_FLAG.search(buffer)
                if fm:
                    print("[FLAG ENCONTRADA]", fm.group(0))
                    break
                # senão continuamos tentando
                print("[!] Timeout esperando dados. Continuando...")
                continue

            # Se vimos 'pronto' -> responder 'pronto' (uma vez)
            if idx == 0 and not sent_ready:
                print("[>] Servidor pediu 'pronto' -> enviando 'pronto'")
                s.sendall(b"pronto\n")
                sent_ready = True
                # depois de 'pronto' vamos aguardar o enunciado (loop volta)
                continue

            # Se vimos um enunciado de desafio (ou parte dele), extraímos target + digit
            if RE_CHALL.search(buffer):
                target, digit = parse_target_digit(buffer)
                # se ainda não pegamos dígito, tentamos ler mais até obter digit e numero na mesma mensagem
                if target is None or digit is None:
                    # ler até aparecer o digit também
                    idx2, buffer = recv_until_patterns(s, [RE_DIGIT, RE_FLAG], total_timeout=30.0)
                    if idx2 is None:
                        print("[!] Não conseguimos obter target/digit completos. Buffer:\n", buffer[-400:])
                        # tentamos continuar (não fechar)
                        continue
                    target, digit = parse_target_digit(buffer)
                    if target is None or digit is None:
                        print("[!] Ainda sem target/digit claros, ignorando e aguardando próximo bloco.")
                        continue

                print(f"[DESAFIO] target={target} digit={digit}")
                expr = generate_expression(target, digit, max_digits=max_digits)
                if expr is None:
                    print(f"[!] Não achei expressão com max_digits={max_digits}. Tentando fallback simples...")
                    d = int(digit)
                    if d != 0 and target % d == 0:
                        times = abs(target) // d
                        expr = "+".join([digit]*times)
                    else:
                        # envio algo mínimo (pior caso)
                        expr = digit

                print("[>] Enviando expressão:", expr)
                s.sendall((expr + "\n").encode())

                # após enviar: aguardar confirmação (Correto/Errado) com timeout razoável
                idx_conf, conf_buf = recv_until_patterns(s, [RE_CORRECT, RE_INCORRECT, RE_FLAG, RE_CHALL], total_timeout=30.0)
                # imprime trecho
                tail = conf_buf[-400:] if len(conf_buf) > 0 else ""
                print("[<] Recebido (confirmação/next):\n", tail)
                # checar flag
                fm = RE_FLAG.search(conf_buf)
                if fm:
                    print("[FLAG]", fm.group(0))
                    break

                # se confirmação positiva ou negativa apareceu, continuamos e esperamos próximo enunciado
                # caso a próxima CHALL já venha no mesmo pacote, loop continuará e a processará
                solved += 1
                # opcional: se queremos parar após X desafios
                if expect_count is not None and solved >= expect_count:
                    print(f"[+] Alcançado expect_count={expect_count}. Saindo.")
                    break
                # continue loop para capturar próximo enunciado
                continue

            # safety catch-all
            print("[DEBUG] loop chegou ao fim sem ação via buffer. buffer tail:\n", buffer[-300:])

# ------------------ CLI ------------------ #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=HOST_DEFAULT)
    ap.add_argument("--port", default=PORT_DEFAULT, type=int)
    ap.add_argument("--max-digits", default=7, type=int)
    ap.add_argument("--expect-count", default=None, type=int,
                    help="(opcional) parar após esse número de resoluções")
    args = ap.parse_args()

    try:
        solve_over_nc(args.host, args.port, max_digits=args.max_digits, expect_count=args.expect_count)
    except KeyboardInterrupt:
        print("\n[!] Interrompido pelo usuário")

if __name__ == "__main__":
    main()
