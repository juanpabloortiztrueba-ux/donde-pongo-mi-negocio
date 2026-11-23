# Ficha de alcaldía: Iztacalco (Ciudad de México), clave 09006

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 404,695 habitantes (lugar 22 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 117,720. AGEB urbanas: 110. Superficie urbana de esas AGEB: 23.0 km².
- Densidad: 17,624 hab/km² (lugar 2 de 76).
- Edad: 0-14 años 17.1 %; 15-24 14.4 %; 25-59 50.9 %; 60 o más 17.5 %.
- Escolaridad promedio de la población de 15 y más: 11.5 años (lugar 6 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 45.3 %; con internet: 77.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 90.6 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 0.0 %, medio 96.1 %, alto 3.9 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 16.5 %; Bajo 76.4 %; Medio 7.1 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 17,402 (43.0 por cada 1 000 habitantes, lugar 67 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 17,467. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 111,415.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 7,606 | 43.7 % |
| 81 Otros servicios excepto actividades gubernamentales | 2,813 | 16.2 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,281 | 13.1 % |
| 31 Industrias manufactureras | 871 | 5.0 % |
| 62 Servicios de salud y de asistencia social | 848 | 4.9 % |
| 43 Comercio al por mayor | 542 | 3.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,587 |
| 812110 | Salones y clínicas de belleza y peluquerías | 946 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 497 |
| 465311 | Comercio al por menor de artículos de papelería | 485 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 466 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 397 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 359 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 358 |
| 461121 | Comercio al por menor de carnes rojas | 336 |
| 621211 | Consultorios dentales del sector privado | 331 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,689 | 41.7 |
| barberia_estetica | 946 | 23.4 |
| carniceria | 630 | 15.6 |
| fruteria | 497 | 12.3 |
| papeleria | 485 | 12.0 |
| taller_mecanico | 399 | 9.9 |
| taqueria | 397 | 9.8 |
| fonda | 389 | 9.6 |
| cafeteria | 358 | 8.8 |
| farmacia | 343 | 8.5 |
| consultorio_dental | 331 | 8.2 |
| tienda_ropa | 293 | 7.2 |
| lavanderia | 287 | 7.1 |
| tortilleria | 263 | 6.5 |
| ferreteria | 255 | 6.3 |
| purificadora | 194 | 4.8 |
| panaderia | 171 | 4.2 |
| cafe_internet | 151 | 3.7 |
| consultorio_medico | 139 | 3.4 |
| tienda_mascotas | 133 | 3.3 |
| veterinaria | 117 | 2.9 |
| tienda_celulares | 85 | 2.1 |
| heladeria | 79 | 2.0 |
| gimnasio | 78 | 1.9 |
| zapateria | 65 | 1.6 |
| optica | 62 | 1.5 |
| cerrajeria | 60 | 1.5 |
| pasteleria | 54 | 1.3 |
| floreria | 53 | 1.3 |
| pizzeria | 40 | 1.0 |
| spa | 37 | 0.9 |
| bar | 36 | 0.9 |
| laboratorio_clinico | 29 | 0.7 |
| sushi | 18 | 0.4 |
| guarderia | 12 | 0.3 |
| comida_china | 10 | 0.2 |
| escuela_idiomas | 9 | 0.2 |
| libreria | 5 | 0.1 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| AGRÍCOLA ORIENTAL | 19 | 89,487 | 4,371 | medio |
| AGRÍCOLA PANTITLAN | 14 | 73,979 | 2,629 | medio |
| GRANJAS MÉXICO | 6 | 18,509 | 1,261 | medio |
| GABRIEL RAMOS MILLÁN SECCIÓN BRAMADERO | 8 | 21,232 | 1,238 | medio |
| CAMPAMENTO DOS DE OCTUBRE | 5 | 20,202 | 705 | medio |
| JUVENTINO ROSAS | 2 | 12,579 | 635 | medio |
| VIADUCTO PIEDAD | 2 | 10,324 | 575 | medio |
| EL RODEO | 2 | 8,565 | 483 | medio |
| AMPLIACIÓN GABRIEL RAMOS MILLÁN | 3 | 9,458 | 449 | medio |
| SANTA ANITA | 2 | 11,136 | 435 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| MILITAR MARTE | 4,940 | 8.7 |
| REFORMA IZTACCIHUATL NORTE | 6,979 | 8.6 |
| REFORMA IZTACCIHUATL SUR | 3,924 | 8.5 |
| SANTIAGO SUR | 7,388 | 7.3 |
| INPI PICOS | 3,851 | 7.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LA CRUZ | 4,869 | 5.3 |
| CARLOS ZAPATA VELA | 7,542 | 5.3 |
| SAN FRANCISCO XICANTONGO | 7,901 | 5.5 |
| JUVENTINO ROSAS | 12,579 | 5.7 |
| SAN MIGUEL | 4,801 | 5.7 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,020.4 millones de pesos por trimestre.
- Por hogar: 8,668 pesos por trimestre (lugar 11 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
