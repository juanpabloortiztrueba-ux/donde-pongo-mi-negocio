# Ficha de municipio: Villa del Carbón (Estado de México), clave 15112

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 14,477 habitantes (lugar 65 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 3,879. AGEB urbanas: 8. Superficie urbana de esas AGEB: 9.9 km².
- Densidad: 1,458 hab/km² (lugar 75 de 76).
- Edad: 0-14 años 26.9 %; 15-24 17.3 %; 25-59 44.5 %; 60 o más 11.0 %.
- Escolaridad promedio de la población de 15 y más: 9.2 años (lugar 68 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 41.6 %; con internet: 35.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 100.0 %, medio 0.0 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 13.2 %; Medio 48.4 %; Alto 4.7 %; Muy alto 33.8 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,618 (111.8 por cada 1 000 habitantes, lugar 4 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,408. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 6,288.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 745 | 46.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 188 | 11.6 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 181 | 11.2 % |
| 31 Industrias manufactureras | 171 | 10.6 % |
| 62 Servicios de salud y de asistencia social | 64 | 4.0 % |
| 43 Comercio al por mayor | 52 | 3.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 167 |
| 316211 | Fabricación de calzado con corte de piel y cuero | 82 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 63 |
| 812110 | Salones y clínicas de belleza y peluquerías | 51 |
| 465311 | Comercio al por menor de artículos de papelería | 49 |
| 463310 | Comercio al por menor de calzado | 40 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 34 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 27 |
| 463216 | Comercio al por menor de ropa de cuero y piel y de otros artículos de estos materiales | 27 |
| 311812 | Panificación tradicional | 27 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 173 | 119.5 |
| tienda_ropa | 63 | 43.5 |
| barberia_estetica | 51 | 35.2 |
| papeleria | 49 | 33.8 |
| carniceria | 44 | 30.4 |
| zapateria | 40 | 27.6 |
| tortilleria | 35 | 24.2 |
| fonda | 33 | 22.8 |
| taller_mecanico | 29 | 20.0 |
| taqueria | 27 | 18.7 |
| ferreteria | 27 | 18.7 |
| panaderia | 27 | 18.7 |
| consultorio_dental | 23 | 15.9 |
| cafeteria | 21 | 14.5 |
| fruteria | 20 | 13.8 |
| farmacia | 19 | 13.1 |
| consultorio_medico | 15 | 10.4 |
| floreria | 15 | 10.4 |
| tienda_celulares | 13 | 9.0 |
| bar | 11 | 7.6 |
| cafe_internet | 7 | 4.8 |
| gimnasio | 6 | 4.1 |
| heladeria | 6 | 4.1 |
| pizzeria | 5 | 3.5 |
| pasteleria | 4 | 2.8 |
| lavanderia | 4 | 2.8 |
| veterinaria | 3 | 2.1 |
| purificadora | 3 | 2.1 |
| laboratorio_clinico | 3 | 2.1 |
| cerrajeria | 3 | 2.1 |
| spa | 3 | 2.1 |
| optica | 2 | 1.4 |
| tienda_mascotas | 2 | 1.4 |
| sushi | 1 | 0.7 |
| escuela_idiomas | 1 | 0.7 |
| guarderia | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| libreria | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| VILLA DEL CARBON | 4 | 5,642 | 1,078 | bajo |
| LOMA ALTA | 1 | 4,879 | 223 | bajo |
| SAN JERONIMO ZACAPEXCO | 2 | 2,103 | 163 | bajo |
| LOS DOMINGUEZ | 1 | 1,853 | 139 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 17.3 millones de pesos por trimestre.
- Por hogar: 4,453 pesos por trimestre (lugar 68 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
