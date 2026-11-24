# Ficha de alcaldía: La Magdalena Contreras (Ciudad de México), clave 09008

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 246,428 habitantes (lugar 31 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 67,755. AGEB urbanas: 52. Superficie urbana de esas AGEB: 18.1 km².
- Densidad: 13,583 hab/km² (lugar 9 de 76).
- Edad: 0-14 años 19.1 %; 15-24 15.7 %; 25-59 49.8 %; 60 o más 15.4 %.
- Escolaridad promedio de la población de 15 y más: 10.8 años (lugar 20 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 45.3 %; con internet: 74.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 21.5 %, medio 71.5 %, alto 7.1 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 13.1 %; Bajo 48.8 %; Medio 34.9 %; Alto 3.3 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 8,547 (34.7 por cada 1 000 habitantes, lugar 75 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 8,045. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 44,946.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 3,953 | 46.3 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,297 | 15.2 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 1,025 | 12.0 % |
| 62 Servicios de salud y de asistencia social | 667 | 7.8 % |
| 31 Industrias manufactureras | 384 | 4.5 % |
| 61 Servicios educativos | 249 | 2.9 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,144 |
| 812110 | Salones y clínicas de belleza y peluquerías | 551 |
| 465311 | Comercio al por menor de artículos de papelería | 322 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 270 |
| 461122 | Comercio al por menor de carne de aves | 233 |
| 621113 | Consultorios de medicina especializada del sector privado | 214 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 210 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 174 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 173 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 147 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,193 | 48.4 |
| barberia_estetica | 551 | 22.4 |
| carniceria | 358 | 14.5 |
| papeleria | 322 | 13.1 |
| consultorio_medico | 284 | 11.5 |
| fruteria | 210 | 8.5 |
| fonda | 187 | 7.6 |
| tienda_ropa | 174 | 7.1 |
| taqueria | 173 | 7.0 |
| farmacia | 147 | 6.0 |
| tortilleria | 145 | 5.9 |
| consultorio_dental | 144 | 5.8 |
| taller_mecanico | 143 | 5.8 |
| cafeteria | 134 | 5.4 |
| panaderia | 132 | 5.4 |
| ferreteria | 103 | 4.2 |
| lavanderia | 87 | 3.5 |
| cafe_internet | 61 | 2.5 |
| tienda_celulares | 52 | 2.1 |
| gimnasio | 50 | 2.0 |
| tienda_mascotas | 49 | 2.0 |
| floreria | 48 | 1.9 |
| heladeria | 46 | 1.9 |
| purificadora | 44 | 1.8 |
| veterinaria | 43 | 1.7 |
| zapateria | 38 | 1.5 |
| pasteleria | 34 | 1.4 |
| pizzeria | 25 | 1.0 |
| optica | 23 | 0.9 |
| cerrajeria | 21 | 0.9 |
| spa | 16 | 0.6 |
| sushi | 14 | 0.6 |
| bar | 10 | 0.4 |
| guarderia | 9 | 0.4 |
| laboratorio_clinico | 9 | 0.4 |
| comida_china | 3 | 0.1 |
| libreria | 2 | 0.1 |
| escuela_idiomas | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN BERNABÉ OCOTEPEC | 3 | 21,829 | 896 | medio |
| SAN JERÓNIMO LÍDICE | 9 | 19,123 | 545 | alto |
| CUAUHTÉMOC | 2 | 10,258 | 533 | medio |
| DE SAN NICOLÁS TOTOLAPAN | 2 | 19,172 | 493 | medio |
| HÉROES DE PADIERNA | 1 | 4,642 | 485 | medio |
| SAN JERÓNIMO ACULCO | 2 | 5,570 | 474 | medio |
| EL OCOTAL | 2 | 18,228 | 440 | bajo |
| EL TORO | 2 | 7,133 | 383 | medio |
| HUAYATLA | 1 | 8,605 | 383 | medio |
| NUEVO ALTO | 1 | 6,547 | 315 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN JERÓNIMO LÍDICE | 19,123 | 8.8 |
| HÉROES DE PADIERNA | 4,642 | 7.6 |
| SAN JERÓNIMO ACULCO | 5,570 | 7.6 |
| NUEVO ALTO | 6,547 | 7.6 |
| SAN FRANCISCO | 8,935 | 7.4 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| TIERRA COLORADA | 6,192 | 3.3 |
| LA CARBONERA | 7,657 | 4.1 |
| LAS CRUCES | 16,334 | 4.2 |
| TIERRA UNIDA | 5,314 | 4.3 |
| AMPLIACIÓN LOMAS DE SAN BERNABÉ | 6,170 | 4.3 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 563.7 millones de pesos por trimestre.
- Por hogar: 8,320 pesos por trimestre (lugar 16 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
