# Ficha de municipio: Cuautitlán Izcalli (Estado de México), clave 15121

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 538,935 habitantes (lugar 12 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 156,779. AGEB urbanas: 203. Superficie urbana de esas AGEB: 91.6 km².
- Densidad: 5,881 hab/km² (lugar 36 de 76).
- Edad: 0-14 años 20.1 %; 15-24 15.4 %; 25-59 49.8 %; 60 o más 14.7 %.
- Escolaridad promedio de la población de 15 y más: 11.4 años (lugar 11 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 57.0 %; con internet: 75.7 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 3.3 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 8.8 %, medio 71.4 %, alto 19.8 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 34.1 %; Bajo 39.4 %; Medio 25.0 %; Alto 1.5 %; Muy alto 0.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 23,899 (44.3 por cada 1 000 habitantes, lugar 61 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 21,023. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 162,979.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 10,217 | 42.8 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,887 | 16.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 3,265 | 13.7 % |
| 62 Servicios de salud y de asistencia social | 1,206 | 5.0 % |
| 31 Industrias manufactureras | 988 | 4.1 % |
| 43 Comercio al por mayor | 734 | 3.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,316 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,436 |
| 465311 | Comercio al por menor de artículos de papelería | 782 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 579 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 557 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 501 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 500 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 473 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 461 |
| 467115 | Comercio al por menor de artículos para la limpieza | 429 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 2,454 | 45.5 |
| barberia_estetica | 1,436 | 26.6 |
| papeleria | 782 | 14.5 |
| carniceria | 696 | 12.9 |
| taller_mecanico | 634 | 11.8 |
| taqueria | 557 | 10.3 |
| fonda | 541 | 10.0 |
| cafeteria | 501 | 9.3 |
| tienda_ropa | 500 | 9.3 |
| farmacia | 412 | 7.6 |
| fruteria | 406 | 7.5 |
| consultorio_dental | 387 | 7.2 |
| tortilleria | 328 | 6.1 |
| ferreteria | 316 | 5.9 |
| lavanderia | 278 | 5.2 |
| consultorio_medico | 259 | 4.8 |
| panaderia | 216 | 4.0 |
| purificadora | 203 | 3.8 |
| cafe_internet | 178 | 3.3 |
| gimnasio | 163 | 3.0 |
| veterinaria | 150 | 2.8 |
| tienda_celulares | 149 | 2.8 |
| heladeria | 148 | 2.7 |
| bar | 130 | 2.4 |
| floreria | 127 | 2.4 |
| tienda_mascotas | 116 | 2.2 |
| zapateria | 102 | 1.9 |
| optica | 85 | 1.6 |
| cerrajeria | 71 | 1.3 |
| pizzeria | 70 | 1.3 |
| spa | 57 | 1.1 |
| laboratorio_clinico | 46 | 0.9 |
| pasteleria | 38 | 0.7 |
| sushi | 24 | 0.4 |
| guarderia | 22 | 0.4 |
| escuela_idiomas | 13 | 0.2 |
| comida_china | 7 | 0.1 |
| libreria | 6 | 0.1 |
| coworking | 3 | 0.1 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SANTA MARÍA GUADALUPE LAS TORRES PRIMERA SECCIÓN | 7 | 20,935 | 942 | medio |
| SAN FRANCISCO TEPOJACO | 6 | 18,360 | 915 | medio |
| EL SOCORRO | 4 | 7,372 | 863 | medio |
| CENTRO URBANO | 1 | 1,132 | 832 | medio |
| LUIS ECHEVERRÍA | 3 | 12,217 | 778 | medio |
| CUMBRIA | 5 | 13,477 | 748 | alto |
| BOSQUES DE MORELOS | 3 | 13,621 | 676 | medio |
| ENSUEÑOS | 2 | 7,977 | 659 | alto |
| SANTA ROSA DE LIMA | 2 | 8,956 | 591 | medio |
| SAN ISIDRO | 4 | 4,569 | 575 | alto |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN MIGUEL | 3,152 | 9.2 |
| PASEOS DE IZCALLI | 9,723 | 9.0 |
| HACIENDA DEL PARQUE PRIMERA SECCIÓN | 4,168 | 9.0 |
| LA PIEDAD ORIENTE | 4,120 | 9.0 |
| LAGO DE GUADALUPE | 3,254 | 8.9 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SANTA MARIA TIANGUISTENGO | 7,321 | 4.3 |
| SAN FRANCISCO TEPOJACO | 18,360 | 4.5 |
| INFONAVIT NORTE SECCIÓN 1 | 7,467 | 4.5 |
| EL ROSARIO | 7,574 | 4.6 |
| SAN LORENZO RÍO TENCO | 3,118 | 4.7 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,494.1 millones de pesos por trimestre.
- Por hogar: 9,530 pesos por trimestre (lugar 7 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
