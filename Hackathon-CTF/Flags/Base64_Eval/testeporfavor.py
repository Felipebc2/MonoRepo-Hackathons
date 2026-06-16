import base64

# Queremos que b64encode(inp.encode()) == b'0o471'
L = '0o471'
inp = base64.b64decode(L + '==')  # adiciona padding pra ser válido
print(inp)
print(inp.decode('utf-8', errors='replace'))
print(base64.b64encode(inp))  # deve voltar a ser b'0o471'
