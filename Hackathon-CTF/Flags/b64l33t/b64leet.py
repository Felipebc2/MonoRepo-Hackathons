#!/usr/bin/env python3
import socket
import base64

HOST = "20.102.93.39"
PORT = 33231

payload_bytes = base64.b64decode(b'0o52')

with socket.create_connection((HOST, PORT), timeout=10) as s:
    # recebe banner / prompt inicial (se houver)
    banner = s.recv(4096)
    if banner:
        try:
            print(banner.decode('utf-8', errors='replace'))
        except:
            print(repr(banner))

    # enviar os bytes seguidos de newline (input() no server espera linha)
    s.sendall(payload_bytes + b'\n')

    # ler resposta (flag)
    resp = b""
    while True:
        try:
            part = s.recv(4096)
        except Exception:
            break
        if not part:
            break
        resp += part
        # se parecer que já veio a flag, podemos parar - mas aqui tentamos ler tudo disponível
    try:
        print(resp.decode('utf-8', errors='replace'))
    except:
        print(repr(resp))
