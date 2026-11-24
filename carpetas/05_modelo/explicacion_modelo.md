# Qué hace el modelo y qué no puede decir

Generado por `scripts/04a_carpetas.py` el 2026-11-23. El diseño viene de `docs/CONTRATO.md`; los resultados, de `reports/validacion.md` y `models/metadata.json` cuando existen.

## Qué es

El modelo de **aperturas** aprende en qué AGEB aparecen establecimientos de un giro. Para cada pareja (AGEB, giro), la etiqueta es 1 si en el DENUE de mayo de 2026 hay al menos un establecimiento del giro que no estaba en el DENUE de noviembre de 2020 (se empata por identificador y, como respaldo, por nombre y coordenadas). También hay una variante «sobrevivió»: el establecimiento está en ambos cortes. Las variables son las de `agebs_features` (población, densidad, NSE estimado, gasto potencial, transporte, escuelas, hospitales, plazas, negocios por sector alrededor) más competencia y complementarios del giro **en el corte de 2020**, para no filtrar información del futuro. El algoritmo es `HistGradientBoostingClassifier` de scikit-learn (no LightGBM, porque en esta Mac falta libomp y rompería la replicabilidad).

## Cómo se califica una zona

La función `app/motor.py: score_giro(giro_clave)` regresa, por AGEB: probabilidad de apertura, demanda, competencia, complementarios, score y razones. La forma exacta en que se combinan esos componentes está en `app/motor.py` y se describe en la validación de abajo; esta explicación no la repite para no contradecir al código. Las razones son los números que explican el score, para que la respuesta cite cifras.

## Cómo se valida

Validación espacial: se deja fuera cada vez un grupo de alcaldías o municipios (GroupKFold por `cvegeo_mun`), de modo que el modelo se prueba en municipios que no vio. Se reportan AUC, precisión en el top-k y la comparación con una línea base ingenua (ordenar solo por densidad de población). Si el modelo no le gana a la línea base, hay que decirlo.

## Resultados de la validación

Copiados de `reports/validacion.md` (modificado el 2026-11-23). Esa es la fuente; si cambia, volver a generar.

## Validación del modelo de aperturas (etapa Modelo E)

Generado por `scripts/03_entrenar.py` el 2026-11-23 · modelo `89c7b8e6f737` · sklearn HistGradientBoostingClassifier (scikit-learn 1.9.1).

### Qué predice

Para cada par (AGEB urbana de la ZMVM, giro de `config/giros.yaml`) la probabilidad de que **aparezca al menos un establecimiento del giro** en el DENUE de 05/2026 que no estaba en el DENUE de 11/2020 (ventana de ~5.5 años). Un establecimiento es «nuevo» si su `id` no está en el corte 11/2020 y tampoco hay, a ≤ 50 m, un establecimiento del corte 11/2020 que desapareció con el mismo nombre normalizado (cambio de `id`). El giro se identifica con `codigo_act` (actual) y `codigo_act_actual` (histórico, traducido a SCIAN 2023 por Datos B), más el filtro por nombre `scian_con_filtro`.

- Ids: 1,081,737 en 05/2026, 996,622 en 11/2020, 651,710 en ambos. Empatados por nombre y distancia: 5,430. Nuevos: **424,595**. Del corte 11/2020 siguen en 05/2026 el 65.95 %.
- **Aviso fuerte: «apareció en el DENUE» no es lo mismo que «abrió».** De los nuevos, 382,982 tienen `fecha_alta` 2024: es la carga de los Censos Económicos 2024, que además de aperturas reales suma negocios que ya existían y el DENUE no tenía. Fuente: DENUE 05/2026 y 11/2020 (INEGI, ver `data/FUENTES.md`).
- Filas de entrenamiento: 235,000 (5 875 AGEB × 40 giros); tasa base global 0.322. Por giro va de 0.0002 (renta_bicicletas) a 0.86 (abarrotes).

### Sin fuga de información

- Todo lo que sale del DENUE se calcula en el **corte 11/2020** (sectores SCIAN a 500 m y 1 km, empleo, población diurna, escuelas, hospitales, plazas, competencia y complementarios del giro). La etiqueta sale de lo que aparece después.
- Transporte en 11/2020: se quitan las estaciones con `anio_apertura` > 2020 (Cablebus líneas 1, 2, 3; Metrobus líneas 3, 4, 5, 7, 51 filas) y el Tren Interurbano (sin año en el archivo; su tramo en la ZMVM no operaba en 2020, supuesto del autor). Mexibús y Mexicable no traen año de apertura en `transporte.parquet` y se dejan (posible fuga menor).
- Censo 2020 y marginación CONAPO 2020 son anteriores a la ventana. El decil imputado usa variables del Censo 2020; el gasto potencial usa la ENIGH 2024 (gasto por decil), que no contiene información de establecimientos.
- No entran nombres de colonia, municipio ni coordenadas. Sí entra `es_cdmx` (entidad).
- Para recomendar, el modelo entrenado con 11/2020 → 05/2026 se aplica a las mismas variables medidas en **05/2026** (`score_giro`), suponiendo que la relación se mantiene en la siguiente ventana.

