# Ficha de alcaldía: Tláhuac (Ciudad de México), clave 09011

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 382,271 habitantes (lugar 25 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 104,356. AGEB urbanas: 110. Superficie urbana de esas AGEB: 39.1 km².
- Densidad: 9,764 hab/km² (lugar 20 de 76).
- Edad: 0-14 años 21.2 %; 15-24 16.8 %; 25-59 50.0 %; 60 o más 12.0 %.
- Escolaridad promedio de la población de 15 y más: 10.6 años (lugar 27 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 39.3 %; con internet: 68.3 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 33.3 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 16.3 %, medio 83.7 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 2.6 %; Bajo 60.2 %; Medio 34.8 %; Alto 1.0 %; Muy alto 1.4 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 17,711 (46.3 por cada 1 000 habitantes, lugar 59 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 18,514. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 77,155.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 8,694 | 49.1 % |
| 81 Otros servicios excepto actividades gubernamentales | 2,929 | 16.5 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 1,745 | 9.9 % |
| 31 Industrias manufactureras | 1,024 | 5.8 % |
| 62 Servicios de salud y de asistencia social | 811 | 4.6 % |
| 43 Comercio al por mayor | 401 | 2.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,312 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,069 |
| 465311 | Comercio al por menor de artículos de papelería | 681 |
| 464111 | Farmacias sin minisúper | 398 |
| 461122 | Comercio al por menor de carne de aves | 372 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 365 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 361 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 353 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 345 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 342 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 2,403 | 62.9 |
| barberia_estetica | 1,069 | 28.0 |
| papeleria | 681 | 17.8 |
| carniceria | 633 | 16.6 |
| farmacia | 439 | 11.5 |
| taller_mecanico | 386 | 10.1 |
| tienda_ropa | 365 | 9.5 |
| tortilleria | 355 | 9.3 |
| taqueria | 345 | 9.0 |
| fruteria | 342 | 8.9 |
| ferreteria | 329 | 8.6 |
| consultorio_dental | 280 | 7.3 |
| fonda | 270 | 7.1 |
| purificadora | 262 | 6.9 |
| cafeteria | 236 | 6.2 |
| lavanderia | 186 | 4.9 |
| panaderia | 174 | 4.6 |
| cafe_internet | 123 | 3.2 |
| consultorio_medico | 116 | 3.0 |
| tienda_mascotas | 115 | 3.0 |
| tienda_celulares | 102 | 2.7 |
| gimnasio | 97 | 2.5 |
| veterinaria | 84 | 2.2 |
| zapateria | 68 | 1.8 |
| heladeria | 62 | 1.6 |
| optica | 62 | 1.6 |
| floreria | 58 | 1.5 |
| pasteleria | 56 | 1.5 |
| pizzeria | 49 | 1.3 |
| cerrajeria | 37 | 1.0 |
| bar | 35 | 0.9 |
| spa | 24 | 0.6 |
| laboratorio_clinico | 22 | 0.6 |
| sushi | 17 | 0.4 |
| guarderia | 13 | 0.3 |
| libreria | 6 | 0.2 |
| comida_china | 5 | 0.1 |
| escuela_idiomas | 3 | 0.1 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| MIGUEL HIDALGO | 6 | 26,026 | 1,254 | medio |
| LA CONCHITA | 6 | 23,070 | 1,081 | medio |
| LA ASUNCION | 4 | 7,540 | 965 | medio |
| DEL MAR | 6 | 15,422 | 916 | medio |
| SELENE | 5 | 16,056 | 787 | medio |
| ZAPOTITLA | 4 | 16,489 | 669 | bajo |
| SAN FRANCISCO TLALTENCO | 2 | 8,498 | 590 | medio |
| SAN MIGUEL | 2 | 9,518 | 575 | medio |
| LA NOPALERA | 2 | 6,985 | 568 | medio |
| LOS OLIVOS | 2 | 10,032 | 526 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| VILLA CENTROAMERICANA | 6,295 | 6.7 |
| SAN AGUSTIN | 4,106 | 6.1 |
| SANTA ANA | 5,292 | 6.0 |
| LOS OLIVOS | 10,032 | 6.0 |
| LA DRAGA | 7,148 | 5.9 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| TEMPILULI | 3,719 | 3.2 |
| AMPLIACION LA CONCHITA | 5,557 | 3.5 |
| LA ESTACION | 7,502 | 3.8 |
| SAN ISIDRO | 5,167 | 4.1 |
| AGRICOLA METROPOLITANA | 6,573 | 4.3 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 705.1 millones de pesos por trimestre.
- Por hogar: 6,757 pesos por trimestre (lugar 27 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
