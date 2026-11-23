# Evaluación del agente (2026-11-23 15:10)

Modelo: qwen3:8b (Ollama, think=False). Preguntas: 20 de 20 (`eval/preguntas.yaml`). Script: `eval/evaluar.py`.

**Resultado: 20/20 pasan; trampa pasa → APROBADO** (criterio del contrato: ≥ 18/20 y la trampa pasa).

- Latencia: mediana 117.2 s, p90 152.6 s, máxima 172.2 s (objetivo de mediana ≤ 90 s: NO; una respuesta de más de 180 s falla).
- Memoria (MacBook Air M4, 16 GB): swap 4586.0 MB al inicio, máximo 14379.0 MB, 13565.62 MB al final; memoria libre mínima 16 % (`memory_pressure`).

## Checks

- `sin_tokens`: ningún valor de `.env` aparece en la respuesta ni en lo que regresaron las herramientas.
- `fuentes`: la respuesta tiene sección de fuentes y nombra al menos una fuente real (INEGI, DENUE, ENIGH, CONAPO, Banxico, carpetas...).
- `latencia`: ≤ 180 s.
- `top_agebs`: cada AGEB citada existe en `agebs_features`, salió de una herramienta, su colonia (de `agebs_features`) aparece en la respuesta y hay al menos 5 (o las que regresó la herramienta).
- `municipio`, `giro`, `nse`, `macro_usada`: se usó la herramienta con el giro/filtro esperado y las AGEB son del municipio pedido.
- `macro_cifras` (pregunta macro): la respuesta cita al menos 2 cifras de `contexto_macro`.
- `cifras`: a lo más 1 cifra sin origen y al menos 90 % de las cifras citadas coinciden con un número de las herramientas, con tolerancia de redondeo según los decimales escritos («0.43 millones» = 430,000; una fracción de la herramienta puede citarse como %). No se verifican enteros ≤ 10 (enumeraciones, deciles), años ni fechas.
- `trampa_fuera_de_alcance`: dice que está fuera de alcance y no da ninguna AGEB.
- `aviso_prob_baja`: si `recomendar_zonas` avisa que la prob. de apertura es baja en todo el top, la respuesta lo dice y aclara que el score es relativo al giro.
- `sin_giros_inventados`: sin `sugerir_giros`, la respuesta no habla de «viabilidad» ni lista «giros que conviene».
- `sugerir_usada`, `alternativas`, `score_relativo` (preguntas sin giro): se usó `sugerir_giros`, la respuesta nombra al menos 3 de los giros que regresó y dice que el score es relativo dentro de cada giro.

## Resultados por pregunta

| # | Pregunta | Pasa | Latencia (s) | Herramientas | Cifras ok | Checks que fallan |
|---|---|---|---|---|---|---|
| 1 | Quiero poner una heladería, ¿en qué colonias me conviene? | sí | 77.7 | perfil_giro, recomendar_zonas | 34/34 | - |
| 2 | ¿Dónde abro una cafetería de especialidad? | sí | 114.7 | perfil_giro, recomendar_zonas | 35/35 | - |
| 3 | Busco dónde poner un gimnasio, ¿qué zonas me recomiendas? | sí | 109.2 | perfil_giro, recomendar_zonas | 33/33 | - |
| 4 | Quiero abrir una farmacia en Iztapalapa | sí | 99.6 | perfil_giro, recomendar_zonas | 34/34 | - |
| 5 | ¿Dónde conviene poner una papelería? | sí | 102.1 | perfil_giro, recomendar_zonas | 35/35 | - |
| 6 | Una lavandería de autoservicio, ¿dónde la pongo? | sí | 119.0 | perfil_giro, recomendar_zonas | 33/33 | - |
| 7 | Quiero poner una veterinaria en Naucalpan | sí | 123.0 | perfil_giro, recomendar_zonas | 35/35 | - |
| 8 | ¿En qué colonias pongo una taquería? | sí | 112.7 | perfil_giro, recomendar_zonas | 38/38 | - |
| 9 | Tienda de abarrotes en Ecatepec, ¿qué colonias? | sí | 115.4 | perfil_giro, recomendar_zonas | 32/32 | - |
| 10 | Quiero abrir una barbería en una zona de nivel alto | sí | 113.2 | perfil_giro, recomendar_zonas | 32/32 | - |
| 11 | ¿Dónde pongo un consultorio dental? | sí | 141.8 | perfil_giro, recomendar_zonas | 32/32 | - |
| 12 | Quiero abrir una guardería en Tlalnepantla | sí | 152.6 | perfil_giro, recomendar_zonas | 31/31 | - |
| 13 | ¿Dónde abro una ferretería? | sí | 132.7 | perfil_giro, recomendar_zonas | 30/30 | - |
| 14 | Una pastelería en Benito Juárez, ¿dónde? | sí | 132.9 | perfil_giro, recomendar_zonas | 34/34 | - |
| 15 | Quiero poner una librería | sí | 143.0 | perfil_giro, recomendar_zonas | 31/31 | - |
| 16 | Quiero un negocio de renta de bicicletas, ¿dónde lo pongo? | sí | 164.3 | perfil_giro, recomendar_zonas | 31/31 | - |
| 17 | Quiero poner un negocio en Coyoacán, ¿qué me recomiendas y dónde? | sí | 172.2 | perfil_giro, sugerir_giros, recomendar_zonas | 46/46 | - |
| 18 | Quiero algo barato para una zona de nivel bajo, ¿qué pongo y dónde? | sí | 138.9 | perfil_giro, sugerir_giros, recomendar_zonas | 46/46 | - |
| 19 | ¿Cómo está la economía para abrir un negocio? Inflación, tasa de Banxico y tipo de cambio | sí | 59.6 | perfil_giro, contexto_macro | 16/17 | - |
| 20 | Quiero poner una heladería en Monterrey | sí | 33.5 | perfil_giro, recomendar_zonas, buscar_carpetas | 2/2 | - |

## Respuestas completas

### 1. Quiero poner una heladería, ¿en qué colonias me conviene?

_llm, 1 rondas, 77.7 s; herramientas: perfil_giro({"texto": "Quiero poner una heladería, ¿en qué colonias me conviene?"}); recomendar_zonas({"giro": "heladeria"})_

