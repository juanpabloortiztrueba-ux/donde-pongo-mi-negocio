# Ficha de municipio: Acolman (Estado de México), clave 15002

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 160,121 habitantes (lugar 36 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 43,758. AGEB urbanas: 58. Superficie urbana de esas AGEB: 35.0 km².
- Densidad: 4,577 hab/km² (lugar 43 de 76).
- Edad: 0-14 años 24.0 %; 15-24 18.2 %; 25-59 48.4 %; 60 o más 9.4 %.
- Escolaridad promedio de la población de 15 y más: 10.0 años (lugar 50 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 40.4 %; con internet: 50.9 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 80.6 %, medio 19.4 %, alto 0.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 44.9 %; Medio 26.0 %; Alto 15.3 %; Muy alto 13.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 9,199 (57.5 por cada 1 000 habitantes, lugar 38 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 7,237. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 35,196.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 4,499 | 48.9 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,432 | 15.6 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 942 | 10.2 % |
| 31 Industrias manufactureras | 620 | 6.7 % |
| 62 Servicios de salud y de asistencia social | 336 | 3.7 % |
| 43 Comercio al por mayor | 258 | 2.8 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,229 |
| 812110 | Salones y clínicas de belleza y peluquerías | 516 |
| 465311 | Comercio al por menor de artículos de papelería | 398 |
| 467115 | Comercio al por menor de artículos para la limpieza | 261 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 243 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 204 |
| 464111 | Farmacias sin minisúper | 187 |
| 461122 | Comercio al por menor de carne de aves | 183 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 181 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 171 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,262 | 78.8 |
| barberia_estetica | 516 | 32.2 |
| papeleria | 398 | 24.9 |
| carniceria | 281 | 17.5 |
| taller_mecanico | 237 | 14.8 |
| farmacia | 198 | 12.4 |
| ferreteria | 181 | 11.3 |
| fruteria | 171 | 10.7 |
| tortilleria | 167 | 10.4 |
| tienda_ropa | 150 | 9.4 |
| fonda | 147 | 9.2 |
| taqueria | 137 | 8.6 |
| panaderia | 116 | 7.2 |
| cafeteria | 110 | 6.9 |
| purificadora | 102 | 6.4 |
| consultorio_dental | 88 | 5.5 |
| lavanderia | 87 | 5.4 |
| heladeria | 75 | 4.7 |
| cafe_internet | 62 | 3.9 |
| consultorio_medico | 57 | 3.6 |
| gimnasio | 53 | 3.3 |
| tienda_mascotas | 52 | 3.2 |
| tienda_celulares | 50 | 3.1 |
| floreria | 37 | 2.3 |
| bar | 34 | 2.1 |
| pasteleria | 25 | 1.6 |
| pizzeria | 23 | 1.4 |
| zapateria | 22 | 1.4 |
| veterinaria | 19 | 1.2 |
| cerrajeria | 15 | 0.9 |
| spa | 14 | 0.9 |
| laboratorio_clinico | 11 | 0.7 |
| optica | 8 | 0.5 |
| sushi | 4 | 0.2 |
| escuela_idiomas | 3 | 0.2 |
| comida_china | 3 | 0.2 |
| guarderia | 3 | 0.2 |
| libreria | 1 | 0.1 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| GEOVILLAS DE TERRANOVA | 5 | 35,108 | 1,294 | bajo |
| LA LAGUNA | 6 | 19,670 | 851 | bajo |
| TEPEXPAN | 3 | 8,858 | 790 | medio |
| ACOLMAN DE NEZAHUALCOYOTL | 4 | 6,449 | 590 | medio |
| SAN MIGUEL TOTOLCINGO | 2 | 5,407 | 568 | bajo |
| LAS BRISAS | 5 | 9,301 | 548 | bajo |
| LOS ÁNGELES | 1 | 4,498 | 541 | bajo |
| SAN MATEO CHIPILTEPEC | 4 | 9,377 | 537 | bajo |
| SAN MARCOS NEPANTLA | 4 | 5,462 | 523 | bajo |
| SANTA CATARINA | 2 | 6,708 | 483 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| ACOLMAN DE NEZAHUALCOYOTL | 6,449 | 5.4 |
| TEPEXPAN | 8,858 | 5.0 |
| GRANJAS FAMILIARES | 4,908 | 4.8 |
| GEOVILLAS DE TERRANOVA | 35,108 | 4.8 |
| MISION SAN AGUSTIN | 5,561 | 4.8 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LAS BRISAS | 9,301 | 3.2 |
| SAN MARCOS NEPANTLA | 5,462 | 3.2 |
| LÁZARO CARDENAS | 7,976 | 3.3 |
| SAN MATEO CHIPILTEPEC | 9,377 | 3.7 |
| LA LAGUNA | 19,670 | 3.7 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 234.2 millones de pesos por trimestre.
- Por hogar: 5,351 pesos por trimestre (lugar 50 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