### Modelo y validación espacial

Un modelo global con el giro como variable categórica (`giro_cod`) y 101 variables. Parámetros: `{"learning_rate": 0.06, "max_iter": 800, "max_leaf_nodes": 31, "min_samples_leaf": 80, "l2_regularization": 1.0, "early_stopping": true, "validation_fraction": 0.1, "n_iter_no_change": 25, "random_state": 0}`; 546 iteraciones en el ajuste final.
Validación **GroupKFold por municipio** (`cvegeo_mun`, 5 pliegues): cada municipio queda entero en entrenamiento o en prueba, así que el modelo se evalúa en alcaldías y municipios que no vio.

| Pliegue | Filas de prueba | Municipios en prueba | AUC | Iteraciones |
|---|---|---|---|---|
| 0 | 47,040 | 15 | 0.892 | 491 |
| 1 | 46,960 | 14 | 0.894 | 545 |
| 2 | 47,040 | 15 | 0.882 | 500 |
| 3 | 47,000 | 16 | 0.891 | 438 |
| 4 | 46,960 | 16 | 0.893 | 559 |

Fuera de pliegue (todas las filas): AUC global **0.891**, average precision 0.811. El AUC global mezcla giros (parte se explica por la tasa base de cada giro); lo que importa es el AUC **dentro** de cada giro, abajo.

### Por giro: modelo contra líneas base

Puntuaciones comparadas, todas fuera de pliegue y dentro de cada giro (5 875 AGEB): **modelo** (probabilidad); **densidad** de población (hab/km², Censo 2020); **competencia** (competidores del giro con peso Huff en su radio, 11/2020); **comp. AGEB** (competidores del giro dentro de la propia AGEB, 11/2020); **actividad** (establecimientos de todo tipo a 500 m, 11/2020); y el **score** combinado de `score_giro` (ver abajo). AP = average precision; P@k = proporción de las k AGEB mejor puntuadas donde sí apareció el giro.

Resumen (giros con ≥ 30 AGEB con apertura, 38 de 40): el modelo supera en AUC a la densidad en **38**, a la competencia Huff en **38**, a la competencia dentro de la AGEB en **38** y a la actividad en **38**; en P@100 iguala o supera a densidad y competencia a la vez en 38. AUC medio: modelo 0.806, densidad 0.542, competencia 0.652, competencia en la AGEB 0.711, actividad 0.636, score vigente 0.579, score anterior (v2.1) 0.583. **El score no se diseñó para predecir aperturas crudas y por eso queda debajo**: ver «¿Por qué el score no predice aperturas crudas y está bien?» abajo.

