# Ficha de municipio: Ecatepec de Morelos (Estado de México), clave 15033

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 1,643,623 habitantes (lugar 2 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 448,138. AGEB urbanas: 395. Superficie urbana de esas AGEB: 128.8 km².
- Densidad: 12,764 hab/km² (lugar 14 de 76).
- Edad: 0-14 años 21.8 %; 15-24 16.3 %; 25-59 48.3 %; 60 o más 13.5 %.
- Escolaridad promedio de la población de 15 y más: 10.2 años (lugar 37 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 41.4 %; con internet: 64.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 53.6 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 46.1 %, medio 51.5 %, alto 2.3 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 4.5 %; Bajo 28.8 %; Medio 48.6 %; Alto 17.6 %; Muy alto 0.5 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 90,374 (55.0 por cada 1 000 habitantes, lugar 44 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 78,484. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 361,937.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 44,240 | 49.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 15,343 | 17.0 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 9,983 | 11.0 % |
| 31 Industrias manufactureras | 4,536 | 5.0 % |
| 62 Servicios de salud y de asistencia social | 3,493 | 3.9 % |
| 61 Servicios educativos | 2,190 | 2.4 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 10,723 |
| 812110 | Salones y clínicas de belleza y peluquerías | 5,506 |
| 465311 | Comercio al por menor de artículos de papelería | 3,407 |
| 467115 | Comercio al por menor de artículos para la limpieza | 2,416 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 2,197 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 1,929 |
| 461122 | Comercio al por menor de carne de aves | 1,921 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 1,918 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 1,818 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 1,740 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 11,024 | 67.1 |
| barberia_estetica | 5,506 | 33.5 |
| papeleria | 3,407 | 20.7 |
| carniceria | 3,082 | 18.8 |
| taller_mecanico | 2,451 | 14.9 |
| tienda_ropa | 1,918 | 11.7 |
| farmacia | 1,889 | 11.5 |
| fruteria | 1,818 | 11.1 |
| taqueria | 1,740 | 10.6 |
| tortilleria | 1,634 | 9.9 |
| ferreteria | 1,478 | 9.0 |
| fonda | 1,381 | 8.4 |
| cafeteria | 1,323 | 8.0 |
| consultorio_dental | 1,155 | 7.0 |
| panaderia | 1,045 | 6.4 |
| purificadora | 947 | 5.8 |
| lavanderia | 896 | 5.5 |
| cafe_internet | 745 | 4.5 |
| heladeria | 715 | 4.4 |
| tienda_celulares | 550 | 3.3 |
| tienda_mascotas | 490 | 3.0 |
| consultorio_medico | 490 | 3.0 |
| gimnasio | 488 | 3.0 |
| floreria | 395 | 2.4 |
| zapateria | 389 | 2.4 |
| veterinaria | 293 | 1.8 |
| optica | 249 | 1.5 |
| bar | 244 | 1.5 |
| cerrajeria | 210 | 1.3 |
| pizzeria | 207 | 1.3 |
| pasteleria | 207 | 1.3 |
| spa | 137 | 0.8 |
| laboratorio_clinico | 95 | 0.6 |
| guarderia | 62 | 0.4 |
| sushi | 56 | 0.3 |
| escuela_idiomas | 39 | 0.2 |
| libreria | 31 | 0.2 |
| comida_china | 18 | 0.1 |
| coworking | 1 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| JARDINES DE MORELOS | 14 | 64,604 | 4,525 | medio |
| CIUDAD CUAUHTEMOC | 16 | 76,115 | 4,089 | bajo |
| GRANJAS VALLE DE GUADALUPE | 6 | 44,395 | 2,735 | bajo |
| SAN CRISTOBAL CENTRO | 5 | 14,805 | 2,246 | medio |
| SANTA CLARA COATITLA | 5 | 26,692 | 2,119 | bajo |
| CD AZTECA | 6 | 32,479 | 1,809 | medio |
| GUADALUPE VICTORIA | 8 | 34,350 | 1,783 | medio |
| SAN AGUSTIN | 5 | 29,093 | 1,768 | bajo |
| HANK GONZALEZ | 4 | 23,733 | 1,648 | bajo |
| LAS AMERICAS | 6 | 43,499 | 1,412 | alto |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LAS AMERICAS | 43,499 | 8.3 |
| IZCALLI ECATEPEC | 4,189 | 7.8 |
| OLIMPICA JAJALPA | 6,370 | 7.4 |
| VALLE DE ARAGON TERCERA SECCION | 20,895 | 7.1 |
| BUGAMBILIAS | 3,283 | 7.0 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN ANDRES DE LA CAÑADA | 7,371 | 2.7 |
| LOS BORDOS | 16,326 | 2.8 |
| TABLAS DEL POZO | 18,365 | 3.0 |
| LA PALMA | 12,013 | 3.0 |
| BENITO JUAREZ XALOSTOC NORTE | 8,702 | 3.1 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 2,960.3 millones de pesos por trimestre.
- Por hogar: 6,606 pesos por trimestre (lugar 30 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
