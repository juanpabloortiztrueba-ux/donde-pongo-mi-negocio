# Ficha de municipio: Naucalpan de Juárez (Estado de México), clave 15057

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 795,819 habitantes (lugar 5 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 230,421. AGEB urbanas: 203. Superficie urbana de esas AGEB: 79.6 km².
- Densidad: 9,994 hab/km² (lugar 19 de 76).
- Edad: 0-14 años 20.5 %; 15-24 15.9 %; 25-59 48.6 %; 60 o más 14.9 %.
- Escolaridad promedio de la población de 15 y más: 10.7 años (lugar 24 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 45.8 %; con internet: 67.5 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.3 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 60.0 %, medio 21.6 %, alto 18.5 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 17.2 %; Bajo 15.9 %; Medio 59.5 %; Alto 7.5 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 36,539 (45.9 por cada 1 000 habitantes, lugar 60 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 34,133. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 238,976.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 16,618 | 45.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 5,685 | 15.6 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 4,511 | 12.3 % |
| 62 Servicios de salud y de asistencia social | 1,631 | 4.5 % |
| 31 Industrias manufactureras | 1,559 | 4.3 % |
| 43 Comercio al por mayor | 1,134 | 3.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 4,244 |
| 812110 | Salones y clínicas de belleza y peluquerías | 2,303 |
| 465311 | Comercio al por menor de artículos de papelería | 1,203 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 898 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 867 |
| 461122 | Comercio al por menor de carne de aves | 754 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 753 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 711 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 669 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 668 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 4,449 | 55.9 |
| barberia_estetica | 2,303 | 28.9 |
| carniceria | 1,234 | 15.5 |
| papeleria | 1,203 | 15.1 |
| tienda_ropa | 898 | 11.3 |
| fonda | 890 | 11.2 |
| taller_mecanico | 835 | 10.5 |
| taqueria | 753 | 9.5 |
| fruteria | 711 | 8.9 |
| cafeteria | 668 | 8.4 |
| farmacia | 663 | 8.3 |
| consultorio_dental | 586 | 7.4 |
| ferreteria | 524 | 6.6 |
| tortilleria | 523 | 6.6 |
| panaderia | 396 | 5.0 |
| consultorio_medico | 345 | 4.3 |
| lavanderia | 302 | 3.8 |
| cafe_internet | 272 | 3.4 |
| tienda_celulares | 262 | 3.3 |
| zapateria | 250 | 3.1 |
| gimnasio | 205 | 2.6 |
| floreria | 179 | 2.2 |
| purificadora | 170 | 2.1 |
| heladeria | 161 | 2.0 |
| tienda_mascotas | 157 | 2.0 |
| veterinaria | 146 | 1.8 |
| optica | 132 | 1.7 |
| cerrajeria | 125 | 1.6 |
| pasteleria | 124 | 1.6 |
| bar | 111 | 1.4 |
| pizzeria | 107 | 1.3 |
| spa | 84 | 1.1 |
| laboratorio_clinico | 77 | 1.0 |
| sushi | 40 | 0.5 |
| guarderia | 28 | 0.4 |
| libreria | 20 | 0.3 |
| escuela_idiomas | 13 | 0.2 |
| comida_china | 12 | 0.2 |
| coworking | 4 | 0.1 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CIUDAD SATELITE | 4 | 7,450 | 1,400 | alto |
| SAN RAFAEL CHAMAPA | 6 | 26,886 | 1,017 | bajo |
| MERCADO | 1 | 2,365 | 996 | medio |
| SAN ANTONIO ZOMEYUCAN | 4 | 23,862 | 975 | bajo |
| LOMAS DE SOTELO | 1 | 1,856 | 949 | alto |
| EL MOLINITO | 2 | 12,440 | 909 | bajo |
| SANTA CRUZ ACATLAN | 1 | 3,098 | 879 | medio |
| BENITO JUAREZ | 3 | 24,263 | 865 | bajo |
| LOS REMEDIOS | 3 | 14,872 | 812 | medio |
| SAN MIGUEL TECAMACHALCO | 2 | 13,027 | 810 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| PASEOS DEL BOSQUE | 4,797 | 9.4 |
| COLON ECHEGARAY | 3,446 | 9.3 |
| CD SATELITE | 13,468 | 9.3 |
| JARDINES DE SAN MATEO | 7,492 | 9.3 |
| LOMAS VERDES III SECCION | 6,640 | 9.2 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| PALACIO | 3,595 | 3.0 |
| SAN JOSE POZA HONDA | 6,084 | 3.1 |
| ALFREDO V BONFIL | 9,504 | 3.1 |
| BENITO JUAREZ | 24,263 | 3.2 |
| SAN LORENZO TOTOLINGA 2DA SECCION | 5,314 | 3.2 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,852.8 millones de pesos por trimestre.
- Por hogar: 8,041 pesos por trimestre (lugar 18 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.
