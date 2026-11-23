# Ficha de municipio: Tepotzotlán (Estado de México), clave 15095

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 82,053 habitantes (lugar 41 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 21,505. AGEB urbanas: 34. Superficie urbana de esas AGEB: 33.0 km².
- Densidad: 2,489 hab/km² (lugar 61 de 76).
- Edad: 0-14 años 23.4 %; 15-24 17.0 %; 25-59 48.1 %; 60 o más 11.5 %.
- Escolaridad promedio de la población de 15 y más: 10.0 años (lugar 46 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 46.7 %; con internet: 55.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 47.9 %, medio 52.1 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 36.3 %; Medio 48.8 %; Alto 14.8 %; Muy alto 0.1 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 5,280 (64.3 por cada 1 000 habitantes, lugar 28 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 4,597. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 37,906.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 2,444 | 46.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 773 | 14.6 % |
| 81 Otros servicios excepto actividades gubernamentales | 739 | 14.0 % |
| 31 Industrias manufactureras | 210 | 4.0 % |
| 62 Servicios de salud y de asistencia social | 163 | 3.1 % |
| 43 Comercio al por mayor | 130 | 2.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 672 |
| 812110 | Salones y clínicas de belleza y peluquerías | 265 |
| 465311 | Comercio al por menor de artículos de papelería | 184 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 169 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 148 |
| 467115 | Comercio al por menor de artículos para la limpieza | 126 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 113 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 95 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 94 |
| 722511 | Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida | 91 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 698 | 85.1 |
| barberia_estetica | 265 | 32.3 |
| papeleria | 184 | 22.4 |
| fonda | 150 | 18.3 |
| tienda_ropa | 148 | 18.0 |
| carniceria | 148 | 18.0 |
| taller_mecanico | 125 | 15.2 |
| fruteria | 95 | 11.6 |
| cafeteria | 94 | 11.5 |
| ferreteria | 85 | 10.4 |
| farmacia | 84 | 10.2 |
| taqueria | 82 | 10.0 |
| tortilleria | 75 | 9.1 |
| consultorio_dental | 56 | 6.8 |
| panaderia | 53 | 6.5 |
| cafe_internet | 51 | 6.2 |
| heladeria | 38 | 4.6 |
| purificadora | 34 | 4.1 |
| floreria | 28 | 3.4 |
| lavanderia | 27 | 3.3 |
| consultorio_medico | 26 | 3.2 |
| bar | 25 | 3.0 |
| gimnasio | 24 | 2.9 |
| zapateria | 24 | 2.9 |
| tienda_mascotas | 23 | 2.8 |
| tienda_celulares | 20 | 2.4 |
| pizzeria | 19 | 2.3 |
| pasteleria | 18 | 2.2 |
| veterinaria | 14 | 1.7 |
| cerrajeria | 9 | 1.1 |
| optica | 8 | 1.0 |
| laboratorio_clinico | 8 | 1.0 |
| spa | 5 | 0.6 |
| comida_china | 1 | 0.1 |
| sushi | 1 | 0.1 |
| escuela_idiomas | 1 | 0.1 |
| libreria | 1 | 0.1 |
| coworking | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| RICARDO FLORES MAGON | 4 | 12,875 | 693 | medio |
| SAN MATEO XOLOC | 4 | 10,787 | 675 | medio |
| SAN MARTIN | 2 | 3,978 | 657 | medio |
| TEXCACOAC | 2 | 3,113 | 551 | medio |
| SANTA CRUZ DEL MONTE | 2 | 7,463 | 356 | bajo |
| SANTIAGO | 3 | 8,496 | 309 | bajo |
| CAPULA | 1 | 4,295 | 293 | medio |
| CAÑADA DE CISNEROS | 1 | 3,966 | 265 | bajo |
| LAS ANIMAS | 2 | 3,209 | 243 | bajo |
| EL TREBOL | 3 | 7,269 | 220 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN MARTIN | 3,978 | 6.8 |
| CAPULA | 4,295 | 6.3 |
| TEXCACOAC | 3,113 | 6.3 |
| EL TREBOL | 7,269 | 6.2 |
| LA LUZ | 3,519 | 5.2 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SANTA CRUZ DEL MONTE | 7,463 | 3.5 |
| SANTIAGO | 8,496 | 3.6 |
| CAÑADA DE CISNEROS | 3,966 | 3.9 |
| SANTIAGO CENTRO | 3,057 | 4.0 |
| SAN JOSE | 4,323 | 4.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 135.5 millones de pesos por trimestre.
- Por hogar: 6,302 pesos por trimestre (lugar 31 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
