# Ficha de municipio: Papalotla (Estado de México), clave 15069

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 4,784 habitantes (lugar 74 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 1,215. AGEB urbanas: 3. Superficie urbana de esas AGEB: 2.2 km².
- Densidad: 2,207 hab/km² (lugar 64 de 76).
- Edad: 0-14 años 24.0 %; 15-24 17.4 %; 25-59 46.9 %; 60 o más 11.6 %.
- Escolaridad promedio de la población de 15 y más: 10.8 años (lugar 22 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 53.2 %; con internet: 65.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 0.0 %, medio 100.0 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 100.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 355 (74.2 por cada 1 000 habitantes, lugar 20 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 279. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 1,569.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 145 | 40.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 54 | 15.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 49 | 13.8 % |
| 31 Industrias manufactureras | 32 | 9.0 % |
| 62 Servicios de salud y de asistencia social | 16 | 4.5 % |
| 61 Servicios educativos | 11 | 3.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 48 |
| 812110 | Salones y clínicas de belleza y peluquerías | 15 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 14 |
| 465311 | Comercio al por menor de artículos de papelería | 12 |
| 722517 | Restaurantes con servicio de preparación de pizzas, hamburguesas, hot dogs y pollos rostizados para llevar | 12 |
| 311812 | Panificación tradicional | 11 |
| 465912 | Comercio al por menor de regalos | 11 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 8 |
| 461122 | Comercio al por menor de carne de aves | 7 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 7 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 48 | 100.3 |
| barberia_estetica | 15 | 31.4 |
| carniceria | 14 | 29.3 |
| papeleria | 12 | 25.1 |
| fonda | 12 | 25.1 |
| panaderia | 11 | 23.0 |
| taller_mecanico | 9 | 18.8 |
| tortilleria | 8 | 16.7 |
| farmacia | 8 | 16.7 |
| cafeteria | 7 | 14.6 |
| tienda_ropa | 6 | 12.5 |
| fruteria | 6 | 12.5 |
| pizzeria | 4 | 8.4 |
| heladeria | 4 | 8.4 |
| taqueria | 4 | 8.4 |
| lavanderia | 4 | 8.4 |
| ferreteria | 3 | 6.3 |
| consultorio_dental | 2 | 4.2 |
| cafe_internet | 2 | 4.2 |
| purificadora | 2 | 4.2 |
| tienda_celulares | 2 | 4.2 |
| pasteleria | 2 | 4.2 |
| cerrajeria | 1 | 2.1 |
| consultorio_medico | 1 | 2.1 |
| veterinaria | 1 | 2.1 |
| spa | 1 | 2.1 |
| laboratorio_clinico | 1 | 2.1 |
| floreria | 1 | 2.1 |
| gimnasio | 1 | 2.1 |
| coworking | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| bar | 0 | 0.0 |
| sushi | 0 | 0.0 |
| libreria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| tienda_mascotas | 0 | 0.0 |
| zapateria | 0 | 0.0 |
| optica | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| BELEM | 1 | 2,969 | 261 | medio |
| COXOTLA | 1 | 1,658 | 88 | medio |
| MAZATLA | 1 | 157 | 6 | medio |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 9.2 millones de pesos por trimestre.
- Por hogar: 7,601 pesos por trimestre (lugar 23 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
