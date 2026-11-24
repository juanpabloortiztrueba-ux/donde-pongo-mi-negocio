# Ficha de municipio: Amecameca (Estado de México), clave 15009

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 44,404 habitantes (lugar 46 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 11,250. AGEB urbanas: 16. Superficie urbana de esas AGEB: 11.2 km².
- Densidad: 3,956 hab/km² (lugar 51 de 76).
- Edad: 0-14 años 23.8 %; 15-24 17.2 %; 25-59 46.4 %; 60 o más 12.6 %.
- Escolaridad promedio de la población de 15 y más: 10.1 años (lugar 42 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 33.6 %; con internet: 43.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 79.0 %, medio 21.0 %, alto 0.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 12.3 %; Medio 18.5 %; Alto 60.8 %; Muy alto 8.4 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 3,343 (75.3 por cada 1 000 habitantes, lugar 18 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 2,846. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 13,366.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,732 | 51.8 % |
| 81 Otros servicios excepto actividades gubernamentales | 466 | 13.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 344 | 10.3 % |
| 31 Industrias manufactureras | 166 | 5.0 % |
| 62 Servicios de salud y de asistencia social | 134 | 4.0 % |
| 61 Servicios educativos | 93 | 2.8 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 457 |
| 465311 | Comercio al por menor de artículos de papelería | 162 |
| 812110 | Salones y clínicas de belleza y peluquerías | 137 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 88 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 82 |
| 465912 | Comercio al por menor de regalos | 77 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 73 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 67 |
| 461122 | Comercio al por menor de carne de aves | 66 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 59 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 477 | 107.4 |
| papeleria | 162 | 36.5 |
| barberia_estetica | 137 | 30.9 |
| carniceria | 115 | 25.9 |
| tienda_ropa | 88 | 19.8 |
| tortilleria | 74 | 16.7 |
| fonda | 72 | 16.2 |
| taqueria | 67 | 15.1 |
| taller_mecanico | 63 | 14.2 |
| farmacia | 59 | 13.3 |
| ferreteria | 59 | 13.3 |
| fruteria | 52 | 11.7 |
| consultorio_dental | 39 | 8.8 |
| cafeteria | 37 | 8.3 |
| purificadora | 33 | 7.4 |
| zapateria | 33 | 7.4 |
| consultorio_medico | 30 | 6.8 |
| cafe_internet | 25 | 5.6 |
| heladeria | 25 | 5.6 |
| tienda_celulares | 25 | 5.6 |
| panaderia | 24 | 5.4 |
| tienda_mascotas | 23 | 5.2 |
| floreria | 21 | 4.7 |
| gimnasio | 20 | 4.5 |
| lavanderia | 19 | 4.3 |
| bar | 17 | 3.8 |
| veterinaria | 14 | 3.2 |
| optica | 13 | 2.9 |
| pizzeria | 12 | 2.7 |
| laboratorio_clinico | 8 | 1.8 |
| pasteleria | 7 | 1.6 |
| cerrajeria | 6 | 1.4 |
| escuela_idiomas | 5 | 1.1 |
| libreria | 3 | 0.7 |
| comida_china | 1 | 0.2 |
| sushi | 1 | 0.2 |
| spa | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| guarderia | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 1 | 5,444 | 895 | medio |
| AMECAMECA | 1 | 3,695 | 715 | medio |
| AMECAMECA DE JUAREZ | 3 | 7,378 | 467 | bajo |
| CALTENCO | 2 | 9,754 | 382 | bajo |
| ATENCO | 1 | 6,330 | 297 | bajo |
| SAN PEDRO NEXAPA | 2 | 5,440 | 224 | bajo |
| SAN ANTONIO ZOYATZINGO | 2 | 3,223 | 213 | bajo |
| SAN FRANCISCO ZENTLALPAN | 1 | 2,024 | 112 | bajo |
| EL CASTILLO | 1 | 1,110 | 24 | bajo |
| PANOHAYA | 1 | 5 | 14 | NO ENCONTRADO |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| CENTRO | 5,444 | 5.6 |
| AMECAMECA | 3,695 | 5.2 |
| AMECAMECA DE JUAREZ | 7,378 | 4.0 |
| CALTENCO | 9,754 | 3.9 |
| ATENCO | 6,330 | 3.8 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN PEDRO NEXAPA | 5,440 | 2.5 |
| SAN ANTONIO ZOYATZINGO | 3,223 | 3.7 |
| ATENCO | 6,330 | 3.8 |
| CALTENCO | 9,754 | 3.9 |
| AMECAMECA DE JUAREZ | 7,378 | 4.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 58.7 millones de pesos por trimestre.
- Por hogar: 5,217 pesos por trimestre (lugar 53 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
