> Copia de `reports/validacion_score.md` hecha por `scripts/03b_validar_score.py` el 2026-11-23. La fuente es ese reporte.

# Validación del score: ¿predice algo que le importe a quien abre un negocio?

Generado por `scripts/03b_validar_score.py` el 2026-11-23 · score `3.0-nucleo-aprendido` · datos: DENUE 11/2020 y 05/2026 (INEGI), Censo 2020 (INEGI), ENIGH 2024 (INEGI), CONAPO 2020, modelo propio de aperturas (`reports/validacion.md`).

## En corto

- El score anterior (v2.1, pesos del autor 30/25/15/20/10) tenía un AUC medio de 0.583 para predecir aperturas crudas, debajo de la competencia en la AGEB (0.711). **Eso es lo esperado, no un error**: las aperturas se aglomeran donde ya hay competidores, y un score que castiga la competencia por diseño tiene que quedar por debajo de quien la premia (sección 1).
- Contra crecimiento neto (aperturas − desapariciones), el score anterior casi no le ganaba a nada: ρ = 0.046 (la mejor línea base ingenua, competencia Huff, 0.126). El score nuevo (3.0: núcleo sin parámetros y pesos aprendidos fuera de muestra, sección 3) llega a ρ = **0.159 fuera de muestra** (0.182 con los pesos entregados, ajustados con todos los datos, que son los que ya vieron el municipio de prueba).
- **Pero esa mejora viene casi entera de la carga de los Censos Económicos 2024, no de aperturas.** 90.5 % de los «nuevos» entre las AGEB elegibles tienen `fecha_alta` 2024: negocios que ya existían y no estaban en el DENUE 2020. Donde 2020 subregistró queda un stock de 2020 bajo con muchos «nuevos», y el núcleo λ/(1 + competidores) premia justo eso. Al usar el score, el DENUE 2026 ya trae la carga, así que esa ventaja no se traslada. Con el objetivo limpio (crecimiento neto sin carga censal = (altas reales − desapariciones) / establecimientos de 2020) el score nuevo saca ρ = 0.037 fuera de muestra (0.039 con los pesos entregados) contra 0.055 del anterior. **En los dos objetivos limpios que ya había el nuevo empata o pierde:** altas fuera de la carga censal 0.046 contra 0.108; sobrevivencia 0.022 contra 0.028. Ojo: como las altas reales son pocas frente a los cierres, el crecimiento neto sin carga se parece mucho a la sobrevivencia (casi es menos cierres), así que no cuenta como una evidencia independiente.
- Por eso **la elección del score 3.0 sobre el 2.1 no es una victoria empírica**: con estos datos (dos cortes del DENUE, sin ventas ni rentas) ninguno de los dos predice bien lo limpio (el mayor ρ de cualquiera de los dos en un objetivo limpio es 0.108). Se conserva el 3.0 como decisión de diseño, explicada en la sección 3, y se dice que la validación solo descarta, no confirma.
- **La sobrevivencia no se puede predecir con estos datos**: ninguna puntuación pasa de ρ ≈ 0.076 dentro de un giro. Se reporta `prob_sobrevive` como dato de riesgo, no como criterio de orden.
- El decil imputado acierta el decil exacto 17.9 % de las veces, pero **la banda de NSE que usa el producto (bajo, medio, alto) la acierta 57.7 %** (azar: 36 %; siempre decir «medio»: 40 %). Es una pista, no una medición (sección 4).

## 1. Diagnóstico: por qué el score no predice aperturas crudas

Hipótesis: las aperturas se aglomeran donde ya hay competencia (economías de aglomeración, tráfico de clientes, locales que cambian de dueño) y una parte grande de lo que «apareció» en 2026 es la carga de los Censos Económicos 2024, no aperturas. Un score que baja el puntaje por competencia queda por debajo de las líneas base que la premian. Se comprueba con cuatro números:

1. **Más competidores, más aperturas.** Promedio de 34 giros: probabilidad de que aparezca ≥ 1 negocio del giro en la AGEB de 18 % si en 2020 no había ninguno, 39 % si había 1 o 2 y 66 % si había 3 o más. Donde había 3 o más aparecieron 0.32 negocios nuevos por cada establecimiento de 2020 y desaparecieron 0.32: las aperturas crecen casi proporcionales al stock.
2. **Elasticidad.** Regresión de log(1 + aperturas) sobre log(1 + establecimientos de 2020) y log(población), con efectos fijos de giro y errores por municipio: el coeficiente de la competencia previa es 0.38 (EE 0.01); el de la población, 0.06 (EE 0.01). Un 10 % más de competidores previos se asocia con ~3.8 % más aperturas. Es asociación, no causalidad.
3. **Rotación y carga censal.** Entre AGEB con ≥ 3 establecimientos del giro en 2020, la correlación de Spearman entre aperturas y cierres es 0.27 (promedio de 28 giros): donde más abren, más desaparecen; una apertura bruta mezcla expansión con rotación. Además, 93 % de los «nuevos» de los 40 giros tienen `fecha_alta` 2024 (carga de los Censos Económicos), así que «apareció» no es «abrió».
4. **Qué le hace el score a esa señal.** AUC medio contra aperturas crudas, por giro:

