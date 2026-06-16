#!/usr/bin/env python3
# find_input_for_1337.py
# Tenta encontrar uma entrada 'inp' tal que eval(b64encode(inp.encode())) == 1337
# Depois, se encontrar, conecta ao host/porta indicados e envia o inp + newline.

import base64
import itertools
import socket
import sys
import time

HOST = "20.102.93.39"
PORT = 33420   # conforme você indicou na sessão
MAXLEN = 3     # comprimento máximo de bytes a testar (1..MAXLEN). 3 => ~16.7M testes.
# Aumente para 4 se quiser (256^4 = 4.2e9, bem pesado).

def is_valid_utf8(b: bytes) -> bool:
    try:
        b.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

def try_find(maxlen=MAXLEN, report_every=1000000):
    """
    Itera sobre todas as sequências de bytes de comprimento 1..maxlen;
    verifica se elas decodificam em UTF-8; para as que decodificam, calcula
    base64.b64encode(bytes) e faz eval(...) nesse resultado. Se eval == 1337, retorna
    a string (decoded utf-8) e o valor da base64.
    """
    tried = 0
    t0 = time.time()
    for L in range(1, maxlen+1):
        # iterando sobre todos os bytes^L -> grande; iteramos em ordem natural
        # para economia de memória, usamos nested loops via product
        for tup in itertools.product(range(256), repeat=L):
            b = bytes(tup)
            tried += 1
            if tried % report_every == 0:
                dt = time.time() - t0
                print(f"[{time.strftime('%H:%M:%S')}] tried {tried:,} (len {L}) — {tried/dt:.1f} it/s")
            if not is_valid_utf8(b):
                continue
            # candidate string (what we'd type)
            s = b.decode('utf-8')
            # base64 bytes that server will eval
            X = base64.b64encode(b)
            # X is bytes, but eval accepts bytes; we'll eval as bytes to match server
            # CUIDADO: usando eval localmente (intencional)
            try:
                val = eval(X)
            except Exception:
                continue
            if isinstance(val, int) and val == 1337:
                print("FOUND!")
                print("input bytes (repr):", repr(b))
                print("input string to send :", repr(s))
                print("base64 output         :", X)
                return s, X
    return None, None

def send_to_server(inp_str, host=HOST, port=PORT, timeout=10.0):
    print(f"Conectando a {host}:{port} e enviando input...")
    with socket.create_connection((host, port), timeout=timeout) as sock:
        # ler banner/prompt inicial (se houver)
        try:
            sock.settimeout(1.0)
            banner = sock.recv(4096)
            if banner:
                print("banner:", banner.decode('utf-8', errors='replace'))
        except Exception:
            pass
        # enviar linha
        sock.sendall(inp_str.encode('utf-8') + b'\n')
        # ler resposta (até fechar ou timeout)
        sock.settimeout(3.0)
        out = b''
        try:
            while True:
                part = sock.recv(4096)
                if not part:
                    break
                out += part
        except Exception:
            pass
        print("=== resposta bruta do servidor ===")
        print(out.decode('utf-8', errors='replace'))
        print("=== fim resposta ===")

if __name__ == "__main__":
    print("Iniciando busca (padrão MAXLEN=%d). Atenção: pode demorar." % MAXLEN)
    s, X = try_find()
    if s is None:
        print("Não encontrei nada com MAXLEN =", MAXLEN)
        sys.exit(2)
    print("Entrada encontrada (string):", repr(s))
    print("Base64 correspondente : ", X)
    # perguntar ao usuário se deseja enviar (ou enviar direto)
    yn = input("Deseja enviar essa entrada agora ao servidor? (y/N) ")
    if yn.lower().startswith('y'):
        send_to_server(s)
    else:
        print("Pronto — copie esta string e envie com nc / netcat:")
        print(repr(s))

