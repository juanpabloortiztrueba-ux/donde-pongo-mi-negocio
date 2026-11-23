# Ficha de municipio: Isidro Fabela (Estado de México), clave 15038

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 2,399 habitantes (lugar 76 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 593. AGEB urbanas: 1. Superficie urbana de esas AGEB: 1.1 km².
- Densidad: 2,121 hab/km² (lugar 66 de 76).
- Edad: 0-14 años 24.6 %; 15-24 17.0 %; 25-59 45.8 %; 60 o más 12.6 %.
- Escolaridad promedio de la población de 15 y más: 9.6 años (lugar 59 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 45.3 %; con internet: 54.2 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 100.0 %, medio 0.0 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 100.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 400 (166.7 por cada 1 000 habitantes, lugar 2 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 328. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 1,370.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 185 | 46.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 59 | 14.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 59 | 14.8 % |
| 31 Industrias manufactureras | 14 | 3.5 % |
| 62 Servicios de salud y de asistencia social | 13 | 3.2 % |
| 43 Comercio al por mayor | 11 | 2.8 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 40 |
| 812110 | Salones y clínicas de belleza y peluquerías | 24 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 20 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 15 |
| 465912 | Comercio al por menor de regalos | 13 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 12 |
| 467115 | Comercio al por menor de artículos para la limpieza | 10 |
| 465311 | Comercio al por menor de artículos de papelería | 8 |
| 464111 | Farmacias sin minisúper | 8 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 8 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 41 | 170.9 |
| barberia_estetica | 24 | 100.0 |
| tienda_ropa | 20 | 83.4 |
| cafeteria | 15 | 62.5 |
| carniceria | 14 | 58.4 |
| taqueria | 12 | 50.0 |
| fonda | 10 | 41.7 |
| farmacia | 8 | 33.3 |
| papeleria | 8 | 33.3 |
| fruteria | 7 | 29.2 |
| tortilleria | 7 | 29.2 |
| panaderia | 6 | 25.0 |
| consultorio_dental | 5 | 20.8 |
| ferreteria | 5 | 20.8 |
| taller_mecanico | 5 | 20.8 |
| gimnasio | 4 | 16.7 |
| floreria | 4 | 16.7 |
| cafe_internet | 4 | 16.7 |
| zapateria | 3 | 12.5 |
| heladeria | 3 | 12.5 |
| tienda_celulares | 3 | 12.5 |
| bar | 2 | 8.3 |
| pizzeria | 2 | 8.3 |
| tienda_mascotas | 2 | 8.3 |
| spa | 1 | 4.2 |
| lavanderia | 1 | 4.2 |
| pasteleria | 1 | 4.2 |
| guarderia | 1 | 4.2 |
| cerrajeria | 1 | 4.2 |
| escuela_idiomas | 0 | 0.0 |
| libreria | 0 | 0.0 |
| purificadora | 0 | 0.0 |
| veterinaria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |
| consultorio_medico | 0 | 0.0 |
| laboratorio_clinico | 0 | 0.0 |
| optica | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| MIRAFLORES | 1 | 2,399 | 391 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 3.4 millones de pesos por trimestre.
- Por hogar: 5,731 pesos por trimestre (lugar 43 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