| Puntuación | AUC |
|---|---|
| Prob. de apertura de la AGEB (modelo) | 0.806 |
| Competencia en la AGEB | 0.711 |
| Competencia Huff | 0.652 |
| Aperturas esperadas (modelo) | 0.676 |
| Score anterior **sin** el castigo por competencia (contrafactual) | 0.624 |
| Score anterior (v2.1, pesos del autor) | 0.583 |
| Gasto potencial × captura | 0.436 |
| Población objetivo × NSE × captura | 0.468 |
| Captura Huff (1/(1+competidores)) | 0.348 |

La captura Huff (el castigo por competencia) tiene AUC por debajo de 0.5 contra aperturas: ordena al revés. Los términos de demanda y población la multiplican y pesaban 40 % del score anterior. Quitarle el castigo (mismo score, sin multiplicar por la captura) sube su AUC, lo que confirma que la causa es la competencia y no un error de cálculo. **La respuesta corta: el score no predice aperturas crudas porque no intenta hacerlo; premia lugares con aperturas esperadas y pocos competidores, y las aperturas crudas se dan donde ya hay muchos.**

## 2. Qué se midió y contra qué

Por (AGEB, giro), con los cortes DENUE 11/2020 y 05/2026. Todo se mide en el mismo círculo (`radio_influencia_m` del giro, peso Huff) que usa el score, con al menos 3 establecimientos ponderados del giro en 2020 (tasas con denominadores chicos son puro ruido). Las etiquetas se empatan como en `03_entrenar.py`: por `id` y, de respaldo, por nombre normalizado a ≤ 50 m; el giro, por SCIAN con el cruce histórico→actual de `data/processed/scian_hist_a_actual.csv`.

| Objetivo | Definición | Métrica | Giros |
|---|---|---|---|
| Sobrevivencia | establecimientos de 2020 que siguen en 2026 / establecimientos de 2020 | ρ de Spearman | 36 |
| Crecimiento neto | (aperturas − desapariciones) / establecimientos de 2020 | ρ de Spearman | 36 |
| Altas fuera de la carga censal | aperturas con `fecha_alta` ≠ 2024 / establecimientos de 2020 (las únicas que se parecen a aperturas reales y siguen abiertas en 2026) | ρ de Spearman | 36 |
| Crecimiento neto sin carga censal | (altas fuera de la carga − desapariciones) / establecimientos de 2020: el crecimiento neto sin los negocios que ya existían y solo aparecieron por la carga de 2024 | ρ de Spearman | 36 |
| Aperturas crudas (referencia) | apareció ≥ 1 negocio del giro en la AGEB | AUC | 38 |

Límites de los objetivos: «desapareció del DENUE» puede ser un cierre o un cambio de registro que no se pudo empatar; la tasa de aperturas netas se normaliza por el stock de 2020, así que comparte denominador con la competencia (por eso se repite sin normalizar y por habitante, abajo); la sobrevivencia **de las aperturas** (negocios abiertos después de 2020 que ya cerraron) no se puede medir con dos cortes: solo se ven las que siguen abiertas, por eso el objetivo de sobrevivencia usa los establecimientos de 2020.

Validación espacial: los mismos 5 pliegues por municipio (`GroupKFold`) del modelo de aperturas. Valor = promedio entre giros (± error estándar entre giros). Lift = tasa en el 5 % o 10 % mejor puntuado de las AGEB elegibles entre la tasa base del giro (promedio de giros; en crecimiento neto la tasa base es casi cero y a veces negativa, así que no se da el cociente y solo la diferencia en puntos porcentuales, Δ pts, entre la tasa del 10 % mejor puntuado y la del giro).

### Crecimiento neto — ρ de Spearman

