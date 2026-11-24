# Ficha de alcaldía: Miguel Hidalgo (Ciudad de México), clave 09016

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 414,470 habitantes (lugar 21 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 146,752. AGEB urbanas: 130. Superficie urbana de esas AGEB: 46.2 km².
- Densidad: 8,980 hab/km² (lugar 23 de 76).
- Edad: 0-14 años 15.1 %; 15-24 12.0 %; 25-59 54.3 %; 60 o más 17.2 %.
- Escolaridad promedio de la población de 15 y más: 13.1 años (lugar 2 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 55.1 %; con internet: 84.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 74.7 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 0.4 %, medio 68.8 %, alto 30.7 %, sin estimación 0.2 %.
- Decil estimado típico (mediana ponderada por población): 8.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 52.9 %; Bajo 45.4 %; Medio 1.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 25,329 (61.1 por cada 1 000 habitantes, lugar 32 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 27,327. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 405,176.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 8,204 | 32.4 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 3,692 | 14.6 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,118 | 12.3 % |
| 54 Servicios profesionales, científicos y técnicos | 1,786 | 7.1 % |
| 62 Servicios de salud y de asistencia social | 1,648 | 6.5 % |
| 43 Comercio al por mayor | 1,335 | 5.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 812110 | Salones y clínicas de belleza y peluquerías | 1,049 |
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 912 |
| 722511 | Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida | 772 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 723 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 589 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 559 |
| 621113 | Consultorios de medicina especializada del sector privado | 492 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 479 |
| 621211 | Consultorios dentales del sector privado | 412 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 406 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,186 | 28.6 |
| barberia_estetica | 1,049 | 25.3 |
| fonda | 894 | 21.6 |
| cafeteria | 723 | 17.4 |
| consultorio_medico | 680 | 16.4 |
| taqueria | 589 | 14.2 |
| tienda_ropa | 559 | 13.5 |
| carniceria | 493 | 11.9 |
| consultorio_dental | 412 | 9.9 |
| fruteria | 337 | 8.1 |
| papeleria | 296 | 7.1 |
| taller_mecanico | 293 | 7.1 |
| tienda_celulares | 289 | 7.0 |
| farmacia | 250 | 6.0 |
| lavanderia | 238 | 5.7 |
| ferreteria | 207 | 5.0 |
| zapateria | 205 | 4.9 |
| floreria | 202 | 4.9 |
| tortilleria | 180 | 4.3 |
| panaderia | 140 | 3.4 |
| cafe_internet | 126 | 3.0 |
| heladeria | 103 | 2.5 |
| gimnasio | 97 | 2.3 |
| veterinaria | 96 | 2.3 |
| cerrajeria | 93 | 2.2 |
| optica | 90 | 2.2 |
| tienda_mascotas | 87 | 2.1 |
| spa | 80 | 1.9 |
| laboratorio_clinico | 77 | 1.9 |
| purificadora | 58 | 1.4 |
| bar | 53 | 1.3 |
| sushi | 51 | 1.2 |
| pizzeria | 45 | 1.1 |
| libreria | 32 | 0.8 |
| pasteleria | 31 | 0.7 |
| guarderia | 20 | 0.5 |
| escuela_idiomas | 13 | 0.3 |
| comida_china | 11 | 0.3 |
| coworking | 8 | 0.2 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| TACUBA | 4 | 20,147 | 1,788 | medio |
| TACUBAYA | 3 | 11,946 | 1,503 | medio |
| GRANADA | 4 | 28,832 | 1,377 | alto |
| LOMAS DE CHAPULTEPEC III SECCIÓN | 4 | 6,795 | 1,366 | alto |
| ANZURES | 4 | 7,320 | 1,253 | alto |
| POLANCO V SECCIÓN | 3 | 10,102 | 1,190 | alto |
| ESCANDÓN II SECCIÓN | 3 | 21,564 | 1,160 | medio |
| BOSQUE DE CHAPULTEPEC | 3 | 574 | 811 | medio |
| SAN MIGUEL CHAPULTEPEC I SECCIÓN | 2 | 9,463 | 795 | medio |
| TLAXPANA | 2 | 12,298 | 777 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| RESIDENCIAL MILITAR | 4,081 | 9.6 |
| POLANCO IV SECCIÓN | 5,295 | 9.1 |
| LOMAS DE CHAPULTEPEC VIII SECCIÓN | 3,598 | 9.1 |
| GRANADA | 28,832 | 9.0 |
| POLANCO II SECCIÓN | 3,488 | 9.0 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| FRANCISCO I. MADERO | 3,263 | 5.0 |
| AMÉRICA | 3,137 | 5.2 |
| PENSIL SUR | 4,656 | 5.2 |
| SAN DIEGO OCOYOACAC | 7,185 | 5.3 |
| PENSIL NORTE | 13,975 | 5.4 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,649.2 millones de pesos por trimestre.
- Por hogar: 11,238 pesos por trimestre (lugar 2 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
