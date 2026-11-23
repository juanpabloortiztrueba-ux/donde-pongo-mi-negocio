# Ficha de municipio: Coacalco de Berriozábal (Estado de México), clave 15020

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 293,245 habitantes (lugar 27 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 89,664. AGEB urbanas: 70. Superficie urbana de esas AGEB: 21.9 km².
- Densidad: 13,363 hab/km² (lugar 11 de 76).
- Edad: 0-14 años 19.5 %; 15-24 16.0 %; 25-59 50.6 %; 60 o más 13.9 %.
- Escolaridad promedio de la población de 15 y más: 11.5 años (lugar 8 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 48.5 %; con internet: 75.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 29.9 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 10.7 %, medio 88.2 %, alto 1.2 %.
- Decil estimado típico (mediana ponderada por población): 7.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 33.4 %; Bajo 58.2 %; Medio 8.4 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 11,554 (39.4 por cada 1 000 habitantes, lugar 72 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 11,018. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 58,388.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 5,305 | 45.9 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,872 | 16.2 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 1,621 | 14.0 % |
| 62 Servicios de salud y de asistencia social | 593 | 5.1 % |
| 31 Industrias manufactureras | 488 | 4.2 % |
| 61 Servicios educativos | 427 | 3.7 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,093 |
| 812110 | Salones y clínicas de belleza y peluquerías | 785 |
| 465311 | Comercio al por menor de artículos de papelería | 447 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 308 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 282 |
| 464111 | Farmacias sin minisúper | 277 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 259 |
| 467115 | Comercio al por menor de artículos para la limpieza | 248 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 239 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 231 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,163 | 39.7 |
| barberia_estetica | 785 | 26.8 |
| papeleria | 447 | 15.2 |
| carniceria | 347 | 11.8 |
| cafeteria | 308 | 10.5 |
| farmacia | 304 | 10.4 |
| fonda | 288 | 9.8 |
| tienda_ropa | 259 | 8.8 |
| taqueria | 225 | 7.7 |
| taller_mecanico | 213 | 7.3 |
| fruteria | 189 | 6.4 |
| consultorio_dental | 188 | 6.4 |
| tortilleria | 162 | 5.5 |
| lavanderia | 143 | 4.9 |
| tienda_celulares | 128 | 4.4 |
| ferreteria | 127 | 4.3 |
| panaderia | 125 | 4.3 |
| purificadora | 119 | 4.1 |
| consultorio_medico | 100 | 3.4 |
| cafe_internet | 92 | 3.1 |
| tienda_mascotas | 91 | 3.1 |
| heladeria | 79 | 2.7 |
| veterinaria | 72 | 2.5 |
| gimnasio | 65 | 2.2 |
| floreria | 63 | 2.1 |
| optica | 59 | 2.0 |
| bar | 56 | 1.9 |
| zapateria | 54 | 1.8 |
| cerrajeria | 33 | 1.1 |
| pizzeria | 33 | 1.1 |
| spa | 21 | 0.7 |
| pasteleria | 21 | 0.7 |
| guarderia | 20 | 0.7 |
| laboratorio_clinico | 20 | 0.7 |
| sushi | 17 | 0.6 |
| escuela_idiomas | 16 | 0.5 |
| libreria | 8 | 0.3 |
| comida_china | 6 | 0.2 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| COACALCO VILLA DE LAS FLORES SECCIÓN T | 7 | 41,332 | 2,380 | medio |
| SAN FRANCISCO COACALCO | 4 | 18,409 | 1,126 | medio |
| SAN FRANCISCO COACALCO SECCIÓN HÉROES Y SECCIÓN HACIENDA | 3 | 46,861 | 1,105 | medio |
| SAN LORENZO TETLIXTAC | 3 | 13,554 | 839 | medio |
| PARQUE RESIDENCIAL COACALCO SECCIONES PRIMERA, SEGUNDA Y TERCERA | 5 | 16,122 | 775 | medio |
| SAN RAFAEL COACALCO | 15 | 27,246 | 678 | bajo |
| UNIDAD COACALCO VILLA DE LAS FLORES PROLONGACIÓN PRIMERA SECCIÓN | 1 | 10,294 | 534 | medio |
| BOSQUES DEL VALLE PRIMERA Y SEGUNDA SECCIÓN | 3 | 11,047 | 402 | medio |
| LOS ACUALES | 2 | 6,925 | 373 | medio |
| REPÚBLICA MEXICANA | 1 | 8,474 | 311 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| COSMOPOL | 4,325 | 7.5 |
| UNIDAD COACALCO VILLA DE LAS FLORES PROLONGACIÓN PRIMERA SECCIÓN | 10,294 | 7.2 |
| SAN FRANCISCO COACALCO SECCIÓN HÉROES Y SECCIÓN HACIENDA | 46,861 | 7.0 |
| SAN FRANCISCO COACALCO | 18,409 | 7.0 |
| EL LAUREL | 4,397 | 7.0 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| POTRERO LA LAGUNA | 8,003 | 4.2 |
| SAN RAFAEL COACALCO | 27,246 | 4.3 |
| HABITACIONAL LOS PORTALES ORIENTE | 3,199 | 4.3 |
| REPÚBLICA MEXICANA | 8,474 | 4.8 |
| JALATLACO | 3,939 | 4.8 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 750.2 millones de pesos por trimestre.
- Por hogar: 8,367 pesos por trimestre (lugar 15 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
