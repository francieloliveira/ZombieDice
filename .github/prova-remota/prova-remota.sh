#!/bin/bash
# FRA-620. Prova remota no Linux, dentro de um container sem rede.
# Fonte: tuttidash/tools/prova-remota-linux (o TuttiDash regenera esta cópia).
# Este arquivo vale como blob do commit da base (SHA completo em PROVA_BASE_SHA).
# Uso: prova-remota.sh <checkout-da-base> <checkout-do-head>
# Do head só se lê a lista de arquivos (git diff --name-only) e o código entra
# no container só para leitura. Nenhum script do head roda fora do container.
set -euo pipefail

IMAGEM="python:3.12-slim@sha256:aa943ce411423c7582288f18707ff66eddcbaeb510502d747a72aeb34f30d159"
PASTA=".github/prova-remota"

if [ "$#" -ne 2 ]; then
  echo "uso: $0 <checkout-da-base> <checkout-do-head>" >&2
  exit 2
fi
base=$(cd "$1" && pwd -P)
head=$(cd "$2" && pwd -P)
if [ "$head" = "$base" ] || [ "${head#"$base"/}" != "$head" ] || [ "${base#"$head"/}" != "$base" ]; then
  echo "prova-remota: base e head têm de ser pastas separadas" >&2
  exit 2
fi
[[ "${PROVA_BASE_SHA-}" =~ ^[0-9a-f]{40}$ ]] || { echo "prova-remota: SHA da base incompleto" >&2; exit 2; }
[[ "${PROVA_HEAD_SHA-}" =~ ^[0-9a-f]{40}$ ]] || { echo "prova-remota: SHA do head incompleto" >&2; exit 2; }
[ "$(git -C "$base" rev-parse HEAD)" = "$PROVA_BASE_SHA" ] || { echo "prova-remota: base não é o SHA anunciado" >&2; exit 2; }
[ "$(git -C "$head" rev-parse HEAD)" = "$PROVA_HEAD_SHA" ] || { echo "prova-remota: head não é o SHA anunciado" >&2; exit 2; }

modulo="$base/$PASTA/prova_remota.py"
config="$base/$PASTA/config.json"
for f in "$modulo" "$config"; do
  if [ -L "$f" ] || [ ! -f "$f" ]; then
    echo "prova-remota: $f ausente ou symlink na base" >&2
    exit 2
  fi
done
git -C "$base" diff --quiet HEAD -- "$PASTA" || {
  echo "prova-remota: $PASTA diverge do commit da base" >&2
  exit 2
}

# O token não entra em nada daqui para frente.
unset GITHUB_TOKEN GH_TOKEN ACTIONS_RUNTIME_TOKEN ACTIONS_ID_TOKEN_REQUEST_TOKEN ACTIONS_ID_TOKEN_REQUEST_URL

git -C "$head" cat-file -e "${PROVA_BASE_SHA}^{commit}" 2>/dev/null || {
  echo "prova-remota: o checkout do head não tem a base; sem lista de arquivos não há prova" >&2
  exit 2
}
classe=$(git -C "$head" diff --name-only -z --no-renames "${PROVA_BASE_SHA}...${PROVA_HEAD_SHA}" \
  | python3 "$modulo" classificar "$config")
echo "$classe" | python3 -c 'import json,sys
d = json.load(sys.stdin)
print("arquivos do PR:", len(d["arquivos"]))
for m in d["motivos"]:
    print("  -", m)'
if ! echo "$classe" | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin)["verde"] else 1)'; then
  echo "prova-remota: precisa da prova no Mac (o Linux não testa o app nem altera a própria prova)."
  exit 1
fi

docker run --rm --network none --read-only --tmpfs /tmp:rw,size=256m \
  --cap-drop ALL --security-opt no-new-privileges --pids-limit 512 --memory 2g \
  -e HOME=/tmp -e PYTHONDONTWRITEBYTECODE=1 -e PYTHONNOUSERSITE=1 \
  -v "$head":/src:ro -v "$modulo":/prova/prova_remota.py:ro -w /src \
  "$IMAGEM" python /prova/prova_remota.py executar "$classe"
