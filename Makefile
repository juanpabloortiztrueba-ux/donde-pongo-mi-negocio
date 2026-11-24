# Donde pongo mi negocio — tareas. En Windows sin make, corre los comandos de cada regla (ver README).
PY := uv run python
PESADO := OMP_NUM_THREADS=6 nice -n 10

.PHONY: setup datos features entrenar carpetas indexar app tablero tablero-red web evaluar pruebas todo

setup:            ## ambiente de Python y modelos locales (~6 GB de Ollama)
	uv sync
	ollama pull qwen3:8b
	ollama pull nomic-embed-text

datos:            ## descarga y limpia INEGI, CONAPO, ENIGH, Banxico y transporte (~20 min, ~1 GB de descarga)
	$(PY) scripts/01a_censo_marco.py
	$(PY) scripts/01b_denue.py
	$(PY) scripts/01c_enigh_macro.py
	$(PY) scripts/01d_macro_series.py
	$(PY) scripts/01c_transporte.py
	$(PY) scripts/validar_giros.py --md reports/validacion_giros.md

features:         ## variables por AGEB (~5 s)
	$(PY) scripts/02_features.py

entrenar:         ## modelo de aperturas y scores (~5 min)
	$(PESADO) $(PY) scripts/03_entrenar.py

carpetas:         ## documentos de carpetas/ que salen del codigo (~20 s, sin Ollama)
	$(PY) scripts/04a_carpetas.py

indexar:          ## carpetas + embeddings con nomic-embed-text (~1 min; necesita Ollama)
	$(PY) scripts/04_indexar.py

app:              ## interfaz vieja de Streamlit (respaldo) en http://localhost:8501 (abrela en el navegador)
	uv run streamlit run app/ui.py

tablero:          ## tablero web en http://127.0.0.1:8501 (abre el navegador)
	uv run python -m app.servidor

tablero-red:      ## tablero web visible en tu red local (cualquiera en tu Wi-Fi puede abrirlo)
	uv run python -m app.servidor --red

web:              ## reconstruye web/dist (necesita Node 20+; solo hace falta si cambias web/src)
	cd web && npm ci && npm run build

evaluar:          ## 28 preguntas al agente (~20 min; necesita Ollama) -> reports/evaluacion.md
	nice -n 10 $(PY) eval/evaluar.py --rehacer

pruebas:          ## pruebas sin LLM (~20 s)
	uv run pytest -q

todo: setup datos features entrenar indexar pruebas evaluar
