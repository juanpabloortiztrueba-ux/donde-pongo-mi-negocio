# Evaluación del agente (2026-11-24 10:32)

Modelo: qwen3:8b (Ollama, think=False). Preguntas: 28 de 28 (`eval/preguntas.yaml`). Script: `eval/evaluar.py`.

**Resultado: 28/28 pasan; trampa pasa; colonia y seguimiento 6/6 → APROBADO** (criterio: ≥ 90 % de las preguntas, la trampa, y todas las de colonia y de seguimiento).

- Latencia: mediana 38.2 s, p90 54.7 s, máxima 67.0 s (meta: mediana ≤ 120 s y máxima ≤ 165 s: cumplida; una respuesta de más de 165 s falla).
- Memoria (MacBook Air M4, 16 GB): swap 4533.69 MB al inicio, máximo 15496.0 MB, 15496.0 MB al final; memoria libre mínima 17 % (`memory_pressure`).

## Checks

- `sin_tokens`: ningún valor de `.env` aparece en la respuesta ni en lo que regresaron las herramientas.
- `fuentes`: la respuesta tiene sección de fuentes y nombra al menos una fuente real (INEGI, DENUE, ENIGH, CONAPO, Banxico, carpetas...).
- `fuentes_completas`: todas las fuentes que regresaron las herramientas están en la respuesta (no se corta la lista).
- `latencia`: ≤ 165 s.
- `formato`: sin «prob. de apertura % 63» (debe ser «63 %»), sin «tipo de cambio fijo» (es FIX), sin «None» ni «nan» impresos (un dato vacío se dice «NO ENCONTRADO») y sin respuesta cortada por `num_predict`.
- `top_agebs`: cada AGEB citada existe en `agebs_features`, salió de una herramienta, su colonia (de `agebs_features`) aparece en la respuesta y hay al menos 5 (o las que regresó la herramienta).
- `colonia_de_su_ageb`: cada renglón de zona (desde la línea con la clave AGEB hasta la siguiente) trae la colonia de SU AGEB y no la de otra zona citada.
- `cifras_por_zona`: las cifras de cada renglón coinciden con las de la zona a la que se atribuyen (no con las de otra).
- `lectura_cifras_de_su_zona`: en la «Lectura» del modelo, cada frase que nombra una zona solo usa cifras de esa zona (si un nombre está dentro de otro más largo, «Granada» en «Ampliación Granada», manda la coincidencia más larga) y cada cifra se compara solo con el campo que nombra («prob. de apertura», «gasto potencial», «ingreso», «competidores», «edad clave») o, sin magnitud, con los campos del renglón de la zona; no con cualquier número del resultado.
- `lectura_cifras_de_su_zona` (a partir de la evaluación final): además, cada cifra tiene que salir de alguna herramienta y ser de su tipo (un % solo se compara con campos en %, los pesos con pesos); las de `perfil_giro`, `contexto_macro` y `ficha_municipio` valen en cualquier frase; la viabilidad de un giro de `sugerir_giros` solo vale con ese giro; y a un giro sin `recomendar_zonas` no se le atribuyen zonas ni gasto potencial.
- `lectura_superlativos`: «mayor», «menor», «lidera(n)», «destaca», «mejor(es)»... junto con una magnitud (prob. de apertura, gasto, ingreso, competidores, edad, score u «oportunidad / mejor opción») solo valen si la zona nombrada es de las primeras del top en esa magnitud (`app/lectura.py`); sin magnitud escrita se deduce de la cifra que sigue («lidera con un 12.5 %»); el giro que «lidera» es el 1 de `sugerir_giros`; y «En <colonia pedida>, la colonia Z» solo si Z está dentro de la colonia.
- `avisos_del_giro`: los avisos «giro raro», el del rubro ENIGH sustituto y el del rubro ENIGH amplio («el gasto potencial usa el rubro ENIGH ... completo; sirve para ordenar zonas dentro del giro, no para comparar entre giros») de `recomendar_zonas` aparecen en la respuesta (en los riesgos).
- `referencia_edad`: la edad clave del giro en la ZMVM va en su propia línea («Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).»), no dentro del encabezado del top.
- `sinonimo_dicho`: si la pregunta usó otro nombre del giro («nevería»), una línea dice con qué giro del catálogo se quedó («Tomé «nevería» como heladería...»).
- `aviso_ageb_vacia`: una zona del top con menos de 200 habitantes o menos de 50 hogares lleva en su renglón el aviso de que el gasto viene del radio de influencia.
- `ingreso_municipio`: si la pregunta pide el ingreso («¿cuánto ganan?») y hay ficha del municipio, la respuesta trae el ingreso trimestral mediano estimado por hogar del municipio.
- `macro_mecanismo` (pregunta «¿cómo influye...?»): la respuesta explica el mecanismo (costo, insumos, crédito, financiamiento, margen, precio).
- `colonias_con_origen`: ninguna colonia del catálogo de `agebs_features`, renglón de lista en negritas ni nombre escrito como «colonia X» / «fraccionamiento X» aparece sin salir de las herramientas, de la pregunta o del historial.
- `municipio`, `giro`, `nse`, `macro_usada`: se usó la herramienta con el giro/filtro esperado y las AGEB son del municipio pedido.
- `macro_cifras` (pregunta macro): la respuesta cita al menos 2 cifras de `contexto_macro`.
- `macro_breve` (giro con `contexto_macro`): al menos 2 cifras de la línea macro y el párrafo no pasa de 600 caracteres.
- `ingreso_y_edad`: al menos el 60 % de las zonas citadas traen su ingreso trimestral estimado en pesos y el % de la edad clave del giro.
- `colonia_respetada` (preguntas con colonia): toda AGEB citada es de la colonia o está a ≤ 2 km de su centroide (calculado aquí desde `agebs_features`), al menos una es de la colonia misma y la herramienta recibió el filtro; con una colonia inexistente: la respuesta dice «no se encontró», nombra la colonia y explica qué da a cambio, y no aplicó filtro.
- `seguimiento_mantiene_giro` (preguntas con historial): el giro de los turnos anteriores se conserva en la herramienta y en la respuesta.
- `cifras`: a lo más 0 cifras sin origen y al menos 95 % de las cifras citadas coinciden con un número de las herramientas, con tolerancia de redondeo según los decimales escritos («0.43 millones» = 430,000; una fracción de la herramienta puede citarse como %). No se verifican enteros ≤ 10 (enumeraciones, deciles), años ni fechas.
- `trampa_fuera_de_alcance`: dice que está fuera de alcance y no da ninguna AGEB.
- `aviso_prob_baja`: si `recomendar_zonas` avisa que la prob. de apertura es baja en todo el top, la respuesta lo dice y aclara que el score es relativo al giro.
- `score_relativo_dicho`: con zonas recomendadas, la respuesta dice que el score es relativo dentro del giro.
- `sin_giros_inventados`: sin `sugerir_giros`, la respuesta no habla de «viabilidad» ni lista «giros que conviene».
- `sugerir_usada`, `alternativas`, `score_relativo`, `orden_sugerir`, `inversion_explicada` (preguntas sin giro): se usó `sugerir_giros`, la respuesta nombra al menos 3 de los giros que regresó, y la Lectura los nombra en el orden de la herramienta, dice que el score es relativo dentro de cada giro y, si pidió algo barato, explica que se entendió como poca inversión.

## Resultados por pregunta

| # | Pregunta | Pasa | Latencia (s) | Herramientas | Cifras ok | Checks que fallan |
|---|---|---|---|---|---|---|
| 1 | Quiero poner una heladería, ¿en qué colonias me conviene? | sí | 43.7 | perfil_giro, recomendar_zonas, contexto_macro | 60/60 | - |
| 2 | ¿Dónde abro una cafetería de especialidad? | sí | 28.9 | perfil_giro, recomendar_zonas, contexto_macro | 63/63 | - |
| 3 | Busco dónde poner un gimnasio, ¿qué zonas me recomiendas? | sí | 22.5 | perfil_giro, recomendar_zonas, contexto_macro | 58/58 | - |
| 4 | Quiero abrir una farmacia en Iztapalapa | sí | 28.1 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 66/66 | - |
| 5 | ¿Dónde conviene poner una papelería? | sí | 25.1 | perfil_giro, recomendar_zonas, contexto_macro | 50/50 | - |
| 6 | Una lavandería de autoservicio, ¿dónde la pongo? | sí | 28.1 | perfil_giro, recomendar_zonas, contexto_macro | 51/51 | - |
| 7 | Quiero poner una veterinaria en Naucalpan | sí | 30.1 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 72/72 | - |
| 8 | ¿En qué colonias pongo una taquería? | sí | 30.8 | perfil_giro, recomendar_zonas, contexto_macro | 60/60 | - |
| 9 | Tienda de abarrotes en Ecatepec, ¿qué colonias? | sí | 33.3 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 74/74 | - |
| 10 | Quiero abrir una barbería en una zona de nivel alto | sí | 30.7 | perfil_giro, recomendar_zonas, contexto_macro | 59/59 | - |
| 11 | ¿Dónde pongo un consultorio dental? | sí | 26.8 | perfil_giro, recomendar_zonas, contexto_macro | 56/56 | - |
| 12 | Quiero abrir una guardería en Tlalnepantla | sí | 51.1 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 63/63 | - |
| 13 | ¿Dónde abro una ferretería? | sí | 44.6 | perfil_giro, recomendar_zonas, contexto_macro | 56/56 | - |
| 14 | Una pastelería en Benito Juárez, ¿dónde? | sí | 41.9 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 76/76 | - |
| 15 | Quiero poner una librería | sí | 29.6 | perfil_giro, recomendar_zonas, contexto_macro | 51/51 | - |
| 16 | Quiero un negocio de renta de bicicletas, ¿dónde lo pongo? | sí | 32.5 | perfil_giro, recomendar_zonas, contexto_macro | 50/50 | - |
| 17 | Quiero poner un negocio en Coyoacán, ¿qué me recomiendas y dónde? | sí | 62.3 | perfil_giro, sugerir_giros, recomendar_zonas, ficha_municipio | 85/85 | - |
| 18 | Quiero algo barato para una zona de nivel bajo, ¿qué pongo y dónde? | sí | 49.4 | perfil_giro, sugerir_giros, recomendar_zonas | 69/69 | - |
| 19 | ¿Cómo está la economía para abrir un negocio? Inflación, tasa de Banxico y tipo de cambio | sí | 52.6 | perfil_giro, contexto_macro | 26/26 | - |
| 20 | Quiero poner una heladería en Monterrey | sí | 34.5 | perfil_giro, recomendar_zonas, buscar_carpetas | 2/2 | - |
| 21 | Quiero abrir una nevería en Polanco | sí | 49.3 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 75/75 | - |
| 22 | ¿Dónde pongo una cafetería en la Condesa? | sí | 67.0 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 79/79 | - |
| 23 | Quiero abrir una farmacia en Santa Fe | sí | 55.6 | perfil_giro, recomendar_zonas, contexto_macro | 53/53 | - |
| 24 | Quiero abrir una papelería en la colonia Villa Esperanza Imaginaria | sí | 33.6 | perfil_giro, recomendar_zonas, contexto_macro | 53/53 | - |
| 25 | ¿Y en Coyoacán? | sí | 54.7 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 72/72 | - |
| 26 | ¿Y una veterinaria? | sí | 47.6 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 72/72 | - |
| 27 | Quiero una heladería en Coyoacán para niños, ¿cuánto ganan ahí y qué porcentaje de la gente es menor de 14 años? | sí | 54.3 | perfil_giro, recomendar_zonas, contexto_macro, ficha_municipio | 65/65 | - |
| 28 | Quiero abrir una taquería, ¿cómo influyen la inflación y la tasa de Banxico? | sí | 43.3 | perfil_giro, contexto_macro, recomendar_zonas | 64/64 | - |

