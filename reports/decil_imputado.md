# Decil de ingreso imputado por AGEB

Generado por `scripts/02_features.py` el 2026-11-23. Es **estimacion en areas pequenas**: el Censo 2020 no
trae ingreso, asi que se aprende en la ENIGH 2024 como se relaciona el ingreso del hogar con rasgos que *tambien* publica
el Censo por AGEB, y se aplica ese modelo a cada AGEB. Es una estimacion, no un dato medido.

## Datos
- ENIGH 2024 (INEGI), `data/processed/enigh_hogares.parquet`, ambito `zmvm` (hogares urbanos de los municipios de la ZMVM,
  de las entidades 09, 13 y 15): **3,767 hogares muestrales** en 695 UPM, 6.77 millones de hogares expandidos.
  Se excluyeron 0 hogares con ingreso corriente <= 0 (no entran al logaritmo).
- Censo 2020 (INEGI) por AGEB, `data/processed/agebs_base.parquet`: escolaridad promedio, % de viviendas con auto, internet
  y PC, y promedio de ocupantes.
- Los deciles son los de la ENIGH **dentro del ambito `zmvm`** (hogares ordenados por ingreso corriente trimestral y
  cortados en 10 partes iguales con el factor de expansion). Un decil 1 aqui es el 10 % mas pobre **de la ZMVM**, no del pais.
  Los cortes (ingreso trimestral, pesos 2024) son: 31,269, 41,135, 49,941, 58,558, 68,594, 81,555, 97,997, 126,348, 172,909.
  Reconstruidos desde esos cortes, coinciden con la columna `decil` de Datos C en 100.0% de los hogares (ponderado).

## Modelo
`log(ingreso corriente trimestral del hogar) = b0 + b1*escolaridad_jefe + b2*auto + b3*internet + b4*pc + b5*integrantes + e`,
minimos cuadrados ponderados con el factor de expansion; errores estandar robustos por UPM.

| Variable | Coeficiente (log ingreso) | Error est. (por UPM) | t |
|---|---|---|---|
| Intercepto | 10.0217 | 0.032 | 313.0 |
| Escolaridad del jefe (anios) | 0.0382 | 0.0026 | 14.9 |
| Tiene auto (0-1) | 0.3237 | 0.0223 | 14.5 |
| Tiene internet (0-1) | 0.2339 | 0.0258 | 9.1 |
| Tiene PC/laptop/tablet (0-1) | 0.2795 | 0.0211 | 13.3 |
| Integrantes del hogar | 0.0823 | 0.0058 | 14.2 |

Ajuste dentro de la muestra: R2 ponderado = 0.401; desviacion de los residuos (sigma_res) = 0.532 en log.

### Validacion cruzada (5 pliegues por UPM)
| Modelo | R2 | RMSE log | Spearman | Decil exacto | Decil +-1 | Prob. media al decil real |
|---|---|---|---|---|---|---|
| Regresion lineal ponderada (el que se usa) | 0.398 | 0.533 | 0.651 | 17.9% | 50.4% | 0.151 |
| Gradient boosting (solo comparacion) | 0.425 | 0.521 | 0.658 | 20.2% | 52.1% | 0.159 |

"Prob. media al decil real" es la probabilidad que el modelo asigna al decil verdadero del hogar (azar = 0.100).
El gradient boosting solo se calcula para ver si una forma no lineal ganaria mucho; **se usa la lineal** porque debe poder
aplicarse a promedios de AGEB (una regresion lineal en logs aplicada al promedio de las covariables da el promedio de las
predicciones, un arbol no) y porque se interpreta.

## De AGEB a decil
1. Cada AGEB recibe sus covariables del Censo en la escala de la ENIGH: porcentajes de 0 a 1 para auto, internet y PC;
   `escolaridad_prom` y `prom_ocupantes` tal cual. Los huecos protegidos por el INEGI (`*`) se rellenan con el promedio
   del municipio ponderado por hogares (hasta 2 covariables faltantes; con mas, o sin hogares, la AGEB queda sin decil).
2. Prediccion mu = log del ingreso trimestral tipico del hogar de la AGEB.
3. **Calibracion de nivel**: el Censo mide cosas parecidas pero no iguales (escolaridad de *toda la poblacion de 15+*, no del jefe;
   ocupantes por *vivienda*, no por hogar). Se suma una constante delta = +0.005 (en log) para que el promedio de mu,
   ponderado por hogares, sea igual al promedio de log(ingreso) de la ENIGH `zmvm`.
