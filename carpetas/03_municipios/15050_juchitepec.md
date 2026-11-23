# Ficha de municipio: Juchitepec (Estado de México), clave 15050

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 25,268 habitantes (lugar 57 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 6,425. AGEB urbanas: 12. Superficie urbana de esas AGEB: 3.3 km².
- Densidad: 7,649 hab/km² (lugar 26 de 76).
- Edad: 0-14 años 27.3 %; 15-24 17.6 %; 25-59 44.6 %; 60 o más 10.2 %.
- Escolaridad promedio de la población de 15 y más: 9.0 años (lugar 73 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 24.3 %; con internet: 30.3 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 100.0 %, medio 0.0 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 2.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 37.9 %; Alto 32.5 %; Muy alto 29.5 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,533 (60.7 por cada 1 000 habitantes, lugar 33 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,231. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 5,108.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 868 | 56.6 % |
| 81 Otros servicios excepto actividades gubernamentales | 180 | 11.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 152 | 9.9 % |
| 31 Industrias manufactureras | 90 | 5.9 % |
| 62 Servicios de salud y de asistencia social | 57 | 3.7 % |
| 43 Comercio al por mayor | 37 | 2.4 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 231 |
| 465311 | Comercio al por menor de artículos de papelería | 76 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 62 |
| 812110 | Salones y clínicas de belleza y peluquerías | 59 |
| 465912 | Comercio al por menor de regalos | 47 |
| 461140 | Comercio al por menor de semillas y granos alimenticios, especias y chiles secos | 46 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 45 |
| 461121 | Comercio al por menor de carnes rojas | 37 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 36 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 27 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 239 | 94.6 |
| papeleria | 76 | 30.1 |
| tienda_ropa | 62 | 24.5 |
| carniceria | 62 | 24.5 |
| barberia_estetica | 59 | 23.3 |
| fruteria | 45 | 17.8 |
| tortilleria | 36 | 14.2 |
| farmacia | 29 | 11.5 |
| cafeteria | 27 | 10.7 |
| taqueria | 26 | 10.3 |
| panaderia | 24 | 9.5 |
| fonda | 23 | 9.1 |
| taller_mecanico | 20 | 7.9 |
| ferreteria | 18 | 7.1 |
| cafe_internet | 15 | 5.9 |
| consultorio_medico | 14 | 5.5 |
| consultorio_dental | 14 | 5.5 |
| floreria | 11 | 4.4 |
| heladeria | 9 | 3.6 |
| pizzeria | 9 | 3.6 |
| gimnasio | 9 | 3.6 |
| tienda_celulares | 8 | 3.2 |
| zapateria | 8 | 3.2 |
| bar | 7 | 2.8 |
| purificadora | 7 | 2.8 |
| lavanderia | 7 | 2.8 |
| tienda_mascotas | 7 | 2.8 |
| pasteleria | 6 | 2.4 |
| laboratorio_clinico | 4 | 1.6 |
| spa | 2 | 0.8 |
| cerrajeria | 2 | 0.8 |
| veterinaria | 1 | 0.4 |
| optica | 1 | 0.4 |
| escuela_idiomas | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| libreria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| JUCHI | 2 | 7,391 | 719 | bajo |
| CALAYUCO | 2 | 5,325 | 267 | bajo |
| SANTA TERESA | 2 | 3,311 | 209 | bajo |
| SAGRADO CORAZON | 1 | 3,757 | 175 | bajo |
| CUAUHTZOZONGO | 1 | 3,658 | 100 | bajo |
| CUAUTZOTZONGO | 1 | 1,132 | 44 | bajo |
| SANTA CECILIA | 1 | 464 | 11 | bajo |
| SAN PEDRO | 1 | 181 | 5 | bajo |
| CALOYUCA | 1 | 49 | 1 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 24.0 millones de pesos por trimestre.
- Por hogar: 3,732 pesos por trimestre (lugar 74 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
