# Ficha de municipio: Ixtapaluca (Estado de México), clave 15039

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 524,818 habitantes (lugar 14 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 142,615. AGEB urbanas: 163. Superficie urbana de esas AGEB: 54.6 km².
- Densidad: 9,621 hab/km² (lugar 21 de 76).
- Edad: 0-14 años 23.9 %; 15-24 18.2 %; 25-59 48.9 %; 60 o más 8.9 %.
- Escolaridad promedio de la población de 15 y más: 10.1 años (lugar 40 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 36.5 %; con internet: 61.5 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 52.8 %, medio 46.9 %, alto 0.3 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 8.3 %; Bajo 35.0 %; Medio 32.4 %; Alto 16.5 %; Muy alto 7.8 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 25,610 (48.8 por cada 1 000 habitantes, lugar 54 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 21,272. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 95,582.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 13,247 | 51.7 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,880 | 15.2 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,981 | 11.6 % |
| 31 Industrias manufactureras | 1,292 | 5.0 % |
| 62 Servicios de salud y de asistencia social | 851 | 3.3 % |
| 61 Servicios educativos | 732 | 2.9 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 3,565 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,575 |
| 465311 | Comercio al por menor de artículos de papelería | 1,120 |
| 467115 | Comercio al por menor de artículos para la limpieza | 668 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 641 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 622 |
| 464111 | Farmacias sin minisúper | 598 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 588 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 572 |
| 461122 | Comercio al por menor de carne de aves | 568 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 3,665 | 69.8 |
| barberia_estetica | 1,575 | 30.0 |
| papeleria | 1,120 | 21.3 |
| carniceria | 868 | 16.5 |
| fruteria | 641 | 12.2 |
| farmacia | 640 | 12.2 |
| tienda_ropa | 572 | 10.9 |
| fonda | 520 | 9.9 |
| taller_mecanico | 467 | 8.9 |
| cafeteria | 457 | 8.7 |
| ferreteria | 442 | 8.4 |
| taqueria | 419 | 8.0 |
| tortilleria | 406 | 7.7 |
| panaderia | 329 | 6.3 |
| consultorio_dental | 281 | 5.4 |
| purificadora | 262 | 5.0 |
| heladeria | 182 | 3.5 |
| cafe_internet | 180 | 3.4 |
| lavanderia | 171 | 3.3 |
| gimnasio | 137 | 2.6 |
| tienda_mascotas | 134 | 2.6 |
| tienda_celulares | 122 | 2.3 |
| consultorio_medico | 116 | 2.2 |
| floreria | 114 | 2.2 |
| veterinaria | 111 | 2.1 |
| pizzeria | 102 | 1.9 |
| bar | 98 | 1.9 |
| zapateria | 93 | 1.8 |
| optica | 68 | 1.3 |
| pasteleria | 59 | 1.1 |
| cerrajeria | 56 | 1.1 |
| spa | 45 | 0.9 |
| laboratorio_clinico | 20 | 0.4 |
| sushi | 16 | 0.3 |
| guarderia | 15 | 0.3 |
| comida_china | 11 | 0.2 |
| escuela_idiomas | 10 | 0.2 |
| libreria | 6 | 0.1 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN BUENAVENTURA | 12 | 49,241 | 1,564 | medio |
| CENTRO | 3 | 12,587 | 1,431 | medio |
| GEOVILLAS DE SANTA BARBARA | 3 | 34,120 | 1,182 | medio |
| SAN JERONIMO | 6 | 38,350 | 1,177 | bajo |
| ALFREDO DEL MAZO | 4 | 18,342 | 1,125 | bajo |
| TEJALPA | 6 | 17,808 | 1,057 | bajo |
| SANTA BARBARA | 5 | 19,438 | 1,031 | medio |
| AYOTLA | 3 | 11,430 | 992 | medio |
| LA VENTA | 2 | 6,282 | 875 | medio |
| EL MOLINO | 4 | 17,638 | 846 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| GEOVILLAS DE SANTA BARBARA | 34,120 | 7.1 |
| LA VENTA | 6,282 | 6.7 |
| ROSA DE SAN FRANCISCO | 4,171 | 6.7 |
| ARBOLADA | 8,638 | 6.4 |
| SAN BUENAVENTURA | 49,241 | 6.4 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| AMPLIACION ACOZAC | 3,529 | 2.1 |
| MANUEL AVILA CAMACHO | 3,478 | 2.1 |
| REY IZCOATL | 7,293 | 2.2 |
| 6 DE JUNIO | 5,023 | 2.2 |
| EL MIRADOR | 4,622 | 2.6 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 893.7 millones de pesos por trimestre.
- Por hogar: 6,267 pesos por trimestre (lugar 32 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
