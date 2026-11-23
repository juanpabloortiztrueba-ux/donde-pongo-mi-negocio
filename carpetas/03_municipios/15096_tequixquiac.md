# Ficha de municipio: Tequixquiac (Estado de México), clave 15096

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 33,176 habitantes (lugar 52 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 9,032. AGEB urbanas: 20. Superficie urbana de esas AGEB: 20.8 km².
- Densidad: 1,592 hab/km² (lugar 72 de 76).
- Edad: 0-14 años 24.9 %; 15-24 17.6 %; 25-59 46.7 %; 60 o más 10.5 %.
- Escolaridad promedio de la población de 15 y más: 9.4 años (lugar 64 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 43.2 %; con internet: 37.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 92.8 %, medio 7.2 %, alto 0.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 66.3 %; Alto 33.4 %; Muy alto 0.3 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 2,772 (83.6 por cada 1 000 habitantes, lugar 12 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 2,104. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 11,144.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,304 | 47.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 398 | 14.4 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 318 | 11.5 % |
| 31 Industrias manufactureras | 180 | 6.5 % |
| 62 Servicios de salud y de asistencia social | 128 | 4.6 % |
| 32 Industrias manufactureras | 66 | 2.4 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 322 |
| 812110 | Salones y clínicas de belleza y peluquerías | 146 |
| 465311 | Comercio al por menor de artículos de papelería | 103 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 87 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 76 |
| 461122 | Comercio al por menor de carne de aves | 58 |
| 467115 | Comercio al por menor de artículos para la limpieza | 56 |
| 465912 | Comercio al por menor de regalos | 55 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 54 |
| 466410 | Comercio al por menor de artículos usados | 53 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 330 | 99.5 |
| barberia_estetica | 146 | 44.0 |
| papeleria | 103 | 31.0 |
| carniceria | 91 | 27.4 |
| tienda_ropa | 87 | 26.2 |
| tortilleria | 76 | 22.9 |
| fonda | 62 | 18.7 |
| farmacia | 55 | 16.6 |
| taller_mecanico | 53 | 16.0 |
| ferreteria | 44 | 13.3 |
| cafeteria | 40 | 12.1 |
| taqueria | 37 | 11.2 |
| panaderia | 34 | 10.2 |
| fruteria | 32 | 9.6 |
| consultorio_dental | 26 | 7.8 |
| cafe_internet | 23 | 6.9 |
| bar | 20 | 6.0 |
| gimnasio | 17 | 5.1 |
| consultorio_medico | 15 | 4.5 |
| zapateria | 13 | 3.9 |
| tienda_celulares | 13 | 3.9 |
| floreria | 12 | 3.6 |
| heladeria | 12 | 3.6 |
| laboratorio_clinico | 11 | 3.3 |
| pizzeria | 10 | 3.0 |
| purificadora | 10 | 3.0 |
| lavanderia | 8 | 2.4 |
| veterinaria | 8 | 2.4 |
| pasteleria | 7 | 2.1 |
| spa | 7 | 2.1 |
| tienda_mascotas | 6 | 1.8 |
| cerrajeria | 5 | 1.5 |
| guarderia | 2 | 0.6 |
| optica | 2 | 0.6 |
| libreria | 1 | 0.3 |
| sushi | 1 | 0.3 |
| escuela_idiomas | 1 | 0.3 |
| comida_china | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN MATEO | 3 | 8,232 | 694 | bajo |
| CENTRO | 1 | 2,382 | 580 | medio |
| EL REFUGIO | 1 | 6,201 | 389 | bajo |
| TLAPANALOYA | 3 | 4,303 | 362 | bajo |
| SAN JOSE | 3 | 5,858 | 357 | bajo |
| EJIDAL ADOLFO LOPEZ MATEOS | 2 | 3,020 | 215 | bajo |
| FRANCISCO I MADERO | 2 | 2,134 | 97 | bajo |
| MONTE ALTO | 3 | 1,032 | 72 | bajo |
| Tequixquiac | 1 | 4 | 0 | NO ENCONTRADO |
| Tlapanaloya | 1 | 10 | 0 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 41.1 millones de pesos por trimestre.
- Por hogar: 4,555 pesos por trimestre (lugar 66 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
