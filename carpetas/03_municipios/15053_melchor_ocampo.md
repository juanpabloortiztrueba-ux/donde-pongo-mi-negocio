# Ficha de municipio: Melchor Ocampo (Estado de México), clave 15053

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 59,014 habitantes (lugar 43 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 14,657. AGEB urbanas: 21. Superficie urbana de esas AGEB: 11.5 km².
- Densidad: 5,125 hab/km² (lugar 39 de 76).
- Edad: 0-14 años 25.5 %; 15-24 17.7 %; 25-59 46.9 %; 60 o más 9.7 %.
- Escolaridad promedio de la población de 15 y más: 9.9 años (lugar 51 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 41.0 %; con internet: 53.3 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 56.4 %, medio 43.6 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 36.8 %; Medio 34.3 %; Alto 29.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 3,269 (55.4 por cada 1 000 habitantes, lugar 42 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 2,044. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 11,130.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,640 | 50.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 553 | 16.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 379 | 11.6 % |
| 31 Industrias manufactureras | 167 | 5.1 % |
| 62 Servicios de salud y de asistencia social | 116 | 3.5 % |
| 61 Servicios educativos | 80 | 2.4 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 490 |
| 812110 | Salones y clínicas de belleza y peluquerías | 202 |
| 465311 | Comercio al por menor de artículos de papelería | 132 |
| 467115 | Comercio al por menor de artículos para la limpieza | 91 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 85 |
| 461122 | Comercio al por menor de carne de aves | 80 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 78 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 74 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 74 |
| 464111 | Farmacias sin minisúper | 72 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 507 | 85.9 |
| barberia_estetica | 202 | 34.2 |
| papeleria | 132 | 22.4 |
| carniceria | 128 | 21.7 |
| taller_mecanico | 89 | 15.1 |
| fruteria | 78 | 13.2 |
| farmacia | 76 | 12.9 |
| ferreteria | 74 | 12.5 |
| tienda_ropa | 74 | 12.5 |
| fonda | 63 | 10.7 |
| tortilleria | 62 | 10.5 |
| taqueria | 50 | 8.5 |
| cafeteria | 48 | 8.1 |
| panaderia | 43 | 7.3 |
| consultorio_dental | 32 | 5.4 |
| purificadora | 24 | 4.1 |
| lavanderia | 21 | 3.6 |
| cafe_internet | 21 | 3.6 |
| bar | 20 | 3.4 |
| heladeria | 20 | 3.4 |
| gimnasio | 18 | 3.1 |
| consultorio_medico | 17 | 2.9 |
| tienda_celulares | 14 | 2.4 |
| tienda_mascotas | 14 | 2.4 |
| floreria | 13 | 2.2 |
| pizzeria | 12 | 2.0 |
| veterinaria | 10 | 1.7 |
| zapateria | 8 | 1.4 |
| laboratorio_clinico | 8 | 1.4 |
| optica | 7 | 1.2 |
| pasteleria | 6 | 1.0 |
| cerrajeria | 6 | 1.0 |
| spa | 3 | 0.5 |
| guarderia | 2 | 0.3 |
| escuela_idiomas | 1 | 0.2 |
| comida_china | 1 | 0.2 |
| libreria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 3 | 11,489 | 1,008 | medio |
| VISITACION | 3 | 11,663 | 729 | bajo |
| SAN ISIDRO | 1 | 4,036 | 331 | medio |
| SAN FRANCISCO TENOPALCO | 4 | 5,086 | 233 | bajo |
| LOMAS DE TENOPALCO | 2 | 4,769 | 203 | bajo |
| 2 DE SEPTIEMBRE | 1 | 4,428 | 178 | bajo |
| LOS ALAMOS | 2 | 5,634 | 174 | medio |
| EDUCACION | 2 | 5,576 | 165 | medio |
| SEÑOR DE LOS MILAGROS | 2 | 3,441 | 155 | medio |
| EL MIRADOR | 1 | 2,892 | 84 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| CENTRO | 11,489 | 6.0 |
| SAN ISIDRO | 4,036 | 6.0 |
| LOS ALAMOS | 5,634 | 5.6 |
| SEÑOR DE LOS MILAGROS | 3,441 | 5.1 |
| EDUCACION | 5,576 | 4.5 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| 2 DE SEPTIEMBRE | 4,428 | 3.1 |
| LOMAS DE TENOPALCO | 4,769 | 3.1 |
| SAN FRANCISCO TENOPALCO | 5,086 | 3.5 |
| VISITACION | 11,663 | 4.2 |
| EDUCACION | 5,576 | 4.5 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 88.5 millones de pesos por trimestre.
- Por hogar: 6,038 pesos por trimestre (lugar 36 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