| Puntuación | Valor | Lift 5 % | Lift 10 % | Δ pts 10 % |
|---|---|---|---|---|
| Score anterior (v2.1, pesos del autor) | 0.046 ± 0.023 | — | — | +1.9 |
| **Score nuevo, pesos fuera de muestra (cifra principal)** | **0.159 ± 0.022** | — | — | +10.6 |
| Score nuevo, pesos entregados (dentro de muestra) | 0.182 ± 0.024 | — | — | +11.8 |
| Sensibilidad: pesos aprendidos solo con objetivos limpios (fuera de muestra) | -0.024 ± 0.025 | — | — | -2.3 |
| Núcleo: aperturas por competidor | 0.230 ± 0.029 | — | — | +16.2 |
| Aperturas esperadas (modelo) | 0.064 ± 0.016 | — | — | +1.0 |
| Captura Huff (1/(1+competidores)) | 0.126 ± 0.019 | — | — | +10.8 |
| Gasto potencial × captura | -0.001 ± 0.023 | — | — | +0.8 |
| Población objetivo × NSE × captura | 0.101 ± 0.023 | — | — | +7.2 |
| Flujo de gente (proxy) | -0.040 ± 0.023 | — | — | -3.3 |
| Complementarios | 0.023 ± 0.021 | — | — | -0.4 |
| Prob. de apertura de la AGEB (modelo) | 0.061 ± 0.011 | — | — | +1.9 |
| Prob. de seguir abierto (modelo dedicado) | -0.001 ± 0.013 | — | — | +0.2 |
| Densidad de población | 0.015 ± 0.012 | — | — | -1.7 |
| Competencia Huff | -0.126 ± 0.019 | — | — | -3.3 |
| Competencia en la AGEB | -0.035 ± 0.008 | — | — | -1.9 |
| Actividad (negocios a 500 m) | 0.025 ± 0.018 | — | — | -0.6 |

Mejor línea base ingenua (con su mejor dirección): competencia Huff, 0.126.

Este objetivo mezcla aperturas reales con la carga de los Censos Económicos 2024; el siguiente objetivo limpio (neto sin carga censal) y la tabla de robustez muestran cuánto de esta ventaja queda sin la carga.

### Sobrevivencia — ρ de Spearman

| Puntuación | Valor | Lift 5 % | Lift 10 % | Δ pts 10 % |
|---|---|---|---|---|
| Score anterior (v2.1, pesos del autor) | 0.028 ± 0.016 | 0.98 | 0.98 | -1.0 |
| **Score nuevo, pesos fuera de muestra (cifra principal)** | **0.022 ± 0.016** | 0.99 | 0.99 | -0.6 |
| Score nuevo, pesos entregados (dentro de muestra) | 0.025 ± 0.017 | 0.99 | 0.99 | -0.6 |
| Sensibilidad: pesos aprendidos solo con objetivos limpios (fuera de muestra) | 0.038 ± 0.018 | 0.98 | 0.98 | -1.4 |
| Núcleo: aperturas por competidor | -0.009 ± 0.021 | 0.97 | 0.97 | -1.8 |
| Aperturas esperadas (modelo) | -0.001 ± 0.012 | 1.01 | 1.01 | +0.4 |
| Captura Huff (1/(1+competidores)) | -0.003 ± 0.016 | 0.99 | 0.99 | -0.5 |
| Gasto potencial × captura | 0.016 ± 0.020 | 0.98 | 0.99 | -0.6 |
| Población objetivo × NSE × captura | 0.022 ± 0.018 | 0.99 | 0.99 | -0.4 |
| Flujo de gente (proxy) | 0.035 ± 0.017 | 0.99 | 0.99 | -0.6 |
| Complementarios | 0.042 ± 0.014 | 1.01 | 1.01 | +0.7 |
| Prob. de apertura de la AGEB (modelo) | -0.000 ± 0.009 | 1.01 | 1.01 | +0.7 |
| Prob. de seguir abierto (modelo dedicado) | 0.076 ± 0.011 | 1.03 | 1.02 | +1.5 |
| Densidad de población | 0.022 ± 0.010 | 1.00 | 1.00 | +0.2 |
| Competencia Huff | 0.003 ± 0.016 | 1.01 | 1.01 | +0.5 |
| Competencia en la AGEB | -0.000 ± 0.006 | 1.01 | 1.01 | +0.8 |
| Actividad (negocios a 500 m) | 0.033 ± 0.012 | 0.99 | 1.00 | +0.3 |

Mejor línea base ingenua (con su mejor dirección): actividad (negocios a 500 m), 0.033.

### Altas fuera de la carga censal — ρ de Spearman