| Giro | AGEB con apertura | Tasa | AUC modelo | AUC dens. | AUC comp. | AUC comp. AGEB | AUC activ. | AUC score vigente | AUC score anterior | AP modelo | AP dens. | AP comp. | P@50 modelo | P@100 modelo | P@100 dens. | P@100 comp. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| abarrotes | 5,051 | 0.860 | **0.929** | 0.633 | 0.773 | 0.898 | 0.661 | 0.621 | 0.630 | **0.987** | 0.885 | 0.950 | 1.00 | 1.00 | 0.72 | 0.99 |
| barberia_estetica | 4,718 | 0.803 | **0.928** | 0.665 | 0.762 | 0.895 | 0.750 | 0.582 | 0.656 | **0.980** | 0.842 | 0.921 | 1.00 | 1.00 | 0.61 | 0.99 |
| papeleria | 3,804 | 0.647 | **0.856** | 0.591 | 0.688 | 0.806 | 0.590 | 0.585 | 0.560 | **0.908** | 0.681 | 0.784 | 0.98 | 0.99 | 0.53 | 0.89 |
| carniceria | 3,567 | 0.607 | **0.892** | 0.609 | 0.731 | 0.851 | 0.621 | 0.624 | 0.606 | **0.923** | 0.651 | 0.788 | 1.00 | 0.99 | 0.44 | 0.89 |
| fonda | 3,546 | 0.604 | **0.847** | 0.561 | 0.686 | 0.786 | 0.691 | 0.653 | 0.653 | **0.890** | 0.611 | 0.762 | 1.00 | 1.00 | 0.36 | 1.00 |
| farmacia | 3,464 | 0.590 | **0.843** | 0.573 | 0.669 | 0.776 | 0.643 | 0.589 | 0.579 | **0.876** | 0.609 | 0.732 | 1.00 | 1.00 | 0.36 | 0.91 |
| taqueria | 3,379 | 0.575 | **0.831** | 0.563 | 0.668 | 0.776 | 0.676 | 0.651 | 0.644 | **0.862** | 0.594 | 0.719 | 1.00 | 1.00 | 0.42 | 0.92 |
| cafeteria | 3,306 | 0.563 | **0.834** | 0.555 | 0.684 | 0.772 | 0.683 | 0.658 | 0.668 | **0.862** | 0.568 | 0.729 | 1.00 | 1.00 | 0.27 | 0.94 |
| tienda_ropa | 3,139 | 0.534 | **0.881** | 0.556 | 0.658 | 0.810 | 0.660 | 0.516 | 0.550 | **0.895** | 0.544 | 0.669 | 1.00 | 1.00 | 0.32 | 0.81 |
| fruteria | 3,042 | 0.518 | **0.844** | 0.572 | 0.681 | 0.792 | 0.578 | 0.611 | 0.573 | **0.842** | 0.542 | 0.664 | 0.96 | 0.96 | 0.28 | 0.72 |
| taller_mecanico | 2,930 | 0.499 | **0.831** | 0.542 | 0.627 | 0.784 | 0.609 | 0.486 | 0.503 | **0.820** | 0.501 | 0.611 | 0.98 | 0.96 | 0.23 | 0.77 |
| consultorio_dental | 2,610 | 0.444 | **0.820** | 0.580 | 0.665 | 0.763 | 0.691 | 0.552 | 0.615 | **0.767** | 0.471 | 0.592 | 0.94 | 0.94 | 0.26 | 0.77 |
| ferreteria | 2,499 | 0.425 | **0.803** | 0.514 | 0.623 | 0.742 | 0.573 | 0.551 | 0.520 | **0.738** | 0.411 | 0.544 | 0.96 | 0.93 | 0.18 | 0.74 |
| tortilleria | 2,448 | 0.417 | **0.819** | 0.564 | 0.665 | 0.772 | 0.587 | 0.647 | 0.605 | **0.745** | 0.443 | 0.567 | 0.96 | 0.94 | 0.29 | 0.72 |
| panaderia | 2,447 | 0.417 | **0.798** | 0.561 | 0.641 | 0.713 | 0.618 | 0.623 | 0.600 | **0.715** | 0.436 | 0.539 | 0.96 | 0.89 | 0.27 | 0.63 |
| purificadora | 2,377 | 0.405 | **0.816** | 0.574 | 0.681 | 0.722 | 0.605 | 0.609 | 0.564 | **0.730** | 0.426 | 0.583 | 0.92 | 0.92 | 0.20 | 0.76 |
| lavanderia | 2,021 | 0.344 | **0.772** | 0.576 | 0.635 | 0.723 | 0.634 | 0.558 | 0.588 | **0.609** | 0.368 | 0.443 | 0.82 | 0.81 | 0.21 | 0.54 |
| tienda_mascotas | 2,015 | 0.343 | **0.784** | 0.585 | 0.639 | 0.649 | 0.664 | 0.580 | 0.594 | **0.632** | 0.379 | 0.452 | 0.88 | 0.81 | 0.22 | 0.50 |
| heladeria | 1,944 | 0.331 | **0.775** | 0.520 | 0.611 | 0.669 | 0.598 | 0.581 | 0.559 | **0.610** | 0.324 | 0.429 | 0.84 | 0.83 | 0.07 | 0.61 |
| gimnasio | 1,838 | 0.313 | **0.763** | 0.509 | 0.577 | 0.655 | 0.602 | 0.541 | 0.534 | **0.587** | 0.299 | 0.385 | 0.86 | 0.87 | 0.14 | 0.49 |
| tienda_celulares | 1,774 | 0.302 | **0.818** | 0.542 | 0.654 | 0.720 | 0.663 | 0.572 | 0.577 | **0.671** | 0.307 | 0.454 | 0.98 | 0.97 | 0.09 | 0.65 |
| consultorio_medico | 1,609 | 0.274 | **0.772** | 0.522 | 0.632 | 0.699 | 0.641 | 0.532 | 0.574 | **0.550** | 0.268 | 0.396 | 0.94 | 0.85 | 0.15 | 0.58 |
| floreria | 1,383 | 0.235 | **0.800** | 0.472 | 0.605 | 0.680 | 0.600 | 0.532 | 0.528 | **0.560** | 0.209 | 0.309 | 0.90 | 0.84 | 0.06 | 0.38 |
| bar | 1,348 | 0.229 | **0.775** | 0.471 | 0.594 | 0.613 | 0.582 | 0.541 | 0.538 | **0.499** | 0.206 | 0.327 | 0.80 | 0.78 | 0.06 | 0.64 |
| cafe_internet | 1,344 | 0.229 | **0.745** | 0.555 | 0.630 | 0.710 | 0.609 | 0.602 | 0.583 | **0.453** | 0.243 | 0.342 | 0.78 | 0.73 | 0.11 | 0.57 |
| veterinaria | 1,210 | 0.206 | **0.755** | 0.555 | 0.619 | 0.644 | 0.630 | 0.570 | 0.595 | **0.416** | 0.214 | 0.278 | 0.64 | 0.64 | 0.11 | 0.43 |
| pizzeria | 1,191 | 0.203 | **0.764** | 0.514 | 0.592 | 0.615 | 0.616 | 0.575 | 0.555 | **0.442** | 0.197 | 0.280 | 0.82 | 0.70 | 0.10 | 0.50 |
| spa | 984 | 0.167 | **0.762** | 0.516 | 0.633 | 0.598 | 0.635 | 0.575 | 0.594 | **0.395** | 0.163 | 0.258 | 0.66 | 0.58 | 0.07 | 0.42 |
| zapateria | 887 | 0.151 | **0.828** | 0.490 | 0.662 | 0.752 | 0.653 | 0.544 | 0.546 | **0.538** | 0.140 | 0.288 | 1.00 | 0.92 | 0.03 | 0.55 |
| optica | 844 | 0.144 | **0.797** | 0.518 | 0.662 | 0.697 | 0.686 | 0.563 | 0.598 | **0.448** | 0.143 | 0.262 | 0.90 | 0.84 | 0.05 | 0.46 |
| pasteleria | 728 | 0.124 | **0.744** | 0.522 | 0.577 | 0.612 | 0.584 | 0.544 | 0.537 | **0.283** | 0.126 | 0.157 | 0.44 | 0.47 | 0.06 | 0.21 |
| cerrajeria | 536 | 0.091 | **0.729** | 0.555 | 0.583 | 0.634 | 0.630 | 0.579 | 0.576 | **0.209** | 0.100 | 0.120 | 0.44 | 0.32 | 0.07 | 0.18 |
| sushi | 520 | 0.089 | **0.802** | 0.539 | 0.666 | 0.608 | 0.680 | 0.627 | 0.644 | **0.301** | 0.091 | 0.200 | 0.52 | 0.51 | 0.04 | 0.38 |
| laboratorio_clinico | 503 | 0.086 | **0.795** | 0.437 | 0.644 | 0.667 | 0.609 | 0.471 | 0.511 | **0.321** | 0.070 | 0.172 | 0.68 | 0.59 | 0.01 | 0.29 |
| guarderia | 197 | 0.034 | **0.707** | 0.540 | 0.580 | 0.565 | 0.576 | 0.555 | 0.553 | **0.076** | 0.036 | 0.046 | 0.12 | 0.11 | 0.03 | 0.06 |
| escuela_idiomas | 186 | 0.032 | **0.792** | 0.475 | 0.713 | 0.626 | 0.657 | 0.561 | 0.575 | **0.181** | 0.028 | 0.119 | 0.36 | 0.24 | 0.01 | 0.22 |
| libreria | 167 | 0.028 | **0.827** | 0.474 | 0.762 | 0.652 | 0.714 | 0.625 | 0.648 | **0.202** | 0.025 | 0.161 | 0.38 | 0.29 | 0.02 | 0.26 |
| comida_china | 133 | 0.023 | **0.752** | 0.504 | 0.617 | 0.555 | 0.671 | 0.631 | 0.615 | **0.106** | 0.024 | 0.072 | 0.18 | 0.17 | 0.02 | 0.15 |
| coworking * | 23 | 0.004 | **0.919** | 0.428 | 0.803 | 0.564 | 0.794 | 0.890 | 0.884 | **0.129** | 0.003 | 0.106 | 0.12 | 0.11 | 0.00 | 0.10 |
| renta_bicicletas * | 1 | 0.000 | **0.002** | 0.010 | 0.481 | 0.499 | 0.074 | 0.342 | 0.352 | **0.000** | 0.000 | 0.000 | 0.00 | 0.00 | 0.00 | 0.00 |

