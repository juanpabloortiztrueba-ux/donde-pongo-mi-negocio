# Ficha de municipio: Jilotzingo (Estado de México), clave 15046

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 8,923 habitantes (lugar 69 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 2,232. AGEB urbanas: 3. Superficie urbana de esas AGEB: 4.7 km².
- Densidad: 1,881 hab/km² (lugar 69 de 76).
- Edad: 0-14 años 26.6 %; 15-24 17.2 %; 25-59 46.3 %; 60 o más 10.0 %.
- Escolaridad promedio de la población de 15 y más: 9.4 años (lugar 63 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 39.6 %; con internet: 43.9 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 100.0 %, medio 0.0 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 47.9 %; Alto 52.1 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 645 (72.3 por cada 1 000 habitantes, lugar 21 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 485. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 2,394.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 326 | 50.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 82 | 12.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 76 | 11.8 % |
| 61 Servicios educativos | 25 | 3.9 % |
| 62 Servicios de salud y de asistencia social | 22 | 3.4 % |
| 31 Industrias manufactureras | 21 | 3.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 91 |
| 465311 | Comercio al por menor de artículos de papelería | 36 |
| 812110 | Salones y clínicas de belleza y peluquerías | 29 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 20 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 16 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 16 |
| 464111 | Farmacias sin minisúper | 15 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 14 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 14 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 13 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 95 | 106.5 |
| papeleria | 36 | 40.3 |
| barberia_estetica | 29 | 32.5 |
| carniceria | 21 | 23.5 |
| tienda_ropa | 20 | 22.4 |
| farmacia | 16 | 17.9 |
| cafeteria | 14 | 15.7 |
| taqueria | 13 | 14.6 |
| tortilleria | 12 | 13.4 |
| taller_mecanico | 12 | 13.4 |
| fruteria | 9 | 10.1 |
| cafe_internet | 8 | 9.0 |
| ferreteria | 8 | 9.0 |
| consultorio_dental | 7 | 7.8 |
| heladeria | 6 | 6.7 |
| gimnasio | 6 | 6.7 |
| panaderia | 5 | 5.6 |
| tienda_celulares | 4 | 4.5 |
| floreria | 4 | 4.5 |
| fonda | 4 | 4.5 |
| consultorio_medico | 4 | 4.5 |
| zapateria | 4 | 4.5 |
| pizzeria | 3 | 3.4 |
| lavanderia | 3 | 3.4 |
| veterinaria | 3 | 3.4 |
| bar | 2 | 2.2 |
| purificadora | 2 | 2.2 |
| laboratorio_clinico | 1 | 1.1 |
| sushi | 1 | 1.1 |
| comida_china | 1 | 1.1 |
| escuela_idiomas | 1 | 1.1 |
| tienda_mascotas | 1 | 1.1 |
| cerrajeria | 1 | 1.1 |
| pasteleria | 1 | 1.1 |
| optica | 1 | 1.1 |
| spa | 0 | 0.0 |
| libreria | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| GRANDE | 1 | 4,275 | 291 | bajo |
| SANTA MARIA MAZATLA | 1 | 3,650 | 230 | bajo |
| SANTA ANA JILOTZINGO | 1 | 998 | 112 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 11.4 millones de pesos por trimestre.
- Por hogar: 5,094 pesos por trimestre (lugar 54 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