| Puntuación | Valor | Lift 5 % | Lift 10 % | Δ pts 10 % |
|---|---|---|---|---|
| Score anterior (v2.1, pesos del autor) | 0.108 ± 0.017 | 1.57 | 1.38 | +1.7 |
| **Score nuevo, pesos fuera de muestra (cifra principal)** | **0.046 ± 0.018** | 1.24 | 1.16 | +0.9 |
| Score nuevo, pesos entregados (dentro de muestra) | 0.045 ± 0.019 | 1.24 | 1.17 | +0.9 |
| Sensibilidad: pesos aprendidos solo con objetivos limpios (fuera de muestra) | 0.148 ± 0.014 | 1.62 | 1.46 | +1.9 |
| Núcleo: aperturas por competidor | -0.026 ± 0.022 | 1.11 | 1.01 | +0.2 |
| Aperturas esperadas (modelo) | 0.082 ± 0.015 | 1.20 | 1.11 | +0.1 |
| Captura Huff (1/(1+competidores)) | -0.100 ± 0.014 | 1.08 | 1.17 | +0.4 |
| Gasto potencial × captura | 0.042 ± 0.020 | 1.69 | 1.57 | +2.0 |
| Población objetivo × NSE × captura | -0.009 ± 0.024 | 1.30 | 1.23 | +1.0 |
| Flujo de gente (proxy) | 0.147 ± 0.012 | 1.51 | 1.42 | +1.0 |
| Complementarios | 0.109 ± 0.015 | 1.39 | 1.24 | +0.6 |
| Prob. de apertura de la AGEB (modelo) | 0.022 ± 0.009 | 1.15 | 1.13 | +0.1 |
| Prob. de seguir abierto (modelo dedicado) | -0.045 ± 0.014 | 0.83 | 0.89 | -0.7 |
| Densidad de población | -0.036 ± 0.017 | 0.84 | 0.84 | -0.5 |
| Competencia Huff | 0.100 ± 0.014 | 1.10 | 1.04 | -0.1 |
| Competencia en la AGEB | 0.026 ± 0.009 | 1.17 | 1.10 | +0.0 |
| Actividad (negocios a 500 m) | 0.098 ± 0.013 | 1.54 | 1.32 | +0.7 |

Mejor línea base ingenua (con su mejor dirección): competencia Huff, 0.100.

### Crecimiento neto sin carga censal — ρ de Spearman

| Puntuación | Valor | Lift 5 % | Lift 10 % | Δ pts 10 % |
|---|---|---|---|---|
| Score anterior (v2.1, pesos del autor) | 0.055 ± 0.018 | — | — | +0.6 |
| **Score nuevo, pesos fuera de muestra (cifra principal)** | **0.037 ± 0.019** | — | — | +0.3 |
| Score nuevo, pesos entregados (dentro de muestra) | 0.039 ± 0.020 | — | — | +0.3 |
| Sensibilidad: pesos aprendidos solo con objetivos limpios (fuera de muestra) | 0.077 ± 0.018 | — | — | +0.5 |
| Núcleo: aperturas por competidor | -0.008 ± 0.023 | — | — | -1.6 |
| Aperturas esperadas (modelo) | -0.004 ± 0.011 | — | — | +0.5 |
| Captura Huff (1/(1+competidores)) | -0.001 ± 0.016 | — | — | -0.1 |
| Gasto potencial × captura | 0.048 ± 0.021 | — | — | +1.4 |
| Población objetivo × NSE × captura | 0.025 ± 0.021 | — | — | +0.6 |
| Flujo de gente (proxy) | 0.065 ± 0.017 | — | — | +0.4 |
| Complementarios | 0.057 ± 0.014 | — | — | +1.4 |
| Prob. de apertura de la AGEB (modelo) | -0.005 ± 0.009 | — | — | +0.8 |
| Prob. de seguir abierto (modelo dedicado) | 0.045 ± 0.013 | — | — | +0.9 |
| Densidad de población | -0.004 ± 0.012 | — | — | -0.3 |
| Competencia Huff | 0.001 ± 0.016 | — | — | +0.4 |
| Competencia en la AGEB | -0.005 ± 0.007 | — | — | +0.8 |
| Actividad (negocios a 500 m) | 0.043 ± 0.012 | — | — | +1.0 |

Mejor línea base ingenua (con su mejor dirección): actividad (negocios a 500 m), 0.043.

### Aperturas crudas (referencia) — AUC

