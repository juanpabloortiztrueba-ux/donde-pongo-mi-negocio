# Ficha de municipio: Tultitlán (Estado de México), clave 15109

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 511,910 habitantes (lugar 16 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 144,817. AGEB urbanas: 137. Superficie urbana de esas AGEB: 51.1 km².
- Densidad: 10,014 hab/km² (lugar 18 de 76).
- Edad: 0-14 años 22.1 %; 15-24 16.4 %; 25-59 49.3 %; 60 o más 12.1 %.
- Escolaridad promedio de la población de 15 y más: 10.4 años (lugar 32 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 41.7 %; con internet: 66.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 29.5 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 43.9 %, medio 54.5 %, alto 1.6 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 6.3 %; Bajo 45.3 %; Medio 41.6 %; Alto 6.8 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 22,163 (43.3 por cada 1 000 habitantes, lugar 65 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 19,929. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 113,510.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 10,864 | 49.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,643 | 16.4 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,432 | 11.0 % |
| 31 Industrias manufactureras | 1,052 | 4.7 % |
| 62 Servicios de salud y de asistencia social | 726 | 3.3 % |
| 43 Comercio al por mayor | 703 | 3.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,962 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,324 |
| 465311 | Comercio al por menor de artículos de papelería | 928 |
| 467115 | Comercio al por menor de artículos para la limpieza | 604 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 510 |
| 464111 | Farmacias sin minisúper | 504 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 475 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 454 |
| 461122 | Comercio al por menor de carne de aves | 454 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 403 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 3,066 | 59.9 |
| barberia_estetica | 1,324 | 25.9 |
| papeleria | 928 | 18.1 |
| carniceria | 713 | 13.9 |
| taller_mecanico | 605 | 11.8 |
| farmacia | 541 | 10.6 |
| fruteria | 475 | 9.3 |
| tienda_ropa | 403 | 7.9 |
| taqueria | 391 | 7.6 |
| fonda | 387 | 7.6 |
| ferreteria | 383 | 7.5 |
| cafeteria | 372 | 7.3 |
| tortilleria | 357 | 7.0 |
| panaderia | 309 | 6.0 |
| consultorio_dental | 236 | 4.6 |
| purificadora | 193 | 3.8 |
| lavanderia | 175 | 3.4 |
| cafe_internet | 173 | 3.4 |
| heladeria | 147 | 2.9 |
| tienda_celulares | 119 | 2.3 |
| gimnasio | 116 | 2.3 |
| floreria | 104 | 2.0 |
| consultorio_medico | 102 | 2.0 |
| tienda_mascotas | 88 | 1.7 |
| veterinaria | 83 | 1.6 |
| zapateria | 75 | 1.5 |
| pizzeria | 63 | 1.2 |
| pasteleria | 59 | 1.2 |
| optica | 53 | 1.0 |
| cerrajeria | 49 | 1.0 |
| laboratorio_clinico | 31 | 0.6 |
| bar | 29 | 0.6 |
| spa | 24 | 0.5 |
| guarderia | 19 | 0.4 |
| comida_china | 6 | 0.1 |
| sushi | 6 | 0.1 |
| escuela_idiomas | 4 | 0.1 |
| libreria | 1 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN PABLO DE LAS SALINAS | 6 | 39,703 | 1,683 | medio |
| TERCERA UNIDAD JOSÉ MARÍA MORELOS (UNIDAD MORELOS TERCERA SECCIÓN) | 6 | 30,569 | 1,319 | medio |
| SAN JUAN | 2 | 8,201 | 817 | medio |
| SANTIAGUITO | 2 | 4,780 | 652 | medio |
| SAN FRANCISCO CHILPAN | 2 | 12,075 | 637 | medio |
| SOLIDARIDAD PRIMERA SECCIÓN | 1 | 10,806 | 619 | bajo |
| FUENTES DEL VALLE PRIMERA Y SEGUNDA SECCIÓN | 2 | 20,922 | 561 | medio |
| VALLE DE TULES | 2 | 9,319 | 552 | medio |
| LAZARO CARDENAS | 1 | 4,473 | 538 | bajo |
| AMPLIACIÓN BUENAVISTA SEGUNDA SECCIÓN | 2 | 12,212 | 522 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LOS PORTALES | 3,240 | 8.3 |
| REAL DEL BOSQUE | 11,953 | 7.8 |
| IZCALLI DEL VALLE | 8,760 | 7.0 |
| LOMAS DE CARTAGENA | 12,317 | 6.8 |
| AGAVES TULTITLÁN | 3,069 | 6.5 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LLANURA VERDE | 3,644 | 3.3 |
| UNIDAD MORELOS TERCERA SECCIÓN INFONAVIT | 4,380 | 3.6 |
| SAN MARCOS | 8,206 | 3.9 |
| SIERRA DE GUADALUPE (SANTA MARÍA GUADALUPE) | 6,104 | 4.0 |
| AMPLIACIÓN EL TESORO | 8,087 | 4.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 960.5 millones de pesos por trimestre.
- Por hogar: 6,632 pesos por trimestre (lugar 28 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