4. **Calibracion ecologica (estiramiento)**: entre municipios, el ingreso de la ENIGH sube mucho mas rapido que el modelo de hogares
   (el modelo de hogares esta "aplanado" porque auto o internet de *un* hogar es una medida ruidosa del ingreso; el
   porcentaje de una AGEB promedia ese ruido y ademas refleja el barrio). Regresando el log del ingreso ENIGH sobre mu en los
   35 municipios con >= 30 hogares muestrales (ponderado por hogares muestrales) sale una pendiente de 2.52
   (error est. aprox. 0.18; quitando un municipio a la vez: 2.43 a 2.58). Se estira mu
   alrededor de su promedio con lambda = 2.52 (tope 2.61: con mas, la varianza entre AGEB pasaria la varianza total
   menos la de los residuos). Sin este paso casi ninguna AGEB llegaba al decil 9-10 y Benito Juarez o Miguel Hidalgo quedaban
   claramente por debajo de lo que mide la ENIGH (diferencia media absoluta por municipio 0.144 sin estirar y 0.093 con lambda).
   **Es un supuesto fuerte**: la relacion entre municipios se traslada a AGEB; solo la ENIGH por municipio (no por AGEB) permite verificarlo.
5. **Dispersion dentro de la AGEB**: no todos los hogares de una AGEB son iguales. Se toma sigma^2 = Var(log ingreso ENIGH zmvm) -
   Var entre AGEB de mu = 0.472 - 0.176 = 0.296  (sigma = 0.544;
   la desviacion de los residuos del modelo, 0.532, es el piso). Incluye lo que el modelo no explica, aunque
   parte sea diferencia entre AGEB: es la eleccion prudente (no sobreestima la certeza).
6. Con ingreso lognormal(mu, sigma) y los cortes de decil de la ENIGH se calcula **P(decil k | AGEB)** para k=1..10
   (columnas `p_decil_01` a `p_decil_10`).
7. `decil_imputado` = decil donde cae el hogar tipico (exp(mu)); `decil_esperado` = sum k*P(k). `nse`: bajo = deciles 1-4,
   medio = 5-8, alto = 9-10 (convencion de este proyecto, no una clasificacion oficial; AMAI usa otra). `p_nse_*` suma las
   probabilidades de cada grupo.

AGEB con decil: 5,792 de 5,875; sin decil: 83 (sin hogares, o con mas de 2 covariables protegidas).

## Resultados
Hogares por decil imputado, sumando las AGEB de la ZMVM (si el metodo fuera perfecto, 10 % cada uno):

| Decil | Hogares esperados (P) | Hogares en AGEB con decil modal |
|---|---|---|
| 1 | 11.0% | 0.7% |
| 2 | 10.0% | 5.4% |
| 3 | 9.4% | 13.0% |
| 4 | 8.8% | 16.1% |
| 5 | 9.2% | 16.7% |
| 6 | 10.0% | 15.8% |
| 7 | 9.8% | 11.2% |
| 8 | 11.4% | 9.3% |
| 9 | 9.9% | 8.0% |
| 10 | 10.4% | 3.9% |

NSE por AGEB (decil del hogar tipico):

| NSE | AGEB | Hogares |
|---|---|---|
| bajo (deciles 1-4) | 2273 | 2,125,216 |
| medio (5-8) | 2802 | 3,209,441 |
| alto (9-10) | 717 | 720,886 |

### Comprobaciones fuera del ajuste
- **Marginacion CONAPO 2020**: correlacion de Spearman entre mu y el indice de marginacion `im_2020` (alto = menos marginacion)
  en 5,706 AGEB = **0.878**. Decil imputado medio por grado de marginacion:

| Grado de marginacion CONAPO 2020 | AGEB | Decil imputado medio | Mediana |
|---|---|---|---|
| Muy bajo | 1004 | 8.59 | 9.0 |
| Bajo | 1959 | 6.24 | 6.0 |
| Medio | 1781 | 4.25 | 4.0 |
| Alto | 760 | 2.91 | 3.0 |
| Muy alto | 202 | 1.89 | 2.0 |

- **Municipios**: se compara el log del ingreso promedio de la ENIGH (municipios con >= 30 hogares muestrales, 35 municipios;
  la ENIGH **no** es representativa por municipio, asi que es una referencia ruidosa) contra el estimado desde el Censo:
  Pearson = 0.913, Spearman = 0.903, diferencia media absoluta = 0.093 en log (esto ya usa lambda, asi que es un ajuste, no una prueba independiente).