| Puntuación | Valor | Lift 5 % | Lift 10 % | Δ pts 10 % |
|---|---|---|---|---|
| Score anterior (v2.1, pesos del autor) | 0.583 ± 0.007 | 1.16 | 1.16 | +4.7 |
| **Score nuevo, pesos fuera de muestra (cifra principal)** | **0.577 ± 0.007** | 1.13 | 1.12 | +3.6 |
| Score nuevo, pesos entregados (dentro de muestra) | 0.579 ± 0.007 | 1.15 | 1.15 | +4.1 |
| Sensibilidad: pesos aprendidos solo con objetivos limpios (fuera de muestra) | 0.578 ± 0.008 | 1.06 | 1.07 | +1.0 |
| Núcleo: aperturas por competidor | 0.563 ± 0.008 | 1.12 | 1.12 | +2.4 |
| Aperturas esperadas (modelo) | 0.676 ± 0.008 | 2.07 | 1.84 | +19.4 |
| Captura Huff (1/(1+competidores)) | 0.348 ± 0.008 | 0.52 | 0.52 | -15.9 |
| Gasto potencial × captura | 0.436 ± 0.008 | 0.66 | 0.67 | -12.0 |
| Población objetivo × NSE × captura | 0.468 ± 0.010 | 0.79 | 0.80 | -6.2 |
| Flujo de gente (proxy) | 0.601 ± 0.009 | 1.41 | 1.30 | +5.6 |
| Complementarios | 0.637 ± 0.008 | 1.80 | 1.64 | +13.8 |
| Prob. de apertura de la AGEB (modelo) | 0.806 ± 0.008 | 2.82 | 2.43 | +32.2 |
| Prob. de seguir abierto (modelo dedicado) | 0.547 ± 0.009 | 0.99 | 1.05 | +1.8 |
| Densidad de población | 0.542 ± 0.008 | 0.64 | 0.81 | -4.3 |
| Competencia Huff | 0.652 ± 0.008 | 1.99 | 1.75 | +17.0 |
| Competencia en la AGEB | 0.711 ± 0.014 | 2.44 | 2.10 | +27.1 |
| Actividad (negocios a 500 m) | 0.636 ± 0.007 | 1.70 | 1.62 | +13.3 |

Mejor línea base ingenua (con su mejor dirección): competencia en la AGEB, 0.711.

#### Por giro: crecimiento neto, con y sin carga censal

| Giro | ρ score anterior | ρ score nuevo (fuera de muestra) | ρ mejor línea base (abs.) | Δ pts 10 % nuevo | ρ neto sin carga: anterior | nuevo |
|---|---|---|---|---|---|---|
| tienda_mascotas | 0.187 | 0.382 | 0.245 | +38.2 | 0.178 | 0.190 |
| sushi | 0.442 | 0.355 | 0.212 | +24.3 | 0.411 | 0.365 |
| spa | 0.267 | 0.341 | 0.284 | +37.5 | 0.180 | 0.233 |
| consultorio_dental | -0.065 | 0.317 | 0.373 | +12.9 | -0.095 | 0.138 |
| gimnasio | 0.107 | 0.309 | 0.231 | +17.2 | 0.248 | 0.272 |
| veterinaria | 0.172 | 0.275 | 0.178 | +19.8 | 0.110 | 0.075 |
| floreria | 0.110 | 0.259 | 0.155 | +22.0 | -0.043 | -0.105 |
| purificadora | 0.087 | 0.250 | 0.048 | +15.9 | 0.075 | 0.073 |
| lavanderia | -0.011 | 0.208 | 0.225 | +10.5 | 0.062 | 0.009 |
| barberia_estetica | -0.118 | 0.206 | 0.208 | +12.3 | 0.102 | 0.086 |
| taqueria | 0.147 | 0.194 | 0.130 | +11.2 | 0.078 | 0.054 |
| pizzeria | 0.138 | 0.191 | 0.194 | +22.0 | 0.032 | -0.012 |
| pasteleria | 0.066 | 0.189 | 0.241 | +4.1 | -0.029 | 0.092 |
| ferreteria | -0.021 | 0.183 | 0.103 | +7.4 | 0.081 | 0.095 |
| tortilleria | 0.153 | 0.179 | 0.076 | +5.8 | 0.138 | 0.165 |
| tienda_ropa | -0.072 | 0.178 | 0.239 | +28.2 | 0.081 | -0.004 |
| fruteria | 0.127 | 0.169 | 0.110 | +11.6 | 0.092 | -0.028 |
| farmacia | 0.045 | 0.166 | 0.099 | +10.6 | 0.070 | 0.092 |
| tienda_celulares | 0.025 | 0.166 | 0.085 | +23.6 | -0.029 | -0.093 |
| cerrajeria | 0.110 | 0.159 | 0.117 | +8.4 | 0.007 | -0.103 |
| zapateria | 0.061 | 0.159 | 0.047 | +6.0 | 0.018 | -0.001 |
| consultorio_medico | 0.060 | 0.149 | 0.159 | +7.8 | -0.051 | 0.038 |
| cafeteria | 0.136 | 0.142 | 0.140 | +11.7 | -0.016 | -0.049 |
| taller_mecanico | -0.295 | 0.141 | 0.315 | +4.3 | 0.083 | -0.099 |
| carniceria | 0.068 | 0.135 | 0.158 | +8.9 | 0.004 | -0.092 |
| papeleria | -0.015 | 0.130 | 0.116 | +6.4 | 0.067 | 0.093 |
| fonda | 0.093 | 0.123 | 0.081 | +3.9 | 0.146 | 0.040 |
| heladeria | 0.036 | 0.119 | 0.148 | +9.7 | -0.019 | -0.047 |
| panaderia | 0.093 | 0.100 | 0.157 | +4.4 | 0.042 | 0.002 |
| laboratorio_clinico | -0.012 | 0.073 | 0.174 | +2.9 | 0.044 | 0.054 |
| abarrotes | -0.043 | 0.072 | 0.109 | +3.5 | 0.092 | 0.081 |
| bar | -0.043 | 0.063 | 0.079 | +4.2 | 0.029 | -0.018 |
| optica | -0.074 | 0.055 | 0.172 | +0.2 | -0.087 | -0.045 |
| cafe_internet | 0.095 | 0.031 | 0.203 | -0.2 | 0.069 | -0.043 |
| escuela_idiomas | -0.099 | -0.069 | 0.164 | -5.2 | 0.017 | 0.023 |
| libreria | -0.312 | -0.359 | 0.289 | -29.8 | -0.209 | -0.210 |

