# Ficha de municipio: Cuautitlán (Estado de México), clave 15024

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 172,626 habitantes (lugar 35 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 50,339. AGEB urbanas: 44. Superficie urbana de esas AGEB: 24.5 km².
- Densidad: 7,051 hab/km² (lugar 28 de 76).
- Edad: 0-14 años 21.7 %; 15-24 17.1 %; 25-59 52.5 %; 60 o más 8.6 %.
- Escolaridad promedio de la población de 15 y más: 11.3 años (lugar 13 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 52.0 %; con internet: 73.2 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 12.1 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 4.7 %, medio 90.8 %, alto 4.5 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 33.4 %; Bajo 48.9 %; Medio 16.0 %; Alto 1.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 8,301 (48.1 por cada 1 000 habitantes, lugar 56 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 5,510. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 50,660.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 3,838 | 46.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,123 | 13.5 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 1,077 | 13.0 % |
| 62 Servicios de salud y de asistencia social | 391 | 4.7 % |
| 31 Industrias manufactureras | 375 | 4.5 % |
| 43 Comercio al por mayor | 239 | 2.9 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 803 |
| 812110 | Salones y clínicas de belleza y peluquerías | 397 |
| 465311 | Comercio al por menor de artículos de papelería | 275 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 233 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 208 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 170 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 165 |
| 464111 | Farmacias sin minisúper | 157 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 150 |
| 461122 | Comercio al por menor de carne de aves | 149 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 868 | 50.3 |
| barberia_estetica | 397 | 23.0 |
| papeleria | 275 | 15.9 |
| carniceria | 244 | 14.1 |
| tienda_ropa | 233 | 13.5 |
| farmacia | 171 | 9.9 |
| taqueria | 170 | 9.8 |
| fonda | 169 | 9.8 |
| taller_mecanico | 158 | 9.2 |
| fruteria | 150 | 8.7 |
| cafeteria | 147 | 8.5 |
| ferreteria | 145 | 8.4 |
| consultorio_dental | 121 | 7.0 |
| tortilleria | 112 | 6.5 |
| panaderia | 77 | 4.5 |
| gimnasio | 73 | 4.2 |
| tienda_celulares | 69 | 4.0 |
| consultorio_medico | 68 | 3.9 |
| purificadora | 59 | 3.4 |
| zapateria | 58 | 3.4 |
| lavanderia | 57 | 3.3 |
| cafe_internet | 57 | 3.3 |
| heladeria | 52 | 3.0 |
| tienda_mascotas | 49 | 2.8 |
| bar | 45 | 2.6 |
| floreria | 37 | 2.1 |
| veterinaria | 36 | 2.1 |
| optica | 30 | 1.7 |
| laboratorio_clinico | 27 | 1.6 |
| cerrajeria | 25 | 1.4 |
| pizzeria | 21 | 1.2 |
| pasteleria | 18 | 1.0 |
| spa | 15 | 0.9 |
| guarderia | 9 | 0.5 |
| comida_china | 5 | 0.3 |
| sushi | 5 | 0.3 |
| libreria | 4 | 0.2 |
| escuela_idiomas | 3 | 0.2 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO CUAUTITLAN | 1 | 1,533 | 1,245 | medio |
| SAN MATEO IXTACALCO | 3 | 6,241 | 857 | medio |
| SANTA ELENA | 2 | 25,447 | 827 | medio |
| LAZARO CARDENAS | 2 | 8,408 | 595 | medio |
| GUADALUPE | 1 | 3,179 | 407 | medio |
| LOS MORALES | 1 | 3,444 | 405 | medio |
| JOYAS DE CUAUTITLAN | 1 | 11,327 | 301 | medio |
| SAN BLAS II | 1 | 1,651 | 213 | medio |
| SANTA MARIA HUECATITLA | 1 | 3,885 | 212 | medio |
| TLATENCO | 1 | 3,985 | 203 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| PASEOS DEL BOSQUE | 3,824 | 8.5 |
| SAN ROQUE | 3,792 | 8.1 |
| HACIENDA CUAUTITLAN | 11,236 | 7.8 |
| GALAXIA | 7,580 | 7.8 |
| LA ALBORADA | 6,296 | 7.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| TLATENCO | 3,985 | 4.5 |
| LA PROVIDENCIA | 3,673 | 4.7 |
| SANTA MARIA HUECATITLA | 3,885 | 4.7 |
| LOMA BONITA | 3,447 | 4.8 |
| LAZARO CARDENAS | 8,408 | 5.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 431.2 millones de pesos por trimestre.
- Por hogar: 8,565 pesos por trimestre (lugar 12 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
