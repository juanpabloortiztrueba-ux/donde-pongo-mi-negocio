# Ficha de municipio: Huehuetoca (Estado de México), clave 15035

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 150,233 habitantes (lugar 39 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 43,166. AGEB urbanas: 58. Superficie urbana de esas AGEB: 23.3 km².
- Densidad: 6,460 hab/km² (lugar 34 de 76).
- Edad: 0-14 años 28.2 %; 15-24 17.6 %; 25-59 48.3 %; 60 o más 5.8 %.
- Escolaridad promedio de la población de 15 y más: 10.1 años (lugar 45 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 33.7 %; con internet: 49.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 83.9 %, medio 16.1 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 7.5 %; Bajo 46.6 %; Medio 45.9 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 5,883 (39.2 por cada 1 000 habitantes, lugar 73 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 4,385. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 24,078.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 3,096 | 52.6 % |
| 81 Otros servicios excepto actividades gubernamentales | 864 | 14.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 629 | 10.7 % |
| 31 Industrias manufactureras | 343 | 5.8 % |
| 61 Servicios educativos | 196 | 3.3 % |
| 62 Servicios de salud y de asistencia social | 188 | 3.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 996 |
| 812110 | Salones y clínicas de belleza y peluquerías | 362 |
| 465311 | Comercio al por menor de artículos de papelería | 355 |
| 467115 | Comercio al por menor de artículos para la limpieza | 185 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 163 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 126 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 115 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 111 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 110 |
| 464111 | Farmacias sin minisúper | 104 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,045 | 69.6 |
| barberia_estetica | 362 | 24.1 |
| papeleria | 355 | 23.6 |
| tortilleria | 163 | 10.8 |
| carniceria | 128 | 8.5 |
| farmacia | 120 | 8.0 |
| taller_mecanico | 119 | 7.9 |
| fruteria | 111 | 7.4 |
| tienda_ropa | 110 | 7.3 |
| fonda | 107 | 7.1 |
| cafeteria | 101 | 6.7 |
| ferreteria | 96 | 6.4 |
| taqueria | 89 | 5.9 |
| panaderia | 69 | 4.6 |
| consultorio_dental | 51 | 3.4 |
| purificadora | 51 | 3.4 |
| lavanderia | 46 | 3.1 |
| gimnasio | 46 | 3.1 |
| tienda_celulares | 41 | 2.7 |
| bar | 37 | 2.5 |
| heladeria | 36 | 2.4 |
| consultorio_medico | 34 | 2.3 |
| cafe_internet | 33 | 2.2 |
| floreria | 24 | 1.6 |
| zapateria | 22 | 1.5 |
| tienda_mascotas | 21 | 1.4 |
| optica | 17 | 1.1 |
| pizzeria | 16 | 1.1 |
| pasteleria | 14 | 0.9 |
| veterinaria | 14 | 0.9 |
| cerrajeria | 12 | 0.8 |
| laboratorio_clinico | 11 | 0.7 |
| spa | 7 | 0.5 |
| guarderia | 6 | 0.4 |
| comida_china | 2 | 0.1 |
| sushi | 1 | 0.1 |
| libreria | 1 | 0.1 |
| escuela_idiomas | 1 | 0.1 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 2 | 4,007 | 926 | medio |
| SALITRILLO | 3 | 7,699 | 639 | bajo |
| SANTA TERESA III | 2 | 13,639 | 483 | bajo |
| EX HACIENDA DE XALPA | 2 | 9,114 | 424 | bajo |
| CITARA | 12 | 12,303 | 358 | bajo |
| SAN BARTOLO | 3 | 8,024 | 341 | bajo |
| PUENTE GRANDE | 1 | 5,028 | 332 | bajo |
| SANTA TERESA IV | 2 | 8,220 | 263 | bajo |
| SANTA TERESA I | 1 | 7,140 | 251 | bajo |
| SANTA MARIA | 1 | 4,185 | 187 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| URBI VILLA DEL REY | 8,806 | 6.0 |
| PRIVADAS DEL VALLE | 3,733 | 5.0 |
| CENTRO | 4,007 | 4.9 |
| CITARA | 12,303 | 4.5 |
| EX HACIENDA DE XALPA | 9,114 | 4.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SANTA TERESA IV | 8,220 | 2.4 |
| EL DORADO | 5,223 | 2.6 |
| DORADO | 9,970 | 2.6 |
| SANTA TERESA VII | 4,154 | 2.8 |
| SANTA TERESA V | 4,394 | 2.8 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 215.8 millones de pesos por trimestre.
- Por hogar: 5,000 pesos por trimestre (lugar 59 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
