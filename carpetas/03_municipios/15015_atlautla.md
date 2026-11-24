# Ficha de municipio: Atlautla (Estado de México), clave 15015

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 28,851 habitantes (lugar 54 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 6,685. AGEB urbanas: 20. Superficie urbana de esas AGEB: 8.8 km².
- Densidad: 3,279 hab/km² (lugar 57 de 76).
- Edad: 0-14 años 27.1 %; 15-24 17.7 %; 25-59 44.0 %; 60 o más 10.9 %.
- Escolaridad promedio de la población de 15 y más: 8.8 años (lugar 75 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 29.0 %; con internet: 19.9 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 99.9 %, medio 0.1 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 2.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Alto 62.8 %; Muy alto 37.2 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,709 (59.2 por cada 1 000 habitantes, lugar 35 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,421. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 5,590.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 914 | 53.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 198 | 11.6 % |
| 31 Industrias manufactureras | 189 | 11.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 162 | 9.5 % |
| 62 Servicios de salud y de asistencia social | 42 | 2.5 % |
| 43 Comercio al por mayor | 36 | 2.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 352 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 95 |
| 465311 | Comercio al por menor de artículos de papelería | 82 |
| 812110 | Salones y clínicas de belleza y peluquerías | 71 |
| 311812 | Panificación tradicional | 71 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 57 |
| 465912 | Comercio al por menor de regalos | 46 |
| 461122 | Comercio al por menor de carne de aves | 45 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 35 |
| 464111 | Farmacias sin minisúper | 34 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 355 | 123.0 |
| tortilleria | 95 | 32.9 |
| papeleria | 82 | 28.4 |
| carniceria | 72 | 25.0 |
| panaderia | 71 | 24.6 |
| barberia_estetica | 71 | 24.6 |
| fruteria | 57 | 19.8 |
| farmacia | 36 | 12.5 |
| tienda_ropa | 35 | 12.1 |
| fonda | 33 | 11.4 |
| taqueria | 27 | 9.4 |
| cafe_internet | 25 | 8.7 |
| cafeteria | 24 | 8.3 |
| ferreteria | 21 | 7.3 |
| taller_mecanico | 20 | 6.9 |
| tienda_mascotas | 15 | 5.2 |
| bar | 12 | 4.2 |
| consultorio_dental | 11 | 3.8 |
| pasteleria | 10 | 3.5 |
| floreria | 10 | 3.5 |
| heladeria | 9 | 3.1 |
| pizzeria | 9 | 3.1 |
| consultorio_medico | 8 | 2.8 |
| zapateria | 7 | 2.4 |
| gimnasio | 7 | 2.4 |
| tienda_celulares | 6 | 2.1 |
| purificadora | 6 | 2.1 |
| lavanderia | 5 | 1.7 |
| veterinaria | 2 | 0.7 |
| laboratorio_clinico | 2 | 0.7 |
| optica | 1 | 0.3 |
| renta_bicicletas | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| spa | 0 | 0.0 |
| libreria | 0 | 0.0 |
| cerrajeria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |
| guarderia | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN JACINTO | 1 | 2,907 | 308 | bajo |
| SAN BARTOLO | 1 | 3,750 | 265 | bajo |
| EL CENTRO | 1 | 3,734 | 262 | bajo |
| LA NATIVIDAD | 1 | 4,445 | 218 | bajo |
| SAN JUAN TEHUIXTITLAN | 1 | 3,202 | 213 | bajo |
| SAN JUAN TEPECOCULCO | 4 | 4,568 | 199 | bajo |
| SAN ANDRES TLALAMAC | 2 | 3,980 | 177 | bajo |
| CHAMIZAL | 1 | 488 | 21 | bajo |
| SAN FRANCISCO | 1 | 825 | 18 | bajo |
| SAN ANDRS TLALAMAC | 1 | 320 | 9 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN BARTOLO | 3,750 | 3.1 |
| LA NATIVIDAD | 4,445 | 2.8 |
| EL CENTRO | 3,734 | 2.7 |
| SAN JUAN TEHUIXTITLAN | 3,202 | 2.7 |
| SAN JUAN TEPECOCULCO | 4,568 | 2.5 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN ANDRES TLALAMAC | 3,980 | 2.0 |
| SAN JUAN TEPECOCULCO | 4,568 | 2.5 |
| SAN JUAN TEHUIXTITLAN | 3,202 | 2.7 |
| EL CENTRO | 3,734 | 2.7 |
| LA NATIVIDAD | 4,445 | 2.8 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 24.5 millones de pesos por trimestre.
- Por hogar: 3,664 pesos por trimestre (lugar 75 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