> **Top 5 para heladeria**  
> 1. **FUENTES DE ARAGON**, Ecatepec de Morelos (AGEB 1503300011773): score 93.2/100 (relativo al giro). Por qué: prob. de apertura % 63, gasto potencial por trimestre $97,000, competidores ponderados 1.2, captura % 46, residentes objetivo en el radio 2,230, empleos en el radio 1,290, NSE estimado medio.  
> 2. **AGUA AZUL**, Nezahualcóyotl (AGEB 1505800010740): score 90.0/100. Por qué: prob. de apertura % 64, gasto potencial por trimestre $65,000, competidores ponderados 0.4, captura % 72, residentes objetivo en el radio 2,030, empleos en el radio 1,120, NSE estimado medio.  
> 3. **MIXCOATL**, Iztapalapa (AGEB 0900700014202): score 89.8/100. Por qué: prob. de apertura % 34, gasto potencial por trimestre $64,000, competidores ponderados 0.2, captura % 83, residentes objetivo en el radio 2,550, empleos en el radio 1,410, NSE estimado bajo.  
> 4. **ROMA NORTE**, Cuauhtémoc (AGEB 0901500011110): score 89.7/100. Por qué: prob. de apertura % 60, gasto potencial por trimestre $112,000, competidores ponderados 0.8, captura % 55, residentes objetivo en el radio 1,490, empleos en el radio 5,440, NSE estimado medio.  
> 5. **JARDINES DE ARAGON**, Ecatepec de Morelos (AGEB 150330001174A): score 89.7/100. Por qué: prob. de apertura % 55, gasto potencial por trimestre $86,000, competidores ponderados 0.8, captura % 55, residentes objetivo en el radio 1,820, empleos en el radio 930, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: algunas colonias tienen competidores ponderados altos.  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no garantiza rentabilidad.  
> - Supuestos: el ticket promedio es un supuesto, no una cifra real.  
> - "Apareció en el DENUE" no es lo mismo que "abrió": el modelo usa datos de 2020 a 2026.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 2. ¿Dónde abro una cafetería de especialidad?

_llm, 1 rondas, 114.7 s; herramientas: perfil_giro({"texto": "¿Dónde abro una cafetería de especialidad?"}); recomendar_zonas({"giro": "cafeteria"})_

> **Top 5 para cafetería**  
> 1. **GRANADA**, Miguel Hidalgo (AGEB 0901600010571): score 93.6/100 (relativo al giro). Por qué: prob. de apertura 88%, gasto potencial por trimestre $17,792,000, competidores ponderados 2.5, captura 29%, residentes objetivo en el radio 1,070, empleos en el radio 4,630, NSE estimado alto.  
> 2. **AMPLIACIÓN NÁPOLES**, Benito Juárez (AGEB 090140001037A): score 93.5/100. Por qué: prob. de apertura 67%, gasto potencial por trimestre $21,530,000, competidores ponderados 3.0, captura 25%, residentes objetivo en el radio 1,270, empleos en el radio 1,460, NSE estimado alto.  
> 3. **ESCANDÓN I SECCIÓN**, Miguel Hidalgo (AGEB 0901600011211): score 93.5/100. Por qué: prob. de apertura 92%, gasto potencial por trimestre $18,344,000, competidores ponderados 4.6, captura 18%, residentes objetivo en el radio 1,600, empleos en el radio 3,400, NSE estimado medio.  
> 4. **SANTA MARÍA NONOALCO**, Benito Juárez (AGEB 0901400010543): score 92.5/100. Por qué: prob. de apertura 87%, gasto potencial por trimestre $21,907,000, competidores ponderados 3.6, captura 22%, residentes objetivo en el radio 1,640, empleos en el radio 1,700, NSE estimado alto.  
> 5. **ROMA SUR**, Cuauhtémoc (AGEB 0901500011464): score 92.4/100. Por qué: prob. de apertura 72%, gasto potencial por trimestre $19,613,000, competidores ponderados 5.4, captura 16%, residentes objetivo en el radio 1,440, empleos en el radio 2,100, NSE estimado alto.  
> 
> **Riesgos:**  
> - Competencia: colonias con muchos negocios complementarios (ej. librerías, bibliotecas, museos).  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no garantiza rentabilidad.  
> - Supuestos: el ticket promedio es estimado, no se basa en datos reales.  
> - "Apareció en el DENUE" no significa que abrió, ya que el modelo usa datos de censos económicos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 3. Busco dónde poner un gimnasio, ¿qué zonas me recomiendas?

_llm, 1 rondas, 109.2 s; herramientas: perfil_giro({"texto": "Busco dónde poner un gimnasio, ¿qué zonas me recomiendas?"}); recomendar_zonas({"giro": "gimnasio"})_

> **Top 5 para gimnasio**  
> 1. **ESCANDÓN I SECCIÓN**, Miguel Hidalgo (AGEB 0901600011211): score 91.7/100 (relativo al giro). Por qué: prob. de apertura % 50, gasto potencial por trimestre $7,647,000, competidores ponderados 13.3, captura % 7, residentes objetivo en el radio 20,350, empleos en el radio 44,840, NSE estimado medio.  
> 2. **AMPLIACIÓN GRANADA**, Miguel Hidalgo (AGEB 0901600010459): score 91.5/100 (relativo al giro). Por qué: prob. de apertura % 54, gasto potencial por trimestre $6,629,000, competidores ponderados 12.3, captura % 8, residentes objetivo en el radio 21,560, empleos en el radio 52,320, NSE estimado medio.  
> 3. **NÁPOLES**, Benito Juárez (AGEB 0901400010191): score 91.5/100 (relativo al giro). Por qué: prob. de apertura % 17, gasto potencial por trimestre $8,738,000, competidores ponderados 11.9, captura % 8, residentes objetivo en el radio 19,630, empleos en el radio 46,900, NSE estimado alto.  
> 4. **SAN PEDRO DE LOS PINOS**, Benito Juárez (AGEB 0901400010187): score 91.2/100 (relativo al giro). Por qué: prob. de apertura % 51, gasto potencial por trimestre $7,774,000, competidores ponderados 11.8, captura % 8, residentes objetivo en el radio 20,800, empleos en el radio 39,290, NSE estimado alto.  
> 5. **ESCANDÓN II SECCIÓN**, Miguel Hidalgo (AGEB 0901600011207): score 91.1/100 (relativo al giro). Por qué: prob. de apertura % 39, gasto potencial por trimestre $7,373,000, competidores ponderados 14.3, captura % 7, residentes objetivo en el radio 19,680, empleos en el radio 45,940, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: hay 12 a 14 competidores ponderados en las colonias top.  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no garantiza rentabilidad.  
> - Supuestos: el ticket promedio de $550 MXN es un supuesto, no un dato real.  
> - "Apareció en el DENUE" no es lo mismo que "abrió": parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket)

### 4. Quiero abrir una farmacia en Iztapalapa

_llm, 1 rondas, 99.6 s; herramientas: perfil_giro({"texto": "Quiero abrir una farmacia en Iztapalapa"}); recomendar_zonas({"giro": "farmacia", "municipio": "Iztapalapa"})_

