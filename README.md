# ¿Dónde pongo mi negocio?

Modelo **local** al que le dices «quiero poner una heladería» y te responde **en qué colonias de la Zona Metropolitana del Valle de México (ZMVM)** conviene, con números y fuentes reales (INEGI, DENUE, ENIGH, CONAPO, Banxico). Corre en tu computadora con [Ollama](https://ollama.com/download) y `qwen3:8b`; no manda nada a internet. Lo que no está en los datos lo dice: «NO ENCONTRADO».

Proyecto de la materia Herramientas Computacionales (Universidad Panamericana), 2026.

## Qué hace, en una línea por pieza

| Pieza | Qué hace | Archivo |
|---|---|---|
| Datos | Censo 2020 por AGEB urbana, Marco Geoestadístico, marginación CONAPO, DENUE (05/2026 y 11/2020), ENIGH 2024, macro de Banxico/INEGI, estaciones de transporte | `scripts/01*.py` → `data/processed/` |
| Variables | Población, NSE estimado, negocios por sector, transporte, gasto potencial por AGEB | `scripts/02_features.py`, `app/motor.py` |
| Modelo | Probabilidad de que aparezca un negocio del giro en cada AGEB (HistGradientBoosting, validación espacial por municipio) + score 0-100 con pesos aprendidos y validado contra crecimiento neto, sobrevivencia y altas | `scripts/03_entrenar.py`, `scripts/03b_validar_score.py`, `reports/validacion.md`, `reports/validacion_score.md` |
| Carpetas (RAG) | Metodología, una ficha por municipio, teoría de localización, explicación del modelo | `carpetas/`, `scripts/04_indexar.py`, `app/rag.py` |
| Agente | `qwen3:8b` con herramientas en Python puro (sin LLM, probadas). Entiende colonias (`app/lugares.py`) y preguntas de seguimiento; el código arma los datos y el LLM solo escribe la «Lectura», que `app/lectura.py` revisa contra los datos | `app/herramientas.py`, `app/agente.py`, `app/lugares.py`, `app/lectura.py` |
| Interfaz | Tablero web (mapa, chat, fichas, comparador, macro, modelo) y, de respaldo, chat con mapa en Streamlit | `app/servidor.py` + `web/`; `app/ui.py` |
| Evaluación | 31 preguntas con checks automáticos (colonias, seguimientos, trampa fuera de alcance, preguntas fuera de tema) | `eval/`, `reports/evaluacion.md` |

La ZMVM son 76 municipios (16 alcaldías, 59 del Estado de México y Tizayuca), según la delimitación SEDATU-CONAPO-INEGI 2015 (`data/processed/zmvm_municipios.csv`).

## Requisitos

- **Computadora**: 16 GB de RAM recomendados (el modelo ocupa ~6 GB en memoria). Probado en MacBook Air M4 de 16 GB. En Windows sirve una PC con 16 GB; con GPU NVIDIA es más rápido, sin GPU funciona pero tarda más.
- **Espacio**: ~6 GB para los modelos de Ollama (`qwen3:8b` 5.2 GB, `nomic-embed-text` 0.3 GB) + ~1 GB para el repo y el ambiente de Python (`.venv` ~0.7 GB, datos procesados ~0.1 GB). Si vuelves a descargar los datos, ~1.5 GB temporales más (los zip se borran solos).
- **Programas**: [uv](https://docs.astral.sh/uv/getting-started/installation/) (maneja Python 3.12 y las librerías), [Ollama](https://ollama.com/download) y git. En Windows, [Git para Windows](https://git-scm.com/download/win).

## Ruta rápida (≈10 min): usar los datos que ya vienen en el repo

El repo trae `data/processed/`, `data/index/` y `models/`, así que no hace falta descargar nada de INEGI.

### Mac

```bash
git clone https://github.com/juanpabloortiztrueba-ux/donde-pongo-mi-negocio.git donde-pongo-mi-negocio
cd donde-pongo-mi-negocio
make setup        # uv sync + ollama pull qwen3:8b + ollama pull nomic-embed-text  (~5-10 min, casi todo es la descarga de 5.5 GB)
make tablero      # levanta el tablero web; abre http://127.0.0.1:8501 (make app = la interfaz vieja de Streamlit, respaldo)
```

Si no tienes `make`: `xcode-select --install`, o corre los comandos de la tabla de abajo.

### Windows (PowerShell)

```powershell
# 1. Instala uv y Ollama
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
#    Ollama: descarga el instalador de https://ollama.com/download y ábrelo (queda corriendo en la bandeja)

# 2. Clona y prepara
git clone https://github.com/juanpabloortiztrueba-ux/donde-pongo-mi-negocio.git donde-pongo-mi-negocio
cd donde-pongo-mi-negocio
uv sync
ollama pull qwen3:8b
ollama pull nomic-embed-text

# 3. Abre el tablero (o doble clic en iniciar.bat); queda en http://127.0.0.1:8501
.\iniciar.bat
#    Respaldo, la interfaz vieja de Streamlit: uv run streamlit run app/ui.py
```

`iniciar.bat` se escribió para Windows, pero solo se ha probado en Mac. Si algo falla, los mismos pasos a mano están en la tabla de abajo, columna «Windows / sin make».

### Primer uso

Escribe en el chat, por ejemplo: «quiero poner una heladería», «una farmacia en Iztapalapa», «una cafetería en la Roma», «¿y en Coyoacán?» (hereda el giro), «algo barato para una zona de nivel bajo» o «¿cómo está la inflación?». Cada respuesta tarda **unos 30 a 75 s** en una MacBook Air M4 de 16 GB (mediana 39.8 s, p90 61.4 s y máxima 73.7 s en la evaluación de 31 preguntas del 2026-11-24, `reports/evaluacion.md`; con la Mac muy cargada puede tardar más). Mientras el modelo está cargado usa ~6 GB de memoria; si la Mac anda justa, cierra otras apps (en esa evaluación el swap subió de 4.9 a ~12.3 GB y volvió a 5.0 GB al descargar el modelo con `ollama stop qwen3:8b`). Si preguntas algo que no es de negocios («¿cómo me llamo?», «hola», deportes), contesta al instante con un texto fijo que dice para qué sirve, sin usar el modelo. Si Ollama no está corriendo, la app responde con una plantilla armada directo de los datos (sin LLM) y lo avisa. En el tablero, el mapa pinta el score de la última recomendación sobre fondo liso (sin internet); el mapa base de OpenStreetMap es opcional. En la interfaz de Streamlit el mapa de la derecha cambia al giro y filtros de la última recomendación; ahí el mapa interactivo usa internet para el fondo y, sin internet, se activa «Mapa estático».

Para comprobar que todo funciona sin esperar la evaluación completa, corre 3 preguntas del evaluador (heladería, un negocio en Coyoacán y la trampa de Monterrey; ~5 min, necesita Ollama): `uv run python eval/evaluar.py --rehacer --ids 1,17,20`. El resumen final dirá «3/3 pasan; trampa ok» y `aprobado=False`: es normal, «aprobado» exige el 90 % de las 31 preguntas, la trampa, las tres fuera de tema y todas las de colonia y seguimiento. (Sin `--rehacer` solo recalifica las respuestas guardadas en el repo, sin llamar al modelo.)

Desde la terminal, sin interfaz:

```bash
uv run python app/agente.py "quiero poner una cafetería en Coyoacán"
```

## Ruta completa: reconstruir todo desde las fuentes

Necesitas tokens gratuitos. Copia la plantilla (`cp .env.example .env`; en Windows `copy .env.example .env`) y llénala. El `.env` está en `.gitignore`: **no** se sube a git. La ruta rápida (arriba) no necesita tokens.

```
DENUE_TOKEN=...     # https://www.inegi.org.mx/servicios/api_denue.html (solo para verificar conteos)
BANXICO_TOKEN=...   # https://www.banxico.org.mx/SieAPIRest/service/v1/token
INEGI_TOKEN=...     # https://www.inegi.org.mx/app/desarrolladores/generatoken/Usuarios/token_Verify
```

| Paso | Mac (`make`) | Windows / sin make | Tiempo aprox. (MacBook Air M4) |
|---|---|---|---|
| Ambiente y modelos | `make setup` | `uv sync`, `ollama pull qwen3:8b`, `ollama pull nomic-embed-text` | 5-10 min (descarga 5.5 GB) |
| Datos | `make datos` | `uv run python scripts/01a_censo_marco.py`, luego `01b_denue.py`, `01c_enigh_macro.py`, `01c_transporte.py`, `validar_giros.py --md reports/validacion_giros.md` | ~20 min (descarga ~1 GB; Censo y Marco ~5 min, DENUE ~10 min, ENIGH/macro/transporte ~2 min) |
| Variables | `make features` | `uv run python scripts/02_features.py` | ~5 s |
| Modelo y score | `make entrenar` | `$env:OMP_NUM_THREADS=6; uv run python scripts/03_entrenar.py` (al final encadena `03b_validar_score.py` y regenera los scores) | unos minutos más que el modelo solo (~5 min) |
| Carpetas + índice | `make indexar` | `uv run python scripts/04_indexar.py` | ~1 min (Ollama encendido) |
| Pruebas | `make pruebas` | `uv run pytest -q` | ~20 s (sin `.env` una prueba, la de tokens, sale «skipped»: es normal) |
| Evaluación | `make evaluar` | `uv run python eval/evaluar.py --rehacer` | ~20 min (31 preguntas; necesita Ollama) |
| Preguntas del tablero | `make historial` | `uv run python scripts/historial.py` | segundos |
| Tablero | `make tablero` | `uv run python -m app.servidor` | segundos |
| App de respaldo (Streamlit) | `make app` | `uv run streamlit run app/ui.py` | segundos |
| Todo | `make todo` | los pasos anteriores en orden | ~1 h |

`make historial` muestra las últimas 20 preguntas que llegaron al tablero (fecha, modo, latencia, pregunta y primeras líneas de la respuesta); `make historial ARGS="--todas"` las muestra todas.
El servidor las guarda en `data/historial/preguntas.jsonl` (solo en tu Mac, fuera de git, sin tokens); no registra las del evaluador ni las de las pruebas.

Para regenerar solo el score (por ejemplo, si cambian los datos): `OMP_NUM_THREADS=6 nice -n 10 uv run python scripts/03b_validar_score.py` y luego `uv run python scripts/03_entrenar.py --solo-scores`. El `03_entrenar.py` completo ya encadena ambos.

Los scripts son idempotentes: si un archivo ya existe y está bien, no se vuelve a bajar. Cada descarga queda registrada en `data/FUENTES.md` con URL, fecha y sha256. Si el servidor del INEGI se cuelga, vuelve a correr el paso: retoma.

## Tablero

Además de la interfaz de Streamlit (`make app`, queda como respaldo), el proyecto trae un **tablero web**: un mapa del score por AGEB, chat con el agente, fichas de colonia, comparador de giros, contexto macro y una vista del modelo y los datos. Está hecho con React (estilo «stageshow» en modo plano) y lo sirve FastAPI. El build ya viene en `web/dist`: **no hace falta Node**.

```bash
make tablero                          # http://127.0.0.1:8501 (abre el navegador)
uv run python -m app.servidor         # lo mismo; opciones: --puerto 8501 --red --web <carpeta> --sin-navegador
```

- Sin internet funciona todo (mapas con fondo liso, letra y librerías empaquetadas). El mapa base de OpenStreetMap es opcional y solo aparece si hay internet.
- Sin Ollama funcionan el mapa, las fichas, el comparador, el macro y los datos; solo el chat necesita `qwen3:8b`. El tablero muestra a la vista si Ollama e internet están disponibles.
- Para tocar la interfaz (`web/src`): `make web` (necesita Node 20+) reconstruye `web/dist`; para desarrollar, `cd web && API_PUERTO=8501 VITE_PUERTO=5173 npx vite`.
- Pruebas de la API: `uv run pytest -q tests/test_api_base.py tests/test_api_preguntar.py tests/test_api_explorar.py tests/test_api_contexto.py`.

## Usarlo desde otra computadora

1. **En la misma red Wi-Fi.** En tu Mac: `make tablero-red` (o `./iniciar.command --red`). La terminal imprime una dirección tipo `http://192.168.x.x:8501`; ábrela en la otra computadora o en el celular. **Ojo: cualquiera conectado a esa misma red puede abrirla** y usar el modelo local. Se apaga con Ctrl+C. Si la Mac tiene el firewall prendido, acepta el aviso de «permitir conexiones entrantes».
2. **Clonando el repositorio.** En otra computadora solo se necesita **uv**:
   - Mac: doble clic en `iniciar.command` (la primera vez, clic derecho → Abrir). Windows: doble clic en `iniciar.bat`.
   - Si falta uv, el lanzador lo explica y lo instala con el instalador oficial solo si contestas `s`. Después corre `uv sync` y abre el tablero.
   - **Ollama es opcional**: sin él, todo funciona menos el chat. Para el chat, instala Ollama desde https://ollama.com y deja que el lanzador ofrezca `ollama pull qwen3:8b` y `nomic-embed-text` (≈ 6 GB).
   - Para comprobar que quedó bien sin abrir nada: `./iniciar.command --revisar` (Windows: `iniciar.bat --revisar`); termina con código 0 si todo respondió.
3. **Por internet, con un túnel** (Cloudflare Tunnel o similar). Existe y serviría para enseñarlo fuera de tu red, pero **no está configurado**: lo decide Juan Pablo. Quien abra el túnel expone el tablero y el modelo local a cualquiera que tenga el enlace.

## Cómo decide (resumen)

Para cada giro (40 en `config/giros.yaml`) y cada AGEB urbana (5,875):

`score = 100 · [0.35 · aperturas esperadas por competidor + 0.05 · gasto potencial × captura Huff + 0.20 · población objetivo × ajuste a NSE × captura + 0.10 · flujo de gente + 0.30 · negocios complementarios]`, con cada término en percentil dentro de la ZMVM **para ese giro** (versión `3.0-nucleo-aprendido`).

- **Los pesos no los puso el autor**: se aprendieron fuera de muestra por municipio, no negativos y sumando 1 (redondeados a 0.05, con un piso de 0.25 para gasto + población, porque la teoría de localización dice que la demanda importa), contra tres objetivos: crecimiento neto, sobrevivencia y altas fuera de la carga censal (`models/pesos_score.json`, `reports/validacion_score.md`). El reporte incluye la sensibilidad con objetivos limpios y el objetivo «crecimiento neto sin carga censal».
- **Todo se mide en el mismo círculo** (el radio de influencia del giro) alrededor del sitio, repartiendo la población, el gasto y la intensidad de aperturas de cada AGEB en una malla de 100 m dentro de su polígono. Así una AGEB enorme no gana sólo por tener más gente (ver «Sesgo por tamaño de AGEB» en `reports/validacion.md`).
- **Flujo de gente**: no hay aforos peatonales abiertos; se usan el empleo del DENUE en el radio, los negocios de corredor comercial (SCIAN 46, 72 y 81) y el Metro y estaciones a 1 km.
- **El score es relativo dentro de cada giro**: ordena colonias para un giro, no dice si el giro es viable ni compara giros. Para «¿qué negocio pongo?», `sugerir_giros` ordena por probabilidad absoluta de apertura × probabilidad de seguir abierto.

- **Aperturas esperadas por competidor** (primer término): la probabilidad de apertura del modelo, convertida a aperturas esperadas en el círculo y dividida entre la competencia (captura Huff). La probabilidad en sí: modelo entrenado con lo que apareció en el DENUE entre 11/2020 y 05/2026, validado dejando municipios completos fuera (AUC global 0.89; ver `reports/validacion.md`).
- **Gasto potencial**: hogares de la AGEB × gasto trimestral del rubro ENIGH 2024 según su decil de ingreso **estimado** (`reports/decil_imputado.md`).
- **Captura Huff**: `1 / (1 + competidores ponderados por distancia)`.

El agente no calcula cifras: las toma de las herramientas (`app/herramientas.py`), que regresan JSON con números ya redondeados y sus fuentes.

## Pregunta de examen: ¿por qué el score no predice aperturas crudas y está bien?

Porque las aperturas se aglomeran donde ya hay competencia: en las AGEB con 3 o más negocios del giro en 2020 aparecieron 3 nuevos por cada 10 existentes y desaparecieron otros 3 (rotación). Un score de ubicación que castiga la competencia, como debe hacerlo, queda debajo de ella: AUC 0.579 contra 0.711 de la simple competencia en la AGEB. Por eso se midió contra lo que importa al decidir: en crecimiento neto el score saca ρ = 0.182 dentro de muestra y **0.159 fuera de muestra** (cifra principal), contra 0.126 de la mejor línea base y 0.046 del score anterior. Detalle en `reports/validacion.md` y `carpetas/05_modelo/preguntas_de_examen_del_score.md`.

**Salvedad que hay que decir siempre**: el score 3.0 **no se demuestra mejor** que el anterior (2.1). Su ventaja en crecimiento neto viene de la carga de los Censos Económicos 2024 (90.5 % de los «nuevos» entre las AGEB elegibles). En los objetivos limpios empata o pierde: neto sin carga censal 0.037 contra 0.055, altas fuera de la carga 0.046 contra 0.108, sobrevivencia 0.022 contra 0.028. Se conserva por decisión de diseño, no como victoria empírica.

## Límites (léelos antes de usarlo para una decisión real)

- **La sobrevivencia de un negocio no se puede predecir con estos datos** (ρ ≤ 0.08 dentro de un giro).
- **El score no gana** en altas fuera de la carga censal ni en crecimiento neto por habitante.
- El 93 % de los «nuevos» del DENUE 2026 es carga de los Censos Económicos 2024: «apareció» no es «abrió» y «desapareció» no es «cerró».
- La banda de NSE imputada (bajo, medio, alto) acierta 57.7 % de los hogares (bajo 59 %, medio 70 %, alto 29 %: el alto se subdetecta); el decil exacto, 17.9 %, y ±1 decil, 50.4 %.
- «Barato» se interpreta como poca inversión, y no hay dato de inversión por giro (NO ENCONTRADO): se aproxima con el establecimiento típico más chico del DENUE (`criterio_inversion`). La edad clave por giro y las alertas de colonia son criterio del proyecto, no dato medido. El INPC de alimentos es NO ENCONTRADO (`macro.json` guarda la evidencia de la búsqueda).
- La «Lectura» del LLM se revisa en código (`app/lectura.py`): se quitan las frases con superlativos falsos o con una zona de fuera «en» la colonia pedida. Una colonia inventada que empieza como una real se avisa («NO ENCONTRADO… se usó la más parecida»).
- «Apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos.
- El NSE, el decil y el ingreso por colonia son **estimaciones**: la ENIGH no es representativa por municipio ni por colonia.
- «Colonia» = el asentamiento más frecuente del DENUE dentro de la AGEB, no un límite oficial de colonia.
- Tickets promedio, radios de influencia y clientes objetivo de cada giro son supuestos del autor (`config/giros.yaml`).
- Los datos del Censo son de 2020. No hay rentas de locales, tráfico peatonal ni seguridad.
- Solo la ZMVM. Fuera de ella (Monterrey, Guadalajara...) el agente dice que está fuera de alcance.

## RAG local en R

La carpeta `rag_r/` adapta al proyecto la guía «RAG local en R» del profesor: un script de R (`httr2`) que busca en `carpetas/` con `embeddinggemma` y responde con `qwen3:1.7b`, citando los IDs de los fragmentos. Es independiente del agente de Python.
Requiere `ollama pull embeddinggemma`, `ollama pull qwen3:1.7b` y `install.packages("httr2")`. Se corre con `Rscript rag_r/00_corpus.R` y `Rscript rag_r/rag_local.R`, desde la raíz del repo.
Las preguntas, las salidas reales y la tabla de evaluación quedan en `rag_r/`; el detalle y dónde se cumple cada punto de la guía están en [`rag_r/README.md`](rag_r/README.md).

## Estructura

```
app/            motor.py (conteos, score), rag.py (búsqueda en carpetas), herramientas.py, agente.py, ui.py (Streamlit, respaldo),
                servidor.py + api/ (tablero web: FastAPI)
web/            tablero web (React + Vite + TypeScript); web/dist es el build versionado; web/src/kit = stageshow (MIT)
iniciar.command / iniciar.bat   doble clic para abrir el tablero (Mac / Windows)
carpetas/       documentos que consulta el agente (Markdown)
config/         giros.yaml (40 giros: SCIAN, sinónimos, supuestos)
data/processed  tablas limpias (parquet/csv/json);  data/index: embeddings
data/raw        descargas (no va en git)
docs/           CONTRATO.md (qué produce cada etapa) y BITACORA.md (qué se hizo y por qué)
eval/           preguntas.yaml y evaluar.py
models/         modelo entrenado, métricas y scores
reports/        validación del modelo, decil imputado, giros y evaluación del agente
scripts/        01 datos → 02 variables → 03 modelo → 04 índice
tests/          pruebas sin LLM (uv run pytest -q)
```

## Fuentes

INEGI (Censo de Población y Vivienda 2020, Marco Geoestadístico 2020, DENUE, ENIGH 2024, SCIAN 2023, Banco de Indicadores), CONAPO (Índice de marginación urbana 2020; delimitación de zonas metropolitanas), Banco de México (SIE), Datos Abiertos CDMX (Metro, Metrobús, STE, GTFS) y OpenStreetMap (Mexibús y Mexicable). URL, fechas y sha256 de cada archivo en [`data/FUENTES.md`](data/FUENTES.md).
