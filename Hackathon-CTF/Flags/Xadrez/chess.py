# extrai a mensagem da imagem de xadrez
# preencha/ajuste BOARD com as 8 linhas (a8..h8) até (a1..h1)
BOARD = [
    list("ABIDAIDI"),   # rank 8: a8..h8
    list("DP_4F{9D"),   # rank 7
    list("_ABCD DCA".replace(" ", "")),  # rank 6  (ajuste se vir diferente)
    list("831NM3__".replace("_","_")),    # rank 5  (preencha se faltou algo)
    list("8_48CC{Z"),   # rank 4
    list("HKI}KL0L"),   # rank 3
    list("ESSAASS?".replace("?","S")),    # rank 2  (se a última não for S, corrija)
    list("10_1}_3}")    # rank 1
]

# sequência de casas (sua saída do script)
seq = "e4, e5, f3, e7, c3, e8, c4, c6, d3, c5, e3, e3, e3, f6, d2, e7, c1, a3, a3, d6, e1, g4, d5, d7, f6, e7, g4, d7, f7, d8, c3, b5, c6, b8, g5, c8, e6, b6, a8, b8, a7, b7, a6, b4, d4, d4, d4, c5, c5, c5, e5, f8, d6, f7, d8"
squares = [s.strip() for s in seq.split(",")]

files = "abcdefgh"
ranks = "87654321"

def get_char(square):
    f, r = square[0], square[1]
    r_idx = ranks.index(r)  # 0..7 (a8 linha 0)
    f_idx = files.index(f)  # 0..7 (a..h)
    return BOARD[r_idx][f_idx]

msg = "".join(get_char(sq) for sq in squares)
print(msg)

