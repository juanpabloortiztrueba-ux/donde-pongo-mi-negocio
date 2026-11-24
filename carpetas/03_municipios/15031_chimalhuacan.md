# Ficha de municipio: Chimalhuacán (Estado de México), clave 15031

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 703,215 habitantes (lugar 7 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 180,284. AGEB urbanas: 134. Superficie urbana de esas AGEB: 48.3 km².
- Densidad: 14,571 hab/km² (lugar 6 de 76).
- Edad: 0-14 años 27.2 %; 15-24 18.2 %; 25-59 46.1 %; 60 o más 8.4 %.
- Escolaridad promedio de la población de 15 y más: 9.1 años (lugar 69 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 26.8 %; con internet: 51.3 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 39.5 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 99.7 %, medio 0.3 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 0.1 %; Medio 12.1 %; Alto 78.8 %; Muy alto 9.1 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 37,176 (52.9 por cada 1 000 habitantes, lugar 45 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 29,692. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 117,464.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 20,915 | 56.3 % |
| 81 Otros servicios excepto actividades gubernamentales | 5,326 | 14.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 3,666 | 9.9 % |
| 31 Industrias manufactureras | 2,190 | 5.9 % |
| 61 Servicios educativos | 852 | 2.3 % |
| 62 Servicios de salud y de asistencia social | 823 | 2.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 6,064 |
| 812110 | Salones y clínicas de belleza y peluquerías | 2,121 |
| 465311 | Comercio al por menor de artículos de papelería | 1,746 |
| 467115 | Comercio al por menor de artículos para la limpieza | 1,052 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 1,011 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 943 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 907 |
| 461122 | Comercio al por menor de carne de aves | 891 |
| 464111 | Farmacias sin minisúper | 838 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 829 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 6,173 | 87.8 |
| barberia_estetica | 2,121 | 30.2 |
| papeleria | 1,746 | 24.8 |
| carniceria | 1,327 | 18.9 |
| fruteria | 1,011 | 14.4 |
| tienda_ropa | 907 | 12.9 |
| farmacia | 896 | 12.7 |
| tortilleria | 837 | 11.9 |
| ferreteria | 672 | 9.6 |
| fonda | 643 | 9.1 |
| taller_mecanico | 617 | 8.8 |
| purificadora | 596 | 8.5 |
| taqueria | 595 | 8.5 |
| cafeteria | 591 | 8.4 |
| panaderia | 397 | 5.6 |
| cafe_internet | 323 | 4.6 |
| consultorio_dental | 240 | 3.4 |
| heladeria | 227 | 3.2 |
| lavanderia | 208 | 3.0 |
| gimnasio | 206 | 2.9 |
| tienda_celulares | 197 | 2.8 |
| zapateria | 175 | 2.5 |
| tienda_mascotas | 145 | 2.1 |
| pizzeria | 143 | 2.0 |
| floreria | 137 | 1.9 |
| consultorio_medico | 116 | 1.6 |
| pasteleria | 79 | 1.1 |
| optica | 75 | 1.1 |
| bar | 75 | 1.1 |
| veterinaria | 68 | 1.0 |
| cerrajeria | 63 | 0.9 |
| laboratorio_clinico | 37 | 0.5 |
| spa | 33 | 0.5 |
| sushi | 16 | 0.2 |
| guarderia | 12 | 0.2 |
| comida_china | 9 | 0.1 |
| libreria | 7 | 0.1 |
| escuela_idiomas | 4 | 0.1 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| ACUITLAPILCO | 4 | 41,471 | 1,962 | bajo |
| SANTA MARIA NATIVITAS | 4 | 22,330 | 1,465 | bajo |
| SAN PABLO | 4 | 22,720 | 1,410 | bajo |
| XOCHITENCO | 2 | 29,492 | 1,280 | bajo |
| 2 SECCION ACUITLAPILCO | 1 | 18,328 | 1,042 | bajo |
| FUNDIDORES | 3 | 21,277 | 1,016 | bajo |
| XALTIPAC | 4 | 15,139 | 882 | bajo |
| TALABARTEROS | 1 | 12,179 | 874 | bajo |
| CANTEROS | 2 | 15,635 | 860 | bajo |
| CABECERA MUNICIPAL | 2 | 9,053 | 855 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| TEPALCATES | 5,084 | 4.4 |
| VILLA SAN LORENZO CHIMALCO | 5,639 | 4.2 |
| SAN MIGUEL | 5,203 | 4.1 |
| TALABARTEROS | 12,179 | 4.0 |
| SANTA MARIA NATIVITAS | 22,330 | 4.0 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| ESCALERILLAS | 4,079 | 1.8 |
| LOMAS DE CHOCOLIN | 6,013 | 1.9 |
| LA JOYA | 3,014 | 2.0 |
| AMPLIACION SAN PABLO | 3,363 | 2.1 |
| CORTE SAN PABLO | 11,369 | 2.1 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 790.8 millones de pesos por trimestre.
- Por hogar: 4,386 pesos por trimestre (lugar 70 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
