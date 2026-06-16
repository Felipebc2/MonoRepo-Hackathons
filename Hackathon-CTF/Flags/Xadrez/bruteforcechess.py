# bf_flag.py
# brute-force over pale/dark choices per square with pruning targeted to this CTF
from itertools import product
import time
import re

# === CONFIGURAR AQUI ===
# Sequence length must match number of squares (56 in seu caso)
N = 56

# Preencha com os caracteres que você leu nas imagens:
# - pale_chars[i] = caractere visível na imagem "pálida" (board_hidden_letters_inverted)
# - dark_chars[i] = caractere visível na imagem original (as letras escuras)
# Se alguma for desconhecida, coloque '_' ou '' e o script tratará.
#
# Exemplo mínimo: se você leu 'I' em e4 (posição 0) e 'C' como letra escura, escreva:
# pale_chars[0] = 'I'; dark_chars[0] = 'C'
#
# IMPORTANTE: a ordem das casas é a lista gerada pelo seu script (56 casas).
# Substitua os exemplos abaixo pelos valores reais que você extraiu.
pale_chars = list("I D P { ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ?".replace(" ", "") )
dark_chars = list("C M L F I A 4 B } 1 K K K D A F _ H H C } { N 4 D F { 4 { D I 3 B B _ I D A A B D P _ _ 8 8 8 1 1 1 M I C { D".replace(" ", ""))

# If those placeholder strings aren't length N, user must fill them.
if len(pale_chars) != N or len(dark_chars) != N:
    print("AVISO: pale_chars/dark_chars não tem comprimento correto ({}/{})".format(len(pale_chars), len(dark_chars)))
    print("Ajuste os arrays com os caracteres que você leu; eles devem ter tamanho", N)
    raise SystemExit(1)

# Allowed charset to reduce noise: A-Z, 0-9, underscore, braces
ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}")

# Positions you want to fix (se já tem certeza): dict idx->char
fixed = {
    0: 'I',  # e4
    1: 'D',  # e5
    2: 'P',  # f3
    3: '{',  # e7
}
# You can add more fixed positions if tem certeza (ex: fixed[55] = '}')

# Target pattern: starts with IDP{ and contains closing brace; ajuste se preciso
def looks_valid_prefix(s):
    # must start with IDP{
    if len(s) < 4: return s == "IDP"[:len(s)]
    if not s.startswith("IDP{"): return False
    # all chars allowed
    if any(ch not in ALLOWED for ch in s): return False
    return True

def looks_valid_full(s):
    # must start with IDP{ and end with } (or contain '}' somewhere)
    if not s.startswith("IDP{"): return False
    if '}' not in s: return False
    # single closing brace is typical, but allow multiple if present
    if any(ch not in ALLOWED for ch in s): return False
    return True

start = time.time()

# Precompute per-position options (unique, allowed)
opts = []
for i in range(N):
    optset = []
    for candidate in (pale_chars[i], dark_chars[i]):
        if candidate is None: continue
        if candidate == '': continue
        # uppercase the candidate and trim
        c = candidate.strip().upper()
        if len(c) == 0: continue
        # if multi-char in a cell (rare), split and allow each
        for ch in c:
            if ch in ALLOWED:
                optset.append(ch)
    # always include '_' as fallback if nothing readable
    if not optset:
        optset = ['_']
    # reduce duplicates
    opts.append(sorted(set(optset)))

# Quick check
for i, o in enumerate(opts[:10]):
    print(f"{i:02d} -> {o}")
print("... total positions:", len(opts))

# Backtracking with pruning
results = []
max_results = 20  # limite para não inundar
counter = 0
prune_hits = 0

def dfs(pos, prefix):
    global counter, prune_hits
    # pruning: check prefix validity
    if not looks_valid_prefix(prefix):
        prune_hits += 1
        return
    if pos == N:
        counter += 1
        if looks_valid_full(prefix):
            results.append(prefix)
            print(">>> Candidate found:", prefix)
        return
    # fixed position?
    if pos in fixed:
        ch = fixed[pos]
        if ch not in opts[pos]:
            # se a letra fixa não estiver nas opções, isso é suspeito,
            # mas tentamos seguir mesmo assim (você pode decidir)
            # aqui, rejeitamos para evitar ruído:
            return
        dfs(pos+1, prefix+ch)
        return

    # iterate options for this pos
    for ch in opts[pos]:
        # small heuristic: rarely allow a closing brace early (except expected)
        if ch == '}' and pos < 4:
            continue
        dfs(pos+1, prefix+ch)
        if len(results) >= max_results:
            return

# Start building prefix from zero
dfs(0, "")

elapsed = time.time() - start
print(f"\nFinished. Time: {elapsed:.2f}s, explored(?) results: {counter}, pruned: {prune_hits}")
print("Found results (up to limit):", len(results))
for r in results:
    print(" ->", r)
if not results:
    print("Nenhum candidato encontrado com as restrições atuais.")
    print("Opções para avançar:")
    print(" - Remover/reduzir restrições (fixed, allowed charset)")
    print(" - Corrigir/fornecer pale_chars & dark_chars com precisão")
    print(" - Permitir mais caracteres por casa")