> **Top 5 para farmacia**  
> 1. **JUAN ESCUTIA**, Iztapalapa (AGEB 0900700010017): score 84.4/100 (relativo al giro). Por qué: prob. de apertura 92%, gasto potencial por trimestre $1,053,000, competidores ponderados 3.4, captura 23%, residentes objetivo en el radio 1,850, empleos en el radio 2,010, NSE estimado medio.  
> 2. **IZTLAHUACAN**, Iztapalapa (AGEB 0900700013115): score 79.7/100. Por qué: prob. de apertura 90%, gasto potencial $1,144,000, competidores ponderados 6.1, captura 14%, residentes objetivo 2,770, empleos en el radio 1,150, NSE estimado bajo.  
> 3. **CARLOS HANK GONZÁLEZ**, Iztapalapa (AGEB 0900700014772): score 78.8/100. Por qué: prob. de apertura 90%, gasto potencial $1,337,000, competidores ponderados 8.4, captura 11%, residentes objetivo 2,740, empleos en el radio 1,250, NSE estimado medio.  
> 4. **CONSEJO AGRARISTA MEXICANO**, Iztapalapa (AGEB 090070001419A): score 78.7/100. Por qué: prob. de apertura 24%, gasto potencial $1,407,000, competidores ponderados 7.9, captura 11%, residentes objetivo 2,760, empleos en el radio 1,190, NSE estimado medio.  
> 5. **SAN MIGUEL TEOTONGO SECCIÓN PUENTE**, Iztapalapa (AGEB 0900700012649): score 78.3/100. Por qué: prob. de apertura 78%, gasto potencial $799,000, competidores ponderados 4.6, captura 18%, residentes objetivo 1,920, empleos en el radio 950, NSE estimado bajo.  
> 
> **Riesgos:**  
> - Competencia: El giro es muy competido (cadenas y similares).  
> - Confiabilidad del modelo: El score es un percentil dentro del giro, no una garantía de rentabilidad.  
> - Supuestos: El ticket promedio es un supuesto, no un dato real.  
> - "Apareció en el DENUE" no es lo mismo que "abrió".  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 5. ¿Dónde conviene poner una papelería?

_llm, 1 rondas, 102.1 s; herramientas: perfil_giro({"texto": "¿Dónde conviene poner una papelería?"}); recomendar_zonas({"giro": "papeleria"})_

> **Top 5 para papeleria**  
> 1. **BENITO JUAREZ**, Nezahualcóyotl (AGEB 1505800010577): score 88.8/100 (relativo al giro). Por qué: prob. de apertura 91%, gasto potencial por trimestre $828,000, competidores ponderados 4.2, captura 19%, residentes objetivo en el radio 1,500, empleos en el radio 1,330, NSE estimado medio.  
> 2. **EX HIPÓDROMO DE PERALVILLO**, Cuauhtémoc (AGEB 0901500010150): score 85.0/100. Por qué: prob. de apertura 50%, gasto potencial por trimestre $795,000, competidores ponderados 2.1, captura 33%, residentes objetivo en el radio 1,100, empleos en el radio 1,450.  
> 3. **REFORMA PENSIL**, Miguel Hidalgo (AGEB 0901600011349): score 85.0/100. Por qué: prob. de apertura 82%, gasto potencial por trimestre $1,848,000, competidores ponderados 5.4, captura 16%, residentes objetivo en el radio 2,890, empleos en el radio 1,100.  
> 4. **JUVENTINO ROSAS**, Iztacalco (AGEB 0900600010611): score 84.5/100. Por qué: prob. de apertura 85%, gasto potencial por trimestre $953,000, competidores ponderados 4.9, captura 17%, residentes objetivo en el radio 1,530, empleos en el radio 900.  
> 5. **PEDREGAL DE SANTO DOMINGO**, Coyoacán (AGEB 0900300010785): score 84.5/100. Por qué: prob. de apertura 95%, gasto potencial por trimestre $1,124,000, competidores ponderados 7.1, captura 12%, residentes objetivo en el radio 2,130, empleos en el radio 790.  
> 
> **Riesgos:**  
> - Competencia: algunas colonias tienen más competidores ponderados (ej. PEDREGAL DE SANTO DOMINGO).  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no garantiza rentabilidad.  
> - Supuestos: el ticket promedio es estimado, no hay datos reales.  
> - "Apareció en el DENUE" no es lo mismo que "abrió": parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Economicos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 6. Una lavandería de autoservicio, ¿dónde la pongo?

_llm, 1 rondas, 119.0 s; herramientas: perfil_giro({"texto": "Una lavandería de autoservicio, ¿dónde la pongo?"}); recomendar_zonas({"giro": "lavanderia"})_

> **Top 5 para lavanderia**  
> 1. **AGRÍCOLA PANTITLAN**, Iztacalco (AGEB 0900600010081): score 88.8/100 (relativo al giro). Por qué: prob. de apertura 59%, gasto potencial por trimestre 7,000 MXN, competidores ponderados 8.5, captura 10%, residentes objetivo en el radio 7,600, empleos en el radio 4,590, NSE estimado medio.  
> 2. **DOCTORES**, Cuauhtémoc (AGEB 0901500011549): score 86.7/100. Por qué: prob. de apertura 47%, gasto potencial por trimestre 7,000 MXN, competidores ponderados 9.0, captura 10%, residentes objetivo en el radio 6,210, empleos en el radio 11,670, NSE estimado medio.  
> 3. **CAMPAMENTO DOS DE OCTUBRE**, Iztacalco (AGEB 0900600011041): score 86.5/100. Por qué: prob. de apertura 28%, gasto potencial por trimestre 5,000 MXN, competidores ponderados 7.1, captura 12%, residentes objetivo en el radio 7,850, empleos en el radio 2,580, NSE estimado medio.  
> 4. **ESCANDÓN II SECCIÓN**, Miguel Hidalgo (AGEB 0901600011226): score 85.6/100. Por qué: prob. de apertura 54%, gasto potencial por trimestre 12,000 MXN, competidores ponderados 12.5, captura 7%, residentes objetivo en el radio 6,070, empleos en el radio 17,090, NSE estimado alto.  
> 5. **REFORMA PENSIL**, Miguel Hidalgo (AGEB 0901600011349): score 84.6/100. Por qué: prob. de apertura 58%, gasto potencial por trimestre 8,000 MXN, competidores ponderados 9.0, captura 10%, residentes objetivo en el radio 10,560, empleos en el radio 4,840, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: colonias con alta densidad de negocios (ej. ESCANDÓN II SECCIÓN, 12.5 competidores ponderados).  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no una garantía de rentabilidad.  
> - Supuestos: el ticket promedio de 150 MXN es estimado, no confirmado.  
> - "Apareció en el DENUE" no es lo mismo que "abrió": el modelo usa datos de 2020 a 2026, que no son completos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 7. Quiero poner una veterinaria en Naucalpan

_llm, 1 rondas, 123.0 s; herramientas: perfil_giro({"texto": "Quiero poner una veterinaria en Naucalpan"}); recomendar_zonas({"giro": "veterinaria", "municipio": "Naucalpan de Juárez"})_

