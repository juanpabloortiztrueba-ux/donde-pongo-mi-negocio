# ¿Dónde pongo mi negocio?

Modelo **local** al que le dices «quiero poner una heladería» y te responde **en qué colonias de la Zona Metropolitana del Valle de México (ZMVM)** conviene, con números y fuentes reales (INEGI, DENUE, ENIGH, CONAPO, Banxico). Corre en tu computadora con [Ollama](https://ollama.com/download) y `qwen3:8b`; no manda nada a internet. Lo que no está en los datos lo dice: «NO ENCONTRADO».

Proyecto de la materia Herramientas Computacionales (Universidad Panamericana), 2026.

## Qué hace, en una línea por pieza

| Pieza | Qué hace | Archivo |
|---|---|---|
| Datos | Censo 2020 por AGEB urbana, Marco Geoestadístico, marginación CONAPO, DENUE (05/2026 y 11/2020), ENIGH 2024, macro de Banxico/INEGI, estaciones de transporte | `scripts/01*.py` → `data/processed/` |
| Variables | Población, NSE estimado, negocios por sector, transporte, gasto potencial por AGEB | `scripts/02_features.py`, `app/motor.py` |
| Modelo | Probabilidad de que aparezca un negocio del giro en cada AGEB (HistGradientBoosting, validación espacial por municipio) + score 0-100 | `scripts/03_entrenar.py`, `reports/validacion.md` |
| Carpetas (RAG) | Metodología, una ficha por municipio, teoría de localización, explicación del modelo | `carpetas/`, `scripts/04_indexar.py`, `app/rag.py` |
| Agente | `qwen3:8b` con herramientas en Python puro (sin LLM, probadas) | `app/herramientas.py`, `app/agente.py` |
| Interfaz | Chat + mapa del score con el top 5 marcado | `app/ui.py` |
| Evaluación | 20 preguntas con checks automáticos | `eval/`, `reports/evaluacion.md` |

La ZMVM son 76 municipios (16 alcaldías, 59 del Estado de México y Tizayuca), según la delimitación SEDATU-CONAPO-INEGI 2015 (`data/processed/zmvm_municipios.csv`).

## Requisitos

- **Computadora**: 16 GB de RAM recomendados (el modelo ocupa ~6 GB en memoria). Probado en MacBook Air M4 de 16 GB. En Windows sirve una PC con 16 GB; con GPU NVIDIA es más rápido, sin GPU funciona pero tarda más.
- **Espacio**: ~6 GB para los modelos de Ollama (`qwen3:8b` 5.2 GB, `nomic-embed-text` 0.3 GB) + ~1 GB para el repo y el ambiente de Python (`.venv` ~0.7 GB, datos procesados ~0.1 GB). Si vuelves a descargar los datos, ~1.5 GB temporales más (los zip se borran solos).
- **Programas**: [uv](https://docs.astral.sh/uv/getting-started/installation/) (maneja Python 3.12 y las librerías), [Ollama](https://ollama.com/download) y git. En Windows, [Git para Windows](https://git-scm.com/download/win).

## Ruta rápida (≈10 min): usar los datos que ya vienen en el repo

El repo trae `data/processed/`, `data/index/` y `models/`, así que no hace falta descargar nada de INEGI.

### Mac

```bash
git clone <url-del-repo> donde-pongo-mi-negocio
cd donde-pongo-mi-negocio
make setup        # uv sync + ollama pull qwen3:8b + ollama pull nomic-embed-text  (~5-10 min, casi todo es la descarga de 5.5 GB)
make app          # levanta la app; abre http://localhost:8501 en tu navegador
```

Si no tienes `make`: `xcode-select --install`, o corre los comandos de la tabla de abajo.

### Windows (PowerShell)

```powershell
# 1. Instala uv y Ollama
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
#    Ollama: descarga el instalador de https://ollama.com/download y ábrelo (queda corriendo en la bandeja)

# 2. Clona y prepara
git clone <url-del-repo> donde-pongo-mi-negocio
cd donde-pongo-mi-negocio
uv sync
ollama pull qwen3:8b
ollama pull nomic-embed-text

# 3. Abre la app
uv run streamlit run app/ui.py
```

### Primer uso

Escribe en el chat, por ejemplo: «quiero poner una heladería», «una farmacia en Iztapalapa», «algo barato para una zona de nivel bajo» o «¿cómo está la inflación?». Cada respuesta tarda **~1 a 1.5 min** en una MacBook Air M4 de 16 GB (mediana 85 s en la evaluación de 20 preguntas). Mientras el modelo está cargado usa ~6 GB de memoria; si la Mac anda justa, cierra otras apps (en la evaluación el swap subió de 3.3 a ~10.9 GB y volvió a 4.7 GB al descargar el modelo con `ollama stop qwen3:8b`). Si Ollama no está corriendo, la app responde con una plantilla armada directo de los datos (sin LLM) y lo avisa. El mapa de la derecha cambia al giro y filtros de la última recomendación; también los puedes elegir en la barra lateral. El mapa interactivo usa internet para el fondo (OpenStreetMap); sin internet activa «Mapa estático» y se dibuja con los mismos datos.

Para comprobar que todo funciona sin esperar la evaluación completa, corre 3 preguntas del evaluador (heladería, un negocio en Coyoacán y la trampa de Monterrey; ~5 min, necesita Ollama): `uv run python eval/evaluar.py --rehacer --ids 1,17,20`. El resumen final dirá «3/3 pasan; trampa ok» y `aprobado=False`: es normal, «aprobado» exige las 20 preguntas. (Sin `--rehacer` solo recalifica las respuestas guardadas en el repo, sin llamar al modelo.)

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
| Modelo | `make entrenar` | `$env:OMP_NUM_THREADS=6; uv run python scripts/03_entrenar.py` | ~5 min |
| Carpetas + índice | `make indexar` | `uv run python scripts/04_indexar.py` | ~1 min (Ollama encendido) |
| Pruebas | `make pruebas` | `uv run pytest -q` | ~20 s (sin `.env` una prueba, la de tokens, sale «skipped»: es normal) |
| Evaluación | `make evaluar` | `uv run python eval/evaluar.py --rehacer` | ~20-30 min |
| App | `make app` | `uv run streamlit run app/ui.py` | segundos |
| Todo | `make todo` | los pasos anteriores en orden | ~1 h |

Los scripts son idempotentes: si un archivo ya existe y está bien, no se vuelve a bajar. Cada descarga queda registrada en `data/FUENTES.md` con URL, fecha y sha256. Si el servidor del INEGI se cuelga, vuelve a correr el paso: retoma.

## Cómo decide (resumen)

Para cada giro (40 en `config/giros.yaml`) y cada AGEB urbana (5,875):

`score = 30 % aperturas esperadas (modelo) + 25 % gasto potencial × captura Huff + 15 % población objetivo × ajuste a NSE × captura + 20 % flujo de gente + 10 % negocios complementarios`, cada término en percentil dentro de la ZMVM **para ese giro**.

- **Todo se mide en el mismo círculo** (el radio de influencia del giro) alrededor del sitio, repartiendo la población, el gasto y la intensidad de aperturas de cada AGEB en una malla de 100 m dentro de su polígono. Así una AGEB enorme no gana sólo por tener más gente (ver «Sesgo por tamaño de AGEB» en `reports/validacion.md`).
- **Flujo de gente**: no hay aforos peatonales abiertos; se usan el empleo del DENUE en el radio, los negocios de corredor comercial (SCIAN 46, 72 y 81) y el Metro y estaciones a 1 km.
- **El score es relativo dentro de cada giro**: ordena colonias para un giro, no dice si el giro es viable ni compara giros. Para «¿qué negocio pongo?», `sugerir_giros` ordena por probabilidad absoluta de apertura × probabilidad de seguir abierto.

- **Prob. de apertura**: modelo entrenado con lo que apareció en el DENUE entre 11/2020 y 05/2026, validado dejando municipios completos fuera (AUC global 0.89; ver `reports/validacion.md`).
- **Gasto potencial**: hogares de la AGEB × gasto trimestral del rubro ENIGH 2024 según su decil de ingreso **estimado** (`reports/decil_imputado.md`).
- **Captura Huff**: `1 / (1 + competidores ponderados por distancia)`.

El agente no calcula cifras: las toma de las herramientas (`app/herramientas.py`), que regresan JSON con números ya redondeados y sus fuentes.

## Límites (léelos antes de usarlo para una decisión real)

- «Apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos.
- El NSE, el decil y el ingreso por colonia son **estimaciones**: la ENIGH no es representativa por municipio ni por colonia.
- «Colonia» = el asentamiento más frecuente del DENUE dentro de la AGEB, no un límite oficial de colonia.
- Tickets promedio, radios de influencia y clientes objetivo de cada giro son supuestos del autor (`config/giros.yaml`).
- Los datos del Censo son de 2020. No hay rentas de locales, tráfico peatonal ni seguridad.
- Solo la ZMVM. Fuera de ella (Monterrey, Guadalajara...) el agente dice que está fuera de alcance.

## Estructura

```
app/            motor.py (conteos, score), rag.py (búsqueda en carpetas), herramientas.py, agente.py, ui.py
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
