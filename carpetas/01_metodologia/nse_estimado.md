# Cómo se estima el nivel socioeconómico (NSE) de una AGEB

El Censo 2020 no pregunta el ingreso. El proyecto lo estima con estimación en áreas pequeñas. Detalle completo y pruebas en `reports/decil_imputado.md` (generado por `scripts/02_features.py`). Cifras al 2026-11-23.

## Pasos
1. **Se aprende en la ENIGH 2024** (3 767 hogares urbanos de la ZMVM) una regresión de `log(ingreso corriente trimestral del hogar)` contra escolaridad del jefe, tener automóvil, internet y computadora, e integrantes del hogar. R² ponderado dentro de la muestra 0.40 y, con validación cruzada por unidad primaria de muestreo, 0.398. Todos los coeficientes son significativos (t > 9).
2. **Se aplica a las variables del Censo por AGEB** (escolaridad promedio, % de viviendas con auto, internet y PC, ocupantes por vivienda). Son variables parecidas pero no idénticas (el Censo mide la escolaridad de toda la población de 15 años y más, no la del jefe), por eso hay una calibración de nivel.
3. **Calibración ecológica**: entre municipios, el ingreso de la ENIGH sube más rápido de lo que dice el modelo de hogares. Se estira con un factor de 2.52 (rango de 2.43 a 2.58 quitando un municipio a la vez). Es un supuesto fuerte, documentado.
4. **Distribución dentro de la AGEB**: se supone ingreso lognormal alrededor del hogar típico y se calcula la probabilidad de cada decil (`p_decil_01` a `p_decil_10`).
5. `decil_imputado` es el decil del hogar típico. **NSE**: bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 (convención del proyecto; no es la clasificación oficial ni la de AMAI).

## Resultados
2 273 AGEB bajo, 2 802 medio, 717 alto, y 83 sin estimación (sin hogares o con demasiados datos protegidos: se consideran NO ENCONTRADO). La correlación de Spearman con el índice de marginación de CONAPO es 0.88. Benito Juárez y Coyoacán quedan con mediana de decil 9; Iztapalapa entre los más bajos.

## Cómo hablar de esto
Decir «ingreso estimado» o «nivel socioeconómico estimado», nunca «el ingreso de la colonia es». La ENIGH no representa municipios, así que no hay un dato medido de ingreso por colonia. Los deciles son de la ZMVM.

## Gasto potencial
El gasto potencial de una AGEB en un rubro es: hogares × suma sobre deciles de P(decil) × gasto trimestral promedio del hogar en ese decil (ENIGH 2024, ámbito `zmvm`). Está en pesos de 2024 por trimestre. Es un orden de magnitud para comparar zonas, no una proyección de ventas.
