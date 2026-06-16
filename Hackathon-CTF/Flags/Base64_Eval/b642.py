#!/usr/bin/env python3
# brute_try.py
# Testa vários inputs no server até encontrar uma resposta que contenha "flag" ou "IDP{".
# Ajuste HOST, PORTS, candidates e check_flag() conforme necessário.

import socket
import time
from typing import Iterable

HOST = "20.102.93.39"
PORTS = [33405]   # <-- usa apenas essa porta agora
RECV_TOKEN = b'>>> '
RECV_TIMEOUT = 6.0
PER_TRY_TIMEOUT = 2.0
DELAY_BETWEEN_TRIES = 0.12
MAX_RETRIES = 2

# Customize aqui: lista inicial de candidatos (strings que serão enviadas literalmente)
# Incluí variações comuns: números, hex, expressões, etc.
candidates = []
# números como strings (0-5000 -> ajusta se quiseres mais)
candidates += [str(i) for i in range(0, 5000)]
# hex/0x variants for interesting candidates
candidates += [hex(i) for i in range(0, 2000)]
# algumas expressões aritméticas e literais que podem avaliar para 1337
candidates += ["1337", "0x539", "13*103", "1000+337", "int('1337')", "sum([1000,337])"]
# adicionar formas com padding/carriage if needed
candidates += ["1337\r\n", "1337\n"]

# Também podes colocar um arquivo 'payloads.txt' com uma payload por linha.
def load_extra(filename="payloads.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                s = line.rstrip("\n\r")
                if s:
                    yield s
    except FileNotFoundError:
        return
    except Exception as e:
        print("Erro ao ler payloads extras:", e)
        return

def recv_all_until(sock: socket.socket, token: bytes = RECV_TOKEN, timeout: float = RECV_TIMEOUT, chunk=4096) -> bytes:
    sock.settimeout(1.0)
    buf = b''
    t0 = time.time()
    while True:
        if token in buf:
            return buf
        if time.time() - t0 > timeout:
            return buf
        try:
            part = sock.recv(chunk)
        except socket.timeout:
            continue
        except Exception:
            return buf
        if not part:
            return buf
        buf += part

def send_and_recv(host: str, port: int, payload: bytes, recv_token: bytes = RECV_TOKEN) -> bytes:
    """Conecta, espera prompt (se houver), envia payload e coleta resposta."""
    try:
        with socket.create_connection((host, port), timeout=8) as s:
            # Ler até prompt (ou timeout)
            banner = recv_all_until(s, token=recv_token, timeout=RECV_TIMEOUT)
            # enviar payload (garantir newline)
            s.sendall(payload + b'\n')
            # pequena espera para o servidor processar
            time.sleep(0.12)
            s.settimeout(PER_TRY_TIMEOUT)
            resp = b''
            try:
                while True:
                    part = s.recv(4096)
                    if not part:
                        break
                    resp += part
            except socket.timeout:
                pass
            return banner + resp
    except Exception as e:
        # erro de conexão / timeout
        return b''

def looks_like_flag(resp_bytes: bytes) -> bool:
    """Define a heurística para detectar que veio a flag na resposta."""
    if not resp_bytes:
        return False
    text = resp_bytes.decode('utf-8', errors='ignore')
    # Ajuste essas verificações conforme o formato das flags do seu CTF
    checks = ["IDP{", "flag{", "FLAG{", "/app/flag.txt", "CTF{"]
    for c in checks:
        if c in text:
            return True
    # também, se o servidor imprimir uma palavra-chave (ex: conteúdo de flag.txt)
    if "{" in text and "}" in text and len(text) < 2000:
        # heurística básica: se tem chaves, pode ser flag
        return True
    return False

def try_all(host: str, ports: Iterable[int], payloads: Iterable[str], start_index=0):
    # itera payloads e portas
    index = start_index
    for payload_str in payloads:
        payload_bytes = payload_str.encode('latin1', errors='ignore')  # latin1 preserva bytes 0-255 se tu carregar binários
        for port in ports:
            for attempt in range(MAX_RETRIES):
                print(f"[{index}] Tentando porta {port}, tentativa {attempt+1}, payload repr={repr(payload_str)}")
                resp = send_and_recv(host, port, payload_bytes)
                if resp:
                    s = resp.decode('utf-8', errors='replace')
                    # salva log por segurança
                    with open("brute_log.txt", "a", encoding="utf-8") as L:
                        L.write(f"INDEX={index} PORT={port} PAYLOAD={repr(payload_str)}\n")
                        L.write(s + "\n" + "="*60 + "\n")
                    if looks_like_flag(resp):
                        print(">>> POSSÍVEL FLAG ENCONTRADA! <<<")
                        print("PORT:", port)
                        print("PAYLOAD:", repr(payload_str))
                        print("RESPOSTA:\n", s)
                        # salvar em arquivo
                        with open("brute_found.txt", "w", encoding="utf-8") as f:
                            f.write(f"PORT={port}\nPAYLOAD={repr(payload_str)}\n\nRESPONSE:\n{s}\n")
                        return True
                else:
                    # sem resposta, apenas log minimal
                    pass
                time.sleep(DELAY_BETWEEN_TRIES)
        index += 1
    return False

if __name__ == "__main__":
    # compor a lista completa de payloads
    extra = list(load_extra("payloads.txt"))
    full_payloads = candidates + extra
    print(f"Total candidatos: {len(full_payloads)} (incluindo extras: {len(extra)})")
    found = try_all(HOST, PORTS, full_payloads)
    if not found:
        print("Terminei todas as tentativas — não encontrei flag (ver brute_log.txt para detalhes).")
    else:
        print("Flag encontrada — ver brute_found.txt.")
