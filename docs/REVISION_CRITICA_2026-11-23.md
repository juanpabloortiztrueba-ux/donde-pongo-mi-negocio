# Revisión crítica del 2026-11-23

Hallazgos del crítico final (Opus) y del evaluador independiente al cerrar el workflow `wf_f2a2b74d-2df`.
Sirven de lista de trabajo para la siguiente ronda. Cada hallazgo trae la evidencia que dio el revisor.

## Crítico final
Aprobado: no.

### 1. (bloqueante)

Cuando la pregunta nombra una colonia en vez de un municipio, el agente no la toma en cuenta y no lo dice. En pre_consulta solo existe rag.municipios_en, así que no hay filtro ni aviso por colonia. En la demo es muy probable que el profesor diga «en Polanco», «en la Condesa» o «en Santa Fe», y el agente contestaría otra cosa sin avisar.

**Evidencia:** Corrí agente.responder('quiero abrir una neveria en Polanco'). Herramientas llamadas: perfil_giro y recomendar_zonas con {'giro':'heladeria'}, sin filtro. El top 1 salió FUENTES DE ARAGON (Ecatepec) y en ningún lugar dice que Polanco se ignoró. Latencia 97.2 s.

### 2. (importante)

Las preguntas de seguimiento pierden el giro. pre_consulta solo lee la pregunta actual y no el historial que pasa la UI (ss.chat[-4:]). Después de «heladería», un «¿y en Coyoacán?» se trata como «negocio en Coyoacán»: sugiere abarrotes y da el top de abarrotes.

**Evidencia:** responder('¿y en Coyoacán?', historial=[heladería...]) llamó sugerir_giros {'municipio':'Coyoacán'} y luego recomendar_zonas {'giro':'abarrotes'}. La respuesta fue «Top 5 para abarrotes». Tardó 136.7 s.

### 3. (importante)

La respuesta por defecto a «quiero poner una heladería» no trae nada de Banxico ni de macro. Tampoco trae análisis de ingreso en pesos ni de edades, aunque la meta de JP lo pide. Los datos sí existen: ficha_zona devuelve edades_2020, decil_estimado e ingreso_trim_mediano_estimado_mxn, y contexto_macro tiene la tasa objetivo, el FIX y el INPC. Pero pre_consulta solo llama a contexto_macro si la pregunta dice inflación, tasa o dólar, y el formato del prompt solo pide «NSE estimado». El RAG (fichas municipales y teoría de Huff y Christaller) tampoco entra en la ruta principal.

**Evidencia:** Corrida en frío de 'quiero poner una heladeria': herramientas perfil_giro y recomendar_zonas, nada más. En la respuesta no aparecen Banxico, ingreso, decil ni % de 0-14 años, y las Fuentes no listan Banxico. Ni siquiera con 'heladeria en Coyoacan para niños, cuanto ganan ahi?' se contestó el ingreso ni la población infantil (recomendar_zonas solo con municipio).

### 4. (importante)

La latencia es alta para una demo en vivo y la respuesta no se transmite en streaming. La UI muestra un spinner durante 1.3 a 2.3 minutos. La mediana de la evaluación final es 106 s y la máxima 139 s; el README todavía dice «mediana 85 s». Si el usuario escribe otra vez mientras espera, Streamlit vuelve a correr el script y la petición anterior sigue ocupando a Ollama.

**Evidencia:** Mis corridas dieron 77.3 s en frío (heladería), 97.2 s (Polanco), 107.1 s (Coyoacán) y 136.7 s (seguimiento). ui.py usa st.spinner y agente.responder sin stream. En agente.py, OPCIONES pone num_predict 1100. En la BITÁCORA, la evaluación final reporta mediana 106.0 s y p90 128.6 s, y en el README, línea 62, sigue «mediana 85 s».

### 5. (importante)

Hay riesgo de memoria en la demo. qwen3:8b ocupa 5.7 GB con num_ctx 8192, y durante la evaluación el swap llegó a 13.2 GB con 19 % de memoria libre. Con navegador, proyección y Streamlit abiertos al mismo tiempo, en una Air de 16 GB sin ventilador, puede alentarse o colgarse.

**Evidencia:** Con el modelo cargado, ollama ps mostró qwen3:8b 5.7 GB 100% GPU CONTEXT 8192. Antes de cargarlo, vm.swapusage ya marcaba 3.75 GB usados. La BITÁCORA registra swap máximo de 13.2 GB y memoria libre mínima de 19 %.

