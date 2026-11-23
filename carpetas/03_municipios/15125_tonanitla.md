# Ficha de municipio: Tonanitla (Estado de México), clave 15125

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 9,516 habitantes (lugar 68 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 2,512. AGEB urbanas: 5. Superficie urbana de esas AGEB: 2.4 km².
- Densidad: 3,975 hab/km² (lugar 50 de 76).
- Edad: 0-14 años 26.6 %; 15-24 15.3 %; 25-59 49.1 %; 60 o más 9.1 %.
- Escolaridad promedio de la población de 15 y más: 10.8 años (lugar 21 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 55.1 %; con internet: 56.1 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 72.7 %, medio 0.0 %, alto 27.3 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 27.3 %; Alto 61.9 %; Muy alto 10.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 724 (76.1 por cada 1 000 habitantes, lugar 14 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 515. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 2,270.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 335 | 46.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 100 | 13.8 % |
| 81 Otros servicios excepto actividades gubernamentales | 90 | 12.4 % |
| 31 Industrias manufactureras | 56 | 7.7 % |
| 93 Actividades legislativas, gubernamentales, de impartición de justicia y de organismos internacionales y extraterritoriales | 35 | 4.8 % |
| 33 Industrias manufactureras | 25 | 3.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 76 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 26 |
| 812110 | Salones y clínicas de belleza y peluquerías | 26 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 25 |
| 931210 | Administración pública en general | 24 |
| 465311 | Comercio al por menor de artículos de papelería | 22 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 19 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 18 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 17 |
| 722519 | Servicios de preparación de otros alimentos para consumo inmediato | 15 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 81 | 85.1 |
| barberia_estetica | 26 | 27.3 |
| tortilleria | 25 | 26.3 |
| papeleria | 22 | 23.1 |
| taller_mecanico | 19 | 20.0 |
| fruteria | 19 | 20.0 |
| tienda_ropa | 18 | 18.9 |
| carniceria | 18 | 18.9 |
| fonda | 17 | 17.9 |
| farmacia | 15 | 15.8 |
| taqueria | 14 | 14.7 |
| ferreteria | 14 | 14.7 |
| purificadora | 14 | 14.7 |
| cafeteria | 13 | 13.7 |
| floreria | 8 | 8.4 |
| cafe_internet | 8 | 8.4 |
| panaderia | 7 | 7.4 |
| bar | 7 | 7.4 |
| tienda_celulares | 6 | 6.3 |
| consultorio_dental | 4 | 4.2 |
| consultorio_medico | 4 | 4.2 |
| lavanderia | 3 | 3.2 |
| tienda_mascotas | 3 | 3.2 |
| heladeria | 2 | 2.1 |
| zapateria | 2 | 2.1 |
| spa | 2 | 2.1 |
| pizzeria | 2 | 2.1 |
| laboratorio_clinico | 1 | 1.1 |
| gimnasio | 1 | 1.1 |
| veterinaria | 1 | 1.1 |
| optica | 1 | 1.1 |
| pasteleria | 1 | 1.1 |
| escuela_idiomas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| libreria | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| cerrajeria | 0 | 0.0 |
| guarderia | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 1 | 2,686 | 430 | bajo |
| SANTA MARIA | 1 | 3,209 | 204 | bajo |
| LA CONCEPCION | 1 | 1,020 | 77 | bajo |
| VILLAS D TONANITLA | 1 | 1,028 | 6 | alto |
| VILLAS DE TONANITLA | 1 | 1,573 | 6 | alto |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 21.0 millones de pesos por trimestre.
- Por hogar: 8,377 pesos por trimestre (lugar 14 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
