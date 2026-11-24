# Ficha de alcaldía: Xochimilco (Ciudad de México), clave 09013

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 429,481 habitantes (lugar 20 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 113,758. AGEB urbanas: 122. Superficie urbana de esas AGEB: 64.0 km².
- Densidad: 6,713 hab/km² (lugar 31 de 76).
- Edad: 0-14 años 20.0 %; 15-24 16.2 %; 25-59 49.8 %; 60 o más 14.0 %.
- Escolaridad promedio de la población de 15 y más: 10.8 años (lugar 19 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 43.4 %; con internet: 67.5 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 24.4 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 25.7 %, medio 66.7 %, alto 7.5 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 4.9 %; Bajo 45.4 %; Medio 29.9 %; Alto 15.5 %; Muy alto 4.3 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 20,197 (47.0 por cada 1 000 habitantes, lugar 58 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 20,928. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 85,448.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 11,302 | 56.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 2,650 | 13.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,017 | 10.0 % |
| 31 Industrias manufactureras | 954 | 4.7 % |
| 62 Servicios de salud y de asistencia social | 819 | 4.1 % |
| 61 Servicios educativos | 424 | 2.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,568 |
| 466312 | Comercio al por menor de plantas y flores naturales | 2,068 |
| 812110 | Salones y clínicas de belleza y peluquerías | 936 |
| 465311 | Comercio al por menor de artículos de papelería | 633 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 607 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 509 |
| 461122 | Comercio al por menor de carne de aves | 411 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 393 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 382 |
| 464111 | Farmacias sin minisúper | 349 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 2,627 | 61.2 |
| floreria | 2,068 | 48.2 |
| barberia_estetica | 936 | 21.8 |
| carniceria | 718 | 16.7 |
| papeleria | 633 | 14.7 |
| fruteria | 607 | 14.1 |
| tienda_ropa | 393 | 9.2 |
| farmacia | 392 | 9.1 |
| tortilleria | 388 | 9.0 |
| taqueria | 319 | 7.4 |
| taller_mecanico | 318 | 7.4 |
| fonda | 308 | 7.2 |
| consultorio_dental | 296 | 6.9 |
| ferreteria | 274 | 6.4 |
| cafeteria | 267 | 6.2 |
| lavanderia | 207 | 4.8 |
| panaderia | 181 | 4.2 |
| cafe_internet | 142 | 3.3 |
| consultorio_medico | 132 | 3.1 |
| zapateria | 130 | 3.0 |
| purificadora | 129 | 3.0 |
| tienda_celulares | 118 | 2.7 |
| tienda_mascotas | 113 | 2.6 |
| veterinaria | 106 | 2.5 |
| gimnasio | 99 | 2.3 |
| heladeria | 88 | 2.0 |
| pasteleria | 62 | 1.4 |
| pizzeria | 56 | 1.3 |
| optica | 50 | 1.2 |
| cerrajeria | 50 | 1.2 |
| laboratorio_clinico | 27 | 0.6 |
| bar | 24 | 0.6 |
| spa | 21 | 0.5 |
| guarderia | 13 | 0.3 |
| escuela_idiomas | 11 | 0.3 |
| sushi | 9 | 0.2 |
| libreria | 7 | 0.2 |
| comida_china | 1 | 0.0 |
| renta_bicicletas | 1 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| EL ROSARIO | 1 | 1,917 | 1,514 | medio |
| SAN GREGORIO ATLAPULCO | 7 | 34,638 | 1,183 | bajo |
| SAN LORENZO LA CEBADA | 4 | 22,213 | 1,143 | medio |
| XALTOCAN | 2 | 9,532 | 1,086 | medio |
| SAN PEDRO | 2 | 2,939 | 1,003 | medio |
| COAPA | 1 | 55 | 997 | bajo |
| SANTA MARÍA NATIVITAS | 4 | 18,954 | 950 | medio |
| SAN MATEO XALPA | 8 | 25,371 | 837 | medio |
| SANTIAGO TEPALCATLALPAN | 3 | 14,009 | 708 | medio |
| SANTA MARÍA TEPEPAN | 2 | 15,024 | 683 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| BARRIO 18 | 6,773 | 9.0 |
| HUICHAPAN | 5,438 | 8.4 |
| LAS PERITAS | 3,253 | 8.1 |
| TIERRA NUEVA | 4,044 | 8.0 |
| LA CONCHA | 3,393 | 7.6 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| AMPLIACION SAN MARCOS EL RANCHITO | 7,010 | 2.9 |
| TIZICLIPA | 4,664 | 3.3 |
| SAN LORENZO | 5,694 | 3.4 |
| XICALHUACAN | 5,439 | 3.6 |
| AMPLIACION NATIVITAS | 7,325 | 3.7 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 881.0 millones de pesos por trimestre.
- Por hogar: 7,744 pesos por trimestre (lugar 22 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