> **Top 5 para veterinaria**  
> 1. **SAN JOSE DE LOS LEONES II SECCION**, Naucalpan de Juárez (AGEB 1505700010851): score 81.8/100 (relativo al giro). Por qué: prob. de apertura 22%, gasto potencial por trimestre $279,000, competidores ponderados 1.2, captura 46%, residentes objetivo en el radio 18,170, empleos en el radio 4,600, NSE estimado bajo.  
> 2. **SAN RAFAEL CHAMAPA**, Naucalpan de Juárez (AGEB 1505700011794): score 81.3/100. Por qué: prob. de apertura 19%, gasto potencial $277,000, competidores ponderados 2.1, captura 32%, residentes objetivo 17,990, empleos en el radio 5,110, NSE estimado bajo.  
> 3. **BENITO JUAREZ**, Naucalpan de Juárez (AGEB 1505700010955): score 81.0/100. Por qué: prob. de apertura 31%, gasto potencial $271,000, competidores ponderados 2.0, captura 34%, residentes objetivo 17,080, empleos en el radio 4,710, NSE estimado bajo.  
> 4. **ALFREDO V BONFIL**, Naucalpan de Juárez (AGEB 1505700010940): score 80.5/100. Por qué: prob. de apertura 43%, gasto potencial $279,000, competidores ponderados 2.9, captura 26%, residentes objetivo 17,890, empleos en el radio 5,050, NSE estimado bajo.  
> 5. **IZCALLI CHAMAPA**, Naucalpan de Juárez (AGEB 1505700012171): score 79.7/100. Por qué: prob. de apertura 39%, gasto potencial $267,000, competidores ponderados 2.8, captura 27%, residentes objetivo 14,320, empleos en el radio 5,070, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: algunas colonias tienen más competidores ponderados.  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no garantiza rentabilidad.  
> - Supuestos: el ticket promedio es estimado, no real.  
> - "Apareció en el DENUE" no es lo mismo que "abrió".  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 8. ¿En qué colonias pongo una taquería?

_llm, 1 rondas, 112.7 s; herramientas: perfil_giro({"texto": "¿En qué colonias pongo una taquería?"}); recomendar_zonas({"giro": "taqueria"})_

> **Top 5 para taqueria**  
> 1. **SAN RAFAEL**, Cuauhtémoc (AGEB 0901500010682): score 94.1/100 (relativo al giro). Por qué: prob. de apertura 95%, gasto potencial por trimestre $2,036,000, competidores ponderados 4.1, captura 20%, residentes objetivo en el radio 1,710, empleos en el radio 2,380, NSE estimado medio.  
> 2. **DEL VALLE SUR**, Benito Juárez (AGEB 0901400010806): score 91.8/100. Por qué: prob. de apertura 91%, gasto potencial por trimestre $1,974,000, competidores ponderados 4.2, captura 19%, residentes objetivo en el radio 1,270, empleos en el radio 3,290, NSE estimado alto.  
> 3. **ALAMOS**, Benito Juárez (AGEB 0901400010030): score 90.9/100. Por qué: prob. de apertura 89%, gasto potencial por trimestre $1,802,000, competidores ponderados 3.0, captura 25%, residentes objetivo en el radio 1,390, empleos en el radio 1,850, NSE estimado alto.  
> 4. **GABRIEL RAMOS MILLÁN SECCIÓN BRAMADERO**, Iztacalco (AGEB 0900600010734): score 90.5/100. Por qué: prob. de apertura 73%, gasto potencial por trimestre $1,132,000, competidores ponderados 2.6, captura 28%, residentes objetivo en el radio 1,660, empleos en el radio 1,340, NSE estimado medio.  
> 5. **GABRIEL RAMOS MILLÁN SECCIÓN CUCHILLA**, Iztacalco (AGEB 0900600011018): score 89.4/100. Por qué: prob. de apertura 21%, gasto potencial por trimestre $1,080,000, competidores ponderados 1.3, captura 43%, residentes objetivo en el radio 1,520, empleos en el radio 1,250, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: hay 4.1 a 11.6 competidores ponderados en las colonias.  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no una garantía de rentabilidad.  
> - Supuestos: el ticket promedio de $110 MXN es un supuesto.  
> - "Apareció en el DENUE" no es lo mismo que "abrió": parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 9. Tienda de abarrotes en Ecatepec, ¿qué colonias?

_llm, 1 rondas, 115.4 s; herramientas: perfil_giro({"texto": "Tienda de abarrotes en Ecatepec, ¿qué colonias?"}); recomendar_zonas({"giro": "abarrotes", "municipio": "Ecatepec de Morelos"})_

> **Top 5 para abarrotes**  
> 1. **LLANO DE LOS BAEZ**, Ecatepec de Morelos (AGEB 1503300013873): score 84.6/100 (relativo al giro). Por qué: prob. de apertura 99%, gasto potencial por trimestre $14,136,000, competidores ponderados 10.7, captura 9%, residentes objetivo en el radio 900, empleos en el radio 450, NSE estimado medio.  
> 2. **FUENTES DE ARAGON**, Ecatepec de Morelos (AGEB 1503300011773): score 83.5/100. Por qué: prob. de apertura 98%, gasto potencial por trimestre $17,205,000, competidores ponderados 6.0, captura 14%, residentes objetivo en el radio 1,020, empleos en el radio 450, NSE estimado medio.  
> 3. **JARDINES DE ARAGON**, Ecatepec de Morelos (AGEB 150330001174A): score 81.9/100. Por qué: prob. de apertura 99%, gasto potencial por trimestre $12,221,000, competidores ponderados 9.1, captura 10%, residentes objetivo en el radio 740, empleos en el radio 430, NSE estimado medio.  
> 4. **JARDINES DE SANTA CLARA**, Ecatepec de Morelos (AGEB 1503300010493): score 79.1/100. Por qué: prob. de apertura 97%, gasto potencial por trimestre $10,427,000, competidores ponderados 10.5, captura 9%, residentes objetivo en el radio 720, empleos en el radio 540, NSE estimado medio.  
> 5. **CIUDAD AZTECA**, Ecatepec de Morelos (AGEB 1503300010436): score 78.9/100. Por qué: prob. de apertura 100%, gasto potencial por trimestre $10,518,000, competidores ponderados 8.0, captura 11%, residentes objetivo en el radio 700, empleos en el radio 390, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: algunas colonias tienen muchos competidores ponderados.  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no garantiza rentabilidad.  
> - Supuestos: el ticket promedio es un supuesto, no una cifra real.  
> - "Apareció en el DENUE" no es lo mismo que "abrió": parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Economicos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket)

### 10. Quiero abrir una barbería en una zona de nivel alto

_llm, 1 rondas, 113.2 s; herramientas: perfil_giro({"texto": "Quiero abrir una barbería en una zona de nivel alto"}); recomendar_zonas({"giro": "barberia_estetica", "nse": "alto"})_

