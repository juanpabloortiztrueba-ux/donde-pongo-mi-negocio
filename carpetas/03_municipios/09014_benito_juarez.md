# Ficha de alcaldía: Benito Juárez (Ciudad de México), clave 09014

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 434,153 habitantes (lugar 18 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 176,053. AGEB urbanas: 102. Superficie urbana de esas AGEB: 26.5 km².
- Densidad: 16,353 hab/km² (lugar 4 de 76).
- Edad: 0-14 años 11.8 %; 15-24 10.2 %; 25-59 57.9 %; 60 o más 20.1 %.
- Escolaridad promedio de la población de 15 y más: 14.5 años (lugar 1 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 66.9 %; con internet: 91.9 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 100.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 0.0 %, medio 22.0 %, alto 78.0 %.
- Decil estimado típico (mediana ponderada por población): 9.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 90.5 %; Bajo 9.5 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 24,200 (55.7 por cada 1 000 habitantes, lugar 41 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 27,588. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 295,854.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 6,947 | 28.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 3,890 | 16.1 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,679 | 15.2 % |
| 62 Servicios de salud y de asistencia social | 2,138 | 8.8 % |
| 54 Servicios profesionales, científicos y técnicos | 1,896 | 7.8 % |
| 43 Comercio al por mayor | 1,207 | 5.0 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 812110 | Salones y clínicas de belleza y peluquerías | 1,289 |
| 722511 | Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida | 931 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 882 |
| 621211 | Consultorios dentales del sector privado | 704 |
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 697 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 643 |
| 812210 | Lavanderías y tintorerías | 403 |
| 621113 | Consultorios de medicina especializada del sector privado | 381 |
| 541110 | Bufetes jurídicos | 374 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 369 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| barberia_estetica | 1,289 | 29.7 |
| fonda | 1,029 | 23.7 |
| abarrotes | 1,017 | 23.4 |
| cafeteria | 882 | 20.3 |
| consultorio_medico | 725 | 16.7 |
| consultorio_dental | 704 | 16.2 |
| taqueria | 643 | 14.8 |
| lavanderia | 403 | 9.3 |
| carniceria | 391 | 9.0 |
| taller_mecanico | 346 | 8.0 |
| fruteria | 335 | 7.7 |
| tienda_ropa | 306 | 7.0 |
| papeleria | 288 | 6.6 |
| ferreteria | 283 | 6.5 |
| farmacia | 272 | 6.3 |
| veterinaria | 201 | 4.6 |
| tienda_mascotas | 172 | 4.0 |
| panaderia | 163 | 3.8 |
| tortilleria | 150 | 3.5 |
| tienda_celulares | 140 | 3.2 |
| cerrajeria | 128 | 2.9 |
| gimnasio | 127 | 2.9 |
| floreria | 118 | 2.7 |
| cafe_internet | 116 | 2.7 |
| spa | 106 | 2.4 |
| heladeria | 104 | 2.4 |
| zapateria | 103 | 2.4 |
| optica | 97 | 2.2 |
| laboratorio_clinico | 91 | 2.1 |
| bar | 75 | 1.7 |
| sushi | 69 | 1.6 |
| pasteleria | 68 | 1.6 |
| pizzeria | 66 | 1.5 |
| purificadora | 47 | 1.1 |
| guarderia | 36 | 0.8 |
| libreria | 24 | 0.6 |
| escuela_idiomas | 22 | 0.5 |
| comida_china | 10 | 0.2 |
| coworking | 8 | 0.2 |
| renta_bicicletas | 1 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| NARVARTE PONIENTE | 5 | 31,994 | 1,793 | alto |
| DEL VALLE NORTE | 5 | 21,811 | 1,690 | alto |
| DEL VALLE SUR | 5 | 26,134 | 1,595 | alto |
| NÁPOLES | 3 | 14,556 | 1,163 | alto |
| DEL VALLE CENTRO | 6 | 25,524 | 1,107 | alto |
| SAN SIMÓN TICUMAC | 2 | 12,102 | 1,071 | medio |
| ALAMOS | 4 | 21,248 | 1,067 | alto |
| PORTALES NORTE | 4 | 23,611 | 1,017 | alto |
| NARVARTE ORIENTE | 5 | 23,382 | 976 | alto |
| SAN PEDRO DE LOS PINOS | 4 | 17,523 | 968 | alto |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| ACACIAS | 6,105 | 9.0 |
| SAN JOSÉ INSURGENTES | 6,670 | 9.0 |
| GENERAL PEDRO MARÍA ANAYA | 9,199 | 8.8 |
| DEL VALLE CENTRO | 25,524 | 8.8 |
| NÁPOLES | 14,556 | 8.8 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| NATIVITAS | 8,235 | 7.2 |
| SAN SIMÓN TICUMAC | 12,102 | 7.3 |
| MODERNA | 9,797 | 7.6 |
| INDEPENDENCIA | 10,109 | 7.8 |
| NIÑOS HÉROES | 14,571 | 7.9 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 2,407.3 millones de pesos por trimestre.
- Por hogar: 13,674 pesos por trimestre (lugar 1 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