### 6. (importante)

El score final que ordena las colonias casi no tiene validación predictiva. Su AUC medio por giro es 0.583, por debajo de dos líneas base ingenuas: la competencia en la AGEB (0.711) y la competencia Huff (0.652). El 0.806 es del modelo de aperturas solo, y los pesos del score (30/25/15/20/10) son una decisión del autor. Además, el decil imputado acierta el decil exacto solo 17.9 % de las veces (±1: 50.4 %). En un examen es fácil que pregunten esto, y hoy la respuesta solo dice que es «esperado».

**Evidencia:** reports/validacion.md, línea 40: «AUC medio: modelo 0.806, densidad 0.542, competencia 0.652, competencia en la AGEB 0.711, actividad 0.636, score 0.583». En reports/decil_imputado.md, la validación cruzada da «Decil exacto 17.9%, Decil +-1 50.4%».

### 7. (importante)

El entregable final del contrato (repo privado en GitHub) no existe todavía. No hay remote, y el CLI gh, que el contrato dice que JP usará con gh auth login, no está instalado.

**Evidencia:** git remote -v no devolvió nada, y gh repo view respondió «command not found: gh».

### 8. (menor)

Sin internet, el mapa interactivo no carga: folium trae Leaflet y las teselas de un CDN. La UI detecta la falta de red con un HEAD a jsdelivr que se guarda en caché 10 min (ttl=600), así que si la red se cae a media demo el mapa se queda en blanco hasta que se active a mano «Mapa estático». El agente, el RAG (con respaldo léxico) y los datos sí funcionan sin red.

**Evidencia:** ui.py, líneas 45-49: hay_internet() con @st.cache_data(ttl=600), y requests.head('https://cdn.jsdelivr.net', timeout=1.5). El toggle de la línea 133 toma su valor inicial de ahí.

### 9. (menor)

Hay detalles que se notan en pantalla. Las cifras a veces salen como «prob. de apertura % 63» (el modelo copia la clave _pct). En sugerir_giros, el LLM cambió el orden: barbería con 62 % quedó en 5.º lugar, debajo de frutería con 57 %, aunque el prompt pide «en su orden». Roma Norte sale con decil 8 y NSE «medio», algo que un evaluador puede objetar.

**Evidencia:** reports/evaluacion_parcial.jsonl, id 1: «prob. de apertura % 63». En la corrida del seguimiento: «5. barberia_estetica (viabilidad: 62%...)» después de «4. fruteria (57%)». ficha_zona('Roma Norte'): decil_estimado 8, nse_estimado 'medio'.

### 10. (menor)

El flujo de gente solo usa la afluencia por estación del Metro. Metrobús, Tren Ligero y Cablebús tienen afluencia solo por línea (queda NaN por estación), y Mexibús, Mexicable y Suburbano no tienen. Eso sesga el término flujo hacia la CDMX frente al Edomex. Está documentado, pero conviene decirlo en la exposición.

**Evidencia:** transporte.parquet: afluencia_anual NaN al 100 % en todos los sistemas menos Metro (195 estaciones con dato). BITÁCORA, línea 61.

### 11. (menor)

El INPC de alimentos quedó marcado NO ENCONTRADO y se usan proxies (agropecuarios y mercancías). No lo verifiqué, pero es posible que el subíndice por objeto del gasto «Alimentos, bebidas y tabaco» sí exista en el BIE del INEGI. Para una heladería es el dato macro que más importa.

**Evidencia:** macro.json: inpc_alimentos_var_anual.estado = 'NO ENCONTRADO', con proxies 910411 y 910408.

### 12. (menor)

La evaluación de 20/20 está muy ajustada a sus propias preguntas. Ninguna nombra una colonia, ninguna es un seguimiento con historial y ninguna pide ingreso o edades. Por eso los fallos que encontré arriba no aparecen en reports/evaluacion.md.

**Evidencia:** En eval/preguntas.yaml, las 20 preguntas son de una sola vuelta y solo nombran municipios (Iztapalapa, Naucalpan, Ecatepec, Tlalnepantla, Benito Juárez, Coyoacán, Monterrey).

## Evaluador independiente (evaluar#2)
Aprobado: sí; 20/20; mediana 117.2 s.

