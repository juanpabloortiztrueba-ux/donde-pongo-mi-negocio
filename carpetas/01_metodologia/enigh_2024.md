# ENIGH 2024: Encuesta Nacional de Ingresos y Gastos de los Hogares (INEGI)

## Qué es y qué se usó
La ENIGH 2024 Nueva Serie (INEGI, publicada el 2025-07-30) mide cuánto ingresan y en qué gastan los hogares. Se usan los microdatos por hogar (concentrado, gastos del hogar y de las personas). Fuente: https://www.inegi.org.mx/programas/enigh/nc/2024/ . Archivos y sha256 en `data/FUENTES.md`.

## Cómo se usa en el proyecto
1. **Deciles de ingreso.** Los hogares se ordenan por ingreso corriente trimestral y, con el factor de expansión, se cortan en 10 grupos iguales (método del INEGI). Aquí los deciles son los de la ZMVM: un decil 1 es el 10 % de hogares más pobre de la ZMVM, no del país.
2. **Gasto por rubro y decil.** Gasto trimestral promedio del hogar en cada rubro, en pesos corrientes de 2024, **contando como cero a los hogares que no gastaron**. Se guarda además el porcentaje de hogares con gasto, para saber si un promedio descansa en pocos hogares.
3. **Rubro «alimentos y bebidas consumidos fuera del hogar»** (`ali_fuera_total`): claves 1111xx del catálogo de gastos (desayunos, comidas, cenas, entrecomidas, eventos y comida preparada como barbacoa, carnitas, hamburguesas, pizzas y pollos rostizados). El rubro `ali_fuera` del INEGI incluye solo parte de eso; por eso se armó `ali_fuera_total`.
4. **Imputación a AGEB.** Con los hogares de la ENIGH se aprende cómo el ingreso se relaciona con escolaridad del jefe, automóvil, internet, computadora e integrantes, y se aplica a las mismas variables del Censo por AGEB (ver `nse_estimado.md`).

## Ámbitos y representatividad
- La ENIGH 2024 es representativa por entidad, **no por municipio ni por la ZMVM**. El ámbito `zmvm` del proyecto es una submuestra: 3 767 hogares urbanos (6.77 millones de hogares expandidos) de 48 de los 76 municipios.
- Se usan solo hogares urbanos (localidades de 2 500 habitantes o más) para empatar con las AGEB urbanas.
- Hay ámbitos separados `cdmx`, `edomex` y `nacional_urbano`.

## Límites que hay que decir al usar estos datos
- Rubros muy específicos tienen pocos hogares con gasto. Ejemplo: **helados, nieves y paletas** (compras para llevar a casa) los reporta solo entre 2 % y 7 % de los hogares según el decil; sirven para ordenar deciles, no para dimensionar la demanda. Un helado consumido en una heladería cae en «comida fuera del hogar» y no se puede separar.
- Para lavandería de ropa, idiomas, óptica y celulares la cobertura es muy baja (menos de 4 % de hogares).
- Coworking no tiene rubro en la ENIGH (mide hogares, no empresas): NO ENCONTRADO.
- El ingreso de una colonia no es un dato de la ENIGH: es una estimación.
