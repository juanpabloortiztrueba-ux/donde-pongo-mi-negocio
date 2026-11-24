# Ficha de municipio: Chalco (Estado de México), clave 15025

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 382,046 habitantes (lugar 26 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 99,925. AGEB urbanas: 125. Superficie urbana de esas AGEB: 54.6 km².
- Densidad: 7,000 hab/km² (lugar 29 de 76).
- Edad: 0-14 años 26.3 %; 15-24 17.7 %; 25-59 47.5 %; 60 o más 8.4 %.
- Escolaridad promedio de la población de 15 y más: 9.8 años (lugar 56 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 36.0 %; con internet: 54.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 62.9 %, medio 36.9 %, alto 0.2 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 2.5 %; Bajo 26.6 %; Medio 17.7 %; Alto 41.2 %; Muy alto 12.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 21,894 (57.3 por cada 1 000 habitantes, lugar 39 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 16,924. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 81,185.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 11,668 | 53.3 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,131 | 14.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,200 | 10.0 % |
| 31 Industrias manufactureras | 1,072 | 4.9 % |
| 62 Servicios de salud y de asistencia social | 706 | 3.2 % |
| 61 Servicios educativos | 578 | 2.6 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 3,261 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,105 |
| 465311 | Comercio al por menor de artículos de papelería | 959 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 597 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 528 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 460 |
| 467115 | Comercio al por menor de artículos para la limpieza | 447 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 431 |
| 461122 | Comercio al por menor de carne de aves | 423 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 415 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 3,388 | 88.7 |
| barberia_estetica | 1,105 | 28.9 |
| papeleria | 959 | 25.1 |
| carniceria | 759 | 19.9 |
| tienda_ropa | 597 | 15.6 |
| fruteria | 528 | 13.8 |
| farmacia | 428 | 11.2 |
| ferreteria | 415 | 10.9 |
| fonda | 411 | 10.8 |
| tortilleria | 395 | 10.3 |
| taller_mecanico | 383 | 10.0 |
| taqueria | 339 | 8.9 |
| cafeteria | 326 | 8.5 |
| purificadora | 245 | 6.4 |
| consultorio_dental | 207 | 5.4 |
| panaderia | 203 | 5.3 |
| tienda_celulares | 152 | 4.0 |
| cafe_internet | 142 | 3.7 |
| consultorio_medico | 138 | 3.6 |
| lavanderia | 137 | 3.6 |
| heladeria | 136 | 3.6 |
| gimnasio | 130 | 3.4 |
| floreria | 112 | 2.9 |
| zapateria | 104 | 2.7 |
| tienda_mascotas | 96 | 2.5 |
| veterinaria | 76 | 2.0 |
| pizzeria | 70 | 1.8 |
| bar | 55 | 1.4 |
| optica | 47 | 1.2 |
| spa | 43 | 1.1 |
| pasteleria | 40 | 1.0 |
| cerrajeria | 38 | 1.0 |
| laboratorio_clinico | 24 | 0.6 |
| guarderia | 16 | 0.4 |
| sushi | 16 | 0.4 |
| escuela_idiomas | 9 | 0.2 |
| libreria | 7 | 0.2 |
| comida_china | 6 | 0.2 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| EJIDAL | 1 | 3,674 | 2,106 | medio |
| UNION DE GUADALUPE | 5 | 17,508 | 952 | bajo |
| SAN ANTONIO | 3 | 7,992 | 925 | medio |
| CULTURAS DE MEXICO | 4 | 14,356 | 901 | bajo |
| LOS HEROES CHALCO | 3 | 34,277 | 866 | medio |
| SAN PABLO ATLAZALPAN | 4 | 12,407 | 782 | bajo |
| SAN MARCOS HUIXTOCO | 9 | 14,776 | 752 | bajo |
| SANTA MARIA HUEXOCULCO | 3 | 15,154 | 695 | bajo |
| SAN GREGORIO CUAUTZINGO | 3 | 6,999 | 688 | bajo |
| EMILIANO ZAPATA | 2 | 12,046 | 686 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LOS HEROES CHALCO | 34,277 | 6.5 |
| CASCO DE SAN JUAN | 3,893 | 6.4 |
| ALAMOS | 6,283 | 6.3 |
| EX HACIENDA DE GUADALUPE | 5,067 | 5.9 |
| PASEOS DE CHALCO | 6,572 | 5.5 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| EL LLANO | 4,422 | 2.1 |
| SANTA MARIA HUEXOCULCO | 15,154 | 2.2 |
| BARRIO SANTA MARIA | 4,267 | 2.4 |
| COVADONGA | 10,972 | 2.7 |
| SAN JUAN TEZOMPA | 3,096 | 3.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 561.2 millones de pesos por trimestre.
- Por hogar: 5,617 pesos por trimestre (lugar 45 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
