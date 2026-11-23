# Ficha de alcaldía: Gustavo A. Madero (Ciudad de México), clave 09005

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 1,173,351 habitantes (lugar 3 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 340,153. AGEB urbanas: 305. Superficie urbana de esas AGEB: 87.4 km².
- Densidad: 13,428 hab/km² (lugar 10 de 76).
- Edad: 0-14 años 18.1 %; 15-24 15.0 %; 25-59 49.5 %; 60 o más 17.3 %.
- Escolaridad promedio de la población de 15 y más: 11.0 años (lugar 15 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 42.2 %; con internet: 72.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 82.7 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 26.7 %, medio 65.3 %, alto 7.4 %, sin estimación 0.7 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 15.5 %; Bajo 54.4 %; Medio 28.3 %; Alto 1.1 %; Muy alto 0.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 50,927 (43.4 por cada 1 000 habitantes, lugar 63 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 53,172. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 289,264.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 23,120 | 45.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 8,558 | 16.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 6,410 | 12.6 % |
| 62 Servicios de salud y de asistencia social | 2,744 | 5.4 % |
| 31 Industrias manufactureras | 2,172 | 4.3 % |
| 61 Servicios educativos | 1,399 | 2.7 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 4,967 |
| 812110 | Salones y clínicas de belleza y peluquerías | 3,030 |
| 465311 | Comercio al por menor de artículos de papelería | 1,544 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 1,250 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 1,225 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 1,055 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 1,026 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 978 |
| 621211 | Consultorios dentales del sector privado | 958 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 896 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 5,250 | 44.7 |
| barberia_estetica | 3,030 | 25.8 |
| carniceria | 1,565 | 13.3 |
| papeleria | 1,544 | 13.2 |
| taller_mecanico | 1,341 | 11.4 |
| taqueria | 1,225 | 10.4 |
| tienda_ropa | 1,055 | 9.0 |
| fonda | 1,045 | 8.9 |
| cafeteria | 1,026 | 8.7 |
| fruteria | 978 | 8.3 |
| farmacia | 960 | 8.2 |
| consultorio_dental | 958 | 8.2 |
| ferreteria | 872 | 7.4 |
| tortilleria | 810 | 6.9 |
| lavanderia | 597 | 5.1 |
| consultorio_medico | 530 | 4.5 |
| panaderia | 488 | 4.2 |
| cafe_internet | 408 | 3.5 |
| tienda_mascotas | 355 | 3.0 |
| tienda_celulares | 348 | 3.0 |
| purificadora | 343 | 2.9 |
| heladeria | 290 | 2.5 |
| zapateria | 286 | 2.4 |
| veterinaria | 284 | 2.4 |
| gimnasio | 269 | 2.3 |
| optica | 209 | 1.8 |
| floreria | 182 | 1.6 |
| cerrajeria | 155 | 1.3 |
| pizzeria | 149 | 1.3 |
| pasteleria | 110 | 0.9 |
| spa | 98 | 0.8 |
| laboratorio_clinico | 87 | 0.7 |
| bar | 69 | 0.6 |
| sushi | 56 | 0.5 |
| libreria | 34 | 0.3 |
| guarderia | 33 | 0.3 |
| escuela_idiomas | 30 | 0.3 |
| comida_china | 19 | 0.2 |
| coworking | 2 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN FELIPE DE JESÚS | 10 | 44,627 | 2,136 | medio |
| NUEVA ATZACOALCO | 4 | 29,727 | 1,247 | bajo |
| AMPLIACIÓN CASAS ALEMÁN | 4 | 25,478 | 1,167 | medio |
| VILLA GUSTAVO A. MADERO | 1 | 2,985 | 1,057 | medio |
| INDUSTRIAL | 5 | 16,861 | 1,044 | medio |
| MARTÍN CARRERA | 5 | 29,120 | 1,018 | medio |
| PROVIDENCIA | 5 | 25,082 | 1,015 | medio |
| CUAUTEPEC BARRIO ALTO | 1 | 10,026 | 984 | bajo |
| PROGRESO NACIONAL | 5 | 19,918 | 953 | medio |
| VALLEJO | 4 | 20,483 | 924 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| RESIDENCIAL ACUEDUCTO DE GUADALUPE | 5,682 | 9.0 |
| LINDAVISTA SUR | 6,999 | 8.9 |
| CHURUBUSCO TEPEYAC | 3,057 | 8.8 |
| LINDAVISTA NORTE | 9,828 | 8.8 |
| VILLA DE ARAGÓN | 3,222 | 8.1 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| AMPLIACIÓN MALACATES | 4,345 | 2.7 |
| VISTA HERMOSA | 3,544 | 2.8 |
| TLALPEXCO | 10,555 | 3.2 |
| MALACATES | 8,724 | 3.2 |
| LOMAS DE CUAUTEPEC | 10,081 | 3.3 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 2,657.0 millones de pesos por trimestre.
- Por hogar: 7,811 pesos por trimestre (lugar 21 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
