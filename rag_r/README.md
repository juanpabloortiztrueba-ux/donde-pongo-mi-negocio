# RAG local en R

Esta carpeta adapta al proyecto la guía «RAG local en R» del profesor. Un script de R lee los fragmentos de `carpetas/`, los convierte en embeddings con Ollama (`embeddinggemma`), recupera los 3 más parecidos a cada pregunta y se los pasa a `qwen3:1.7b`, que contesta citando los IDs o diciendo «No hay evidencia suficiente en los fragmentos». Es aparte del agente de Python: no lo toca ni lo usa.

Se entrega como script de R (la guía permite script o R Markdown). Solo R base y `httr2`.

## Requisitos

1. Ollama abierto en la misma computadora (`http://127.0.0.1:11434`).
2. Los dos modelos descargados y en la lista:
   ```
   ollama pull embeddinggemma
   ollama pull qwen3:1.7b
   ollama list
   ```
3. `httr2`, una vez, en la consola de R:
   ```r
   install.packages("httr2")
   ```

## Cómo correrlo

Desde la raíz del repo, en este orden:

```
Rscript rag_r/00_corpus.R     # arma rag_r/corpus.csv (menos de 1 segundo)
Rscript rag_r/rag_local.R     # índice, preguntas, prueba controlada y tablas (~2 min la primera vez)
```

La primera corrida construye el índice (933 fragmentos, ~1.5 min) y lo guarda en `rag_r/indice.rds`. Las siguientes lo cargan y tardan menos. El índice se reconstruye solo si cambia el corpus o el modelo de embeddings.

## Qué hay en cada archivo

| Archivo | Qué es |
|---|---|
| `00_corpus.R` | Lee los 92 `.md` de `carpetas/` (todos menos `carpetas/README.md`), los corta por secciones (`##`, y `###` dentro de ellas) y párrafos, y escribe `corpus.csv`. |
| `corpus.csv` | UTF-8, columnas `id`, `fuente`, `texto`. 933 fragmentos de 32 a 257 palabras (mediana 144). |
| `rag_local.R` | La plantilla del profesor adaptada al proyecto. |
| `preguntas.csv` | Las 8 preguntas: `id`, `pregunta`, `tipo` (`con_evidencia` o `sin_evidencia`). |
| `lectura_evaluacion.csv` | Lectura humana de cada respuesta (ver más abajo). La llena quien lee los fragmentos; el script solo la lee, nunca la sobrescribe. |
| `indice.rds` | Índice de embeddings, con el modelo y los `id` y textos con los que se hizo. No va en Git. |
| `salidas/recuperados.csv` | Por pregunta, los 3 fragmentos recuperados: `id_pregunta`, `pregunta`, `lugar`, `id`, `fuente`, `similitud`. |
| `salidas/respuestas.csv` | Por pregunta: `ids_recuperados` y la respuesta real del modelo. |
| `salidas/prueba_controlada.txt` | Pregunta, ID de la evidencia, IDs y texto de los distractores, y las respuestas con y sin evidencia. |
| `salidas/salida_completa.txt` | Todo lo que imprime la corrida, con el texto de cada fragmento recuperado. |
| `salidas/tabla_evaluacion.csv` | La tabla de evaluación. |

Las salidas son las de una corrida completa real; no se escriben a mano. Una corrida nueva las reemplaza.

### Cómo se arma el corpus

- Cada fragmento es una sección o parte de una sección, de 40 a 200 palabras más o menos. Las secciones muy cortas se pegan a la vecina y las muy largas se parten por párrafos; las tablas de las fichas municipales quedan como texto (si una tabla se parte, cada parte repite el encabezado).
- `id` tiene el formato de la guía: `D` + número de documento (en orden alfabético de ruta) y `F` + número de fragmento dentro del documento, por ejemplo `D11-F10`.
- `fuente` es la ruta del archivo y la sección, para volver al pasaje original: `carpetas/03_municipios/09003_coyoacan.md › Gasto potencial en comida fuera del hogar + Fuentes de esta ficha`. Si dos secciones cortas se pegaron, aparecen unidas con `+`.
- `texto` empieza con el título del documento y la sección, para que cada fragmento se entienda solo (por ejemplo, para saber de qué municipio es una tabla).

## Las 8 preguntas son provisionales

La guía pide «las ocho de la guía general», que todavía no tenemos. Las de `preguntas.csv` son provisionales: mezclan metodología (nivel socioeconómico, DENUE), teoría (Huff), validación del modelo, alcance y un dato de una ficha municipal, y dos no tienen evidencia en ninguna carpeta (salario mínimo y pasajeros de la Línea 7 del Metro; se comprobó con búsqueda de texto que el corpus no los trae). Para cambiarlas, edita `preguntas.csv` (mismas columnas, 8 filas), actualiza los `id` en `lectura_evaluacion.csv` y vuelve a correr `rag_local.R`.

## Prueba controlada

Está al final de la sección 3 de `rag_local.R`. Pregunta: «¿Cuál es el gasto potencial total en comida fuera del hogar de Coyoacán por trimestre?». La evidencia es `D11-F10` y el dato clave es `2,120.2` (millones de pesos). Los distractores son los dos fragmentos más parecidos que no son la evidencia y que no contienen el dato clave (se filtran con `grepl`); resultaron ser el mismo apartado de otros dos municipios, sin la cifra de Coyoacán. El script se detiene si el dato clave no está en el texto de la evidencia, y la salida dice si cada respuesta lo menciona.

