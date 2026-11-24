# Ficha de municipio: Axapusco (Estado de México), clave 15016

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 16,627 habitantes (lugar 64 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 4,453. AGEB urbanas: 22. Superficie urbana de esas AGEB: 9.2 km².
- Densidad: 1,815 hab/km² (lugar 71 de 76).
- Edad: 0-14 años 25.8 %; 15-24 17.2 %; 25-59 44.5 %; 60 o más 12.0 %.
- Escolaridad promedio de la población de 15 y más: 9.2 años (lugar 67 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 43.9 %; con internet: 39.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 99.2 %, medio 0.4 %, alto 0.0 %, sin estimación 0.3 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 9.2 %; Medio 52.9 %; Alto 37.9 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,398 (84.1 por cada 1 000 habitantes, lugar 11 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 968. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 5,004.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 679 | 48.6 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 188 | 13.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 172 | 12.3 % |
| 31 Industrias manufactureras | 89 | 6.4 % |
| 62 Servicios de salud y de asistencia social | 56 | 4.0 % |
| 61 Servicios educativos | 36 | 2.6 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 202 |
| 812110 | Salones y clínicas de belleza y peluquerías | 58 |
| 465311 | Comercio al por menor de artículos de papelería | 48 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 34 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 33 |
| 461122 | Comercio al por menor de carne de aves | 32 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 30 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 30 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 27 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 26 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 207 | 124.5 |
| barberia_estetica | 58 | 34.9 |
| papeleria | 48 | 28.9 |
| carniceria | 46 | 27.7 |
| tienda_ropa | 34 | 20.4 |
| cafeteria | 33 | 19.8 |
| taqueria | 30 | 18.0 |
| fonda | 29 | 17.4 |
| tortilleria | 28 | 16.8 |
| farmacia | 26 | 15.6 |
| fruteria | 25 | 15.0 |
| taller_mecanico | 22 | 13.2 |
| bar | 19 | 11.4 |
| ferreteria | 19 | 11.4 |
| panaderia | 18 | 10.8 |
| consultorio_dental | 14 | 8.4 |
| zapateria | 14 | 8.4 |
| heladeria | 11 | 6.6 |
| purificadora | 10 | 6.0 |
| floreria | 10 | 6.0 |
| cafe_internet | 8 | 4.8 |
| tienda_celulares | 8 | 4.8 |
| lavanderia | 7 | 4.2 |
| pizzeria | 6 | 3.6 |
| pasteleria | 6 | 3.6 |
| gimnasio | 6 | 3.6 |
| consultorio_medico | 5 | 3.0 |
| tienda_mascotas | 5 | 3.0 |
| veterinaria | 3 | 1.8 |
| spa | 2 | 1.2 |
| laboratorio_clinico | 2 | 1.2 |
| cerrajeria | 2 | 1.2 |
| optica | 1 | 0.6 |
| comida_china | 1 | 0.6 |
| guarderia | 1 | 0.6 |
| renta_bicicletas | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |
| libreria | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| AXAPUSCO | 3 | 3,802 | 447 | bajo |
| JALTEPEC | 7 | 5,578 | 332 | bajo |
| SANTA MARIA ACTIPAC | 8 | 3,754 | 319 | bajo |
| SANTO DOMINGO AZTACAMECA | 2 | 3,413 | 288 | bajo |
| Santa María Actipac | 2 | 80 | 0 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 20.5 millones de pesos por trimestre.
- Por hogar: 4,630 pesos por trimestre (lugar 65 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