> **Top 5 para barberia_estetica**  
> 1. **ESCANDÓN II SECCIÓN**, Miguel Hidalgo (AGEB 0901600011226): score 81.9/100 (relativo al giro). Por qué: prob. de apertura 99%, gasto potencial por trimestre $2,534,000, competidores ponderados 27.9, captura 3%, residentes objetivo en el radio 3,410, empleos en el radio 8,340, NSE estimado alto.  
> 2. **ALAMOS**, Benito Juárez (AGEB 0901400010134): score 81.7/100. Por qué: prob. de apertura 98%, gasto potencial por trimestre $2,332,000, competidores ponderados 21.5, captura 4%, residentes objetivo en el radio 3,410, empleos en el radio 3,250, NSE estimado alto.  
> 3. **SANTA MARÍA NONOALCO**, Benito Juárez (AGEB 0901400010543): score 78.6/100. Por qué: prob. de apertura 97%, gasto potencial por trimestre $2,208,000, competidores ponderados 14.0, captura 7%, residentes objetivo en el radio 3,390, empleos en el radio 3,860, NSE estimado alto.  
> 4. **AMÉRICAS UNIDAS**, Benito Juárez (AGEB 0901400010492): score 78.2/100. Por qué: prob. de apertura 78%, gasto potencial por trimestre $2,622,000, competidores ponderados 22.5, captura 4%, residentes objetivo en el radio 4,160, empleos en el radio 2,130, NSE estimado alto.  
> 5. **MIXCOAC**, Benito Juárez (AGEB 090140001069A): score 77.9/100. Por qué: prob. de apertura 98%, gasto potencial por trimestre $1,742,000, competidores ponderados 15.6, captura 6%, residentes objetivo en el radio 2,320, empleos en el radio 5,150, NSE estimado alto.  
> 
> **Riesgos:**  
> - Competencia: algunas colonias tienen muchos competidores ponderados (ej. 27.9 en ESCANDÓN II SECCIÓN).  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no una garantía de rentabilidad.  
> - Supuestos: el ticket promedio es un supuesto (180 MXN).  
> - "Apareció en el DENUE" no es lo mismo que "abrió".  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 11. ¿Dónde pongo un consultorio dental?

_llm, 1 rondas, 141.8 s; herramientas: perfil_giro({"texto": "¿Dónde pongo un consultorio dental?"}); recomendar_zonas({"giro": "consultorio_dental"})_

> **Top 5 para consultorio_dental**  
> 1. **SAN RAFAEL**, Cuauhtémoc (AGEB 0901500010678): score 91.5/100 (relativo al giro). Por qué: prob. de apertura 87%, gasto potencial por trimestre $4,037,000, competidores ponderados 24.3, captura 4%, residentes objetivo en el radio 13,090, empleos en el radio 27,940, NSE estimado medio.  
> 2. **TLAXPANA**, Miguel Hidalgo (AGEB 090160001050A): score 89.7/100. Por qué: prob. de apertura 75%, gasto potencial $3,930,000, competidores ponderados 18.2, captura 5%, residentes objetivo 13,260, empleos en el radio 24,090, NSE estimado medio.  
> 3. **DOCTORES**, Cuauhtémoc (AGEB 0901500011036): score 89.5/100. Por qué: prob. de apertura 74%, gasto potencial $2,544,000, competidores ponderados 18.3, captura 5%, residentes objetivo 12,340, empleos en el radio 28,700, NSE estimado medio.  
> 4. **SAN JUANICO**, Miguel Hidalgo (AGEB 0901600010270): score 88.4/100. Por qué: prob. de apertura 73%, gasto potencial $4,054,000, competidores ponderados 24.9, captura 4%, residentes objetivo 17,050, empleos en el radio 14,070, NSE estimado medio.  
> 5. **ANÁHUAC II SECCIÓN**, Miguel Hidalgo (AGEB 0901600010497): score 88.2/100. Por qué: prob. de apertura 57%, gasto potencial $3,862,000, competidores ponderados 14.6, captura 6%, residentes objetivo 13,740, empleos en el radio 20,980, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: hay 24.3% de competidores ponderados en SAN RAFAEL.  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no garantiza rentabilidad.  
> - Supuestos: el ticket promedio de $700 MXN es un supuesto.  
> - "Apareció en el DENUE" no es lo mismo que "abrió".  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 12. Quiero abrir una guardería en Tlalnepantla

_llm, 1 rondas, 152.6 s; herramientas: perfil_giro({"texto": "Quiero abrir una guardería en Tlalnepantla"}); recomendar_zonas({"giro": "guarderia", "municipio": "Tlalnepantla de Baz"})_

> **Top 5 para guarderia**  
> 1. **VIVEROS DE LA LOMA**, Tlalnepantla de Baz (AGEB 151040001075A): score 85.3/100 (relativo al giro). Por qué: prob. de apertura 9%, gasto potencial por trimestre $6,205,000, competidores ponderados 0.8, captura 57%, residentes objetivo en el radio 3,860, empleos en el radio 9,510, NSE estimado alto.  
> 2. **JARDINES DE SANTA MONICA**, Tlalnepantla de Baz (AGEB 1510400010552): score 83.5/100 (relativo al giro). Por qué: prob. de apertura 1%, gasto potencial por trimestre $6,410,000, competidores ponderados 0.3, captura 76%, residentes objetivo en el radio 3,350, empleos en el radio 6,740, NSE estimado alto.  
> 3. **EXHACIENDA SANTA MONICA**, Tlalnepantla de Baz (AGEB 1510400010618): score 83.4/100 (relativo al giro). Por qué: prob. de apertura 7%, gasto potencial por trimestre $5,867,000, competidores ponderados 0.6, captura 63%, residentes objetivo en el radio 3,060, empleos en el radio 8,040, NSE estimado alto.  
> 4. **JARDINES DE STA MONICA**, Tlalnepantla de Baz (AGEB 1510400010548): score 82.6/100 (relativo al giro). Por qué: prob. de apertura 6%, gasto potencial por trimestre $5,734,000, competidores ponderados 0.6, captura 62%, residentes objetivo en el radio 3,480, empleos en el radio 7,280, NSE estimado alto.  
> 5. **VISTA HERMOSA**, Tlalnepantla de Baz (AGEB 1510400010904): score 81.8/100 (relativo al giro). Por qué: prob. de apertura 3%, gasto potencial por trimestre $5,530,000, competidores ponderados 1.1, captura 48%, residentes objetivo en el radio 4,460, empleos en el radio 8,680, NSE estimado medio.  
> 
> **Riesgos:**  
> - **Probabilidad de apertura baja en todo el top (1 a 9 %); en la ZMVM apareció en el 3 % de las AGEB**: el score alto solo dice que estas son las mejores zonas PARA ESTE GIRO, no que el giro sea viable.  
> - «Apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Economicos.  
> - El NSE y el decil por AGEB son estimaciones del proyecto (ENIGH no representa colonias).  
> - Ticket promedio $3,500 MXN es supuesto (supuesto: mensualidad de una guardería privada de barrio (no es ticket por visita)).  
> - La ENIGH no tiene un rubro de guardería; coicop_1010 es educación preescolar y primaria.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md).  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket).

