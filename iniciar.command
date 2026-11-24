#!/bin/bash
# Abre el tablero de «Dónde pongo mi negocio». En la Mac: doble clic.
#   ./iniciar.command            tablero local en http://127.0.0.1:8501
#   ./iniciar.command --red      también desde otras computadoras de tu red (cualquiera en tu Wi-Fi puede abrirlo)
#   ./iniciar.command --revisar  revisión sin preguntas: uv sync, pruebas de la API, arranca en el 8599, pide / y /api/geo/agebs y sale 0 (ok) o 1
cd "$(dirname "$0")" || exit 1
RED=0; REVISAR=0
for a in "$@"; do
  case "$a" in --red) RED=1 ;; --revisar) REVISAR=1 ;; *) echo "Opción desconocida: $a (usa --red o --revisar)"; exit 2 ;; esac
done
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

pregunta() {  # pregunta "texto": en --revisar siempre responde que no
  [ "$REVISAR" = 1 ] && return 1
  printf "%s [s/n] " "$1"; read -r r; [ "$r" = "s" ] || [ "$r" = "S" ]
}

# 1) uv
if ! command -v uv >/dev/null 2>&1; then
  echo "Falta uv, el gestor de Python que usa este proyecto (https://docs.astral.sh/uv/)."
  if pregunta "¿Lo instalo ahora con el instalador oficial (curl -LsSf https://astral.sh/uv/install.sh | sh)?"; then
    curl -LsSf https://astral.sh/uv/install.sh | sh || { echo "No pude instalar uv."; exit 1; }
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  else
    echo "Sin uv no puedo seguir. Instálalo desde https://docs.astral.sh/uv/ y vuelve a abrir este archivo."
    [ "$REVISAR" = 1 ] || read -r -p "Enter para cerrar" _
    exit 1
  fi
fi

# 2) ambiente de Python
uv sync || { echo "uv sync falló."; exit 1; }

# 3) Ollama (opcional: sin él, el tablero funciona en modo sin LLM; solo el chat necesita el modelo)
if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama no está instalado: el tablero funciona en modo sin LLM (mapas, fichas, comparador y datos). Para el chat, instálalo desde https://ollama.com y vuelve a abrir esto."
else
  if ! curl -s --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama está instalado pero apagado. Ábrelo (la app de Ollama) si quieres usar el chat; si no, el tablero sigue en modo sin LLM."
  else
    faltan=""
    for m in qwen3:8b nomic-embed-text; do ollama list 2>/dev/null | awk '{print $1}' | grep -q "^$m" || faltan="$faltan $m"; done
    if [ -n "$faltan" ]; then
      echo "Faltan modelos de Ollama:$faltan (qwen3:8b pesa unos 5 GB)."
      if pregunta "¿Los descargo ahora con ollama pull?"; then for m in $faltan; do ollama pull "$m"; done; else echo "Sigo sin ellos: el chat no va a funcionar."; fi
    fi
  fi
fi

# 4) modo revisión, sin interacción
if [ "$REVISAR" = 1 ]; then
  PUERTO=8599; LOG="${TMPDIR:-/tmp}/tablero-revisar.log"; PID=""
  limpiar() { [ -n "$PID" ] && { pkill -P "$PID" 2>/dev/null; kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null; }; lsof -ti "tcp:$PUERTO" 2>/dev/null | xargs kill 2>/dev/null; true; }
  trap limpiar EXIT
  echo "== pruebas de la API"; uv run pytest -q tests/test_api*.py || { echo "REVISAR: fallaron las pruebas"; exit 1; }
  echo "== arrancando en el puerto $PUERTO"
  nohup uv run python -m app.servidor --puerto "$PUERTO" --sin-navegador > "$LOG" 2>&1 &
  PID=$!
  ok=0
  for _ in $(seq 1 60); do
    curl -sf "http://127.0.0.1:$PUERTO/api/estado" >/dev/null 2>&1 && { ok=1; break; }
    kill -0 "$PID" 2>/dev/null || break
    sleep 1
  done
  [ "$ok" = 1 ] || { echo "REVISAR: /api/estado no respondió en 60 s (log: $LOG)"; exit 1; }
  curl -sf "http://127.0.0.1:$PUERTO/" | grep -qi "<div id=\"root\"" || { echo "REVISAR: / no sirvió la app (¿falta web/dist?)"; exit 1; }
  bytes=$(curl -sf -H 'Accept-Encoding: gzip' "http://127.0.0.1:$PUERTO/api/geo/agebs" | wc -c | tr -d ' ')
  [ "${bytes:-0}" -gt 100000 ] || { echo "REVISAR: /api/geo/agebs vino vacío ($bytes bytes)"; exit 1; }
  echo "REVISAR: todo bien (/api/estado, /, /api/geo/agebs = $bytes bytes comprimidos)"; exit 0
fi

# 5) arrancar
ARGS=""; [ "$RED" = 1 ] && ARGS="--red"
echo "Arrancando el tablero (Ctrl+C para apagarlo)…"
uv run python -m app.servidor $ARGS