En crecimiento neto, el score nuevo (pesos fuera de muestra) supera a la mejor línea base en 18 de 36 giros; el anterior, en 7. Sin la carga censal, el nuevo supera al anterior en 13 de 36 giros. Tabla completa (todos los objetivos, giro por giro): `models/validacion_score.csv`.

### Robustez del crecimiento neto: sin normalizar, por habitante y sin la carga censal

Como la tasa de crecimiento neto comparte denominador con la competencia, se repite sin normalizar (aperturas − desapariciones en el círculo) y por 10 mil habitantes, con todas las AGEB. La última columna quita la carga de los Censos Económicos 2024: (altas fuera de la carga − desapariciones) / establecimientos de 2020, con las mismas AGEB elegibles que la tasa. Valor = ρ de Spearman promedio entre giros.

| Puntuación | Neto sin normalizar | Neto por 10 mil hab. | Neto sin carga censal |
|---|---|---|---|
| Score anterior (v2.1, pesos del autor) | 0.078 | -0.026 | 0.055 |
| Score nuevo, pesos fuera de muestra (cifra principal) | 0.176 | 0.090 | 0.037 |
| Score nuevo, pesos entregados (dentro de muestra) | 0.191 | 0.105 | 0.039 |
| Sensibilidad: pesos aprendidos solo con objetivos limpios (fuera de muestra) | 0.016 | -0.078 | 0.077 |
| Núcleo: aperturas por competidor | 0.247 | 0.220 | -0.008 |
| Captura Huff (1/(1+competidores)) | 0.096 | 0.176 | -0.001 |
| Población objetivo × NSE × captura | 0.146 | 0.095 | 0.025 |
| Flujo de gente (proxy) | -0.011 | -0.098 | 0.065 |
| Prob. de apertura de la AGEB (modelo) | 0.068 | 0.036 | -0.005 |
| Densidad de población | 0.048 | -0.049 | -0.004 |
| Competencia Huff | -0.096 | -0.176 | 0.001 |
| Competencia en la AGEB | -0.058 | -0.087 | -0.005 |
| Actividad (negocios a 500 m) | 0.027 | -0.063 | 0.043 |

Lectura: sin normalizar: el score nuevo (fuera de muestra) saca 0.176 contra 0.096 de competencia Huff (le gana; el núcleo solo saca 0.247); por 10 mil habitantes: el score nuevo (fuera de muestra) saca 0.090 contra 0.176 de competencia Huff (NO le gana; el núcleo solo saca 0.220). La conclusión se sostiene en la tasa y en el conteo; por habitante, el signo de la competencia domina. **Sin la carga censal la ventaja desaparece**: el núcleo cae a -0.008 y la captura Huff a -0.001, el score nuevo queda en 0.039 (0.037 fuera de muestra) y el anterior en 0.055; el mejor de la tabla es el flujo de gente (0.065). Por qué: la carga registra negocios que ya existían; donde el DENUE 2020 los dejó fuera, el stock de 2020 sale bajo y los «nuevos» altos, y λ/(1 + competidores) lo lee como mercado en crecimiento sin saturar. En los cuartiles del stock de 2020 la parte de «nuevos» que es carga va de 89 % a 91 %, y la mediana de nuevos por establecimiento de 2020 (A/H) de 0.31 a 0.35: la contaminación es pareja y no se corrige con un filtro simple.

## 3. Qué se decidió y por qué

