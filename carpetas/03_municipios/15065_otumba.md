# Ficha de municipio: Otumba (Estado de México), clave 15065

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 22,649 habitantes (lugar 59 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 5,977. AGEB urbanas: 18. Superficie urbana de esas AGEB: 11.8 km².
- Densidad: 1,921 hab/km² (lugar 68 de 76).
- Edad: 0-14 años 25.9 %; 15-24 17.4 %; 25-59 45.5 %; 60 o más 11.0 %.
- Escolaridad promedio de la población de 15 y más: 9.5 años (lugar 62 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 53.7 %; con internet: 37.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 85.0 %, medio 15.0 %, alto 0.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 12.7 %; Medio 31.2 %; Alto 55.0 %; Muy alto 1.1 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 2,157 (95.2 por cada 1 000 habitantes, lugar 9 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,630. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 7,758.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,077 | 49.9 % |
| 81 Otros servicios excepto actividades gubernamentales | 279 | 12.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 228 | 10.6 % |
| 31 Industrias manufactureras | 167 | 7.7 % |
| 62 Servicios de salud y de asistencia social | 96 | 4.5 % |
| 43 Comercio al por mayor | 51 | 2.4 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 250 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 108 |
| 812110 | Salones y clínicas de belleza y peluquerías | 91 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 82 |
| 465311 | Comercio al por menor de artículos de papelería | 52 |
| 461122 | Comercio al por menor de carne de aves | 52 |
| 311614 | Elaboración de manteca y otras grasas animales comestibles | 48 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 43 |
| 461121 | Comercio al por menor de carnes rojas | 40 |
| 464111 | Farmacias sin minisúper | 39 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 257 | 113.5 |
| fruteria | 108 | 47.7 |
| carniceria | 92 | 40.6 |
| barberia_estetica | 91 | 40.2 |
| tienda_ropa | 82 | 36.2 |
| papeleria | 52 | 23.0 |
| farmacia | 45 | 19.9 |
| taller_mecanico | 44 | 19.4 |
| taqueria | 39 | 17.2 |
| fonda | 36 | 15.9 |
| tortilleria | 33 | 14.6 |
| ferreteria | 31 | 13.7 |
| cafeteria | 29 | 12.8 |
| consultorio_dental | 27 | 11.9 |
| panaderia | 20 | 8.8 |
| zapateria | 19 | 8.4 |
| tienda_celulares | 19 | 8.4 |
| consultorio_medico | 18 | 7.9 |
| cafe_internet | 16 | 7.1 |
| floreria | 14 | 6.2 |
| lavanderia | 14 | 6.2 |
| heladeria | 11 | 4.9 |
| gimnasio | 11 | 4.9 |
| bar | 11 | 4.9 |
| laboratorio_clinico | 8 | 3.5 |
| purificadora | 8 | 3.5 |
| tienda_mascotas | 6 | 2.6 |
| pizzeria | 6 | 2.6 |
| pasteleria | 5 | 2.2 |
| optica | 4 | 1.8 |
| cerrajeria | 4 | 1.8 |
| veterinaria | 4 | 1.8 |
| spa | 3 | 1.3 |
| comida_china | 2 | 0.9 |
| sushi | 2 | 0.9 |
| guarderia | 2 | 0.9 |
| escuela_idiomas | 1 | 0.4 |
| coworking | 0 | 0.0 |
| libreria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| OTUMBA | 2 | 2,338 | 813 | bajo |
| SANTIAGO TOLMAN | 2 | 5,369 | 404 | bajo |
| OXTOTIPAC | 3 | 3,572 | 270 | bajo |
| OTUMBA DE GOMEZ FARIAS | 1 | 3,502 | 266 | bajo |
| CUAUTLANCINGO | 3 | 3,744 | 193 | bajo |
| CENTRO | 1 | 2,336 | 126 | medio |
| SAN COSME | 2 | 1,640 | 73 | bajo |
| PABELLON | 1 | 109 | 7 | bajo |
| Cuautlacingo | 2 | 37 | 0 | medio |
| Oxtotipac | 1 | 2 | 0 | NO ENCONTRADO |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 30.2 millones de pesos por trimestre.
- Por hogar: 5,056 pesos por trimestre (lugar 56 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