\* Menos de 30 AGEB con apertura: métricas inestables, no usar para decidir.

### Variables que más pesan

Importancia por permutación (caída de average precision al barajar la variable) en un pliegue espacial dejado fuera, 40 000 filas, 3 repeticiones. Archivo completo: `models/importancia.csv`.

| # | Variable | Caída de AP | DE |
|---|---|---|---|
| 1 | `giro_cod` | 0.1624 | 0.0014 |
| 2 | `comp_ageb` | 0.0977 | 0.0014 |
| 3 | `n_establecimientos` | 0.0649 | 0.0007 |
| 4 | `pob_0_14` | 0.0143 | 0.0003 |
| 5 | `comp_1km` | 0.0062 | 0.0003 |
| 6 | `es_cdmx` | 0.0043 | 0.0002 |
| 7 | `nse_fit` | 0.0030 | 0.0002 |
| 8 | `area_km2` | 0.0016 | 0.0004 |
| 9 | `im_2020` | 0.0015 | 0.0002 |
| 10 | `pob_diurna` | 0.0012 | 0.0001 |
| 11 | `pob_15_24` | 0.0010 | 0.0001 |
| 12 | `dist_estacion_m` | 0.0007 | 0.0003 |
| 13 | `sec81_500m` | 0.0007 | 0.0001 |
| 14 | `pob_diurna_area` | 0.0006 | 0.0001 |
| 15 | `pct_viv_auto` | 0.0006 | 0.0001 |
| 16 | `pct_viv_pc` | 0.0006 | 0.0000 |
| 17 | `sec72_500m` | 0.0005 | 0.0002 |
| 18 | `sec61_1km` | 0.0005 | 0.0001 |
| 19 | `sec54_1km` | 0.0004 | 0.0001 |
| 20 | `sec48_1km` | 0.0004 | 0.0001 |

