# Ficha de municipio: Apaxco (Estado de México), clave 15010

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 19,161 habitantes (lugar 61 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 4,993. AGEB urbanas: 15. Superficie urbana de esas AGEB: 6.9 km².
- Densidad: 2,778 hab/km² (lugar 60 de 76).
- Edad: 0-14 años 24.4 %; 15-24 16.4 %; 25-59 46.4 %; 60 o más 12.5 %.
- Escolaridad promedio de la población de 15 y más: 9.9 años (lugar 52 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 47.8 %; con internet: 43.3 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 77.9 %, medio 22.1 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 92.6 %; Alto 7.4 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 2,005 (104.6 por cada 1 000 habitantes, lugar 7 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,623. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 9,420.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 908 | 45.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 278 | 13.9 % |
| 81 Otros servicios excepto actividades gubernamentales | 270 | 13.5 % |
| 31 Industrias manufactureras | 137 | 6.8 % |
| 62 Servicios de salud y de asistencia social | 82 | 4.1 % |
| 33 Industrias manufactureras | 56 | 2.8 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 185 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 85 |
| 812110 | Salones y clínicas de belleza y peluquerías | 81 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 80 |
| 465311 | Comercio al por menor de artículos de papelería | 58 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 51 |
| 465912 | Comercio al por menor de regalos | 43 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 42 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 40 |
| 467115 | Comercio al por menor de artículos para la limpieza | 36 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 192 | 100.2 |
| tortilleria | 85 | 44.4 |
| barberia_estetica | 81 | 42.3 |
| tienda_ropa | 80 | 41.8 |
| papeleria | 58 | 30.3 |
| fonda | 58 | 30.3 |
| carniceria | 51 | 26.6 |
| taller_mecanico | 49 | 25.6 |
| cafeteria | 42 | 21.9 |
| taqueria | 32 | 16.7 |
| farmacia | 29 | 15.1 |
| ferreteria | 29 | 15.1 |
| fruteria | 25 | 13.0 |
| panaderia | 25 | 13.0 |
| consultorio_dental | 20 | 10.4 |
| tienda_celulares | 18 | 9.4 |
| floreria | 16 | 8.4 |
| zapateria | 15 | 7.8 |
| consultorio_medico | 13 | 6.8 |
| purificadora | 11 | 5.7 |
| cafe_internet | 10 | 5.2 |
| tienda_mascotas | 9 | 4.7 |
| bar | 9 | 4.7 |
| gimnasio | 8 | 4.2 |
| heladeria | 8 | 4.2 |
| pasteleria | 7 | 3.7 |
| lavanderia | 7 | 3.7 |
| pizzeria | 7 | 3.7 |
| laboratorio_clinico | 6 | 3.1 |
| guarderia | 4 | 2.1 |
| cerrajeria | 3 | 1.6 |
| veterinaria | 2 | 1.0 |
| escuela_idiomas | 1 | 0.5 |
| optica | 1 | 0.5 |
| sushi | 1 | 0.5 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| libreria | 0 | 0.0 |
| spa | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 3 | 6,835 | 1,095 | bajo |
| SANTA MARIA | 1 | 3,990 | 292 | bajo |
| LA LOMA BONITA | 2 | 2,782 | 261 | bajo |
| APAXCO DE OCAMPO | 1 | 3,556 | 247 | medio |
| ARBOLEDAS | 2 | 675 | 29 | medio |
| TABLON CHICO | 1 | 219 | 24 | bajo |
| LA ESTACION | 1 | 195 | 19 | bajo |
| 23 DE NOVIEMBRE | 1 | 536 | 16 | bajo |
| CAÑADA COLORADA | 1 | 174 | 8 | bajo |
| Apaxco de Ocampo | 2 | 199 | 0 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 27.2 millones de pesos por trimestre.
- Por hogar: 5,438 pesos por trimestre (lugar 49 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