### E1. (menor)

El evaluador tiene huecos (no pasa por construccion, pero es laxo): (a) una colonia sin clave AGEB no se revisa, asi que una colonia inventada pasa; (b) no revisa que la colonia vaya con SU AGEB, solo que el nombre aparezca en algun lado; (c) tolera 1 cifra sin origen por respuesta, y un entero de 2 digitos inventado coincide por azar ~30 % de las veces con algun numero de las herramientas. En las 20 respuestas reales NO hay casos: un chequeo propio renglon por renglon (cifras contra la zona de ESA AGEB, colonia = nom_colonia de agebs_features) da 20/20 OK y no hay nombres en negritas fuera de las herramientas.

**Evidencia:** uv run python scratchpad/mutar.py (calificar() sobre la respuesta 1 alterada): 'gasto inventado' $97,000->$197,000 pasa=True; 'colonias intercambiadas' pasa=True; 'colonia extra sin AGEB' (POLANCO o COLONIA INVENTADA XYZ) pasa=True; 'pct inventado 2 digitos' 63->81 pasa=True. Si fallan bien: 2 cifras inventadas, AGEB inventada, colonia cambiada, top de 3, sin fuentes (resp. 2), trampa con colonias. scratchpad/azar.py: enteros 11-99 al azar coinciden 13-55 %; miles y pesos 0 %. scratchpad/atrib.py: 1..20 OK.

### E2. (menor)

Latencia y memoria al limite: mediana 117.2 s (objetivo de 90 s NO cumplido), p90 152.6 s, maxima 172.2 s (pregunta 17) contra el limite de 180 s del check; el margen es de 8 s. Swap maximo 14.4 GB y memoria libre minima 16 % durante la corrida; con mas presion de memoria alguna pregunta puede pasar de 180 s y fallar.

**Evidencia:** nohup nice -n 10 uv run python eval/evaluar.py --rehacer -> '20/20 pasan; trampa ok; mediana 117.2 s; swap max 14379.0 MB; aprobado=True'; log: [16] 164.3 s swap 12262 MB, [17] 172.2 s swap 14379 MB. Al final se descargo qwen3:8b con ollama stop.

### E3. (menor)

Dos respuestas salen cortadas al final por el tope num_predict=1100 (app/agente.py OPCIONES): la 17 termina en 'config/giros.yaml (supuestos del' y la 18 en 'reports/decil_im'. Solo se pierde la cola de la lista de fuentes, pero se ve descuidado.

**Evidencia:** reports/evaluacion_parcial.jsonl, campo respuesta de id 17 e id 18 (leido con uv run python -c ...).

### E4. (menor)

Lectura economica: el 'gasto potencial por trimestre' usa rubros ENIGH amplios y la respuesta no lo aclara. Cafeteria usa ali_fuera_total (todo lo que se come fuera de casa: $17.8 a $21.9 millones por trimestre en 400 m). Renta de bicicletas usa esparcimiento ($75 a $120 millones). La nota de giros.yaml existe, pero el LLM solo la repite en bicicletas. Ademas, sugerir_giros (viabilidad = prob. de apertura x prob. de seguir abierto) pone abarrotes como el primer giro para Coyoacan y para nivel bajo, aunque el top tiene captura de 5 a 14 % y 8 a 20 competidores ponderados. Mide rotacion, no rentabilidad, y la prob. de seguir abierto viene de un modelo con AUC 0.59. El constructor ya lo avisa en la bitacora.

**Evidencia:** Respuesta 2: 'gasto potencial por trimestre $17,792,000' (Granada). Respuesta 16: '$92,893,000' (Roma Sur), 'prob. de apertura 0 %', 'captura % 100'. Respuesta 17: abarrotes en Carmen Serdan 'competidores ponderados 20, captura % 5'. grep config/giros.yaml: cafeteria rubro_enigh: ali_fuera_total.

### E5. (menor)

Detalles de redaccion: la respuesta macro dice 'Tipo de cambio fijo' en vez de FIX. 'Algo barato' se interpreta como ticket de hasta $100 (ticket_max=100) y no como poca inversion inicial.

**Evidencia:** Respuesta 19: '**Tipo de cambio fijo (USD/MXN):** 19.02'. Respuesta 18, herramientas: sugerir_giros({'nse': 'bajo', 'ticket_max': 100}).
