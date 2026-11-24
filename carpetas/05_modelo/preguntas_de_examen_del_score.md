# Preguntas de examen sobre el score y respuestas cortas

Generado por `scripts/03b_validar_score.py` el 2026-11-23; las cifras salen de `reports/validacion_score.md` (DENUE 11/2020 y 05/2026, Censo 2020, ENIGH 2024 de INEGI; CONAPO 2020; modelo propio). Si algo cambia, vuelve a correr el script: no se editan a mano.

## ¿Por qué el score no predice aperturas crudas y está bien?

**Respuesta corta.** El score no está hecho para adivinar dónde aparecen más negocios, sino dónde conviene poner uno. Las aperturas se aglomeran donde ya hay competencia: en las AGEB con 3 o más negocios del giro en 2020 aparecieron 3 nuevos por cada 10 que ya había y desaparecieron otros 3 (rotación). Un score que castiga la competencia, como debe hacerlo uno de ubicación, queda debajo de la competencia a secas para predecir aperturas crudas: AUC 0.577 contra 0.711 de la competencia en la AGEB y 0.806 del modelo de aperturas. La captura Huff, que es el castigo, tiene AUC 0.348: ordena al revés. Además, 93 % de lo que «apareció» en 2026 viene de la carga de los Censos Económicos 2024, así que «apareció» no es «abrió».

**Qué se hizo.** Se midió contra lo que corresponde a la decisión, por (AGEB, giro): crecimiento neto (aperturas menos desapariciones sobre los establecimientos de 2020), sobrevivencia de los establecimientos de 2020 y altas fuera de la carga censal.

## ¿Los pesos del score los puso el autor?

No. Los aprendió `scripts/03b_validar_score.py`: pesos no negativos que suman 1, ajustados en 4 de 5 pliegues de municipios y probados en el que no vieron (el entregado se reajusta con todo), redondeados a 0.05, con una restricción de que gasto potencial y población objetivo pesen al menos 25 %. Resultado: 0.35 aperturas esperadas por competidor, 0.05 gasto potencial × captura, 0.20 población objetivo × NSE × captura, 0.10 flujo de gente (proxy) y 0.30 complementarios. Antes eran 0.30, 0.25, 0.15, 0.20 y 0.10, puestos por el autor. En crecimiento neto, el score nuevo saca ρ = 0.159 fuera de muestra (0.182 con los pesos entregados, que ya vieron todos los municipios) contra 0.046 del anterior y 0.126 de la mejor línea base ingenua. En altas fuera de la carga censal el nuevo saca 0.046 y el anterior 0.108: ahí pierde, y se dice.

## ¿El score nuevo es mejor que el anterior?

No se puede afirmar. Su ventaja en crecimiento neto viene de la carga de los Censos Económicos 2024: 90.5 % de los «nuevos» entre las AGEB elegibles tienen `fecha_alta` 2024, negocios que ya existían y no estaban en el DENUE 2020; donde 2020 subregistró queda un stock bajo con muchos «nuevos», y el núcleo λ/(1 + competidores) premia justo eso. Al usar el score, el DENUE 2026 ya trae la carga, así que esa ventaja no se traslada. Con el objetivo sin carga censal (altas reales menos desapariciones, sobre el stock de 2020) el nuevo saca ρ = 0.037 fuera de muestra contra 0.055 del anterior; en altas fuera de la carga 0.046 contra 0.108, y en sobrevivencia 0.022 contra 0.028: empata o pierde. Como las altas reales son pocas frente a los cierres, el neto sin carga se parece mucho a la sobrevivencia, así que no es una evidencia independiente. Se conserva el 3.0 como decisión de diseño (pone la saturación en el centro del orden y los pesos son aprendidos con un criterio publicado), no como victoria medida; con dos cortes del DENUE y sin ventas ni rentas, la validación descarta pero no confirma. Sensibilidad: aprendiendo los pesos solo con objetivos limpios, el núcleo anti-saturación se queda en 0.00 y el score ordena hacia donde ya hay negocios (crecimiento neto ρ = -0.024), por eso no se adopta.

## ¿Se puede predecir si un negocio va a sobrevivir?

Con estos datos casi no. Dentro de un giro, la mejor puntuación que se probó (el modelo dedicado de sobrevivencia) saca ρ = 0.076 contra la tasa de sobrevivencia de los establecimientos de 2020 en el círculo del giro, y el score 0.022. Por eso `prob_sobrevive` se reporta como dato de riesgo y no se usa para ordenar. Aviso: «desapareció del DENUE» puede ser un cierre o un cambio de registro que no se pudo empatar.

## ¿Qué tan confiable es el nivel socioeconómico estimado?

El decil exacto de un hogar se acierta 17.9 % de las veces y a ±1 decil 50.4 %. La banda (bajo = deciles 1-4, medio = 5-8, alto = 9-10), que es lo que usa el producto, se acierta 57.7 % (decir siempre «medio» daría 40 %): 59 % en bajo, 70 % en medio y 29 % en alto, donde se subdetecta. Casi nunca confunde bajo con alto (1.1 % de los hogares). Es un estimado a partir del Censo, no un dato medido: se dice «NSE estimado». Fuente: ENIGH 2024 (INEGI), validación cruzada por UPM.

## ¿Qué haría distinto con más datos?

Ventas y rentas por local, flujo peatonal real y cortes anuales del DENUE para separar aperturas de cargas censales. Con eso se podría medir rentabilidad y sobrevivencia de las aperturas, que hoy no se pueden observar con solo dos cortes.
