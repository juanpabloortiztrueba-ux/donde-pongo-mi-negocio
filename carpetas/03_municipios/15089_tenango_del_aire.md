# Ficha de municipio: Tenango del Aire (Estado de México), clave 15089

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 6,426 habitantes (lugar 72 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 1,644. AGEB urbanas: 7. Superficie urbana de esas AGEB: 1.8 km².
- Densidad: 3,492 hab/km² (lugar 54 de 76).
- Edad: 0-14 años 25.8 %; 15-24 16.1 %; 25-59 46.0 %; 60 o más 11.6 %.
- Escolaridad promedio de la población de 15 y más: 10.0 años (lugar 47 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 32.9 %; con internet: 41.9 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 93.5 %, medio 6.5 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 56.9 %; Medio 41.1 %; Alto 1.9 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 602 (93.7 por cada 1 000 habitantes, lugar 10 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 487. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 1,823.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 313 | 52.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 79 | 13.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 56 | 9.3 % |
| 31 Industrias manufactureras | 42 | 7.0 % |
| 62 Servicios de salud y de asistencia social | 28 | 4.7 % |
| 61 Servicios educativos | 15 | 2.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 94 |
| 465311 | Comercio al por menor de artículos de papelería | 32 |
| 812110 | Salones y clínicas de belleza y peluquerías | 27 |
| 461122 | Comercio al por menor de carne de aves | 21 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 20 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 16 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 11 |
| 465912 | Comercio al por menor de regalos | 11 |
| 461140 | Comercio al por menor de semillas y granos alimenticios, especias y chiles secos | 10 |
| 311812 | Panificación tradicional | 9 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 98 | 152.5 |
| papeleria | 32 | 49.8 |
| carniceria | 30 | 46.7 |
| barberia_estetica | 27 | 42.0 |
| tortilleria | 20 | 31.1 |
| tienda_ropa | 16 | 24.9 |
| farmacia | 13 | 20.2 |
| cafeteria | 11 | 17.1 |
| fonda | 10 | 15.6 |
| fruteria | 9 | 14.0 |
| panaderia | 9 | 14.0 |
| ferreteria | 8 | 12.4 |
| consultorio_dental | 7 | 10.9 |
| taller_mecanico | 7 | 10.9 |
| consultorio_medico | 6 | 9.3 |
| cafe_internet | 6 | 9.3 |
| heladeria | 6 | 9.3 |
| taqueria | 6 | 9.3 |
| pasteleria | 5 | 7.8 |
| bar | 5 | 7.8 |
| veterinaria | 5 | 7.8 |
| lavanderia | 5 | 7.8 |
| purificadora | 4 | 6.2 |
| guarderia | 3 | 4.7 |
| tienda_mascotas | 3 | 4.7 |
| pizzeria | 3 | 4.7 |
| tienda_celulares | 2 | 3.1 |
| gimnasio | 2 | 3.1 |
| cerrajeria | 1 | 1.6 |
| floreria | 1 | 1.6 |
| sushi | 0 | 0.0 |
| laboratorio_clinico | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| zapateria | 0 | 0.0 |
| libreria | 0 | 0.0 |
| optica | 0 | 0.0 |
| spa | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| LA PALMA | 2 | 2,220 | 211 | bajo |
| SAN MATEO | 3 | 2,054 | 140 | bajo |
| SAN MIGUEL | 1 | 2,088 | 70 | bajo |
| Tenango del Aire | 1 | 64 | 0 | medio |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 8.0 millones de pesos por trimestre.
- Por hogar: 4,877 pesos por trimestre (lugar 63 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
