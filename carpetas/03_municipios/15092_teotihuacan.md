# Ficha de municipio: Teotihuacán (Estado de México), clave 15092

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 44,178 habitantes (lugar 48 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 12,046. AGEB urbanas: 25. Superficie urbana de esas AGEB: 14.1 km².
- Densidad: 3,142 hab/km² (lugar 59 de 76).
- Edad: 0-14 años 23.5 %; 15-24 16.3 %; 25-59 48.0 %; 60 o más 12.1 %.
- Escolaridad promedio de la población de 15 y más: 10.2 años (lugar 36 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 43.8 %; con internet: 50.6 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 55.3 %, medio 44.7 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 2.2 %; Bajo 41.8 %; Medio 53.6 %; Alto 2.4 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 4,269 (96.6 por cada 1 000 habitantes, lugar 8 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 3,494. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 15,950.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,866 | 43.7 % |
| 81 Otros servicios excepto actividades gubernamentales | 667 | 15.6 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 585 | 13.7 % |
| 31 Industrias manufactureras | 208 | 4.9 % |
| 62 Servicios de salud y de asistencia social | 200 | 4.7 % |
| 32 Industrias manufactureras | 170 | 4.0 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 449 |
| 812110 | Salones y clínicas de belleza y peluquerías | 256 |
| 465311 | Comercio al por menor de artículos de papelería | 132 |
| 461122 | Comercio al por menor de carne de aves | 94 |
| 465912 | Comercio al por menor de regalos | 89 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 86 |
| 722511 | Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida | 85 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 85 |
| 327991 | Fabricación de productos a base de piedras de cantera | 85 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 85 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 469 | 106.2 |
| barberia_estetica | 256 | 57.9 |
| carniceria | 147 | 33.3 |
| fonda | 138 | 31.2 |
| papeleria | 132 | 29.9 |
| cafeteria | 86 | 19.5 |
| tienda_ropa | 85 | 19.2 |
| taller_mecanico | 80 | 18.1 |
| farmacia | 76 | 17.2 |
| taqueria | 74 | 16.8 |
| fruteria | 63 | 14.3 |
| ferreteria | 61 | 13.8 |
| tortilleria | 56 | 12.7 |
| consultorio_dental | 47 | 10.6 |
| panaderia | 40 | 9.1 |
| bar | 38 | 8.6 |
| cafe_internet | 33 | 7.5 |
| heladeria | 31 | 7.0 |
| consultorio_medico | 28 | 6.3 |
| floreria | 28 | 6.3 |
| lavanderia | 27 | 6.1 |
| purificadora | 25 | 5.7 |
| zapateria | 21 | 4.8 |
| tienda_celulares | 19 | 4.3 |
| gimnasio | 18 | 4.1 |
| tienda_mascotas | 17 | 3.8 |
| veterinaria | 14 | 3.2 |
| optica | 12 | 2.7 |
| pizzeria | 12 | 2.7 |
| laboratorio_clinico | 10 | 2.3 |
| spa | 8 | 1.8 |
| pasteleria | 8 | 1.8 |
| escuela_idiomas | 5 | 1.1 |
| cerrajeria | 5 | 1.1 |
| sushi | 3 | 0.7 |
| libreria | 2 | 0.5 |
| comida_china | 2 | 0.5 |
| renta_bicicletas | 1 | 0.2 |
| guarderia | 1 | 0.2 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| TEOTIHUACAN CENTRO | 1 | 2,593 | 754 | medio |
| SANTA MARIA MAQUIXCO | 3 | 6,870 | 576 | bajo |
| CENTRO | 1 | 1,936 | 514 | medio |
| EVANGELISTA | 2 | 6,790 | 438 | medio |
| SAN LORENZO TLALMIMILOLPAN | 3 | 6,042 | 426 | bajo |
| ATLATONGO | 4 | 4,486 | 372 | bajo |
| SAN FRANCISCO MAZAPA | 2 | 3,332 | 288 | bajo |
| SANTA MARIA COATLAN | 2 | 3,464 | 264 | bajo |
| SAN SEBASTIAN XOLALPAN | 1 | 2,279 | 237 | medio |
| PURIFICACION | 1 | 3,363 | 216 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| EVANGELISTA | 6,790 | 5.0 |
| PURIFICACION | 3,363 | 5.0 |
| SAN FRANCISCO MAZAPA | 3,332 | 4.0 |
| SANTA MARIA COATLAN | 3,464 | 4.0 |
| SAN LORENZO TLALMIMILOLPAN | 6,042 | 3.9 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SANTA MARIA MAQUIXCO | 6,870 | 3.6 |
| ATLATONGO | 4,486 | 3.7 |
| SAN LORENZO TLALMIMILOLPAN | 6,042 | 3.9 |
| SANTA MARIA COATLAN | 3,464 | 4.0 |
| SAN FRANCISCO MAZAPA | 3,332 | 4.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 67.5 millones de pesos por trimestre.
- Por hogar: 5,605 pesos por trimestre (lugar 46 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
