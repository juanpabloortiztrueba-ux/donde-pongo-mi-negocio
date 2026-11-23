# Ficha de municipio: Nicolás Romero (Estado de México), clave 15060

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 390,453 habitantes (lugar 24 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 104,334. AGEB urbanas: 91. Superficie urbana de esas AGEB: 59.3 km².
- Densidad: 6,589 hab/km² (lugar 33 de 76).
- Edad: 0-14 años 24.1 %; 15-24 17.3 %; 25-59 48.7 %; 60 o más 9.8 %.
- Escolaridad promedio de la población de 15 y más: 9.8 años (lugar 54 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 40.1 %; con internet: 58.1 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 65.2 %, medio 34.8 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 5.2 %; Bajo 21.5 %; Medio 55.2 %; Alto 16.4 %; Muy alto 1.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 19,654 (50.3 por cada 1 000 habitantes, lugar 48 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 16,328. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 68,906.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 10,258 | 52.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 2,994 | 15.2 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,186 | 11.1 % |
| 31 Industrias manufactureras | 968 | 4.9 % |
| 62 Servicios de salud y de asistencia social | 684 | 3.5 % |
| 61 Servicios educativos | 493 | 2.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 3,149 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,165 |
| 465311 | Comercio al por menor de artículos de papelería | 917 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 592 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 483 |
| 461122 | Comercio al por menor de carne de aves | 414 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 391 |
| 467115 | Comercio al por menor de artículos para la limpieza | 391 |
| 464111 | Farmacias sin minisúper | 388 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 363 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 3,230 | 82.7 |
| barberia_estetica | 1,165 | 29.8 |
| papeleria | 917 | 23.5 |
| carniceria | 714 | 18.3 |
| tienda_ropa | 592 | 15.2 |
| taller_mecanico | 450 | 11.5 |
| farmacia | 433 | 11.1 |
| fruteria | 363 | 9.3 |
| ferreteria | 354 | 9.1 |
| panaderia | 350 | 9.0 |
| taqueria | 338 | 8.7 |
| fonda | 328 | 8.4 |
| tortilleria | 310 | 7.9 |
| cafeteria | 295 | 7.6 |
| consultorio_dental | 264 | 6.8 |
| cafe_internet | 152 | 3.9 |
| purificadora | 141 | 3.6 |
| tienda_celulares | 135 | 3.5 |
| gimnasio | 126 | 3.2 |
| floreria | 122 | 3.1 |
| zapateria | 114 | 2.9 |
| consultorio_medico | 113 | 2.9 |
| heladeria | 108 | 2.8 |
| bar | 98 | 2.5 |
| lavanderia | 89 | 2.3 |
| pasteleria | 81 | 2.1 |
| veterinaria | 56 | 1.4 |
| pizzeria | 40 | 1.0 |
| optica | 38 | 1.0 |
| laboratorio_clinico | 38 | 1.0 |
| tienda_mascotas | 33 | 0.8 |
| cerrajeria | 29 | 0.7 |
| spa | 25 | 0.6 |
| guarderia | 10 | 0.3 |
| comida_china | 8 | 0.2 |
| sushi | 5 | 0.1 |
| libreria | 4 | 0.1 |
| escuela_idiomas | 2 | 0.1 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| BENITO JUÁREZ PRIMERA SECCIÓN CENTRO | 1 | 3,336 | 1,672 | medio |
| GRANJAS GUADALUPE PRIMERA SECCIÓN | 3 | 20,304 | 1,061 | medio |
| ZARAGOZA PRIMERA SECCIÓN | 2 | 19,942 | 958 | bajo |
| SANTA ANITA | 2 | 9,024 | 940 | medio |
| EL TRAFICO | 6 | 20,329 | 930 | bajo |
| HIDALGO PRIMERA SECCIÓN | 2 | 10,412 | 816 | bajo |
| ZONA EJIDAL VICENTE GUERRERO | 3 | 12,919 | 672 | bajo |
| PROGRESO INDUSTRIAL | 3 | 11,534 | 622 | bajo |
| FRANCISCO I. MADERO SEGUNDA SECCIÓN | 1 | 9,851 | 565 | bajo |
| BENITO JUÁREZ SEGUNDA SECCIÓN | 1 | 11,682 | 480 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| BULEVARES DEL LAGO | 8,886 | 7.2 |
| CANTAROS LLL | 12,404 | 7.1 |
| ARCOÍRIS | 3,887 | 7.0 |
| BOSQUES DE LA COLMENA | 8,093 | 6.7 |
| FLORES MAGÓN | 9,124 | 6.1 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| QUINTO BARRIO | 4,063 | 2.2 |
| TRANSFIGURACION | 4,147 | 2.8 |
| AXOTLÁN PARTE ALTA | 4,287 | 2.9 |
| AXOTLÁN PARTE BAJA | 4,158 | 3.0 |
| SAN FRANCISCO MAGU | 5,612 | 3.3 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 621.8 millones de pesos por trimestre.
- Por hogar: 5,959 pesos por trimestre (lugar 37 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
