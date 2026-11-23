# Marco teórico: dónde conviene localizar un negocio

Las ideas de abajo explican por qué el modelo mide demanda, competencia y negocios complementarios alrededor de cada AGEB. Las referencias completas, con la forma en que se verificó cada una, están en `referencias.md`.

## Gravitación comercial: Reilly (1931) y Huff (1964)
Reilly (1931) propuso la «ley de gravitación del comercio al menudeo»: dos ciudades atraen a los compradores de un pueblo intermedio en proporción directa a su población y en proporción inversa al cuadrado de la distancia. Es una regla determinista sobre dos centros.
Huff (1964) la volvió probabilística. La probabilidad de que un consumidor ubicado en `i` compre en el establecimiento `j` es proporcional a su atractivo (por ejemplo, su superficie de venta) dividido entre la distancia elevada a un parámetro de fricción, y se normaliza entre todos los establecimientos que el consumidor tiene a su alcance: P(i,j) = [S_j / d_ij^λ] / suma_k [S_k / d_ik^λ]. El parámetro λ cambia según el tipo de bien y se estima con datos.
**Cómo se usa aquí.** El proyecto no estima la λ de Huff. Toma la idea: un competidor cercano pesa más que uno lejano y el peso cae con la distancia. La función `app/motor.py: conteos_giro` pondera cada establecimiento con 1/(1+(d/d0)²), con d0 igual a la mitad del radio de influencia del giro, y cuenta cero fuera del radio. Es una adaptación sencilla inspirada en Huff, no su fórmula.

## Competencia espacial: Hotelling (1929)
Hotelling (1929) imaginó dos vendedores sobre una calle, con consumidores repartidos en forma pareja y que compran en el más cercano (considerando precio y costo de transporte). Su resultado es el «principio de mínima diferenciación»: los vendedores tienden a ubicarse juntos, en el centro. Es una razón para que los negocios del mismo giro se agrupen.
Matices posteriores: d'Aspremont, Gabszewicz y Thisse (1979) mostraron que con costos de transporte lineales el equilibrio en precios no existe cuando las empresas están cerca, y que con costos cuadráticos pasa lo contrario, las empresas buscan separarse. Eaton y Lipsey (1975) mostraron que el resultado depende del número de empresas y de la forma del mercado, no solo del caso de dos empresas.
**Lectura práctica.** Que ya haya competidores en una zona puede ser mala señal (mercado repartido) o buena (zona probada que atrae clientes). Los datos no deciden eso solos; por eso el modelo mide por separado competencia y aperturas recientes.

## Lugares centrales: Christaller (1933)
Christaller (1933) explicó por qué hay ciudades grandes y pueblos chicos con una jerarquía de «lugares centrales». Dos conceptos sirven al proyecto: el **umbral** (la población mínima que necesita un bien o servicio para ser rentable) y el **alcance** (la distancia máxima que un cliente está dispuesto a recorrer). Un bien de uso diario, como una tienda de abarrotes o una papelería, tiene umbral y alcance chicos y se reparte en todos los barrios. Un bien de compra ocasional, como un gimnasio grande o una librería especializada, tiene umbral y alcance grandes y se concentra en pocas zonas. Lösch (1940) generalizó la idea con áreas de mercado hexagonales por cada bien.
**Cómo se usa aquí.** El campo `radio_influencia_m` de `config/giros.yaml` (300 a 500 m para consumo diario de barrio; 1 a 2 km para giros de destino) es un supuesto razonado en el espíritu del alcance de Christaller, no un valor medido.

## Aglomeración
Marshall (1890) identificó tres razones para que las empresas se junten: mercado de trabajo compartido, proveedores especializados y flujo de ideas. Fujita, Krugman y Venables (1999) las formalizan en economía espacial. Glaeser, Kallal, Scheinkman y Shleifer (1992) comparan la aglomeración de la misma industria con la de industrias distintas como fuente de crecimiento local. Ellison y Glaeser (1997) proponen un índice para medir qué tan concentrada está una industria más allá del azar.
**Cómo se usa aquí.** Para el comercio al menudeo la aglomeración funciona por atracción de clientes: un negocio de comida rinde mejor cerca de escuelas, oficinas, plazas y transporte. Por eso `config/giros.yaml` define `complementarios` (clases SCIAN que atraen al cliente del giro) y el modelo mide cuántos hay alrededor. Esos complementarios son criterio del autor, no evidencia.

## Entrada de negocios: Bresnahan y Reiss (1991), Seim (2006) y Jia (2008)
Bresnahan y Reiss (1991) estudiaron en qué tamaño de mercado cabe un negocio más (médicos, dentistas, farmacias en pueblos chicos): el tamaño de mercado por empresa que se necesita sube conforme entran más competidores. Seim (2006) agrega que las empresas eligen también dónde ubicarse para diferenciarse de las demás (videorrenta en Estados Unidos). Jia (2008) estudia cómo la entrada de grandes cadenas afecta a las pequeñas.
**Cómo se usa aquí.** El modelo de aperturas aprende, con el DENUE de 2020 y de 2026, dónde aparecieron negocios de un giro. Eso es una descripción de dónde entraron empresas, no una prueba de que les haya ido bien (ver `05_modelo/`).

## Resumen de cómo se conectan las ideas con el modelo
| Idea | Autor | Variable del proyecto |
|---|---|---|
| El atractivo cae con la distancia | Reilly, Huff | Competencia y complementarios ponderados por distancia (`conteos_giro`) |
| Los negocios se agrupan | Hotelling, Marshall | Complementarios; competencia en el corte de 2020 como variable del modelo |
| Umbral y alcance | Christaller, Lösch | `radio_influencia_m` por giro; demanda por población y gasto |
| Tamaño de mercado por entrante | Bresnahan y Reiss | Población, hogares y gasto potencial por AGEB |
| Diferenciación al elegir ubicación | Seim | Competencia cercana y NSE objetivo del giro |

## Límite del marco
Estas teorías son de equilibrio y asumen una elección racional de ubicación. En la práctica el precio de la renta, el local disponible, la seguridad y el flujo peatonal por calle definen la decisión final, y el proyecto no los tiene: la unidad más fina es la AGEB.