### 13. ¿Dónde abro una ferretería?

_llm, 1 rondas, 132.7 s; herramientas: perfil_giro({"texto": "¿Dónde abro una ferretería?"}); recomendar_zonas({"giro": "ferreteria"})_

> **Top 5 para ferreteria**  
> 1. **FUENTES DE ARAGON**, Ecatepec de Morelos (AGEB 1503300011788): score 87.4/100 (relativo al giro). Por qué: prob. de apertura 51%, gasto potencial por trimestre $575,000, competidores ponderados 7.7, captura 11%, residentes objetivo en el radio 6,990, empleos en el radio 2,650, NSE estimado medio.  
> 2. **BENITO JUAREZ**, Nezahualcóyotl (AGEB 1505800010609): score 87.2/100. Por qué: prob. de apertura 78%, gasto potencial por trimestre $482,000, competidores ponderados 9.5, captura 9%, residentes objetivo en el radio 7,570, empleos en el radio 4,200, NSE estimado medio.  
> 3. **BUENOS AIRES**, Cuauhtémoc (AGEB 0901500011483): score 86.4/100. Por qué: gasto potencial por trimestre $709,000, competidores ponderados 8.4, captura 11%, residentes objetivo en el radio 7,200, empleos en el radio 4,820, NSE estimado medio.  
> 4. **SAN JUANICO**, Miguel Hidalgo (AGEB 0901600011334): score 86.3/100. Por qué: gasto potencial por trimestre $894,000, competidores ponderados 8.6, captura 10%, residentes objetivo en el radio 10,470, empleos en el radio 4,510, NSE estimado medio.  
> 5. **DOCTORES**, Cuauhtémoc (AGEB 0901500011534): score 85.8/100. Por qué: gasto potencial por trimestre $575,000, competidores ponderados 3.3, captura 23%, residentes objetivo en el radio 5,560, empleos en el radio 11,590, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: colonias con muchos negocios complementarios (pinturas, vidrios, etc.) pueden reducir la rentabilidad.  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no una garantía de éxito.  
> - Supuestos: el ticket promedio es estimado, no una cifra real.  
> - "Apareció en el DENUE" no significa que abrió: parte de lo nuevo entre 2020 y 2026 no está cubierto por los Censos Económicos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket)

### 14. Una pastelería en Benito Juárez, ¿dónde?

_llm, 1 rondas, 132.9 s; herramientas: perfil_giro({"texto": "Una pastelería en Benito Juárez, ¿dónde?"}); recomendar_zonas({"giro": "pasteleria", "municipio": "Benito Juárez"})_

> **Top 5 para pasteleria**  
> 1. **PIEDAD NARVARTE**, Benito Juárez (AGEB 0901400010026): score 86.3/100 (relativo al giro). Por qué: prob. de apertura 16%, gasto potencial por trimestre $4,800,000, competidores ponderados 0.6, captura 61%, residentes objetivo en el radio 5,590, empleos en el radio 7,080, NSE estimado alto.  
> 2. **NARVARTE PONIENTE**, Benito Juárez (AGEB 0901400010079): score 84.9/100 (relativo al giro). Por qué: prob. de apertura 15%, gasto potencial por trimestre $5,231,000, competidores ponderados 1.3, captura 43%, residentes objetivo en el radio 5,670, empleos en el radio 8,480, NSE estimado medio.  
> 3. **NARVARTE ORIENTE**, Benito Juárez (AGEB 0901400010083): score 84.3/100 (relativo al giro). Por qué: prob. de apertura 14%, gasto potencial por trimestre $5,654,000, competidores ponderados 1.8, captura 36%, residentes objetivo en el radio 6,000, empleos en el radio 6,870, NSE estimado alto.  
> 4. **DEL VALLE NORTE**, Benito Juárez (AGEB 090140001005A): score 82.9/100 (relativo al giro). Por qué: prob. de apertura 10%, gasto potencial por trimestre $4,990,000, competidores ponderados 1.1, captura 47%, residentes objetivo en el radio 5,390, empleos en el radio 7,700, NSE estimado alto.  
> 5. **INDEPENDENCIA**, Benito Juárez (AGEB 0901400010469): score 82.4/100 (relativo al giro). Por qué: prob. de apertura 21%, gasto potencial por trimestre $5,870,000, competidores ponderados 2.6, captura 28%, residentes objetivo en el radio 6,610, empleos en el radio 4,690, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: algunas colonias tienen muchos competidores ponderados.  
> - Confiabilidad del modelo: el score es un percentil dentro del giro, no garantiza rentabilidad.  
> - Supuestos: el ticket promedio es un supuesto, no una cifra real.  
> - "Apareció en el DENUE" no es lo mismo que "abrió": parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Economicos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket)

### 15. Quiero poner una librería

_llm, 1 rondas, 143.0 s; herramientas: perfil_giro({"texto": "Quiero poner una librería"}); recomendar_zonas({"giro": "libreria"})_

> **Top 5 para libreria**  
> 1. **ALAMOS**, Benito Juárez (AGEB 090140001012A): score 94.4/100 (relativo al giro). Por qué: prob. de apertura 3%, gasto potencial por trimestre $8,001,000, competidores ponderados 1.1, captura 47%, residentes objetivo en el radio 17,940, empleos en el radio 21,610, NSE estimado alto.  
> 2. **NIÑOS HÉROES**, Benito Juárez (AGEB 0901400010295): score 94.0/100. Por qué: prob. de apertura 2%, gasto potencial por trimestre $8,285,000, competidores ponderados 1.4, captura 41%, residentes objetivo en el radio 18,180, empleos en el radio 17,350, NSE estimado medio.  
> 3. **POSTAL**, Benito Juárez (AGEB 0901400010308): score 93.9/100. Por qué: prob. de apertura 3%, gasto potencial por trimestre $7,565,000, competidores ponderados 1.1, captura 48%, residentes objetivo en el radio 17,160, empleos en el radio 16,700, NSE estimado medio.  
> 4. **NONOALCO TLATELOLCO**, Cuauhtémoc (AGEB 0901500010288): score 92.9/100. Por qué: prob. de apertura 1%, gasto potencial por trimestre $5,082,000, competidores ponderados 1.2, captura 46%, residentes objetivo en el radio 21,570, empleos en el radio 19,730, NSE estimado medio.  
> 5. **MIGUEL ALEMÁN**, Benito Juárez (AGEB 0901400010280): score 92.7/100. Por qué: prob. de apertura 4%, gasto potencial por trimestre $8,308,000, competidores ponderados 1.7, captura 37%, residentes objetivo en el radio 17,990, empleos en el radio 18,560, NSE estimado medio.  
> 
> **Riesgos:**  
> - **Probabilidad de apertura baja en todo el top (1 a 4 %); en la ZMVM apareció en el 3 % de las AGEB**: el score alto solo dice que estas son las mejores zonas PARA ESTE GIRO, no que el giro sea viable.  
> - «Apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos.  
> - El NSE y el decil por AGEB son estimaciones del proyecto (ENIGH no representa colonias).  
> - Ticket promedio $260 MXN es supuesto (supuesto: uno o dos libros).  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket)

