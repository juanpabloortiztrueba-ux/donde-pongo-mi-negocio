# Ficha de municipio: Nezahualcóyotl (Estado de México), clave 15058

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 1,072,676 habitantes (lugar 4 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 297,928. AGEB urbanas: 178. Superficie urbana de esas AGEB: 51.3 km².
- Densidad: 20,890 hab/km² (lugar 1 de 76).
- Edad: 0-14 años 20.2 %; 15-24 15.8 %; 25-59 48.7 %; 60 o más 15.3 %.
- Escolaridad promedio de la población de 15 y más: 10.4 años (lugar 30 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 38.8 %; con internet: 68.7 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 43.7 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 40.0 %, medio 56.4 %, alto 3.6 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 3.5 %; Bajo 13.7 %; Medio 78.1 %; Alto 4.6 %; Muy alto 0.1 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 55,744 (52.0 por cada 1 000 habitantes, lugar 46 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 50,568. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 199,264.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 26,496 | 47.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 9,620 | 17.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 6,590 | 11.8 % |
| 31 Industrias manufactureras | 2,992 | 5.4 % |
| 62 Servicios de salud y de asistencia social | 2,481 | 4.5 % |
| 61 Servicios educativos | 1,440 | 2.6 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 6,003 |
| 812110 | Salones y clínicas de belleza y peluquerías | 3,494 |
| 465311 | Comercio al por menor de artículos de papelería | 1,728 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 1,290 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 1,237 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 1,193 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 1,178 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 1,113 |
| 461121 | Comercio al por menor de carnes rojas | 1,086 |
| 461122 | Comercio al por menor de carne de aves | 1,075 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 6,158 | 57.4 |
| barberia_estetica | 3,494 | 32.6 |
| carniceria | 2,161 | 20.1 |
| papeleria | 1,728 | 16.1 |
| taller_mecanico | 1,478 | 13.8 |
| taqueria | 1,237 | 11.5 |
| fruteria | 1,193 | 11.1 |
| farmacia | 1,182 | 11.0 |
| tienda_ropa | 1,178 | 11.0 |
| fonda | 1,021 | 9.5 |
| cafeteria | 1,002 | 9.3 |
| tortilleria | 957 | 8.9 |
| consultorio_dental | 863 | 8.0 |
| ferreteria | 840 | 7.8 |
| purificadora | 828 | 7.7 |
| lavanderia | 621 | 5.8 |
| cafe_internet | 531 | 5.0 |
| panaderia | 521 | 4.9 |
| consultorio_medico | 450 | 4.2 |
| tienda_celulares | 382 | 3.6 |
| tienda_mascotas | 361 | 3.4 |
| gimnasio | 331 | 3.1 |
| heladeria | 287 | 2.7 |
| zapateria | 281 | 2.6 |
| floreria | 244 | 2.3 |
| veterinaria | 231 | 2.2 |
| optica | 211 | 2.0 |
| pizzeria | 199 | 1.9 |
| bar | 186 | 1.7 |
| cerrajeria | 149 | 1.4 |
| spa | 117 | 1.1 |
| pasteleria | 113 | 1.1 |
| laboratorio_clinico | 79 | 0.7 |
| sushi | 55 | 0.5 |
| guarderia | 40 | 0.4 |
| escuela_idiomas | 35 | 0.3 |
| libreria | 21 | 0.2 |
| comida_china | 18 | 0.2 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| BENITO JUAREZ | 25 | 200,563 | 10,225 | medio |
| EL SOL | 9 | 54,419 | 2,653 | bajo |
| LA PERLA | 7 | 34,659 | 2,054 | medio |
| ESPERANZA | 5 | 28,548 | 2,054 | bajo |
| EVOLUCION | 5 | 32,706 | 2,035 | medio |
| REFORMA | 6 | 30,428 | 1,929 | medio |
| ESTADO DE MEXICO | 8 | 40,179 | 1,884 | bajo |
| AGUA AZUL | 5 | 38,577 | 1,865 | medio |
| JUAREZ PANTITLAN | 4 | 23,981 | 1,642 | bajo |
| METROPOLITANA TERCERA SECCION | 3 | 24,730 | 1,636 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| BOSQUES | 4,010 | 8.9 |
| BOSQUES DE ARAGON | 21,443 | 8.9 |
| PRADOS DE ARAGON | 5,071 | 8.6 |
| VALLE DE ARAGON 1ERA SECCION | 13,189 | 7.6 |
| VALLE DE ARAGON PRIMERA SECCION | 17,253 | 7.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| TLATELCO | 4,290 | 3.2 |
| ORFEBRES | 4,960 | 3.3 |
| VILLA DE SAN AGUSTIN | 4,383 | 3.5 |
| MANANTIALES | 5,963 | 3.8 |
| EL SOL | 54,419 | 4.2 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,970.9 millones de pesos por trimestre.
- Por hogar: 6,615 pesos por trimestre (lugar 29 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
