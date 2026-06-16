#!/usr/bin/env python3
from base64 import b64encode

# este input simula o que você envia para o servidor
# — ele contém bytes fora da faixa UTF-8 (como no payload b'\xd7\xdf\xdb')
inp = "\udcd7\udcdf\udcdb"

print("String Python:", repr(inp))

try:
    b64 = b64encode(inp.encode())
    print("Base64 gerado:", b64)
except Exception as e:
    print("Erro:", repr(e))