### Variante «sobrevivió»

Modelo aparte, por establecimiento del corte 11/2020 de los 40 giros (517,372 filas): ¿sigue en 05/2026 (mismo id o mismo nombre a ≤ 50 m)? Tasa 0.684; AUC fuera de pliegue (GroupKFold por municipio) **0.590**, AP 0.743. Variables: las mismas del corte 11/2020 más el personal ocupado. En `score_giro` se reporta `prob_sobrevive` para un local nuevo de 0 a 5 personas, como dato de riesgo; **no entra al score**. Aviso: desaparecer del DENUE puede ser cierre o un cambio de registro que no se pudo empatar.

### Cómo se arma `score_giro`

`app/motor.py: score_giro(giro_clave)` → una fila por AGEB con `cvegeo, prob_apertura, demanda, competencia, complementarios, score, razones` (más `captura_huff, poblacion_objetivo, demanda_neta, pob_neta, pct_*, prob_sobrevive, nom_mun, nom_colonia, nse`). Los 40 giros ya calculados en el corte 05/2026 están en `models/scores_giros.parquet`.

Todo se mide en el **mismo círculo** de `radio_influencia_m` alrededor del centroide de la AGEB, con reparto **dasimétrico**: la población, el gasto y la intensidad de aperturas de cada AGEB se reparten parejo en una malla de puntos cada 100 m dentro de su polígono (`motor.malla_agebs`). Así una AGEB enorme no suma toda su gente en su centroide y el score no crece con el tamaño de la AGEB (ver «Sesgo por tamaño» abajo).
- `prob_apertura`: probabilidad del modelo con las variables de 05/2026 (por AGEB; crece con el tamaño de la AGEB). `aperturas_esperadas`: la intensidad -ln(1-p) de cada AGEB repartida en su superficie y sumada en el radio. El primer término del score (`prob_apertura` en los pesos, por compatibilidad) es el **núcleo**: `aperturas_esperadas × captura_huff`, o sea aperturas esperadas **por competidor**.
- `demanda`: gasto potencial trimestral del rubro ENIGH del giro (`rubro_enigh`, pesos de 2024) de los hogares dentro del radio de influencia, con peso por distancia w(d) = 1/(1+(d/d0)²), d0 = radio/2, 0 fuera del radio.
- `poblacion_objetivo`: residentes por edad ponderados con `cliente_objetivo` (Censo 2020) dentro del radio; si `demanda_base` es `diurna`, el empleo del DENUE en el radio; si es `mixta`, el promedio. `pob_neta` lo multiplica por `nse_fit` (probabilidad de que el hogar sea del NSE objetivo del giro) y por la captura Huff.
- `competencia`: competidores del giro con peso Huff (`conteos_de_giro`). **Saturación (Huff)**: un local nuevo igual de atractivo que los existentes se lleva `captura_huff = 1/(1 + competencia)` del mercado. `demanda_neta = demanda × captura_huff`.
- `flujo`: no hay aforos peatonales abiertos para la ZMVM; se usan proxies: empleo del DENUE en el radio (`empleo_radio`), negocios de corredor comercial (sectores SCIAN 46, 72 y 81) en el radio (`corredor_radio`) y transporte a 1 km (afluencia anual del Metro y número de estaciones). `flujo` = promedio de sus percentiles (transporte vale la mitad de un término).
- `complementarios`: negocios que atraen al cliente (`complementarios` de giros.yaml), con peso Huff.

**Pesos explícitos** (cada término es el percentil 0-1 de la AGEB dentro de la ZMVM para ese giro; score de 0 a 100):

| Término | Peso |
|---|---|
| percentil de `prob_apertura` | 0.35 |
| percentil de `demanda_neta` | 0.05 |
| percentil de `pob_neta` | 0.20 |
| percentil de `flujo` | 0.10 |
| percentil de `complementarios` | 0.30 |