| Municipio | Hogares muestra | log ingreso ENIGH | log ingreso estimado |
|---|---|---|---|
| 09002 | 111.0 | 11.615 | 11.404 |
| 09003 | 112.0 | 11.535 | 11.593 |
| 09004 | 54.0 | 11.442 | 11.497 |
| 09005 | 257.0 | 11.223 | 11.217 |
| 09006 | 106.0 | 11.369 | 11.356 |
| 09007 | 350.0 | 11.04 | 11.105 |
| 09008 | 70.0 | 11.186 | 11.28 |
| 09009 | 31.0 | 10.868 | 10.966 |
| 09010 | 210.0 | 11.483 | 11.381 |
| 09011 | 54.0 | 11.187 | 11.114 |
| 09012 | 119.0 | 11.457 | 11.422 |
| 09013 | 87.0 | 11.266 | 11.21 |
| 09014 | 138.0 | 11.83 | 11.871 |
| 09015 | 115.0 | 11.202 | 11.303 |
| 09016 | 101.0 | 11.779 | 11.62 |
| 09017 | 103.0 | 11.261 | 11.244 |
| 13069 | 118.0 | 10.878 | 10.967 |
| 15013 | 98.0 | 11.464 | 11.36 |
| 15020 | 98.0 | 11.181 | 11.307 |
| 15025 | 66.0 | 10.958 | 10.878 |
| 15029 | 47.0 | 10.921 | 10.985 |
| 15031 | 87.0 | 10.752 | 10.67 |
| 15033 | 203.0 | 10.991 | 11.057 |
| 15037 | 36.0 | 11.345 | 11.448 |
| 15039 | 51.0 | 10.974 | 10.982 |
| 15057 | 129.0 | 11.256 | 11.181 |
| 15058 | 105.0 | 11.091 | 11.074 |
| 15060 | 40.0 | 11.114 | 10.957 |
| 15070 | 53.0 | 10.974 | 10.837 |
| 15081 | 92.0 | 10.956 | 11.175 |
| 15099 | 30.0 | 10.849 | 11.092 |
| 15104 | 107.0 | 11.014 | 11.202 |
| 15109 | 93.0 | 11.15 | 11.075 |
| 15121 | 106.0 | 11.285 | 11.426 |
| 15122 | 58.0 | 10.77 | 10.687 |

## Gasto potencial por rubro
`gasto_pot_<rubro>_trim` = hogares de la AGEB x sum_k P(decil k) x gasto trimestral promedio del hogar en el decil k
(`enigh_gasto.parquet`, ambito `zmvm`, el mismo en que se definieron los deciles; pesos corrientes de 2024, el promedio cuenta
los ceros). Rubros calculados: los `rubro_enigh` y `rubro_enigh_alt` de `config/giros.yaml` (0 columnas).
Todos los rubros tienen dato.
Avisos: en rubros con pocos hogares que gastan (helados 2-7 %, lavanderia, idiomas) el promedio por decil es ruidoso y no
siempre sube con el decil; sirve para ordenar zonas, no para dimensionar ventas.

## Limites (leer antes de usar el decil)
- El decil es de un **hogar tipico** de la AGEB. Una AGEB con decil 6 puede tener hogares de todos los deciles; por eso se
  guardan las probabilidades, y el gasto potencial las usa en vez del decil solo.
- La ENIGH 2024 es de 2024 y el Censo de 2020; entre ambos hubo inflacion y cambios en internet y escolaridad. Los cortes en pesos
  son de 2024. Con Censo mas viejo que ENIGH, el nivel se calibra con delta, pero el *orden* entre AGEB no se corrige.
- Modelo con 5 covariables: explica una parte del ingreso (R2 arriba). Zonas con ingreso alto sin auto ni internet
  distintos (p. ej. departamentos de lujo con poco auto) se subestiman, y los barrios con muchos hogares de renta o remesas, tambien.
- La pendiente municipal (lambda) sale de 35 puntos ruidosos (la ENIGH no representa municipios); el *orden* de las AGEB no depende
  de ella (esta confirmado por CONAPO), pero cuantas AGEB caen en deciles extremos si.
- Escolaridad: la ENIGH aqui es del jefe del hogar (aproximacion por niveles; ver BITACORA de Datos C); el Censo es de toda
  la poblacion de 15+. La constante delta absorbe la diferencia promedio, no la que cambie de una AGEB a otra.