### 16. Quiero un negocio de renta de bicicletas, ¿dónde lo pongo?

_llm, 1 rondas, 164.3 s; herramientas: perfil_giro({"texto": "Quiero un negocio de renta de bicicletas, ¿dónde lo pongo?"}); recomendar_zonas({"giro": "renta_bicicletas"})_

> **Top 5 para renta_bicicletas**  
> 1. **ROMA SUR**, Cuauhtémoc (AGEB 0901500011360): score 98.1/100 (relativo al giro). Por qué: prob. de apertura 0 %, gasto potencial por trimestre $92,893,000, competidores ponderados 0.0, captura % 100, residentes objetivo en el radio 25,720, empleos en el radio 81,150, NSE estimado alto.  
> 2. **SAN RAFAEL**, Cuauhtémoc (AGEB 0901500010682): score 97.9/100 (relativo al giro). Por qué: prob. de apertura 0 %, gasto potencial por trimestre $75,307,000, competidores ponderados 0.0, captura % 100, residentes objetivo en el radio 27,340, empleos en el radio 92,070, NSE estimado medio.  
> 3. **NARVARTE PONIENTE**, Benito Juárez (AGEB 0901400010079): score 97.8/100 (relativo al giro). Por qué: prob. de apertura 0 %, gasto potencial por trimestre $110,640,000, competidores ponderados 0.0, captura % 100, residentes objetivo en el radio 31,870, empleos en el radio 49,300, NSE estimado medio.  
> 4. **NARVARTE ORIENTE**, Benito Juárez (AGEB 0901400010083): score 97.6/100 (relativo al giro). Por qué: prob. de apertura 0 %, gasto potencial por trimestre $120,325,000, competidores ponderados 0.0, captura % 100, residentes objetivo en el radio 31,910, empleos en el radio 43,420, NSE estimado alto.  
> 5. **GRANADA**, Miguel Hidalgo (AGEB 0901600010478): score 97.5/100 (relativo al giro). Por qué: prob. de apertura 0 %, gasto potencial por trimestre $93,982,000, competidores ponderados 0.0, captura % 100, residentes objetivo en el radio 30,930, empleos en el radio 83,990, NSE estimado alto.  
> 
> **Riesgos:**  
> - **Probabilidad de apertura baja en todo el top (0 a 0 %):** En la ZMVM apareció en el 0 % de las AGEB: el score alto solo dice que estas son las mejores zonas PARA ESTE GIRO, no que el giro sea viable.  
> - «Apareció en el DENUE» no es lo mismo que «abrió»: parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos.  
> - El NSE y el decil por AGEB son estimaciones del proyecto (ENIGH no representa colonias).  
> - Ticket promedio $120 MXN es supuesto (supuesto: una hora o una vuelta de renta).  
> - No hay rubro de renta de bicicletas en la ENIGH; se usa esparcimiento como proxy de gasto discrecional.  
> - Giro raro: solo 1 AGEB con aperturas 2020-2026; el modelo es poco confiable.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)  
> - config/giros.yaml (supuestos del proyecto: radio, cliente objetivo, ticket)

### 17. Quiero poner un negocio en Coyoacán, ¿qué me recomiendas y dónde?

_llm, 1 rondas, 172.2 s; herramientas: perfil_giro({"texto": "Quiero poner un negocio en Coyoacán, ¿qué me recomiendas y dónde?"}); sugerir_giros({"municipio": "Coyoacán"}); recomendar_zonas({"giro": "abarrotes", "municipio": "Coyoacán"})_