Si el giro no tiene rubro ENIGH (`coworking`), el peso de `demanda_neta` pasa a `pob_neta`. **Los pesos no los puso el autor**: los aprendió `scripts/03b_validar_score.py` contra el crecimiento neto, la sobrevivencia y las altas fuera de la carga censal, con pesos no negativos que suman 1, ajustados en pliegues por municipio y reportados en el que no vieron, con la restricción a priori de que la demanda (gasto + población) pese al menos 25 %. Están en `models/pesos_score.json` y la evidencia en `reports/validacion_score.md`. **El score es un percentil dentro de cada giro: ordena sitios para un giro y no compara giros entre sí** (una librería con score 90 puede tener 5 % de probabilidad de apertura). Para comparar giros, `app/herramientas.py: sugerir_giros` usa la probabilidad absoluta de apertura × la de seguir abierto.

### ¿Por qué el score no predice aperturas crudas y está bien?

**Respuesta corta, como la diría Juan Pablo:** «El score no está hecho para adivinar dónde aparecen más negocios, sino dónde conviene poner uno. Las aperturas se aglomeran donde ya hay competencia: en las AGEB con 3 o más negocios del giro en 2020 aparecieron 3 nuevos por cada 10 que ya había y desaparecieron otros 3, o sea que hay mucha rotación. Un score que castiga la competencia, como debe hacerlo uno de ubicación, forzosamente queda debajo de la competencia a secas para predecir aperturas crudas. Por eso lo medí contra lo que sí corresponde a la decisión: crecimiento neto, sobrevivencia y altas fuera de la carga censal. El score nuevo le gana a las líneas base en la tasa de crecimiento neto, pero esa ventaja viene de la carga de los Censos Económicos 2024 (negocios que ya existían y no estaban en el DENUE 2020): quitando la carga (crecimiento neto sin carga censal) no le gana al score anterior, en altas fuera de la carga pierde y en sobrevivencia empata (que ninguna variable predice bien dentro de un giro). Por eso lo conservo como decisión de diseño, no como victoria medida; el detalle y las limitaciones están en `reports/validacion_score.md`.»

Evidencia, promedio entre giros (ρ de Spearman; AUC en la última fila). La probabilidad de apertura es fuera de muestra por municipio; los pesos vigentes se ajustaron con todos los datos y la columna «pesos fuera de muestra» los ajusta sin ver el municipio de prueba:

| Objetivo | Score anterior (v2.1) | Score vigente | Score vigente, pesos fuera de muestra | Mejor línea base ingenua |
|---|---|---|---|---|
| Crecimiento neto | 0.046 | 0.182 | 0.159 | 0.126 |
| Sobrevivencia | 0.028 | 0.025 | 0.022 | 0.033 |
| Altas fuera de la carga censal | 0.108 | 0.045 | 0.046 | 0.100 |
| Crecimiento neto sin carga censal | 0.055 | 0.039 | 0.037 | 0.043 |
| Aperturas crudas (AUC) | 0.583 | 0.579 | 0.577 | 0.711 |

Decil imputado: acierta el decil exacto 17.9 % y ±1 decil 50.4 %; la **banda de NSE** que usa el producto (bajo 1-4, medio 5-8, alto 9-10) la acierta 57.7 % de los hogares (decir siempre «medio» daría 40 %), con 59 % de acierto en bajo, 70 % en medio y 29 % en alto. Fuente: ENIGH 2024 y modelo propio (`reports/validacion_score.md`, sección 4).

### Sesgo por tamaño de AGEB

La etiqueta («apareció ≥ 1 negocio del giro en la AGEB») crece con el tamaño de la AGEB: una AGEB con 29 mil habitantes tiene más oportunidades de que aparezca algo que una de 3 mil. Por eso `prob_apertura` no se usa tal cual en el score: todo se mide en el círculo del radio con reparto dasimétrico (arriba). Spearman entre 5 875 AGEB, promedio de los 40 giros (mínimo y máximo entre giros):

| Medida | Promedio | Mínimo | Máximo |
|---|---|---|---|
| ρ(prob_apertura por AGEB, población de la AGEB) | 0.66 | 0.38 | 0.78 |
| ρ(score, población de la AGEB) | 0.34 | 0.09 | 0.46 |
| ρ(score, área de la AGEB) | -0.25 | -0.48 | -0.15 |
| ρ(score, densidad hab/km²) | 0.60 | 0.45 | 0.75 |

Mediana del top 50 por giro (promedio de los giros): población 4,446 y área 0.23 km²; en toda la ZMVM, 3,236 y 0.26 km². Lo que queda de correlación con la población va de la mano con la densidad (zonas más pobladas por km²), que sí es una razón económica para poner un negocio. Fuente: `models/scores_giros.parquet` y Censo 2020.

### Límites