**Se cambió el score a la versión 3.0; hay que decir con claridad qué prueba ese cambio y qué no.** El anterior no le ganaba a las líneas base en crecimiento neto y el nuevo sí, pero esa ventaja viene de la carga de los Censos Económicos 2024 (sección 2, robustez): sin la carga el nuevo no le gana al anterior. El cambio tiene dos partes:

1. **Núcleo sin parámetros.** El término de aperturas pasó de «aperturas esperadas» a «**aperturas esperadas por competidor**» = aperturas esperadas × captura Huff = λ / (1 + competidores ponderados). Es presión de entrada sobre el stock que ya hay: donde se esperan muchas entradas y casi no hay competidores, el mercado está creciendo sin estar saturado. Se probó también multiplicar por la probabilidad de seguir abierto (la definición «apertura × sobrevivir × captura»): no mejora ningún objetivo, porque dentro de un giro esa probabilidad casi no varía entre lugares.
2. **Pesos aprendidos, no puestos.** Pesos no negativos que suman 1, ajustados en 4 de 5 pliegues de municipios y reportados en el que no vieron (el entregado se reajusta con todos los datos y se redondea a 0.05); el criterio es la correlación de los percentiles del score con los de los tres objetivos, con el mismo peso para crecimiento neto, sobrevivencia y altas fuera de la carga censal. Restricción a priori: la demanda (gasto potencial + población objetivo) pesa al menos 25 %, porque la teoría de localización dice que la demanda atrae entrada y los objetivos, que son de oferta, la ven poco. Costo de la restricción: ρ medio de los tres objetivos, fuera de muestra, 0.076 con el piso y 0.082 sin él. Resultado:

| Término del score | Peso anterior | Pliegue 0 | 1 | 2 | 3 | 4 | Ajuste final | **Entregado (a 0.05)** |
|---|---|---|---|---|---|---|---|---|
| núcleo: aperturas esperadas por competidor | 0.30 | 0.36 | 0.34 | 0.27 | 0.36 | 0.36 | 0.34 | **0.35** |
| gasto potencial × captura Huff | 0.25 | 0.08 | 0.11 | 0.01 | 0.04 | 0.01 | 0.05 | **0.05** |
| población objetivo × NSE × captura | 0.15 | 0.17 | 0.14 | 0.24 | 0.21 | 0.24 | 0.20 | **0.20** |
| flujo de gente (proxy) | 0.20 | 0.16 | 0.12 | 0.26 | 0.09 | 0.00 | 0.13 | **0.10** |
| complementarios | 0.10 | 0.23 | 0.29 | 0.22 | 0.30 | 0.39 | 0.29 | **0.30** |

Entre pliegues, el núcleo (0.27–0.36), la población (0.14–0.24) y los complementarios (0.22–0.39) son estables; el gasto potencial (0.01–0.11) y el flujo (0.00–0.26) no, y por eso los pesos chicos se redondean a 0.05 y no hay que leer de más. La restricción de demanda quedó activa (gasto + población = 0.25). Ojo con el criterio: los tres objetivos pesan igual y se contraponen (el crecimiento neto castiga la competencia, las altas reales la premian y la sobrevivencia es indiferente); con solo crecimiento neto el núcleo llega a ρ = 0.230, el score con los pesos entregados a 0.182 y fuera de muestra a 0.159. Esa mezcla es un juicio, y por eso se publica el detalle. El score sigue siendo un percentil por giro de 0 a 100, interpretable y cabe en una lámina: **score = 100 × [0.35·P(aperturas por competidor) + 0.05·P(gasto × captura) + 0.20·P(población objetivo × NSE × captura) + 0.10·P(flujo) + 0.30·P(complementarios)]**, donde P es el percentil dentro del giro. `prob_sobrevive` queda fuera del score y se reporta como dato de riesgo.

**Qué sostiene la elección del 3.0 y qué no.** Entre los objetivos que no dependen de la carga censal (sobrevivencia, altas fuera de la carga y crecimiento neto sin carga), el 3.0 saca ρ = 0.022, 0.046 y 0.037 fuera de muestra, y el 2.1 0.028, 0.108 y 0.055: empata en sobrevivencia y **pierde en los otros dos**. No hay evidencia limpia de que sea mejor. Se conserva por una razón de diseño y no por una victoria medida: el núcleo «aperturas esperadas por competidor» pone la saturación en el centro del orden (la pregunta de quien abre un negocio es dónde hay espacio, no dónde ya hay muchos), y los pesos quedan aprendidos con un criterio explícito y publicado en lugar de puestos a mano. Su costo está a la vista en las tablas: ni este score ni el anterior pasan de ρ = 0.108 en un objetivo limpio; con dos cortes del DENUE y sin ventas ni rentas la validación sirve para descartar, no para confirmar.