> **Giros que conviene considerar**  
> 1. **abarrotes** (viabilidad: 72%, prob. de apertura: 96%, prob. de seguir abierto: 74%)  
> 2. **barberia_estetica** (viabilidad: 62%, prob. de apertura: 91%, prob. de seguir abierto: 68%)  
> 3. **carniceria** (viabilidad: 62%, prob. de apertura: 83%, prob. de seguir abierto: 75%)  
> 4. **papeleria** (viabilidad: 58%, prob. de apertura: 83%, prob. de seguir abierto: 70%)  
> 5. **fruteria** (viabilidad: 57%, prob. de apertura: 81%, prob. de seguir abierto: 69%)  
> 
> El score 0-100 es relativo dentro de cada giro y no sirve para comparar giros entre sí.  
> 
> **Top 5 para abarrotes**  
> 1. **CULHUACÁN CTM SECCIÓN IX-A**, Coyoacán (AGEB 0900300011497): score 84/100 (relativo al giro). Por qué: prob. de apertura 99%, gasto potencial por trimestre $17,067,000, competidores ponderados 8, captura % 11, residentes objetivo en el radio 960, empleos en el radio 510, NSE estimado medio.  
> 2. **CARMEN SERDÁN**, Coyoacán (AGEB 0900300010959): score 82/100. Por qué: prob. de apertura 99%, gasto potencial por trimestre $16,322,000, competidores ponderados 20, captura % 5, residentes objetivo en el radio 1,160, empleos en el radio 600, NSE estimado medio.  
> 3. **EMILIANO ZAPATA**, Coyoacán (AGEB 0900300011406): score 81/100. Por qué: prob. de apertura 98%, gasto potencial por trimestre $13,199,000, competidores ponderados 13.1, captura % 7, residentes objetivo en el radio 920, empleos en el radio 500, NSE estimado medio.  
> 4. **CULHUACÁN CTM CROC**, Coyoacán (AGEB 0900300011745): score 79/100. Por qué: prob. de apertura 88%, gasto potencial por trimestre $15,882,000, competidores ponderados 6, captura % 14, residentes objetivo en el radio 860, empleos en el radio 620, NSE estimado medio.  
> 5. **PEDREGAL DE SANTO DOMINGO**, Coyoacán (AGEB 0900300010802): score 78/100. Por qué: prob. de apertura 100%, gasto potencial por trimestre $20,905,000, competidores ponderados 20.1, captura % 5, residentes objetivo en el radio 1,580, empleos en el radio 330, NSE estimado medio.  
> 
> **Riesgos:**  
> - Competencia: algunas colonias tienen muchos competidores ponderados (ej. Carmen Serdán).  
> - Confiabilidad del modelo: el score es una estimación basada en datos históricos y supuestos.  
> - Supuestos: el ticket promedio es un supuesto del proyecto.  
> - "Apareció en el DENUE" no es lo mismo que "abrió": parte de lo nuevo entre 2020 y 2026 es cobertura de los Censos Económicos.  
> 
> **Fuentes:**  
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md)  
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo)  
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana  
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_imputado.md)  
> - config/giros.yaml (supuestos del

### 18. Quiero algo barato para una zona de nivel bajo, ¿qué pongo y dónde?

_llm, 1 rondas, 138.9 s; herramientas: perfil_giro({"texto": "Quiero algo barato para una zona de nivel bajo, ¿qué pongo y dónde?"}); sugerir_giros({"nse": "bajo", "ticket_max": 100}); recomendar_zonas({"giro": "abarrotes", "nse": "bajo"})_

> **Giros que conviene considerar:**
> 1. **abarrotes**: viabilidad 52%, prob. de apertura 71%, prob. de seguir abierto 73%.
> 2. **tortilleria**: viabilidad 52%, prob. de apertura 66%, prob. de seguir abierto 79%.
> 3. **fruteria**: viabilidad 46%, prob. de apertura 72%, prob. de seguir abierto 64%.
> 4. **purificadora**: viabilidad 43%, prob. de apertura 57%, prob. de seguir abierto 75%.
> 5. **panaderia**: viabilidad 40%, prob. de apertura 65%, prob. de seguir abierto 61%.
> 
> Los giros se ordenan por viabilidad = prob. de apertura x prob. de seguir abierto (absolutas, comparables entre giros). El score 0-100 es relativo dentro de cada giro: NO compara giros.
> 
> **Top 5 para abarrotes**
> 1. **MORELOS**, Cuauhtémoc (AGEB 0901500010339): score 85.7/100 (relativo al giro). Por qué: prob. de apertura 100%, gasto potencial por trimestre $13,628,000, competidores ponderados 10.6, captura % 9, residentes objetivo en el radio 950, empleos en el radio 720, NSE estimado "bajo".
> 2. **CHINAMPAC DE JUÁREZ**, Iztapalapa (AGEB 090070001579A): score 84.6/100 (relativo al giro). Por qué: prob. de apertura 29%, gasto potencial por trimestre $16,196,000, competidores ponderados 15.1, captura % 6, residentes objetivo en el radio 1,160, empleos en el radio 600, NSE estimado "bajo".
> 3. **INFONAVIT NORTE SECCIÓN 1**, Cuautitlán Izcalli (AGEB 1512100010765): score 83.2/100 (relativo al giro). Por qué: prob. de apertura 98%, gasto potencial por trimestre $16,730,000, competidores ponderados 13.9, captura % 7, residentes objetivo en el radio 1,140, empleos en el radio 340, NSE estimado "bajo".
> 4. **CONSEJO AGRARISTA MEXICANO**, Iztapalapa (AGEB 0900700015056): score 83.1/100 (relativo al giro). Por qué: prob. de apertura 50%, gasto potencial por trimestre $16,358,000, competidores ponderados 10.3, captura % 9, residentes objetivo en el radio 1,140, empleos en el radio 330, NSE estimado "bajo".
> 5. **SAN ANTONIO ZOMEYUCAN**, Naucalpan de Juárez (AGEB 1505700010419): score 82.8/100 (relativo al giro). Por qué: prob. de apertura 100%, gasto potencial por trimestre $16,155,000, competidores ponderados 16.7, captura % 6, residentes objetivo en el radio 1,250, empleos en el radio 480, NSE estimado "bajo".
> 
> **Riesgos:**
> - Competencia: algunas colonias tienen muchos competidores ponderados.
> - Confiabilidad del modelo: el score es una estimación basada en datos históricos.
> - Supuestos: el ticket promedio es un supuesto del proyecto.
> - "Apareció en el DENUE" no es lo mismo que "abrió".
> 
> **Fuentes:**
> - Modelo de aperturas del proyecto (models/metadata.json, reports/validacion.md).
> - INEGI, DENUE corte 05/2026 (y 11/2020 para el modelo).
> - INEGI, Censo de Población y Vivienda 2020, resultados por AGEB urbana.
> - INEGI, ENIGH 2024 (gasto trimestral por decil, ámbito ZMVM); decil por AGEB estimado por el proyecto (reports/decil_im

### 19. ¿Cómo está la economía para abrir un negocio? Inflación, tasa de Banxico y tipo de cambio

_llm, 1 rondas, 59.6 s; herramientas: perfil_giro({"texto": "¿Cómo está la economía para abrir un negocio? Inflación, tasa de Banxico y tipo de cambio"}); contexto_macro({})_

Cifras que no salen de las herramientas: 28

> **Economía para abrir un negocio:**
> 
> - **Tasa objetivo de Banxico:** 6.25% anual (fecha: 2026-11-23).
> - **TIIE 28 días:** 6.51% anual (fecha: 2026-11-23).
> - **Tipo de cambio fijo (USD/MXN):** 19.02 (fecha: 2026-11-20).
> - **Remesas (mensuales en millones de USD):** 5,362 (fecha: 2026-09-01). Variación anual: 1.55%. Acumulado de 12 meses: 63,452 millones de USD.
> - **Inflación general (INPC):** 3.75% anual (fecha: 2026-10).
> - **Inflación de alimentos (proxy):** No encontrado. Sin embargo, el subíndice de mercancias tiene una variación anual de 3.25% (fecha: 2026-10).
> - **Confianza del consumidor:** 45.19 puntos (fecha: 2026-10).
> - **Consumo privado (variación anual):** 1.34% (fecha: 2026-08).
> 
> **Fuentes:**
> - Banco de México, SIE API (series SE27803, SF43718, SF43783, SF61745).
> - INEGI, Banco de Indicadores API (series 454168, 740946, 910406, 910408, 910411).
> 
> **Nota:** Los valores son nacionales y no por colonia. El subíndice de alimentos no está disponible, solo se ofrecen proxies.

### 20. Quiero poner una heladería en Monterrey

_llm, 1 rondas, 33.5 s; herramientas: perfil_giro({"texto": "Quiero poner una heladería en Monterrey"}); recomendar_zonas({"giro": "heladeria", "municipio": "Monterrey"}); buscar_carpetas({"pregunta": "Quiero poner una heladería en Monterrey", "k": 2})_

> La ubicación de una heladería en Monterrey está **fuera de alcance** del modelo, ya que Monterrey no forma parte de la Zona Metropolitana del Valle de México (ZMVM), que incluye las 16 alcaldías de la Ciudad de México, 59 municipios del Estado de México y Tizayuca, Hidalgo. El modelo no cuenta con datos de ciudades fuera de la ZMVM, por lo que no se pueden proporcionar colonias o municipios de Monterrey.
> 
> **Fuentes:**  
> - SEDATU-CONAPO-INEGI, delimitación de zonas metropolitanas 2015 (data/processed/zmvm_municipios.csv)  
> - Carpetas/00_alcance.md (qué no cubre)