- La etiqueta es «apareció en el DENUE», sesgada por la cobertura de los Censos Económicos 2024 (ver arriba).
- Una AGEB con más hogares o más comercio tiene más oportunidades de que aparezca algo: el modelo mide oportunidad de apertura, no rentabilidad ni ventas.
- Los giros raros (renta de bicicletas, coworking, comida china, escuela de idiomas, librería, guardería) tienen pocas aperturas: su probabilidad descansa en el patrón general del modelo global.
- La validación por municipio es espacial pero no perfecta: AGEB vecinas de municipios distintos se parecen.
- La variable que más pesa es `comp_ageb` (negocios del giro que ya había en la AGEB): donde ya hay del giro es donde más aparecen, en parte por rotación (cierra uno y abre otro en el mismo local cuenta como apertura) y en parte por aglomeración.
- Los radios, el cliente objetivo, el NSE objetivo y los complementarios son supuestos de `config/giros.yaml`.

### Ejemplo: heladería, corte 05/2026 (top 5 de `score_giro`)

| AGEB | Municipio | Colonia (DENUE) | NSE | prob_apertura | Gasto potencial helados a 500 m ($/trim) | Competidores Huff | Score |
|---|---|---|---|---|---|---|---|
| 0900700014202 | Iztapalapa | MIXCOATL | bajo | 0.34 | 63,856 | 0.2 | 96.1 |
| 1503300011773 | Ecatepec de Morelos | FUENTES DE ARAGON | medio | 0.63 | 96,748 | 1.2 | 95.7 |
| 1505800010740 | Nezahualcóyotl | AGUA AZUL | medio | 0.64 | 64,831 | 0.4 | 95.1 |
| 1503100010535 | Chimalhuacán | CANTEROS | bajo | 0.74 | 40,648 | 0.5 | 94.2 |
| 1505800010539 | Nezahualcóyotl | BENITO JUAREZ | bajo | 0.73 | 54,535 | 0.8 | 94.0 |

Fuentes: modelo de este reporte; ENIGH 2024 (gasto por decil, ámbito zmvm) y decil imputado (`reports/decil_imputado.md`); DENUE 05/2026; Censo 2020. El rubro `helados` de la ENIGH tiene pocos hogares con gasto: sirve para ordenar, no para dimensionar.

### Reproducir

```bash
OMP_NUM_THREADS=6 nice -n 10 uv run python scripts/03_entrenar.py      # etiquetas, validación, modelos, scores, este reporte
uv run python scripts/03_entrenar.py --solo-reporte                     # solo reescribe este archivo
uv run pytest tests/test_modelo.py -q
```

Tiempo de la última corrida completa: 279 s.

## Metadatos del modelo entrenado

De `models/metadata.json`:

```json
{
 "fecha": "2026-11-23",
 "modelo": "sklearn HistGradientBoostingClassifier",
 "sklearn": "1.9.1",
 "params": {
  "learning_rate": 0.06,
  "max_iter": 800,
  "max_leaf_nodes": 31,
  "min_samples_leaf": 80,
  "l2_regularization": 1.0,
  "early_stopping": true,
  "validation_fraction": 0.1,
  "n_iter_no_change": 25,
  "random_state": 0
 },
 "n_iter_final": 546,
 "modelo_id": "89c7b8e6f737",
 "features": [
  "giro_cod",
  "area_km2",
  "pob_total",
  "pob_0_14",
  "pob_15_24",
  "pob_25_59",
  "pob_60_mas",
  "hogares",
  "viviendas_habitadas",
  "prom_ocupantes",
  "escolaridad_prom",
  "pct_viv_auto",
  "pct_viv_internet",
  "pct_viv_pc",
  "pct_viv_celular",
  "pea",
  "pob_ocupada",
  "im_2020",
  "densidad_hab_km2",
  "decil_esperado",
  "ing_trim_mediano_est",
  "p_nse_bajo",
  "p_nse_medio",
  "p_nse_alto",
  "es_cdmx",
  "sec11_500m",
  "sec11_1km",
  "sec21_500m",
  "sec21_1km",
  "sec22_500m",
  "sec22_1km",
  "sec23_500m",
  "sec23_1km",
  "sec31_500m",
  "sec31_1km",
  "sec32_500m",
  "sec32_1km",
  "sec33_500m",
  "sec33_1km",
  "sec43_500m",
  "sec43_1km",
  "sec46_500m",
  "sec46_1km",
  "sec48_500m",
  "sec48_1km",
  "sec49_500m",
  "sec49_1km",
  "sec51_500m",
  "sec51_1km",
  "sec52_500m",
  "sec52_1km",
  "sec53_500m",
  "sec53_1km",
  "sec54_500m",
  "sec54_1km",
  "sec55_500m",
  "sec55_1km",
  "sec56_500m",
  "sec56_1km",
  "sec61_500m",
  "sec61_1km",
  "sec62_500m",
  "sec62_1km",
  "sec71_500m",
  "sec71_1km",
  "sec72_500m",
  "sec72_1km",
  "sec81_500m",
  "sec81_1km",
  "sec93_500m",
  "sec93_1km",
  "empleo_500m",
  "empleo_1km",
  "estab_500m",
  "estab_1km",
  "pob_diurna",
  "n_establecimientos",
  "n_escuelas_500m",
  "n_escuelas_1km",
  "n_hospitales_500m",
  "n_hospitales_1km",
  "n_plazas_500m",
  "n_plazas_1km",
  "dist_estacion_m",
  "dist_metro_m",
  "afluencia_metro_cercano",
  "n_estaciones_1km",
  "afluencia_metro_1km",
  "comp_huff",
  "comp_1km",
  "comp_ageb",
  "compl_huff",
  "giro_total_log",
  "radio_m",
  "gasto_rubro_ageb",
  "gasto_area",
  "pob_obj_ageb",
  "pob_obj_area",
  "pob_diurna_area",
  "nse_fit",
  "comp_por_10mil_obj"
 ],
 "features_sobrevivencia": [
  "giro_cod",
  "per_ocu_medio",
  "area_km2",
  "pob_total",
  "pob_0_14",
  "pob_15_24",
  "pob_25_59",
  "pob_60_mas",
  "hogares",
  "viviendas_habitadas",
  "prom_ocupantes",
  "escolaridad_prom",
  "pct_viv_auto",
  "pct_viv_internet",
  "pct_viv_pc",
  "pct_viv_celular",
  "pea",
  "pob_ocupada",
  "im_2020",
  "densidad_hab_km2",
  "decil_esperado",
  "ing_trim_mediano_est",
  "p_nse_bajo",
  "p_nse_medio",
  "p_nse_alto",
  "es_cdmx",
  "sec11_500m",
  "sec11_1km",
  "sec21_500m",
  "sec21_1km",
  "sec22_500m",
  "sec22_1km",
  "sec23_500m",
  "sec23_1km",
  "sec31_500m",
  "sec31_1km",
  "sec32_500m",
  "sec32_1km",
  "sec33_500m",
  "sec33_1km",
  "sec43_500m",
  "sec43_1km",
  "sec46_500m",
  "sec46_1km",
  "sec48_500m",
  "sec48_1km",
  "sec49_500m",
  "sec49_1km",
  "sec51_500m",
  "sec51_1km",
  "sec52_500m",
  "sec52_1km",
  "sec53_500m",
  "sec53_1km",
  "sec54_500m",
  "sec54_1km",
  "sec55_500m",
  "sec55_1km",
  "sec56_500m",
  "sec56_1km",
  "sec61_500m",
  "sec61_1km",
  "sec62_500m",
  "sec62_1km",
  "sec71_500m",
  "sec71_1km",
  "sec72_500m",
  "sec72_1km",
  "sec81_500m",
  "sec81_1km",
  "sec93_500m",
  "sec93_1km",
  "empleo_500m",
  "empleo_1km",
  "estab_500m",
  "estab_1km",
  "pob_diurna",
  "n_establecimientos",
  "n_escuelas_500m",
  "n_escuelas_1km",
  "n_hospitales_500m",
  "n_hospitales_1km",

```

## Límites que hay que decir siempre

1. **Aparecer en el DENUE no es abrir ni tener éxito.** Entre los cortes de 2020 y 2026 hay cargas masivas de los Censos Económicos y rotación de identificadores. El modelo describe dónde entraron negocios al directorio, no dónde ganaron dinero.
2. **No hay datos de ventas, rentas ni flujo peatonal por calle.** La unidad más fina es la AGEB (en promedio unas cuantas manzanas). Dentro de una AGEB la esquina importa y el modelo no la ve.
3. **El nivel socioeconómico es una estimación** (ENIGH aplicada al Censo), no un dato medido. La ENIGH no representa municipios. Ver `01_metodologia/nse_estimado.md`.
4. **Los datos son de 2020 (Censo), 2024 (ENIGH) y 2026 (DENUE).** Un barrio que cambió mucho desde 2020 puede estar mal descrito.
5. **Complementarios, radios de influencia, clientes objetivo y tickets son supuestos razonados**, no evidencia. Los tickets en particular son «supuesto» en los 40 giros y deben contrastarse con precios reales.
6. **Giros raros** (renta de bicicletas, coworking) tienen pocas observaciones en el DENUE; el modelo no tiene muestra para ellos y el resultado es poco confiable.
7. **83 AGEB** no tienen NSE ni gasto estimado; para ellas el dato es NO ENCONTRADO.
8. Zona de estudio: solo los 76 municipios de la ZMVM. Fuera de ahí (por ejemplo Monterrey) el modelo no tiene datos y debe decirlo.
