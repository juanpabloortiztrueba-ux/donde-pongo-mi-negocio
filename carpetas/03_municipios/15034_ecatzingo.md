# Ficha de municipio: Ecatzingo (Estado de México), clave 15034

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 8,294 habitantes (lugar 71 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 2,083. AGEB urbanas: 2. Superficie urbana de esas AGEB: 6.3 km².
- Densidad: 1,317 hab/km² (lugar 76 de 76).
- Edad: 0-14 años 30.4 %; 15-24 19.7 %; 25-59 41.0 %; 60 o más 8.9 %.
- Escolaridad promedio de la población de 15 y más: 9.0 años (lugar 74 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 24.4 %; con internet: 20.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 100.0 %, medio 0.0 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 2.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Alto 57.0 %; Muy alto 43.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 458 (55.2 por cada 1 000 habitantes, lugar 43 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 422. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 1,631.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 271 | 59.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 41 | 9.0 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 34 | 7.4 % |
| 31 Industrias manufactureras | 30 | 6.6 % |
| 62 Servicios de salud y de asistencia social | 16 | 3.5 % |
| 61 Servicios educativos | 13 | 2.8 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 120 |
| 465311 | Comercio al por menor de artículos de papelería | 30 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 22 |
| 465912 | Comercio al por menor de regalos | 15 |
| 812110 | Salones y clínicas de belleza y peluquerías | 13 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 12 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 12 |
| 813210 | Asociaciones y organizaciones religiosas | 12 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 9 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 8 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 120 | 144.7 |
| papeleria | 30 | 36.2 |
| tortilleria | 22 | 26.5 |
| carniceria | 14 | 16.9 |
| barberia_estetica | 13 | 15.7 |
| tienda_ropa | 12 | 14.5 |
| fruteria | 12 | 14.5 |
| taqueria | 8 | 9.6 |
| fonda | 7 | 8.4 |
| farmacia | 6 | 7.2 |
| cafe_internet | 5 | 6.0 |
| cafeteria | 4 | 4.8 |
| ferreteria | 4 | 4.8 |
| tienda_mascotas | 4 | 4.8 |
| taller_mecanico | 3 | 3.6 |
| zapateria | 3 | 3.6 |
| panaderia | 3 | 3.6 |
| consultorio_medico | 3 | 3.6 |
| purificadora | 2 | 2.4 |
| floreria | 2 | 2.4 |
| heladeria | 2 | 2.4 |
| consultorio_dental | 2 | 2.4 |
| pizzeria | 2 | 2.4 |
| pasteleria | 2 | 2.4 |
| lavanderia | 1 | 1.2 |
| laboratorio_clinico | 1 | 1.2 |
| bar | 1 | 1.2 |
| gimnasio | 0 | 0.0 |
| coworking | 0 | 0.0 |
| sushi | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| optica | 0 | 0.0 |
| veterinaria | 0 | 0.0 |
| cerrajeria | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| spa | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| libreria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| tienda_celulares | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN JOSE | 1 | 3,565 | 271 | bajo |
| SAN MIGUEL | 1 | 4,729 | 184 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 7.1 millones de pesos por trimestre.
- Por hogar: 3,394 pesos por trimestre (lugar 76 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