## Respuestas completas

### 1. Quiero poner una heladería, ¿en qué colonias me conviene?

_llm, 1 rondas, 43.7 s; herramientas: perfil_giro({"texto": "Quiero poner una heladería, ¿en qué colonias me conviene?"}); recomendar_zonas({"giro": "heladeria"}); contexto_macro({"giro": "heladeria"})_

> **Lectura:** Entre las zonas del top de heladería, Canteros tiene la mayor probabilidad de apertura (74 %); Fuentes de Aragón tiene el mayor gasto potencial ($97,000 por trimestre); Mixcóatl tiene la menor competencia (0.2 competidores ponderados). Fuentes de Aragón lidera con un gasto potencial de $97,000 por trimestre y un ingreso trimestral estimado por hogar de $83,000. Canteros destaca por tener una probabilidad de apertura del 74 % y un 26.5 % de la edad clave (0 a 14 años).
> 
> **Top 5 para heladería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).
> 
> 1. **MIXCOATL**, Iztapalapa (AGEB 0900700014202): score 96.1/100. prob. de apertura 34 %; gasto potencial $64,000 por trimestre; 0.2 competidores ponderados (captura 83 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $49,000; 0 a 14 años: 21.8 %.
> 2. **FUENTES DE ARAGON**, Ecatepec de Morelos (AGEB 1503300011773): score 95.7/100. prob. de apertura 63 %; gasto potencial $97,000 por trimestre; 1.2 competidores ponderados (captura 46 %); NSE estimado medio, decil 7, ingreso trimestral estimado por hogar $83,000; 0 a 14 años: 17.3 %.
> 3. **AGUA AZUL**, Nezahualcóyotl (AGEB 1505800010740): score 95.1/100. prob. de apertura 64 %; gasto potencial $65,000 por trimestre; 0.4 competidores ponderados (captura 72 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $78,800; 0 a 14 años: 20.6 %.
> 4. **CANTEROS**, Chimalhuacán (AGEB 1503100010535): score 94.2/100. prob. de apertura 74 %; gasto potencial $41,000 por trimestre; 0.5 competidores ponderados (captura 69 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $48,600; 0 a 14 años: 26.5 %.
> 5. **BENITO JUAREZ**, Nezahualcóyotl (AGEB 1505800010539): score 94.0/100. prob. de apertura 73 %; gasto potencial $55,000 por trimestre; 0.8 competidores ponderados (captura 56 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $53,500; 0 a 14 años: 21.3 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Riesgos:**
> - El rubro de helados de la ENIGH es consumo en casa y solo 2-7 % de hogares reporta gasto; sirve para ordenar deciles, no para dimensionar.
> - El gasto potencial usa el rubro ENIGH helados, nieves y paletas de hielo (consumo en casa) como sustituto del giro; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 70 pesos es un supuesto (supuesto: una nieve o helado artesanal individual, 2026)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411).

### 2. ¿Dónde abro una cafetería de especialidad?

_llm, 1 rondas, 28.9 s; herramientas: perfil_giro({"texto": "¿Dónde abro una cafetería de especialidad?"}); recomendar_zonas({"giro": "cafeteria"}); contexto_macro({"giro": "cafeteria"})_

> **Lectura:** Entre las zonas del top de cafetería, Granada tiene la mayor probabilidad de apertura (88 %) y el mayor gasto potencial ($17,792,000 por trimestre); Santa Apolonia tiene la menor competencia (0.5 competidores ponderados). Anzures tiene una probabilidad de apertura del 70 % y un gasto potencial de $12,884,000.
> 
> **Top 5 para cafetería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **SANTA APOLONIA**, Azcapotzalco (AGEB 0900200010665): score 97.1/100. prob. de apertura 86 %; gasto potencial $7,822,000 por trimestre; 0.5 competidores ponderados (captura 68 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $72,200; 25 a 59 años: 51.4 %.
> 2. **ANZURES**, Miguel Hidalgo (AGEB 0901600010711): score 96.6/100. prob. de apertura 70 %; gasto potencial $12,884,000 por trimestre; 1.3 competidores ponderados (captura 44 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $158,000; 25 a 59 años: 62.9 %.
> 3. **GRANADA**, Miguel Hidalgo (AGEB 0901600010571): score 95.9/100. prob. de apertura 88 %; gasto potencial $17,792,000 por trimestre; 2.5 competidores ponderados (captura 29 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $169,400; 25 a 59 años: 67.2 %.
> 4. **AMPLIACIÓN GRANADA**, Miguel Hidalgo (AGEB 0901600010459): score 95.5/100. prob. de apertura 75 %; gasto potencial $13,442,000 por trimestre; 1.4 competidores ponderados (captura 42 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $111,400; 25 a 59 años: 59.0 %.
> 5. **GABRIEL RAMOS MILLÁN**, Iztacalco (AGEB 0900600010630): score 94.9/100. prob. de apertura 44 %; gasto potencial $9,856,000 por trimestre; 1.0 competidores ponderados (captura 50 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $75,900; 25 a 59 años: 49.9 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Riesgos:**
> - El rubro de café y bebidas de la ENIGH es café para preparar en casa; el consumo en cafetería cae en alimentos y bebidas fuera del hogar (restaurantes y similares).
> - El gasto potencial usa el rubro ENIGH alimentos y bebidas consumidos fuera del hogar completo; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 95 pesos es un supuesto (supuesto: una bebida y un alimento ligero)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411).

### 3. Busco dónde poner un gimnasio, ¿qué zonas me recomiendas?

_llm, 1 rondas, 22.5 s; herramientas: perfil_giro({"texto": "Busco dónde poner un gimnasio, ¿qué zonas me recomiendas?"}); recomendar_zonas({"giro": "gimnasio"}); contexto_macro({"giro": "gimnasio"})_

> **Lectura:** Entre las zonas del top de gimnasio, Ampliación Nápoles tiene la mayor probabilidad de apertura (59 %) y el mayor gasto potencial ($8,830,000 por trimestre); Argentina Poniente tiene la menor competencia (2.4 competidores ponderados). Del Valle Centro lidera con un ingreso trimestral estimado por hogar de $172,600, mientras que Ampliación Nápoles destaca por su gasto potencial de $8,830,000 por trimestre y una probabilidad de apertura del 59 %.
> 
> **Top 5 para gimnasio** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **DEL VALLE CENTRO**, Benito Juárez (AGEB 0901400010399): score 90.0/100. prob. de apertura 24 %; gasto potencial $8,748,000 por trimestre; 9.2 competidores ponderados (captura 10 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $172,600; 25 a 59 años: 55.8 %.
> 2. **GENERAL PEDRO MARÍA ANAYA**, Benito Juárez (AGEB 0901400010986): score 89.4/100. prob. de apertura 16 %; gasto potencial $5,971,000 por trimestre; 4.0 competidores ponderados (captura 20 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $166,500; 25 a 59 años: 54.8 %.
> 3. **DEL CARMEN**, Coyoacán (AGEB 0900300010041): score 89.1/100. prob. de apertura 48 %; gasto potencial $4,831,000 por trimestre; 3.5 competidores ponderados (captura 22 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $152,200; 25 a 59 años: 51.5 %.
> 4. **AMPLIACIÓN NÁPOLES**, Benito Juárez (AGEB 0901400010384): score 88.6/100. prob. de apertura 59 %; gasto potencial $8,830,000 por trimestre; 10.2 competidores ponderados (captura 9 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $169,100; 25 a 59 años: 62.4 %.
> 5. **ARGENTINA PONIENTE**, Miguel Hidalgo (AGEB 0901600010092): score 88.4/100. prob. de apertura 12 %; gasto potencial $2,695,000 por trimestre; 2.4 competidores ponderados (captura 30 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $147,100; 25 a 59 años: 66.8 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 550 pesos es un supuesto (supuesto: mensualidad de un gimnasio de barrio, 2026 (no es ticket por visita))
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 4. Quiero abrir una farmacia en Iztapalapa

_llm, 1 rondas, 28.1 s; herramientas: perfil_giro({"texto": "Quiero abrir una farmacia en Iztapalapa"}); recomendar_zonas({"giro": "farmacia", "municipio": "Iztapalapa"}); contexto_macro({"giro": "farmacia"}); ficha_municipio({"municipio": "Iztapalapa"})_

> **Lectura:** Entre las zonas del top de farmacia, Juan Escutia tiene la mayor probabilidad de apertura (92 %); Unidad Modelo tiene el mayor gasto potencial ($1,218,000 por trimestre); Aculco tiene la menor competencia (1.0 competidores ponderados).
> 
> **Top 5 para farmacia** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 13.8 % de la población tiene 60 años o más (Censo 2020).
> 
> 1. **JUAN ESCUTIA**, Iztapalapa (AGEB 0900700010017): score 90.9/100. prob. de apertura 92 %; gasto potencial $1,053,000 por trimestre; 3.4 competidores ponderados (captura 23 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $73,600; 60 años o más: 13.4 %.
> 2. **SAN MIGUEL TEOTONGO SECCIÓN PUENTE**, Iztapalapa (AGEB 0900700012649): score 85.4/100. prob. de apertura 78 %; gasto potencial $799,000 por trimestre; 4.6 competidores ponderados (captura 18 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $50,500; 60 años o más: 14.1 %.
> 3. **UNIDAD MODELO**, Iztapalapa (AGEB 0900700012526): score 84.7/100. prob. de apertura 18 %; gasto potencial $1,218,000 por trimestre; 1.4 competidores ponderados (captura 42 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $111,200; 60 años o más: 27.7 %.
> 4. **ACULCO**, Iztapalapa (AGEB 0900700015431): score 82.6/100. prob. de apertura 29 %; gasto potencial $1,067,000 por trimestre; 1.0 competidores ponderados (captura 50 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $98,400; 60 años o más: 18.8 %.
> 5. **LA ERA**, Iztapalapa (AGEB 0900700011655): score 81.6/100. prob. de apertura 68 %; gasto potencial $802,000 por trimestre; 3.7 competidores ponderados (captura 21 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $75,300; 60 años o más: 16.3 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Sobre Iztapalapa:** Población en AGEB urbanas: 1,835,486 habitantes (lugar 1 de 76 en la ZMVM). Densidad: 16,325 hab/km² (lugar 5 de 76). Edad: 0-14 años 20.0 %; 15-24 16.0 %; 25-59 49.7 %; 60 o más 14.3 %. Ingreso trimestral mediano estimado por hogar en Iztapalapa: $64,700 (decil típico 5; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 190 pesos es un supuesto (supuesto: medicamento de receta o patente más un artículo de cuidado personal)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406); carpetas/03_municipios (fichas generadas desde agebs_features).

### 5. ¿Dónde conviene poner una papelería?

_llm, 1 rondas, 25.1 s; herramientas: perfil_giro({"texto": "¿Dónde conviene poner una papelería?"}); recomendar_zonas({"giro": "papeleria"}); contexto_macro({"giro": "papeleria"})_

> **Lectura:** Entre las zonas del top de papelería, Juan Escutia tiene la mayor probabilidad de apertura (92 %); Nonoalco Tlatelolco tiene el mayor gasto potencial ($1,191,000 por trimestre); Tacubaya tiene la menor competencia (1.8 competidores ponderados).
> 
> **Top 5 para papelería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).
> 
> 1. **BENITO JUAREZ**, Nezahualcóyotl (AGEB 1505800010577): score 95.7/100. prob. de apertura 91 %; gasto potencial $828,000 por trimestre; 4.2 competidores ponderados (captura 19 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $67,500; 0 a 14 años: 18.2 %.
> 2. **NONOALCO TLATELOLCO**, Cuauhtémoc (AGEB 0901500010324): score 94.5/100. prob. de apertura 9 %; gasto potencial $1,191,000 por trimestre; 1.9 competidores ponderados (captura 34 %); NSE estimado medio, decil 7, ingreso trimestral estimado por hogar $92,000; 0 a 14 años: 10.4 %.
> 3. **EX HIPÓDROMO DE PERALVILLO**, Cuauhtémoc (AGEB 0901500010150): score 94.2/100. prob. de apertura 50 %; gasto potencial $795,000 por trimestre; 2.1 competidores ponderados (captura 33 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $73,100; 0 a 14 años: 17.1 %.
> 4. **TACUBAYA**, Miguel Hidalgo (AGEB 0901600011175): score 93.3/100. prob. de apertura 65 %; gasto potencial $817,000 por trimestre; 1.8 competidores ponderados (captura 35 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $104,800; 0 a 14 años: 11.1 %.
> 5. **JUAN ESCUTIA**, Iztapalapa (AGEB 0900700010017): score 92.9/100. prob. de apertura 92 %; gasto potencial $669,000 por trimestre; 3.3 competidores ponderados (captura 23 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $73,600; 0 a 14 años: 19.4 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 60 pesos es un supuesto (supuesto: copias, cuadernos y útiles sueltos; sube en temporada escolar)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 6. Una lavandería de autoservicio, ¿dónde la pongo?

_llm, 1 rondas, 28.1 s; herramientas: perfil_giro({"texto": "Una lavandería de autoservicio, ¿dónde la pongo?"}); recomendar_zonas({"giro": "lavanderia"}); contexto_macro({"giro": "lavanderia"})_

> **Lectura:** Entre las zonas del top de lavandería, Hank González y San Juan Ixtacala Plano Norte empatan con la mayor probabilidad de apertura (51 %); Centro tiene la menor competencia (0.8 competidores ponderados). El Centro destaca por su edad clave.
> 
> **Top 5 para lavandería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **CENTRO**, Cuauhtémoc (AGEB 0901500010979): score 94.9/100. prob. de apertura 9 %; gasto potencial no dimensionable (la ENIGH casi no registra gasto en este rubro); 0.8 competidores ponderados (captura 56 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $46,300; 25 a 59 años: 51.7 %.
> 2. **BENITO JUAREZ NORTE XALOSTOC**, Ecatepec de Morelos (AGEB 150330001224A): score 94.5/100. prob. de apertura 36 %; gasto potencial no dimensionable (la ENIGH casi no registra gasto en este rubro); 1.5 competidores ponderados (captura 40 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $49,300; 25 a 59 años: 46.2 %.
> 3. **HANK GONZALEZ**, Ecatepec de Morelos (AGEB 1503300013642): score 94.4/100. prob. de apertura 51 %; gasto potencial no dimensionable (la ENIGH casi no registra gasto en este rubro); 0.9 competidores ponderados (captura 51 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $56,800; 25 a 59 años: 48.5 %.
> 4. **SAN JUAN IXTACALA PLANO NORTE**, Atizapán de Zaragoza (AGEB 1501300011183): score 93.4/100. prob. de apertura 51 %; gasto potencial no dimensionable (la ENIGH casi no registra gasto en este rubro); 3.0 competidores ponderados (captura 25 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $64,400; 25 a 59 años: 49.0 %.
> 5. **TABLAS DEL POZO**, Ecatepec de Morelos (AGEB 1503300012254): score 92.6/100. prob. de apertura 33 %; gasto potencial no dimensionable (la ENIGH casi no registra gasto en este rubro); 1.1 competidores ponderados (captura 48 %); NSE estimado bajo, decil 2, ingreso trimestral estimado por hogar $38,900; 25 a 59 años: 45.7 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - Solo 0.4 % de los hogares reporta gasto en lavandería en la ENIGH (promedio cercano a 1 peso por trimestre): no sirve para dimensionar demanda. La demanda real se apoya en vivienda en renta, departamentos chicos, estudiantes y trabajadores.
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 150 pesos es un supuesto (supuesto: carga de ropa lavada y secada, o prendas de tintorería)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 7. Quiero poner una veterinaria en Naucalpan

_llm, 1 rondas, 30.1 s; herramientas: perfil_giro({"texto": "Quiero poner una veterinaria en Naucalpan"}); recomendar_zonas({"giro": "veterinaria", "municipio": "Naucalpan de Juárez"}); contexto_macro({"giro": "veterinaria"}); ficha_municipio({"municipio": "Naucalpan de Juárez"})_

> **Lectura:** Entre las zonas del top de veterinaria, Alfredo V Bonfil tiene la mayor probabilidad de apertura (43 %); San José de los Leones II Sección y Alfredo V Bonfil empatan con el mayor gasto potencial ($279,000 por trimestre); San José de los Leones II Sección tiene la menor competencia (1.2 competidores ponderados).
> 
> **Top 5 para veterinaria** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **SAN RAFAEL CHAMAPA**, Naucalpan de Juárez (AGEB 1505700011794): score 93.8/100. prob. de apertura 19 %; gasto potencial $277,000 por trimestre; 2.1 competidores ponderados (captura 32 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $46,900; 25 a 59 años: 47.0 %.
> 2. **SAN JOSE DE LOS LEONES II SECCION**, Naucalpan de Juárez (AGEB 1505700010851): score 93.5/100. prob. de apertura 22 %; gasto potencial $279,000 por trimestre; 1.2 competidores ponderados (captura 46 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $45,500; 25 a 59 años: 47.2 %.
> 3. **BENITO JUAREZ**, Naucalpan de Juárez (AGEB 1505700010955): score 92.9/100. prob. de apertura 31 %; gasto potencial $271,000 por trimestre; 2.0 competidores ponderados (captura 34 %); NSE estimado bajo, decil 2, ingreso trimestral estimado por hogar $38,800; 25 a 59 años: 46.7 %.
> 4. **ALFREDO V BONFIL**, Naucalpan de Juárez (AGEB 1505700010940): score 92.4/100. prob. de apertura 43 %; gasto potencial $279,000 por trimestre; 2.9 competidores ponderados (captura 26 %); NSE estimado bajo, decil 2, ingreso trimestral estimado por hogar $40,800; 25 a 59 años: 47.9 %.
> 5. **VALLE DORADO**, Naucalpan de Juárez (AGEB 1505700012557): score 92.1/100. prob. de apertura 6 %; gasto potencial $269,000 por trimestre; 1.7 competidores ponderados (captura 37 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $48,500; 25 a 59 años: 46.7 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Sobre Naucalpan de Juárez:** Población en AGEB urbanas: 795,819 habitantes (lugar 5 de 76 en la ZMVM). Densidad: 9,994 hab/km² (lugar 19 de 76). Edad: 0-14 años 20.5 %; 15-24 15.9 %; 25-59 48.6 %; 60 o más 14.9 %. Ingreso trimestral mediano estimado por hogar en Naucalpan de Juárez: $55,000 (decil típico 4; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 450 pesos es un supuesto (supuesto: consulta general más alimento o vacuna)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406); carpetas/03_municipios (fichas generadas desde agebs_features).

### 8. ¿En qué colonias pongo una taquería?

_llm, 1 rondas, 30.8 s; herramientas: perfil_giro({"texto": "¿En qué colonias pongo una taquería?"}); recomendar_zonas({"giro": "taqueria"}); contexto_macro({"giro": "taqueria"})_

> **Lectura:** Entre las zonas del top de taquería, Gabriel Ramos Millán Sección Bramadero tiene la mayor probabilidad de apertura (73 %); Del Carmen tiene el mayor gasto potencial ($1,785,000 por trimestre); Polanco III Sección tiene la menor competencia (0.3 competidores ponderados).
> 
> **Top 5 para taquería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **POLANCO III SECCIÓN**, Miguel Hidalgo (AGEB 0901600010764): score 96.7/100. prob. de apertura 15 %; gasto potencial $803,000 por trimestre; 0.3 competidores ponderados (captura 79 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $157,400; 25 a 59 años: NO ENCONTRADO (el Censo reserva el dato).
> 2. **GABRIEL RAMOS MILLÁN SECCIÓN CUCHILLA**, Iztacalco (AGEB 0900600011018): score 95.2/100. prob. de apertura 21 %; gasto potencial $1,080,000 por trimestre; 1.3 competidores ponderados (captura 43 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $72,500; 25 a 59 años: 50.8 %.
> 3. **GABRIEL RAMOS MILLÁN SECCIÓN BRAMADERO**, Iztacalco (AGEB 0900600010734): score 94.3/100. prob. de apertura 73 %; gasto potencial $1,132,000 por trimestre; 2.6 competidores ponderados (captura 28 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $66,700; 25 a 59 años: 50.1 %.
> 4. **HIPÓDROMO**, Cuauhtémoc (AGEB 0901500011426): score 92.7/100. prob. de apertura 43 %; gasto potencial $1,373,000 por trimestre; 1.6 competidores ponderados (captura 38 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $142,800; 25 a 59 años: 66.4 %.
> 5. **DEL CARMEN**, Benito Juárez (AGEB 0901400010666): score 92.4/100. prob. de apertura 40 %; gasto potencial $1,785,000 por trimestre; 1.1 competidores ponderados (captura 47 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $130,200; 25 a 59 años: 56.9 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 110 pesos es un supuesto (supuesto: 5-6 tacos y una bebida)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411).

### 9. Tienda de abarrotes en Ecatepec, ¿qué colonias?

_llm, 1 rondas, 33.3 s; herramientas: perfil_giro({"texto": "Tienda de abarrotes en Ecatepec, ¿qué colonias?"}); recomendar_zonas({"giro": "abarrotes", "municipio": "Ecatepec de Morelos"}); contexto_macro({"giro": "abarrotes"}); ficha_municipio({"municipio": "Ecatepec de Morelos"})_

> **Lectura:** Entre las zonas del top de tienda de abarrotes, Ciudad Azteca tiene la mayor probabilidad de apertura (100 %); Llano de los Báez tiene el mayor gasto potencial ($14,136,000 por trimestre); Guadalupe Victoria tiene la menor competencia (4.4 competidores ponderados).
> 
> **Top 5 para tienda de abarrotes** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **GUADALUPE VICTORIA**, Ecatepec de Morelos (AGEB 1503300014496): score 85.9/100. prob. de apertura 93 %; gasto potencial $7,178,000 por trimestre; 4.4 competidores ponderados (captura 19 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $57,900; 25 a 59 años: 49.2 %.
> 2. **LLANO DE LOS BAEZ**, Ecatepec de Morelos (AGEB 1503300013873): score 85.0/100. prob. de apertura 99 %; gasto potencial $14,136,000 por trimestre; 10.7 competidores ponderados (captura 9 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $67,700; 25 a 59 años: 52.4 %.
> 3. **CIUDAD AZTECA**, Ecatepec de Morelos (AGEB 1503300010436): score 83.7/100. prob. de apertura 100 %; gasto potencial $10,518,000 por trimestre; 8.0 competidores ponderados (captura 11 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $78,600; 25 a 59 años: 47.7 %.
> 4. **JARDINES DE ARAGON**, Ecatepec de Morelos (AGEB 150330001174A): score 83.7/100. prob. de apertura 99 %; gasto potencial $12,221,000 por trimestre; 9.1 competidores ponderados (captura 10 %); NSE estimado medio, decil 7, ingreso trimestral estimado por hogar $90,800; 25 a 59 años: 51.6 %.
> 5. **JOSE MARIA MORELOS Y PAVON**, Ecatepec de Morelos (AGEB 1503300012023): score 83.7/100. prob. de apertura 99 %; gasto potencial $6,759,000 por trimestre; 9.2 competidores ponderados (captura 10 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $53,800; 25 a 59 años: 46.9 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Sobre Ecatepec de Morelos:** Población en AGEB urbanas: 1,643,623 habitantes (lugar 2 de 76 en la ZMVM). Densidad: 12,764 hab/km² (lugar 14 de 76). Edad: 0-14 años 21.8 %; 15-24 16.3 %; 25-59 48.3 %; 60 o más 13.5 %. Ingreso trimestral mediano estimado por hogar en Ecatepec de Morelos: $60,500 (decil típico 5; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - El gasto potencial usa el rubro ENIGH alimentos dentro del hogar completo; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 55 pesos es un supuesto (supuesto: compra de reposicion diaria)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411); carpetas/03_municipios (fichas generadas desde agebs_features).

### 10. Quiero abrir una barbería en una zona de nivel alto

_llm, 1 rondas, 30.7 s; herramientas: perfil_giro({"texto": "Quiero abrir una barbería en una zona de nivel alto"}); recomendar_zonas({"giro": "barberia_estetica", "nse": "alto"}); contexto_macro({"giro": "barberia_estetica"})_

> **Lectura:** Entre las zonas del top de barbería y estética, Granada tiene la mayor probabilidad de apertura (99 %) y el mayor gasto potencial ($3,429,000 por trimestre); San Lorenzo tiene la menor competencia (1.1 competidores ponderados). Oxtopulco Universidad lidera con un ingreso trimestral estimado por hogar de $213,600, mientras que Granada destaca por tener una probabilidad de apertura del 99 % y un gasto potencial por trimestre de $3,429,000.
> 
> **Top 5 para barbería y estética** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **ACACIAS**, Benito Juárez (AGEB 0901400010948): score 89.7/100. prob. de apertura 42 %; gasto potencial $2,238,000 por trimestre; 3.4 competidores ponderados (captura 23 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $170,300; 25 a 59 años: 55.1 %.
> 2. **SAN LORENZO**, Tlalnepantla de Baz (AGEB 1510400011885): score 88.6/100. prob. de apertura 88 %; gasto potencial $349,000 por trimestre; 1.1 competidores ponderados (captura 49 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $127,500; 25 a 59 años: 54.4 %.
> 3. **OXTOPULCO UNIVERSIDAD**, Coyoacán (AGEB 0900300010234): score 84.4/100. prob. de apertura 83 %; gasto potencial $1,126,000 por trimestre; 5.7 competidores ponderados (captura 15 %); NSE estimado alto, decil 10, ingreso trimestral estimado por hogar $213,600; 25 a 59 años: 47.0 %.
> 4. **GRANADA**, Miguel Hidalgo (AGEB 0901600010444): score 82.6/100. prob. de apertura 99 %; gasto potencial $3,429,000 por trimestre; 9.2 competidores ponderados (captura 10 %); NSE estimado alto, decil 10, ingreso trimestral estimado por hogar $194,500; 25 a 59 años: 63.5 %.
> 5. **XOCO**, Benito Juárez (AGEB 0901400010952): score 80.6/100. prob. de apertura 95 %; gasto potencial $1,506,000 por trimestre; 7.3 competidores ponderados (captura 12 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $157,800; 25 a 59 años: 54.4 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 180 pesos es un supuesto (supuesto: corte de cabello o servicio de unas)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 11. ¿Dónde pongo un consultorio dental?

_llm, 1 rondas, 26.8 s; herramientas: perfil_giro({"texto": "¿Dónde pongo un consultorio dental?"}); recomendar_zonas({"giro": "consultorio_dental"}); contexto_macro({"giro": "consultorio_dental"})_

> **Lectura:** Entre las zonas del top de consultorio dental, Real de San Vicente I tiene la mayor probabilidad de apertura (90 %); Doctores tiene el mayor gasto potencial ($2,544,000 por trimestre); Luis Donaldo Colosio tiene la menor competencia (5.4 competidores ponderados). Doctores lidera con un ingreso trimestral estimado por hogar de $83,600 y un gasto potencial de $2,544,000 por trimestre.
> 
> **Top 5 para consultorio dental** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **LOMAS CHICOLOAPAN**, Chicoloapan (AGEB 1502900010325): score 89.3/100. prob. de apertura 83 %; gasto potencial $1,449,000 por trimestre; 8.8 competidores ponderados (captura 10 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $68,500; 25 a 59 años: 48.7 %.
> 2. **REAL DE SAN VICENTE I**, Chicoloapan (AGEB 1502900010293): score 88.8/100. prob. de apertura 90 %; gasto potencial $1,432,000 por trimestre; 8.9 competidores ponderados (captura 10 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $64,300; 25 a 59 años: 50.9 %.
> 3. **DOCTORES**, Cuauhtémoc (AGEB 0901500011036): score 87.0/100. prob. de apertura 74 %; gasto potencial $2,544,000 por trimestre; 18.3 competidores ponderados (captura 5 %); NSE estimado medio, decil 7, ingreso trimestral estimado por hogar $83,600; 25 a 59 años: 52.8 %.
> 4. **TEPALCATES**, Chimalhuacán (AGEB 1503100011054): score 86.6/100. prob. de apertura 40 %; gasto potencial $595,000 por trimestre; 6.0 competidores ponderados (captura 14 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $55,800; 25 a 59 años: 46.8 %.
> 5. **LUIS DONALDO COLOSIO**, Chimalhuacán (AGEB 1503100011143): score 85.9/100. prob. de apertura 18 %; gasto potencial $587,000 por trimestre; 5.4 competidores ponderados (captura 16 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $46,600; 25 a 59 años: 47.3 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 700 pesos es un supuesto (supuesto: consulta con limpieza o resina simple)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 12. Quiero abrir una guardería en Tlalnepantla

_llm, 1 rondas, 51.1 s; herramientas: perfil_giro({"texto": "Quiero abrir una guardería en Tlalnepantla"}); recomendar_zonas({"giro": "guarderia", "municipio": "Tlalnepantla de Baz"}); contexto_macro({"giro": "guarderia"}); ficha_municipio({"municipio": "Tlalnepantla de Baz"})_

> **Lectura:** Entre las zonas del top de guardería, Viveros de la Loma tiene el mayor gasto potencial ($6,205,000 por trimestre); Centro, Caracoles y Dr Jorge Jiménez Cantú empatan con la menor competencia (0.0 competidores ponderados). La edad clave (0 a 14 años) es mayor en Caracoles, con 22.9 % de la población.
> 
> **Top 5 para guardería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).
> 
> 1. **CENTRO**, Tlalnepantla de Baz (AGEB 1510400010410): score 92.1/100. prob. de apertura 4 %; gasto potencial $1,956,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $69,500; 0 a 14 años: 16.5 %.
> 2. **CARACOLES**, Tlalnepantla de Baz (AGEB 1510400011211): score 87.0/100. prob. de apertura 4 %; gasto potencial $1,907,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $51,600; 0 a 14 años: 22.9 %.
> 3. **VIVEROS DE LA LOMA**, Tlalnepantla de Baz (AGEB 151040001075A): score 86.3/100. prob. de apertura 9 %; gasto potencial $6,205,000 por trimestre; 0.8 competidores ponderados (captura 57 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $157,800; 0 a 14 años: 12.5 %.
> 4. **DR JORGE JIMENEZ CANTU**, Tlalnepantla de Baz (AGEB 1510400011298): score 86.2/100. prob. de apertura 5 %; gasto potencial $1,925,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $57,900; 0 a 14 años: 21.5 %.
> 5. **FRANCISCO VILLA**, Tlalnepantla de Baz (AGEB 1510400011781): score 85.0/100. prob. de apertura 4 %; gasto potencial $4,675,000 por trimestre; 0.2 competidores ponderados (captura 81 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $67,300; 0 a 14 años: 17.6 %.
> 
> **Ojo:** probabilidad de apertura baja en todo el top (4 a 9 %); en la ZMVM apareció en el 3 % de las AGEB: el score alto solo dice que estas son las mejores zonas PARA ESTE GIRO, no que el giro sea viable.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Sobre Tlalnepantla de Baz:** Población en AGEB urbanas: 671,937 habitantes (lugar 9 de 76 en la ZMVM). Densidad: 9,572 hab/km² (lugar 22 de 76). Edad: 0-14 años 18.7 %; 15-24 15.0 %; 25-59 49.7 %; 60 o más 16.3 %. Ingreso trimestral mediano estimado por hogar en Tlalnepantla de Baz: $68,200 (decil típico 5; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - La ENIGH no tiene un rubro de guardería; el rubro más cercano (COICOP 1010) es educación preescolar y primaria.
> - El gasto potencial usa el rubro ENIGH educación preescolar y primaria como sustituto del giro; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406); carpetas/03_municipios (fichas generadas desde agebs_features).

### 13. ¿Dónde abro una ferretería?

_llm, 1 rondas, 44.6 s; herramientas: perfil_giro({"texto": "¿Dónde abro una ferretería?"}); recomendar_zonas({"giro": "ferreteria"}); contexto_macro({"giro": "ferreteria"})_

> **Lectura:** La mejor opción es la colonia Benito Juárez, en Nezahualcóyotl, con prob. de apertura del 78 % y gasto potencial de $482,000 por trimestre. También destaca la colonia Fuentes de Aragón, en Ecatepec de Morelos, con gasto potencial de $575,000 por trimestre y un ingreso trimestral estimado por hogar de $81,000.
> 
> **Top 5 para ferretería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **BENITO JUAREZ**, Nezahualcóyotl (AGEB 1505800010609): score 92.8/100. prob. de apertura 78 %; gasto potencial $482,000 por trimestre; 9.5 competidores ponderados (captura 9 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $63,600; 25 a 59 años: 48.8 %.
> 2. **FUENTES DE ARAGON**, Ecatepec de Morelos (AGEB 1503300011788): score 90.5/100. prob. de apertura 51 %; gasto potencial $575,000 por trimestre; 7.7 competidores ponderados (captura 11 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $81,000; 25 a 59 años: 50.1 %.
> 3. **CAMPESTRE GUADALUPANA**, Nezahualcóyotl (AGEB 150580001012A): score 89.3/100. prob. de apertura 52 %; gasto potencial $380,000 por trimestre; 5.8 competidores ponderados (captura 15 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $60,300; 25 a 59 años: 49.2 %.
> 4. **GABRIEL RAMOS MILLÁN SECCIÓN BRAMADERO**, Iztacalco (AGEB 0900600010467): score 88.9/100. prob. de apertura 2 %; gasto potencial $418,000 por trimestre; 4.4 competidores ponderados (captura 18 %); NSE estimado bajo, decil 1, ingreso trimestral estimado por hogar $28,700; 25 a 59 años: NO ENCONTRADO (el Censo reserva el dato). **Ojo:** AGEB con 20 habitantes: el gasto viene del radio de influencia, no de quienes viven en la AGEB.
> 5. **JORGE JIMENEZ CANTU**, Tlalnepantla de Baz (AGEB 1510400012351): score 88.4/100. prob. de apertura 30 %; gasto potencial $218,000 por trimestre; 6.2 competidores ponderados (captura 14 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $43,000; 25 a 59 años: 46.0 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - El gasto potencial usa el rubro ENIGH materiales para el mantenimiento y reparación de la vivienda completo; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 180 pesos es un supuesto (supuesto: tornillos, pintura, herramienta de mano)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 14. Una pastelería en Benito Juárez, ¿dónde?

_llm, 1 rondas, 41.9 s; herramientas: perfil_giro({"texto": "Una pastelería en Benito Juárez, ¿dónde?"}); recomendar_zonas({"giro": "pasteleria", "municipio": "Benito Juárez"}); contexto_macro({"giro": "pasteleria"}); ficha_municipio({"municipio": "Benito Juárez"})_

> **Lectura:** Entre las zonas del top de pastelería, Narvarte Poniente tiene la mayor probabilidad de apertura (15 %); Nápoles tiene el mayor gasto potencial ($5,942,000 por trimestre); Letrán Valle y Del Valle Sur empatan con la menor competencia (0.0 competidores ponderados). Nápoles destaca por tener el 63.9 % de la edad clave (25 a 59 años) y el mayor ingreso estimado.
> 
> **Top 5 para pastelería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **PIEDAD NARVARTE**, Benito Juárez (AGEB 0901400010011): score 91.9/100. prob. de apertura 7 %; gasto potencial $4,935,000 por trimestre; 0.3 competidores ponderados (captura 79 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $136,300; 25 a 59 años: 60.9 %.
> 2. **LETRÁN VALLE**, Benito Juárez (AGEB 090140001076A): score 88.4/100. prob. de apertura 7 %; gasto potencial $3,951,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $171,200; 25 a 59 años: 60.0 %.
> 3. **NÁPOLES**, Benito Juárez (AGEB 0901400010204): score 87.4/100. prob. de apertura 6 %; gasto potencial $5,942,000 por trimestre; 0.2 competidores ponderados (captura 80 %); NSE estimado alto, decil 10, ingreso trimestral estimado por hogar $174,000; 25 a 59 años: 63.9 %.
> 4. **DEL VALLE SUR**, Benito Juárez (AGEB 0901400010755): score 86.2/100. prob. de apertura 9 %; gasto potencial $4,156,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $161,200; 25 a 59 años: 56.3 %.
> 5. **NARVARTE PONIENTE**, Benito Juárez (AGEB 0901400010079): score 80.6/100. prob. de apertura 15 %; gasto potencial $5,231,000 por trimestre; 1.3 competidores ponderados (captura 43 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $120,500; 25 a 59 años: 59.1 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Sobre Benito Juárez:** Población en AGEB urbanas: 434,153 habitantes (lugar 18 de 76 en la ZMVM). Densidad: 16,353 hab/km² (lugar 4 de 76). Edad: 0-14 años 11.8 %; 15-24 10.2 %; 25-59 57.9 %; 60 o más 20.1 %. Ingreso trimestral mediano estimado por hogar en Benito Juárez: $142,100 (decil típico 9; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 350 pesos es un supuesto (supuesto: pastel chico o rebanadas y postres para una reunion)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411); carpetas/03_municipios (fichas generadas desde agebs_features).

### 15. Quiero poner una librería

_llm, 1 rondas, 29.6 s; herramientas: perfil_giro({"texto": "Quiero poner una librería"}); recomendar_zonas({"giro": "libreria"}); contexto_macro({"giro": "libreria"})_

> **Lectura:** Entre las zonas del top de librería, Álamos tiene el mayor gasto potencial ($6,436,000 por trimestre); Tacuba y Ampliación Gabriel Ramos Millán empatan con la menor competencia (0.0 competidores ponderados).
> 
> **Top 5 para librería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 15.9 % de la población tiene de 15 a 24 años (Censo 2020).
> 
> 1. **TACUBA**, Miguel Hidalgo (AGEB 0901600010162): score 98.3/100. prob. de apertura 2 %; gasto potencial $5,560,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $109,100; 15 a 24 años: 11.2 %.
> 2. **POPOTLA**, Miguel Hidalgo (AGEB 0901600010177): score 97.5/100. prob. de apertura 3 %; gasto potencial $5,979,000 por trimestre; 0.2 competidores ponderados (captura 82 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $98,600; 15 a 24 años: 12.0 %.
> 3. **ALAMOS**, Benito Juárez (AGEB 0901400010030): score 96.6/100. prob. de apertura 2 %; gasto potencial $6,436,000 por trimestre; 0.7 competidores ponderados (captura 58 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $130,200; 15 a 24 años: 9.8 %.
> 4. **SAN ÁLVARO**, Azcapotzalco (AGEB 090020001081A): score 95.7/100. prob. de apertura 3 %; gasto potencial $4,553,000 por trimestre; 0.4 competidores ponderados (captura 73 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $99,500; 15 a 24 años: 10.8 %.
> 5. **AMPLIACIÓN GABRIEL RAMOS MILLÁN**, Iztacalco (AGEB 0900600010700): score 95.2/100. prob. de apertura 1 %; gasto potencial $3,788,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $71,000; 15 a 24 años: 15.9 %.
> 
> **Ojo:** probabilidad de apertura baja en todo el top (1 a 3 %); en la ZMVM apareció en el 3 % de las AGEB: el score alto solo dice que estas son las mejores zonas PARA ESTE GIRO, no que el giro sea viable.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 260 pesos es un supuesto (supuesto: uno o dos libros)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 16. Quiero un negocio de renta de bicicletas, ¿dónde lo pongo?

_llm, 1 rondas, 32.5 s; herramientas: perfil_giro({"texto": "Quiero un negocio de renta de bicicletas, ¿dónde lo pongo?"}); recomendar_zonas({"giro": "renta_bicicletas"}); contexto_macro({"giro": "renta_bicicletas"})_

> **Lectura:** Entre las zonas del top de renta de bicicletas, Narvarte Poniente tiene el mayor gasto potencial ($110,640,000 por trimestre).
> 
> **Top 5 para renta de bicicletas** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **SAN RAFAEL**, Cuauhtémoc (AGEB 0901500010682): score 98.4/100. prob. de apertura 0 %; gasto potencial $75,307,000 por trimestre (proxy: todo el gasto en esparcimiento, no solo renta de bicicletas); 0.0 competidores ponderados (captura 100 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $115,600; 25 a 59 años: 61.0 %.
> 2. **ROMA SUR**, Cuauhtémoc (AGEB 0901500011360): score 98.2/100. prob. de apertura 0 %; gasto potencial $92,893,000 por trimestre (proxy: todo el gasto en esparcimiento, no solo renta de bicicletas); 0.0 competidores ponderados (captura 100 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $127,200; 25 a 59 años: 61.6 %.
> 3. **TABACALERA**, Cuauhtémoc (AGEB 0901500010729): score 98.1/100. prob. de apertura 0 %; gasto potencial $57,642,000 por trimestre (proxy: todo el gasto en esparcimiento, no solo renta de bicicletas); 0.0 competidores ponderados (captura 100 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $165,600; 25 a 59 años: 76.6 %.
> 4. **SANTA MARÍA LA RIBERA**, Cuauhtémoc (AGEB 0901500010593): score 97.8/100. prob. de apertura 0 %; gasto potencial $75,954,000 por trimestre (proxy: todo el gasto en esparcimiento, no solo renta de bicicletas); 0.0 competidores ponderados (captura 100 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $101,700; 25 a 59 años: 53.4 %.
> 5. **NARVARTE PONIENTE**, Benito Juárez (AGEB 0901400010079): score 97.7/100. prob. de apertura 0 %; gasto potencial $110,640,000 por trimestre (proxy: todo el gasto en esparcimiento, no solo renta de bicicletas); 0.0 competidores ponderados (captura 100 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $120,500; 25 a 59 años: 59.1 %.
> 
> **Ojo:** probabilidad de apertura baja en todo el top (0 %); en la ZMVM apareció en 1 de 5,875 AGEB: el score alto solo dice que estas son las mejores zonas PARA ESTE GIRO, no que el giro sea viable.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - No hay rubro de renta de bicicletas en la ENIGH; se usa esparcimiento como proxy de gasto discrecional.
> - Giro raro: solo 1 AGEB con aperturas 2020-2026; el modelo es poco confiable
> - El gasto potencial usa el rubro ENIGH esparcimiento como sustituto del giro; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 17. Quiero poner un negocio en Coyoacán, ¿qué me recomiendas y dónde?

_llm, 1 rondas, 62.3 s; herramientas: perfil_giro({"texto": "Quiero poner un negocio en Coyoacán, ¿qué me recomiendas y dónde?"}); sugerir_giros({"municipio": "Coyoacán"}); recomendar_zonas({"giro": "abarrotes", "municipio": "Coyoacán"}); ficha_municipio({"municipio": "Coyoacán"})_

> **Lectura:** El giro de abarrotes lidera con mayor viabilidad en Coyoacán, destacando la colonia Culhuacán CTM Sección IX-A con un gasto potencial de $17,067,000 por trimestre y una probabilidad de apertura del 99 %. La colonia Ex-Ejido de San Francisco Culhuacán tiene el mayor ingreso trimestral estimado por hogar ($150,100) y menor competencia (2.9 competidores ponderados).
> 
> **Giros que conviene considerar** (en orden de viabilidad = prob. de apertura × prob. de seguir abierto; el score de las colonias es relativo dentro de cada giro y no compara giros)
> 1. tienda de abarrotes: viabilidad 69 %, prob. de apertura 91 %, prob. de seguir abierto 75 %.
> 2. consultorio dental: viabilidad 59 %, prob. de apertura 79 %, prob. de seguir abierto 74 %.
> 3. tortillería: viabilidad 55 %, prob. de apertura 71 %, prob. de seguir abierto 78 %.
> 4. frutería: viabilidad 55 %, prob. de apertura 77 %, prob. de seguir abierto 71 %.
> 5. carnicería: viabilidad 53 %, prob. de apertura 73 %, prob. de seguir abierto 73 %.
> 
> **Top 5 para tienda de abarrotes** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **CULHUACÁN CTM SECCIÓN IX-A**, Coyoacán (AGEB 0900300011497): score 88.2/100. prob. de apertura 99 %; gasto potencial $17,067,000 por trimestre; 8.0 competidores ponderados (captura 11 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $102,900; 25 a 59 años: 47.0 %.
> 2. **CULHUACÁN CTM CROC**, Coyoacán (AGEB 0900300011745): score 84.9/100. prob. de apertura 88 %; gasto potencial $15,882,000 por trimestre; 6.0 competidores ponderados (captura 14 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $99,100; 25 a 59 años: 52.8 %.
> 3. **EMILIANO ZAPATA**, Coyoacán (AGEB 0900300011406): score 78.9/100. prob. de apertura 98 %; gasto potencial $13,199,000 por trimestre; 13.1 competidores ponderados (captura 7 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $68,400; 25 a 59 años: 48.5 %.
> 4. **CULHUACÁN CTM SECCIÓN VI**, Coyoacán (AGEB 0900300011270): score 78.7/100. prob. de apertura 90 %; gasto potencial $17,018,000 por trimestre; 6.8 competidores ponderados (captura 13 %); NSE estimado medio, decil 7, ingreso trimestral estimado por hogar $94,900; 25 a 59 años: 48.8 %.
> 5. **EX-EJIDO DE SAN FRANCISCO CULHUACÁN**, Coyoacán (AGEB 0900300010516): score 78.2/100. prob. de apertura 78 %; gasto potencial $7,590,000 por trimestre; 2.9 competidores ponderados (captura 26 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $150,100; 25 a 59 años: 47.8 %.
> 
> **Sobre Coyoacán:** Población en AGEB urbanas: 614,447 habitantes (lugar 10 de 76 en la ZMVM). Densidad: 11,459 hab/km² (lugar 15 de 76). Edad: 0-14 años 14.9 %; 15-24 14.1 %; 25-59 50.4 %; 60 o más 20.6 %. Ingreso trimestral mediano estimado por hogar en Coyoacán: $110,800 (decil típico 8; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - El gasto potencial usa el rubro ENIGH alimentos dentro del hogar completo; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 55 pesos es un supuesto (supuesto: compra de reposicion diaria)
> - La probabilidad de seguir abierto viene de un modelo débil (AUC 0.59): mide rotación, no rentabilidad.
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); carpetas/03_municipios (fichas generadas desde agebs_features).

### 18. Quiero algo barato para una zona de nivel bajo, ¿qué pongo y dónde?

_llm, 1 rondas, 49.4 s; herramientas: perfil_giro({"texto": "Quiero algo barato para una zona de nivel bajo, ¿qué pongo y dónde?"}); sugerir_giros({"nse": "bajo", "inversion": "baja"}); recomendar_zonas({"giro": "abarrotes", "nse": "bajo"})_

> **Lectura:** El giro de abarrotes lidera con mayor viabilidad, destacando la colonia Infonavit Norte Sección 1 con un gasto potencial de $16,730,000 por trimestre y una probabilidad de apertura del 98 %. La colonia Guadalupe Victoria destaca por tener el mayor ingreso trimestral estimado por hogar ($57,900) y una alta concentración de la edad clave (25 a 59 años, 49.2 %).
> 
> **Giros que conviene considerar** (en orden de viabilidad = prob. de apertura × prob. de seguir abierto; el score de las colonias es relativo dentro de cada giro y no compara giros)
> 1. tienda de abarrotes: viabilidad 64 %, prob. de apertura 85 %, prob. de seguir abierto 76 %.
> 2. barbería y estética: viabilidad 60 %, prob. de apertura 94 %, prob. de seguir abierto 64 %.
> 3. tortillería: viabilidad 55 %, prob. de apertura 71 %, prob. de seguir abierto 78 %.
> 4. carnicería: viabilidad 47 %, prob. de apertura 71 %, prob. de seguir abierto 67 %.
> 5. frutería: viabilidad 41 %, prob. de apertura 61 %, prob. de seguir abierto 66 %.
> **Nota sobre «barato»:** «barato» se entendió como poca inversión inicial. El proyecto NO tiene la inversión por giro (NO ENCONTRADO; el catálogo solo trae el ticket por venta, que no mide el costo de abrir). Aproximación: giros cuyo establecimiento típico es de los más chicos del DENUE (personal ocupado medio por establecimiento, tercio inferior de los giros del catálogo).
> 
> **Top 5 para tienda de abarrotes** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **CHINAMPAC DE JUÁREZ**, Iztapalapa (AGEB 090070001579A): score 87.6/100. prob. de apertura 29 %; gasto potencial $16,196,000 por trimestre; 15.1 competidores ponderados (captura 6 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $55,000; 25 a 59 años: 48.1 %.
> 2. **INFONAVIT NORTE SECCIÓN 1**, Cuautitlán Izcalli (AGEB 1512100010765): score 86.0/100. prob. de apertura 98 %; gasto potencial $16,730,000 por trimestre; 13.9 competidores ponderados (captura 7 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $51,800; 25 a 59 años: 46.5 %.
> 3. **GUADALUPE VICTORIA**, Ecatepec de Morelos (AGEB 1503300014496): score 85.9/100. prob. de apertura 93 %; gasto potencial $7,178,000 por trimestre; 4.4 competidores ponderados (captura 19 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $57,900; 25 a 59 años: 49.2 %.
> 4. **TERCERA UNIDAD JOSÉ MARÍA MORELOS (UNIDAD MORELOS TERCERA SECCIÓN)**, Tultitlán (AGEB 1510900251650): score 84.7/100. prob. de apertura 100 %; gasto potencial $10,970,000 por trimestre; 8.6 competidores ponderados (captura 10 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $57,200; 25 a 59 años: 49.2 %.
> 5. **SAN MARCOS HUIXTOCO**, Chalco (AGEB 150250013195A): score 84.4/100. prob. de apertura 98 %; gasto potencial $5,989,000 por trimestre; 6.7 competidores ponderados (captura 13 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $51,400; 25 a 59 años: 44.1 %.
> 
> **Riesgos:**
> - El gasto potencial usa el rubro ENIGH alimentos dentro del hogar completo; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 55 pesos es un supuesto (supuesto: compra de reposicion diaria)
> - La probabilidad de seguir abierto viene de un modelo débil (AUC 0.59): mide rotación, no rentabilidad.
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).

### 19. ¿Cómo está la economía para abrir un negocio? Inflación, tasa de Banxico y tipo de cambio

_llm, 1 rondas, 52.6 s; herramientas: perfil_giro({"texto": "¿Cómo está la economía para abrir un negocio? Inflación, tasa de Banxico y tipo de cambio"}); contexto_macro({})_

> **Lectura:** La economía muestra una tasa objetivo de Banxico en 6.25 % anual, inflación general en 3.75 % anual y tipo de cambio FIX en 19.16 MXN por USD. La tasa real aproximada es de 2.5 puntos porcentuales.
> 
> **Indicadores (valores nacionales):**
> - tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745)
> - TIIE a 28 días 6.51 % anual (2026-11-23, serie SF43783)
> - tipo de cambio FIX 19.16 pesos por dólar (2026-11-23, serie SF43718)
> - inflación general (INPC) 3.75 % anual (2026-10, serie 910406)
> - inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411)
> - remesas 5,362 millones de dólares al mes (2026-09, serie SE27803)
> - confianza del consumidor 45.19 puntos del índice (2026-10, serie 454168)
> - consumo privado (IMCP) 1.34 % anual (cifras originales) (2026-08, serie 740946)
> 
> **Cómo influye en el negocio:**
> - La tasa objetivo de Banxico es la tasa de política, no la que paga el negocio: los bancos prestan a la TIIE, que la sigue de cerca, más un margen (que no está en los datos). Con tasa alta cuesta más financiar el equipo, el local y el inventario.
> - La TIIE a 28 días es la referencia de los créditos empresariales: si sube, el financiamiento del negocio sale más caro.
> - La inflación general sube el costo de la renta, los servicios y los insumos, y le quita poder de compra al cliente: el negocio absorbe el aumento en su margen o lo traslada al precio y vende menos.
> - Con la tasa objetivo en 6.25 % anual y la inflación general en 3.75 % anual, la tasa real aproximada es de 2.5 puntos porcentuales (tasa objetivo menos inflación anual); la tasa de política va por encima de la inflación, así que el dinero tiene un costo real positivo, y el crédito del negocio, que se paga a la TIIE más un margen, sale todavía más caro.
> - Un dólar más caro encarece los insumos y el equipo importados y aprieta el margen si no se puede subir el precio.
> - Las remesas sostienen el ingreso de los hogares que las reciben y con ello su gasto en el comercio local.
> - Cuando baja la confianza del consumidor, los hogares posponen gastos que no son indispensables.
> - El consumo privado es la demanda total de los hogares: si crece, hay más ventas para el comercio y los servicios.
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, SCIAN 2023 (data/processed/scian.csv); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Banco de México, SIE API (serie SE27803); Banco de México, SIE API (serie SF43718); Banco de México, SIE API (serie SF43783); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 454168); INEGI, Banco de Indicadores API (BIE, id 740946); INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411).

### 20. Quiero poner una heladería en Monterrey

_llm, 1 rondas, 34.5 s; herramientas: perfil_giro({"texto": "Quiero poner una heladería en Monterrey"}); recomendar_zonas({"giro": "heladeria", "municipio": "Monterrey"}); buscar_carpetas({"pregunta": "Quiero poner una heladería en Monterrey", "k": 2})_

> La ubicación de una heladería en Monterrey está **fuera de alcance** del modelo, ya que Monterrey no forma parte de la Zona Metropolitana del Valle de México (ZMVM). El modelo solo cubre las 16 alcaldías de la Ciudad de México, 59 municipios del Estado de México y Tizayuca, Hidalgo. 
> 
> Si deseas evaluar la viabilidad de una heladería en una zona dentro de la ZMVM, por favor proporciona el municipio o colonia específico donde deseas ubicarla.
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); SEDATU-CONAPO-INEGI, delimitación de zonas metropolitanas 2015 (data/processed/zmvm_municipios.csv); carpetas/00_alcance.md.

### 21. Quiero abrir una nevería en Polanco

_llm, 1 rondas, 49.3 s; herramientas: perfil_giro({"texto": "Quiero abrir una nevería en Polanco"}); recomendar_zonas({"giro": "heladeria", "colonia": "Polanco"}); contexto_macro({"giro": "heladeria"}); ficha_municipio({"municipio": "Miguel Hidalgo"})_

> > Filtro por colonia: «Polanco» (Miguel Hidalgo; 12 AGEB). El top se limita a las AGEB de esa colonia y a las que están a 2 km o menos de su centroide; hay al menos 3 zonas de la colonia misma (si las tiene) y cada zona dice si está dentro y a cuántos km queda.
> 
> Tomé «nevería» como heladería, el giro más cercano del catálogo.
> 
> **Lectura:** Entre las zonas del top de heladería, Polanco V Sección tiene la mayor probabilidad de apertura (50 %) y el mayor gasto potencial ($145,000 por trimestre); Polanco IV Sección, Granada y Polanco I Sección empatan con la menor competencia (0.0 competidores ponderados).
> 
> **Top 5 para heladería (nevería)** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).
> 
> 1. **POLANCO IV SECCIÓN**, Miguel Hidalgo (AGEB 0901600010656): score 76.4/100. prob. de apertura 23 %; gasto potencial $109,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado alto, decil 10, ingreso trimestral estimado por hogar $192,600; 0 a 14 años: 14.1 %. Dentro de Polanco.
> 2. **5 DE MAYO**, Miguel Hidalgo (AGEB 090160001132A): score 71.8/100. prob. de apertura 16 %; gasto potencial $95,000 por trimestre; 1.4 competidores ponderados (captura 41 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $67,700; 0 a 14 años: 16.8 %. A 1.8 km de Polanco.
> 3. **GRANADA**, Miguel Hidalgo (AGEB 0901600010571): score 70.2/100. prob. de apertura 21 %; gasto potencial $140,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $169,400; 0 a 14 años: 12.1 %. A 1.0 km de Polanco.
> 4. **POLANCO V SECCIÓN**, Miguel Hidalgo (AGEB 0901600010660): score 59.1/100. prob. de apertura 50 %; gasto potencial $145,000 por trimestre; 1.1 competidores ponderados (captura 47 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $166,300; 0 a 14 años: 13.1 %. Dentro de Polanco.
> 5. **POLANCO I SECCIÓN**, Miguel Hidalgo (AGEB 0901600010622): score 56.4/100. prob. de apertura 22 %; gasto potencial $115,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $162,900; 0 a 14 años: 20.8 %. Dentro de Polanco.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Sobre Miguel Hidalgo:** Población en AGEB urbanas: 414,470 habitantes (lugar 21 de 76 en la ZMVM). Densidad: 8,980 hab/km² (lugar 23 de 76). Edad: 0-14 años 15.1 %; 15-24 12.0 %; 25-59 54.3 %; 60 o más 17.2 %. Ingreso trimestral mediano estimado por hogar en Miguel Hidalgo: $104,800 (decil típico 8; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - El rubro de helados de la ENIGH es consumo en casa y solo 2-7 % de hogares reporta gasto; sirve para ordenar deciles, no para dimensionar.
> - El gasto potencial usa el rubro ENIGH helados, nieves y paletas de hielo (consumo en casa) como sustituto del giro; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 70 pesos es un supuesto (supuesto: una nieve o helado artesanal individual, 2026)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411); carpetas/03_municipios (fichas generadas desde agebs_features).

### 22. ¿Dónde pongo una cafetería en la Condesa?

_llm, 1 rondas, 67.0 s; herramientas: perfil_giro({"texto": "¿Dónde pongo una cafetería en la Condesa?"}); recomendar_zonas({"giro": "cafeteria", "colonia": "la Condesa"}); contexto_macro({"giro": "cafeteria"}); ficha_municipio({"municipio": "Cuauhtémoc"})_

> > Filtro por colonia: «La Condesa» (Cuauhtémoc; 11 AGEB). El top se limita a las AGEB de esa colonia y a las que están a 2 km o menos de su centroide; hay al menos 3 zonas de la colonia misma (si las tiene) y cada zona dice si está dentro y a cuántos km queda.
> 
> **Lectura:** Entre las zonas del top de cafetería, Hipódromo tiene la mayor probabilidad de apertura (99 %); Roma Sur tiene el mayor gasto potencial ($19,613,000 por trimestre); Escandón I Sección tiene la menor competencia (4.6 competidores ponderados).
> 
> **Top 5 para cafetería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **ESCANDÓN I SECCIÓN**, Miguel Hidalgo (AGEB 0901600011211): score 91.6/100. prob. de apertura 92 %; gasto potencial $18,344,000 por trimestre; 4.6 competidores ponderados (captura 18 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $104,800; 25 a 59 años: 56.8 %. A 1.6 km de la Condesa.
> 2. **ROMA SUR**, Cuauhtémoc (AGEB 0901500011464): score 90.2/100. prob. de apertura 72 %; gasto potencial $19,613,000 por trimestre; 5.4 competidores ponderados (captura 16 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $126,900; 25 a 59 años: 60.5 %. A 1.5 km de la Condesa.
> 3. **CONDESA**, Cuauhtémoc (AGEB 0901500011178): score 86.1/100. prob. de apertura 91 %; gasto potencial $15,225,000 por trimestre; 5.8 competidores ponderados (captura 15 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $129,900; 25 a 59 años: 62.3 %. Dentro de la Condesa.
> 4. **HIPÓDROMO**, Cuauhtémoc (AGEB 090150001120A): score 78.0/100. prob. de apertura 99 %; gasto potencial $11,711,000 por trimestre; 16.1 competidores ponderados (captura 6 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $147,900; 25 a 59 años: 70.4 %. Dentro de la Condesa.
> 5. **HIPÓDROMO CONDESA**, Cuauhtémoc (AGEB 0901500011411): score 77.3/100. prob. de apertura 94 %; gasto potencial $12,604,000 por trimestre; 7.4 competidores ponderados (captura 12 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $154,500; 25 a 59 años: 62.7 %. Dentro de la Condesa.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Sobre Cuauhtémoc:** Población en AGEB urbanas: 545,884 habitantes (lugar 11 de 76 en la ZMVM). Densidad: 16,882 hab/km² (lugar 3 de 76). Edad: 0-14 años 15.3 %; 15-24 12.8 %; 25-59 54.7 %; 60 o más 17.2 %. Ingreso trimestral mediano estimado por hogar en Cuauhtémoc: $77,800 (decil típico 6; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - El rubro de café y bebidas de la ENIGH es café para preparar en casa; el consumo en cafetería cae en alimentos y bebidas fuera del hogar (restaurantes y similares).
> - El gasto potencial usa el rubro ENIGH alimentos y bebidas consumidos fuera del hogar completo; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 95 pesos es un supuesto (supuesto: una bebida y un alimento ligero)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411); carpetas/03_municipios (fichas generadas desde agebs_features).

### 23. Quiero abrir una farmacia en Santa Fe

_llm, 1 rondas, 55.6 s; herramientas: perfil_giro({"texto": "Quiero abrir una farmacia en Santa Fe"}); recomendar_zonas({"giro": "farmacia", "colonia": "Santa Fe"}); contexto_macro({"giro": "farmacia"})_

> > Filtro por colonia: «Santa Fe» (Álvaro Obregón, Cuajimalpa de Morelos; 8 AGEB). El top se limita a las AGEB de esa colonia y a las que están a 2 km o menos de su centroide; hay al menos 3 zonas de la colonia misma (si las tiene) y cada zona dice si está dentro y a cuántos km queda.
> 
> **Lectura:** Entre las zonas del top de farmacia, Santa Fe Cuajimalpa tiene la mayor probabilidad de apertura (91 %); Punta de Ceguaya tiene el mayor gasto potencial ($1,116,000 por trimestre); Santa Fe la Loma tiene la menor competencia (0.0 competidores ponderados). Santa Fe la Loma destaca por tener menor competencia (0.0 competidores ponderados) y una probabilidad de apertura del 9 %.
> 
> **Top 5 para farmacia** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 13.8 % de la población tiene 60 años o más (Censo 2020).
> 
> 1. **SANTA FE**, Álvaro Obregón (AGEB 0901000010309): score 79.3/100. prob. de apertura 44 %; gasto potencial $639,000 por trimestre; 0.2 competidores ponderados (captura 82 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $77,700; 60 años o más: 16.5 %. Dentro de Santa Fe.
> 2. **SANTA LUCIA**, Álvaro Obregón (AGEB 0901000012305): score 72.6/100. prob. de apertura 43 %; gasto potencial $733,000 por trimestre; 1.0 competidores ponderados (captura 49 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $45,400; 60 años o más: 10.8 %. A 1.5 km de Santa Fe.
> 3. **PUNTA DE CEGUAYA**, Álvaro Obregón (AGEB 0901000012023): score 68.3/100. prob. de apertura 35 %; gasto potencial $1,116,000 por trimestre; 1.6 competidores ponderados (captura 39 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $52,900; 60 años o más: 11.5 %. A 1.7 km de Santa Fe.
> 4. **SANTA FE LA LOMA**, Álvaro Obregón (AGEB 0901000012358): score 35.0/100. prob. de apertura 9 %; gasto potencial $436,000 por trimestre; 0.0 competidores ponderados (captura 100 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $162,800; 60 años o más: 9.9 %. Dentro de Santa Fe.
> 5. **SANTA FE CUAJIMALPA**, Cuajimalpa de Morelos (AGEB 0900400010369): score 27.0/100. prob. de apertura 91 %; gasto potencial $998,000 por trimestre; 2.8 competidores ponderados (captura 26 %); NSE estimado alto, decil 10, ingreso trimestral estimado por hogar $229,200; 60 años o más: 7.1 %. Dentro de Santa Fe.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 190 pesos es un supuesto (supuesto: medicamento de receta o patente más un artículo de cuidado personal)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 24. Quiero abrir una papelería en la colonia Villa Esperanza Imaginaria

_llm, 1 rondas, 33.6 s; herramientas: perfil_giro({"texto": "Quiero abrir una papelería en la colonia Villa Esperanza Imaginaria"}); recomendar_zonas({"giro": "papeleria", "colonia": "Villa Esperanza Imaginaria"}); contexto_macro({"giro": "papeleria"})_

> > NO ENCONTRADO: «Villa Esperanza Imaginaria» no aparece como colonia o asentamiento (en la ZMVM). A cambio se muestra el top del giro en toda la ZMVM, SIN filtro de colonia. ¿Quisiste decir: Esperanza (Nezahualcóyotl); España (Hueypoxtla)?
> 
> **Lectura:** Entre las zonas del top de papelería, Juan Escutia tiene la mayor probabilidad de apertura (92 %); Nonoalco Tlatelolco tiene el mayor gasto potencial ($1,191,000 por trimestre); Tacubaya tiene la menor competencia (1.8 competidores ponderados). Juan Escutia destaca por tener la mayor probabilidad de apertura (92 %) y una edad clave de 0 a 14 años con 19.4 %.
> 
> **Top 5 para papelería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).
> 
> 1. **BENITO JUAREZ**, Nezahualcóyotl (AGEB 1505800010577): score 95.7/100. prob. de apertura 91 %; gasto potencial $828,000 por trimestre; 4.2 competidores ponderados (captura 19 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $67,500; 0 a 14 años: 18.2 %.
> 2. **NONOALCO TLATELOLCO**, Cuauhtémoc (AGEB 0901500010324): score 94.5/100. prob. de apertura 9 %; gasto potencial $1,191,000 por trimestre; 1.9 competidores ponderados (captura 34 %); NSE estimado medio, decil 7, ingreso trimestral estimado por hogar $92,000; 0 a 14 años: 10.4 %.
> 3. **EX HIPÓDROMO DE PERALVILLO**, Cuauhtémoc (AGEB 0901500010150): score 94.2/100. prob. de apertura 50 %; gasto potencial $795,000 por trimestre; 2.1 competidores ponderados (captura 33 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $73,100; 0 a 14 años: 17.1 %.
> 4. **TACUBAYA**, Miguel Hidalgo (AGEB 0901600011175): score 93.3/100. prob. de apertura 65 %; gasto potencial $817,000 por trimestre; 1.8 competidores ponderados (captura 35 %); NSE estimado medio, decil 8, ingreso trimestral estimado por hogar $104,800; 0 a 14 años: 11.1 %.
> 5. **JUAN ESCUTIA**, Iztapalapa (AGEB 0900700010017): score 92.9/100. prob. de apertura 92 %; gasto potencial $669,000 por trimestre; 3.3 competidores ponderados (captura 23 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $73,600; 0 a 14 años: 19.4 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 60 pesos es un supuesto (supuesto: copias, cuadernos y útiles sueltos; sube en temporada escolar)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406).

### 25. ¿Y en Coyoacán?

_llm, 1 rondas, 54.7 s; herramientas: perfil_giro({"texto": "heladeria"}); recomendar_zonas({"giro": "heladeria", "municipio": "Coyoacán"}); contexto_macro({"giro": "heladeria"}); ficha_municipio({"municipio": "Coyoacán"})_

> Sigo con heladería (de tu pregunta anterior).
> 
> **Lectura:** En Coyoacán, las colonias con mejor score para heladería son Ajusco y Pedregal de Santo Domingo. Ajusco lidera con un ingreso trimestral estimado por hogar de $70,800 y una probabilidad de apertura del 60 %. Pedregal de Santo Domingo destaca por tener el mayor gasto potencial por trimestre, de $98,000. Ambas tienen un NSE estimado medio y una población con un alto porcentaje de niños de 0 a 14 años.
> 
> **Top 5 para heladería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).
> 
> 1. **AJUSCO**, Coyoacán (AGEB 0900300010817): score 88.8/100. prob. de apertura 60 %; gasto potencial $62,000 por trimestre; 0.3 competidores ponderados (captura 76 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $70,800; 0 a 14 años: 16.5 %.
> 2. **PEDREGAL DE SANTO DOMINGO**, Coyoacán (AGEB 0900300010802): score 86.7/100. prob. de apertura 54 %; gasto potencial $98,000 por trimestre; 1.0 competidores ponderados (captura 50 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $58,900; 0 a 14 años: 20.2 %.
> 3. **EMILIANO ZAPATA**, Coyoacán (AGEB 0900300011393): score 83.3/100. prob. de apertura 14 %; gasto potencial $73,000 por trimestre; 0.4 competidores ponderados (captura 70 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $65,100; 0 a 14 años: 19.4 %.
> 4. **CARMEN SERDÁN**, Coyoacán (AGEB 0900300011389): score 82.3/100. prob. de apertura 27 %; gasto potencial $79,000 por trimestre; 0.9 competidores ponderados (captura 53 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $48,500; 0 a 14 años: 21.6 %.
> 5. **SAN FRANCISCO CULHUACÁN BARRIO DE SAN FRANCISCO**, Coyoacán (AGEB 0900300010357): score 77.6/100. prob. de apertura 37 %; gasto potencial $51,000 por trimestre; 0.4 competidores ponderados (captura 70 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $55,400; 0 a 14 años: 17.1 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Sobre Coyoacán:** Población en AGEB urbanas: 614,447 habitantes (lugar 10 de 76 en la ZMVM). Densidad: 11,459 hab/km² (lugar 15 de 76). Edad: 0-14 años 14.9 %; 15-24 14.1 %; 25-59 50.4 %; 60 o más 20.6 %. Ingreso trimestral mediano estimado por hogar en Coyoacán: $110,800 (decil típico 8; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - El rubro de helados de la ENIGH es consumo en casa y solo 2-7 % de hogares reporta gasto; sirve para ordenar deciles, no para dimensionar.
> - El gasto potencial usa el rubro ENIGH helados, nieves y paletas de hielo (consumo en casa) como sustituto del giro; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 70 pesos es un supuesto (supuesto: una nieve o helado artesanal individual, 2026)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411); carpetas/03_municipios (fichas generadas desde agebs_features).

### 26. ¿Y una veterinaria?

_llm, 1 rondas, 47.6 s; herramientas: perfil_giro({"texto": "¿Y una veterinaria?"}); recomendar_zonas({"giro": "veterinaria", "municipio": "Benito Juárez"}); contexto_macro({"giro": "veterinaria"}); ficha_municipio({"municipio": "Benito Juárez"})_

> Sigo con Benito Juárez (de tu pregunta anterior).
> 
> **Lectura:** Entre las zonas del top de veterinaria, Narvarte Oriente tiene la mayor probabilidad de apertura (57 %); Del Valle Norte tiene el mayor gasto potencial ($1,541,000 por trimestre); Del Valle Centro tiene la menor competencia (6.5 competidores ponderados). Del Valle Centro lidera con el ingreso trimestral estimado por hogar de $172,600.
> 
> **Top 5 para veterinaria** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **DEL VALLE NORTE**, Benito Juárez (AGEB 0901400010223): score 76.0/100. prob. de apertura 42 %; gasto potencial $1,541,000 por trimestre; 7.8 competidores ponderados (captura 11 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $139,800; 25 a 59 años: 59.7 %.
> 2. **NARVARTE ORIENTE**, Benito Juárez (AGEB 0901400010276): score 73.4/100. prob. de apertura 57 %; gasto potencial $1,465,000 por trimestre; 13.8 competidores ponderados (captura 7 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $142,100; 25 a 59 años: 60.0 %.
> 3. **DEL VALLE CENTRO**, Benito Juárez (AGEB 0901400010399): score 73.2/100. prob. de apertura 32 %; gasto potencial $1,430,000 por trimestre; 6.5 competidores ponderados (captura 13 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $172,600; 25 a 59 años: 55.8 %.
> 4. **PIEDAD NARVARTE**, Benito Juárez (AGEB 0901400010026): score 71.8/100. prob. de apertura 42 %; gasto potencial $1,004,000 por trimestre; 10.3 competidores ponderados (captura 9 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $131,600; 25 a 59 años: 61.5 %.
> 5. **AMPLIACIÓN NÁPOLES**, Benito Juárez (AGEB 0901400010384): score 71.7/100. prob. de apertura 46 %; gasto potencial $1,486,000 por trimestre; 8.0 competidores ponderados (captura 11 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $169,100; 25 a 59 años: 62.4 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406).
> 
> **Sobre Benito Juárez:** Población en AGEB urbanas: 434,153 habitantes (lugar 18 de 76 en la ZMVM). Densidad: 16,353 hab/km² (lugar 4 de 76). Edad: 0-14 años 11.8 %; 15-24 10.2 %; 25-59 57.9 %; 60 o más 20.1 %. Ingreso trimestral mediano estimado por hogar en Benito Juárez: $142,100 (decil típico 9; estimación del proyecto con ENIGH 2024 y Censo 2020).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 450 pesos es un supuesto (supuesto: consulta general más alimento o vacuna)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API (BIE, id 910406); carpetas/03_municipios (fichas generadas desde agebs_features).

### 27. Quiero una heladería en Coyoacán para niños, ¿cuánto ganan ahí y qué porcentaje de la gente es menor de 14 años?

_llm, 1 rondas, 54.3 s; herramientas: perfil_giro({"texto": "Quiero una heladería en Coyoacán para niños, ¿cuánto ganan ahí y qué porcentaje de la gente es menor de 14 años?"}); recomendar_zonas({"giro": "heladeria", "municipio": "Coyoacán"}); contexto_macro({"giro": "heladeria"}); ficha_municipio({"municipio": "Coyoacán"})_

> **Lectura:** Entre las zonas del top de heladería, Ajusco tiene la mayor probabilidad de apertura (60 %) y la menor competencia (0.3 competidores ponderados); Pedregal de Santo Domingo tiene el mayor gasto potencial ($98,000 por trimestre). La colonia de Ajusco lidera con un ingreso trimestral estimado de $70,800 por hogar.
> 
> **Ingreso en Coyoacán:** el ingreso trimestral mediano estimado por hogar es de $110,800 (decil típico 8); estimación del proyecto con ENIGH 2024 y Censo 2020. En Coyoacán, 14.9 % de la población tiene de 0 a 14 años (Censo 2020).
> 
> **Top 5 para heladería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 20.7 % de la población tiene de 0 a 14 años (Censo 2020).
> 
> 1. **AJUSCO**, Coyoacán (AGEB 0900300010817): score 88.8/100. prob. de apertura 60 %; gasto potencial $62,000 por trimestre; 0.3 competidores ponderados (captura 76 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $70,800; 0 a 14 años: 16.5 %.
> 2. **PEDREGAL DE SANTO DOMINGO**, Coyoacán (AGEB 0900300010802): score 86.7/100. prob. de apertura 54 %; gasto potencial $98,000 por trimestre; 1.0 competidores ponderados (captura 50 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $58,900; 0 a 14 años: 20.2 %.
> 3. **EMILIANO ZAPATA**, Coyoacán (AGEB 0900300011393): score 83.3/100. prob. de apertura 14 %; gasto potencial $73,000 por trimestre; 0.4 competidores ponderados (captura 70 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $65,100; 0 a 14 años: 19.4 %.
> 4. **CARMEN SERDÁN**, Coyoacán (AGEB 0900300011389): score 82.3/100. prob. de apertura 27 %; gasto potencial $79,000 por trimestre; 0.9 competidores ponderados (captura 53 %); NSE estimado bajo, decil 3, ingreso trimestral estimado por hogar $48,500; 0 a 14 años: 21.6 %.
> 5. **SAN FRANCISCO CULHUACÁN BARRIO DE SAN FRANCISCO**, Coyoacán (AGEB 0900300010357): score 77.6/100. prob. de apertura 37 %; gasto potencial $51,000 por trimestre; 0.4 competidores ponderados (captura 70 %); NSE estimado bajo, decil 4, ingreso trimestral estimado por hogar $55,400; 0 a 14 años: 17.1 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Sobre Coyoacán:** Población en AGEB urbanas: 614,447 habitantes (lugar 10 de 76 en la ZMVM). Densidad: 11,459 hab/km² (lugar 15 de 76). Edad: 0-14 años 14.9 %; 15-24 14.1 %; 25-59 50.4 %; 60 o más 20.6 %.
> 
> **Riesgos:**
> - El rubro de helados de la ENIGH es consumo en casa y solo 2-7 % de hogares reporta gasto; sirve para ordenar deciles, no para dimensionar.
> - El gasto potencial usa el rubro ENIGH helados, nieves y paletas de hielo (consumo en casa) como sustituto del giro; sirve para ordenar zonas dentro del giro, no para comparar entre giros
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 70 pesos es un supuesto (supuesto: una nieve o helado artesanal individual, 2026)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411); carpetas/03_municipios (fichas generadas desde agebs_features).

### 28. Quiero abrir una taquería, ¿cómo influyen la inflación y la tasa de Banxico?

_llm, 1 rondas, 43.3 s; herramientas: perfil_giro({"texto": "Quiero abrir una taquería, ¿cómo influyen la inflación y la tasa de Banxico?"}); contexto_macro({"giro": "taqueria"}); recomendar_zonas({"giro": "taqueria"})_

> **Lectura:** La inflación general (INPC) de 3.75 % anual (2026-10) y la tasa objetivo de Banxico de 6.25 % anual (2026-11) influyen en la taquería al subir el costo de los insumos y la renta, y al hacer más cara la financiación. La tasa real aproximada es de 2.5 puntos porcentuales, lo que significa que el crédito del negocio sale más caro.
> 
> **Top 5 para taquería** (score 0-100 relativo al giro)
> 
> Referencia: en la ZMVM, 49.5 % de la población tiene de 25 a 59 años (Censo 2020).
> 
> 1. **POLANCO III SECCIÓN**, Miguel Hidalgo (AGEB 0901600010764): score 96.7/100. prob. de apertura 15 %; gasto potencial $803,000 por trimestre; 0.3 competidores ponderados (captura 79 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $157,400; 25 a 59 años: NO ENCONTRADO (el Censo reserva el dato).
> 2. **GABRIEL RAMOS MILLÁN SECCIÓN CUCHILLA**, Iztacalco (AGEB 0900600011018): score 95.2/100. prob. de apertura 21 %; gasto potencial $1,080,000 por trimestre; 1.3 competidores ponderados (captura 43 %); NSE estimado medio, decil 6, ingreso trimestral estimado por hogar $72,500; 25 a 59 años: 50.8 %.
> 3. **GABRIEL RAMOS MILLÁN SECCIÓN BRAMADERO**, Iztacalco (AGEB 0900600010734): score 94.3/100. prob. de apertura 73 %; gasto potencial $1,132,000 por trimestre; 2.6 competidores ponderados (captura 28 %); NSE estimado medio, decil 5, ingreso trimestral estimado por hogar $66,700; 25 a 59 años: 50.1 %.
> 4. **HIPÓDROMO**, Cuauhtémoc (AGEB 0901500011426): score 92.7/100. prob. de apertura 43 %; gasto potencial $1,373,000 por trimestre; 1.6 competidores ponderados (captura 38 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $142,800; 25 a 59 años: 66.4 %.
> 5. **DEL CARMEN**, Benito Juárez (AGEB 0901400010666): score 92.4/100. prob. de apertura 40 %; gasto potencial $1,785,000 por trimestre; 1.1 competidores ponderados (captura 47 %); NSE estimado alto, decil 9, ingreso trimestral estimado por hogar $130,200; 25 a 59 años: 56.9 %.
> 
> **Contexto económico:** valores nacionales: tasa objetivo de Banxico 6.25 % anual (2026-11-23, serie SF61745); inflación general (INPC) 3.75 % anual (2026-10, serie 910406); inflación de alimentos, bebidas y tabaco (INPC): NO ENCONTRADO; como aproximación, agropecuarios 2.99 % anual (2026-10, serie 910411).
> 
> **Cómo influye en el negocio:**
> - La tasa objetivo de Banxico es la tasa de política, no la que paga el negocio: los bancos prestan a la TIIE, que la sigue de cerca, más un margen (que no está en los datos). Con tasa alta cuesta más financiar el equipo, el local y el inventario.
> - La inflación general sube el costo de la renta, los servicios y los insumos, y le quita poder de compra al cliente: el negocio absorbe el aumento en su margen o lo traslada al precio y vende menos.
> - Con la tasa objetivo en 6.25 % anual y la inflación general en 3.75 % anual, la tasa real aproximada es de 2.5 puntos porcentuales (tasa objetivo menos inflación anual); la tasa de política va por encima de la inflación, así que el dinero tiene un costo real positivo, y el crédito del negocio, que se paga a la TIIE más un margen, sale todavía más caro.
> - Los insumos que más pesan en este giro (taquería) son carne, tortilla y gas (supuesto del proyecto): cuando su precio sube más que el precio que cobra el negocio, el margen se aprieta. Como aproximación del precio de los alimentos, los precios agropecuarios del INPC variaron 2.99 % anual (2026-10).
> 
> **Riesgos:**
> - «apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos
> - El NSE, el decil y el ingreso por AGEB son estimaciones del proyecto (la ENIGH no representa colonias)
> - El ticket promedio de 110 pesos es un supuesto (supuesto: 5-6 tacos y una bebida)
> 
> **Fuentes:** config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket); INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo); Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md); Banco de México, SIE API (serie SF61745); INEGI, Banco de Indicadores API; INEGI, Banco de Indicadores API (BIE, id 910406); INEGI, Banco de Indicadores API (BIE, id 910408); INEGI, Banco de Indicadores API (BIE, id 910411); INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana; INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).

