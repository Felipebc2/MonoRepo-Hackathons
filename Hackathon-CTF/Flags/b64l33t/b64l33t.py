#!/usr/bin/env python3
# b64_fixed_eval.py
import base64
import string
import socket
import time

# === CONFIGURAÇÕES DO SERVIDOR ===
HOST = "20.102.93.39"
PORT = 33716

# === PARÂMETROS DO DESAFIO ===
a = 1570      # numerador fixo
b = 500       # denominador fixo

# === CONSTANTES ===
BASE64_CHARS = set(string.ascii_letters + string.digits + "+/")

# === FUNÇÕES AUXILIARES ===
def is_base64_usable(s: str) -> bool:
    """Verifica se a string usa apenas caracteres base64 e possui comprimento múltiplo de 4."""
    return len(s) % 4 == 0 and all(ch in BASE64_CHARS for ch in s)

def try_send_bytes(payload_bytes: bytes, newline=b"\n", timeout=3.0):
    """Conecta ao servidor, envia o payload e mostra a resposta."""
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

            # envia o payload
            s.sendall(payload_bytes + newline)

            # lê a resposta
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

# === MAIN ===
def main():
    print(f"Testing fixed values: a={a}, b={b}")
    L = f"{a}/{b}"
    print("Candidate L:", L)

    # 1. Checa se pode ser base64
    if not is_base64_usable(L):
        print("❌ Not a valid Base64 candidate (invalid chars or length not multiple of 4).")
        return

    # 2. Tenta decodificar
    try:
        decoded = base64.b64decode(L, validate=True)
    except Exception as e:
        print("❌ Base64 decode failed:", e)
        return

    # 3. Tenta decodificar em UTF-8 (deve ser possível para o servidor aceitar inp.encode())
    try:
        decoded.decode('utf-8')
    except Exception:
        print("❌ Decoded bytes not valid UTF-8.")
        return

    # 4. Se chegou aqui, é um candidato válido
    print("✅ FOUND candidate L:", L)
    print("decoded repr:", repr(decoded))
    print("decoded hex:", decoded.hex())

    # 5. Envia automaticamente
    print("Sending payload to server (LF and CRLF tries)...")
    try_send_bytes(decoded, newline=b"\n")
    try_send_bytes(decoded, newline=b"\r\n")

if __name__ == "__main__":
    main()