Primero se usó otra pregunta (hogares de Coyoacán, dato `191,517`), pero `qwen3:1.7b` contestó «156» porque confundió el número de AGEB con el de hogares, ya con la evidencia a la vista. Se cambió por la de gasto potencial, que tiene una etiqueta más clara. Es una limitación del modelo chico que conviene decir al presentar.

## Cómo se arma la tabla de evaluación

`salidas/tabla_evaluacion.csv` tiene una fila por pregunta y dos grupos de columnas.

Automáticas (las calcula el script):

- `ids_recuperados`: los 3 IDs que entregó la búsqueda.
- `similitud_maxima`: la similitud coseno del primero. Sirve para ordenar candidatos, no para decidir si hay evidencia.
- `cita_id`: si la respuesta cita algún ID entre corchetes.
- `ids_citados` y `cita_ids_no_recuperados`: los IDs que escribió el modelo y si alguno no estaba entre los recuperados (el modelo chico a veces inventa uno).
- `dice_no_hay_evidencia`: si la respuesta trae la frase exacta «No hay evidencia suficiente en los fragmentos».

De lectura humana (las llena quien lee los fragmentos y la respuesta):

- `contiene_evidencia`: si los fragmentos recuperados traen el dato que responde la pregunta.
- `respuesta_correcta`: si la respuesta es correcta y se apoya en esos fragmentos.
- `comentario`: lo que haga falta aclarar.

Esas tres columnas se escriben en `lectura_evaluacion.csv` (una fila por `id_pregunta`) y el script las copia a la tabla. Así una corrida nueva no borra lo que el equipo ya leyó. Ya están llenas con la lectura del 2026-11-27 de los 3 fragmentos de cada pregunta; si cambian las preguntas o las respuestas, hay que volver a leerlas.

## Decisión sobre el razonamiento de qwen3

Se probó una llamada real a `/api/chat` con `qwen3:1.7b` (Ollama 0.40.17), con y sin `think = FALSE`. En los dos casos `message$content` sale limpio, sin bloque `<think>`: el razonamiento, cuando lo hay, llega aparte en `message$thinking`, que el script no usa. Por eso no se agregó `think = FALSE` ni se quita ningún bloque, y la llamada queda igual que la de la guía.

## Dónde se cumple cada punto de la guía

| Punto de la guía | Dónde |
|---|---|
| Ollama abierto; `ollama pull embeddinggemma` y `qwen3:1.7b`; `ollama list` | Requisitos de este README. `rag_local.R` línea 18 imprime la versión de Ollama y falla si no responde. |
| Instalar `httr2` | Requisitos de este README. Se usa como `httr2::` en `rag_local.R` líneas 12 a 17. |
| Script de R o R Markdown | Script de R: `rag_local.R` (en esta Mac no hay pandoc para renderizar R Markdown). |
| 1. Conexión: `base`, `modelo_chat`, `modelo_embedding`, función `ollama`, `/api/version` | `rag_local.R` líneas 9 a 18. |
| 1. Corpus con `id`, `fuente`, `texto`; `stopifnot` | Lectura de `corpus.csv` y `stopifnot` en líneas 19 y 20. El CSV se arma en `00_corpus.R`. |
| 2. `embeddings()` con `/api/embed` | Líneas 22 a 31 (los textos se mandan por lotes de 32). |
| 2. `indice <- embeddings(corpus$texto)` | Líneas 32 a 43; se guarda en `indice.rds` y se reconstruye si cambia el corpus o el modelo. |
| 2. `recuperar()` con similitud coseno y `k = 3` | Líneas 44 a 53. |
| 3. `responder()` con el prompt de sistema de la guía y `temperature = 0` | Líneas 55 a 68. |
| 3. Ciclo de preguntas: imprime fragmentos y respuesta | Líneas 69 a 89. |
| 3. Prueba controlada con y sin evidencia | Líneas 93 a 117; resultado en `salidas/prueba_controlada.txt`. |
| 4. Corpus propio con columnas `id`, `fuente`, `texto`, IDs únicos y fuente que permite volver al pasaje | `00_corpus.R`; `stopifnot(!anyDuplicated(...))` en ambos scripts. |
| 4. Reconstruir el índice si cambia el corpus o el modelo | `rag_local.R` líneas 32 a 43. |
| 4. Las similitudes ordenan; hay que leer los fragmentos | `salidas/salida_completa.txt` imprime el texto de cada fragmento; `lectura_evaluacion.csv` queda para esa lectura. |
| 4. Reemplazar las dos preguntas por las ocho de la guía general | `preguntas.csv` (provisionales, ver arriba). |
| 4. Prueba controlada con el ID de la evidencia propia y ningún distractor que revele el dato | Líneas 94 a 102 (filtro `grepl` sobre el dato clave); distractores impresos en `prueba_controlada.txt`. |
| 4. Guardar IDs, salidas reales y tabla de evaluación | Carpeta `salidas/` (líneas 90, 91, 117 y 137 de `rag_local.R`). |
