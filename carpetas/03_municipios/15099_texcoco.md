# Ficha de municipio: Texcoco (Estado de México), clave 15099

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 240,464 habitantes (lugar 32 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 62,804. AGEB urbanas: 101. Superficie urbana de esas AGEB: 74.9 km².
- Densidad: 3,210 hab/km² (lugar 58 de 76).
- Edad: 0-14 años 22.8 %; 15-24 18.1 %; 25-59 47.1 %; 60 o más 11.9 %.
- Escolaridad promedio de la población de 15 y más: 10.6 años (lugar 26 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 46.6 %; con internet: 56.6 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 1.3 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 46.8 %, medio 49.1 %, alto 4.1 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 6.3 %; Bajo 35.2 %; Medio 29.3 %; Alto 22.8 %; Muy alto 6.3 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 16,115 (67.0 por cada 1 000 habitantes, lugar 26 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 12,832. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 75,568.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 7,649 | 47.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 2,372 | 14.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,094 | 13.0 % |
| 31 Industrias manufactureras | 766 | 4.8 % |
| 62 Servicios de salud y de asistencia social | 743 | 4.6 % |
| 61 Servicios educativos | 417 | 2.6 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,975 |
| 812110 | Salones y clínicas de belleza y peluquerías | 834 |
| 465311 | Comercio al por menor de artículos de papelería | 501 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 454 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 416 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 319 |
| 465912 | Comercio al por menor de regalos | 319 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 313 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 284 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 284 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 2,030 | 84.4 |
| barberia_estetica | 834 | 34.7 |
| papeleria | 501 | 20.8 |
| carniceria | 452 | 18.8 |
| tienda_ropa | 416 | 17.3 |
| fonda | 362 | 15.1 |
| fruteria | 319 | 13.3 |
| cafeteria | 313 | 13.0 |
| farmacia | 306 | 12.7 |
| taller_mecanico | 306 | 12.7 |
| taqueria | 284 | 11.8 |
| ferreteria | 246 | 10.2 |
| consultorio_dental | 221 | 9.2 |
| tortilleria | 217 | 9.0 |
| panaderia | 186 | 7.7 |
| lavanderia | 183 | 7.6 |
| floreria | 157 | 6.5 |
| consultorio_medico | 154 | 6.4 |
| heladeria | 150 | 6.2 |
| tienda_celulares | 133 | 5.5 |
| cafe_internet | 127 | 5.3 |
| zapateria | 114 | 4.7 |
| purificadora | 96 | 4.0 |
| gimnasio | 77 | 3.2 |
| tienda_mascotas | 69 | 2.9 |
| bar | 66 | 2.7 |
| optica | 65 | 2.7 |
| pizzeria | 56 | 2.3 |
| pasteleria | 49 | 2.0 |
| veterinaria | 41 | 1.7 |
| cerrajeria | 38 | 1.6 |
| spa | 31 | 1.3 |
| laboratorio_clinico | 30 | 1.2 |
| escuela_idiomas | 18 | 0.7 |
| sushi | 14 | 0.6 |
| guarderia | 9 | 0.4 |
| libreria | 6 | 0.2 |
| comida_china | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 2 | 7,526 | 2,483 | medio |
| EL CÁRMEN | 1 | 2,598 | 962 | medio |
| SAN PEDRO | 1 | 4,399 | 809 | medio |
| SAN MIGUEL COATLINCHAN | 4 | 13,601 | 780 | bajo |
| SAN MIGUEL TOCUILA | 2 | 13,442 | 666 | bajo |
| SAN LUIS HUEXOTLA | 3 | 12,327 | 523 | medio |
| SAN JERONIMO AMANALCO | 4 | 7,719 | 516 | bajo |
| SAN MIGUEL TLAIXPAN | 6 | 7,824 | 472 | medio |
| SANTIAGO CUAUTLALPAN | 2 | 5,158 | 468 | medio |
| SAN BERNARDINO | 1 | 8,537 | 458 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN SEBASTIAN | 3,714 | 8.3 |
| LOMAS DE CRISTO | 3,722 | 8.1 |
| ISSSTE | 3,205 | 7.6 |
| NIÑOS HÉROES | 4,755 | 7.4 |
| SAN JUANITO | 4,801 | 7.2 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| VICTOR PUEBLA | 9,641 | 2.6 |
| VICENTE RIVA PALACIO | 3,251 | 3.0 |
| SAN MIGUEL TOCUILA | 13,442 | 3.0 |
| MONTECILLOS | 4,787 | 3.3 |
| SAN JERONIMO AMANALCO | 7,719 | 3.3 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 440.3 millones de pesos por trimestre.
- Por hogar: 7,011 pesos por trimestre (lugar 25 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