**Sensibilidad: qué pasa si el aprendizaje usa solo objetivos limpios.** Se repitió el aprendizaje con sobrevivencia, altas fuera de la carga y crecimiento neto sin carga (mismos pliegues y mismo piso de demanda); **no se entrega**, es para ver el trade-off. Pesos: núcleo: aperturas esperadas por competidor 0.00, gasto potencial × captura Huff 0.25, población objetivo × NSE × captura 0.00, flujo de gente (proxy) 0.50, complementarios 0.25. Fuera de muestra saca ρ = 0.077 en neto sin carga, 0.148 en altas fuera de la carga y 0.038 en sobrevivencia (mejora a ambos scores en lo limpio), pero -0.024 en crecimiento neto y AUC 0.578 en aperturas crudas. Le quita todo el peso al núcleo anti-saturación y ordena hacia donde ya hay negocios (flujo y complementarios): predice dónde hay actividad, no dónde hay hueco. Por eso no se adopta; pero muestra que, si el criterio fuera solo lo limpio, el score sería otro, y que la decisión de diseño es de quien lo usa.

**Lo que el score nuevo no hace.** (1) No predice mejor aperturas crudas: baja a un AUC de 0.577 fuera de muestra (era 0.583), y está bien por la sección 1. (2) No predice sobrevivencia. (3) En altas fuera de la carga censal (ρ = 0.046 fuera de muestra, antes 0.108) no gana: esa señal premia flujo y competencia, que son justo lo que el nuevo score baja o pesa menos. Son pocas altas (el DENUE las registra sobre todo en negocios visibles) y se reportan tal cual. (4) Es evidencia observacional de un solo par de cortes: el modelo de aperturas se entrenó con 2020→2026 y se aplica a 2026 suponiendo que la relación se mantiene. (5) No es mejor que el anterior en lo que no depende de la carga censal: su ventaja en crecimiento neto viene de ella (sección 2).

## 4. Decil imputado: exactitud por banda de NSE

Se repite la validación cruzada de `scripts/02_features.py` (3,767 hogares de la ENIGH 2024, ámbito ZMVM, 695 UPM; regresión lineal ponderada de log ingreso sobre escolaridad del jefe, auto, internet, PC y tamaño del hogar; 5 pliegues por UPM) y se mide por banda de NSE (bajo = deciles 1-4, medio = 5-8, alto = 9-10, convención del proyecto). Fuente: ENIGH 2024 (INEGI) y modelo propio.

- Decil exacto: **17.9 %**; ±1 decil: 50.4 % (el azar da 10 % y ~28 %).
- **Banda exacta: 57.7 %.** Referencias: azar con las proporciones de cada banda, 36 %; decir siempre «medio», 40 %. Error grave (bajo ↔ alto): 1.1 % de los hogares. Probabilidad media que el modelo da a la banda correcta: 0.48.

| Banda real | Hogares (ponderado) | Acierto (la clasificó en su banda) | Cayó en bajo | medio | alto |
|---|---|---|---|---|---|
| bajo | 40 % | **59 %** | 59 % | 39 % | 1 % |
| medio | 40 % | **70 %** | 22 % | 70 % | 8 % |
| alto | 20 % | **29 %** | 3 % | 68 % | 29 % |

**Lectura honesta.** A nivel de hogar el decil es una estimación débil (el Censo no trae ingreso); la banda sirve para distinguir lo bajo de lo alto (solo 1.1 % de los hogares cae a dos bandas de distancia), pero se confunde con la banda vecina y subdetecta lo alto: la regresión es conservadora y manda a «medio» a 68 % de los hogares de nivel alto. El producto no clasifica hogares: asigna el hogar típico de una AGEB y guarda probabilidades (`p_nse_*`). A nivel AGEB y municipio el estimado se contrasta con la marginación de CONAPO 2020 (ρ = 0.88) y con el ingreso promedio municipal de la ENIGH en 35 municipios (ρ = 0.90, `reports/decil_imputado.md`); a nivel AGEB no hay ingreso observado contra el cual medir la banda. Esta validación es por hogar y sin el estiramiento ecológico que se aplica a las AGEB, así que no es exactamente la del producto. Conviene decir «NSE estimado» y no «NSE de la colonia».

## Reproducir

```bash
OMP_NUM_THREADS=6 nice -n 10 uv run python scripts/03b_validar_score.py        # reaprende pesos, evalúa, reescribe este reporte
uv run python scripts/03_entrenar.py --solo-scores                                       # regenera models/scores_giros.parquet con esos pesos
uv run pytest tests/test_modelo.py -q
```
