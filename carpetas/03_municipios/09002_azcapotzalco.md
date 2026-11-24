# Ficha de alcaldía: Azcapotzalco (Ciudad de México), clave 09002

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 432,205 habitantes (lugar 19 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 134,167. AGEB urbanas: 103. Superficie urbana de esas AGEB: 33.3 km².
- Densidad: 12,970 hab/km² (lugar 13 de 76).
- Edad: 0-14 años 16.3 %; 15-24 13.8 %; 25-59 51.7 %; 60 o más 18.2 %.
- Escolaridad promedio de la población de 15 y más: 11.9 años (lugar 5 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 48.1 %; con internet: 79.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 61.6 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 4.3 %, medio 88.9 %, alto 6.7 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 7.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 27.6 %; Bajo 65.5 %; Medio 6.5 %; Alto 0.4 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 18,815 (43.5 por cada 1 000 habitantes, lugar 62 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 19,445. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 169,558.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 7,715 | 41.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 2,898 | 15.4 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,740 | 14.6 % |
| 62 Servicios de salud y de asistencia social | 915 | 4.9 % |
| 43 Comercio al por mayor | 850 | 4.5 % |
| 31 Industrias manufactureras | 761 | 4.0 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,472 |
| 812110 | Salones y clínicas de belleza y peluquerías | 955 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 496 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 495 |
| 465311 | Comercio al por menor de artículos de papelería | 486 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 465 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 454 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 439 |
| 461122 | Comercio al por menor de carne de aves | 365 |
| 461121 | Comercio al por menor de carnes rojas | 352 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,626 | 37.6 |
| barberia_estetica | 955 | 22.1 |
| carniceria | 717 | 16.6 |
| taqueria | 495 | 11.5 |
| papeleria | 486 | 11.2 |
| fonda | 476 | 11.0 |
| taller_mecanico | 466 | 10.8 |
| fruteria | 465 | 10.8 |
| cafeteria | 439 | 10.2 |
| consultorio_dental | 351 | 8.1 |
| tienda_ropa | 343 | 7.9 |
| farmacia | 296 | 6.8 |
| tortilleria | 270 | 6.2 |
| ferreteria | 254 | 5.9 |
| lavanderia | 249 | 5.8 |
| consultorio_medico | 167 | 3.9 |
| panaderia | 163 | 3.8 |
| tienda_mascotas | 132 | 3.1 |
| purificadora | 129 | 3.0 |
| cafe_internet | 117 | 2.7 |
| tienda_celulares | 111 | 2.6 |
| veterinaria | 107 | 2.5 |
| heladeria | 102 | 2.4 |
| optica | 87 | 2.0 |
| zapateria | 76 | 1.8 |
| gimnasio | 75 | 1.7 |
| floreria | 72 | 1.7 |
| cerrajeria | 58 | 1.3 |
| pasteleria | 45 | 1.0 |
| pizzeria | 43 | 1.0 |
| bar | 36 | 0.8 |
| spa | 34 | 0.8 |
| laboratorio_clinico | 34 | 0.8 |
| sushi | 26 | 0.6 |
| libreria | 14 | 0.3 |
| guarderia | 14 | 0.3 |
| comida_china | 13 | 0.3 |
| escuela_idiomas | 8 | 0.2 |
| renta_bicicletas | 2 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO DE AZCAPOTZALCO | 2 | 8,369 | 1,221 | medio |
| PRO HOGAR | 3 | 12,348 | 1,096 | medio |
| INDUSTRIAL VALLEJO | 2 | 1,221 | 1,070 | bajo |
| EL ROSARIO | 8 | 28,453 | 1,066 | medio |
| AMPLIACIÓN SAN PEDRO XALPA | 4 | 19,496 | 833 | bajo |
| NUEVA SANTA MARÍA | 5 | 13,437 | 749 | alto |
| SANTA BÁRBARA | 3 | 13,399 | 650 | medio |
| PASTEROS | 2 | 20,059 | 647 | medio |
| CLAVERÍA | 3 | 7,092 | 610 | alto |
| DEL RECREO | 2 | 12,800 | 476 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| CLAVERÍA | 7,092 | 8.3 |
| PRADOS DEL ROSARIO | 5,082 | 8.2 |
| IGNACIO ALLENDE | 6,915 | 8.0 |
| SAN PEDRO XALPA | 12,035 | 7.8 |
| NUEVA SANTA MARÍA | 13,437 | 7.8 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| AMPLIACIÓN SAN PEDRO XALPA | 19,496 | 4.5 |
| COLTONGO | 5,207 | 4.9 |
| SANTA LUCIA | 6,499 | 5.2 |
| SANTIAGO AHUIZOTLA | 12,855 | 5.2 |
| ALDANA | 3,168 | 5.5 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,229.3 millones de pesos por trimestre.
- Por hogar: 9,163 pesos por trimestre (lugar 10 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
