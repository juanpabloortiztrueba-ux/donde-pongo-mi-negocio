# Validacion de config/giros.yaml

Generado por `scripts/validar_giros.py`. Fuentes: `data/processed/scian.csv`, `denue_actual.parquet` (05/2026), `denue_hist.parquet` (11/2020), `enigh_gasto.parquet`.

40 giros, 0 errores, 4 avisos.

```
              clave  denue_actual  denue_hist_2020  compl_estab          rubro_enigh  hogares_con_gasto_pct  ticket  radio_m  ticket_supuesto
          heladeria          6001             4818        13726              helados                    4.7      70      500             True
          cafeteria         20154            17592         9232      ali_fuera_total                   78.4      95      400             True
           gimnasio          5464             4531        12614     gimnasio_deporte                    5.3     550     1500             True
           farmacia         20605            15792        32116           medic_prod                   60.5     190      500             True
          papeleria         35869            35281        13909            papeleria                   28.8      60      400             True
         lavanderia         10342            11546        62166      lavanderia_ropa                    0.4     150      800             True
        veterinaria          4333             3492        27453 veterinaria_mascotas                    7.2     450     1200             True
           taqueria         21930            21055        28027      antojitos_tacos                   28.9     110      400             True
          abarrotes        122955           111151        49932           ali_dentro                   99.1      55      300             True
  barberia_estetica         59483            44811        42075  peluqueria_estetica                   56.0     180      600             True
 consultorio_dental         15049            13265        31046               dental                    8.4     700     1200             True
          guarderia           753              928        37092          coicop_1010                   12.1    3500     1000             True
         ferreteria         16303            14618        33250          coicop_0431                    9.7     180      800             True
         pasteleria          2586             2352        67367         pan_pasteles                   70.8     350      800             True
           libreria           750              739        22764      libros_revistas                    8.7     260     1500             True
   renta_bicicletas             7                9        24655              esparci                   61.8     120     2000             True
        tortilleria         17263            16963       212807             cereales                   97.4      35      300             True
              fonda         23408            22957        19772  restaurante_comidas                   64.5     100      400             True
           pizzeria          3150             2689        11653        comida_rapida                   21.6     220     1000             True
             optica          4226             3518        32244         coicop_06131                    3.3    1500     1500             True
        tienda_ropa         27310            21874        43470              vestido                   68.1     450     1000             True
          zapateria          6280             6750        41305              calzado                   55.8     550     1000             True
         cerrajeria          2881             2852        10382          coicop_0432                   17.0     250     1500             True
    taller_mecanico         22772            21832        20697             mantenim                   47.4    1800     1500             True
       purificadora          9191             6741       132017          coicop_0125                   53.2      40      700             True
          panaderia         10743             9787       198914         pan_pasteles                   70.8      60      400             True
    tienda_mascotas          5812             3616        33971          coicop_0932                   15.1     280     1200             True
    escuela_idiomas           489              595         4083          coicop_1050                    0.4    1200     2000             True
                spa          2016             1163        36641           cuida_pers                   98.7     800     1500             True
      cafe_internet          7905            12319        44707            papeleria                   28.8      35      400             True
           floreria          7997             6840        47955          coicop_0931                    9.9     450     1000             True
         carniceria         34263            30780       189879               carnes                   92.5     160      400             True
           fruteria         25875            24175       201288               frutas                   71.8      90      400             True
       comida_china           345              252        28275  restaurante_comidas                   64.5     170     1000             True
              sushi          1006              587        33090  restaurante_comidas                   64.5     280     1500             True
                bar          3418             2485        27655      ali_fuera_total                   78.4     320      800             True
          coworking            41               25        27575        NO ENCONTRADO                    NaN    2800     2000             True
 consultorio_medico         10669            10091        40177      consulta_medica                   37.2     400     1000             True
laboratorio_clinico          1795             1655        46374          coicop_0641                    6.5     450     2000             True
   tienda_celulares          8474             6342        11667          coicop_0812                    3.1     600     1000             True
```

## Avisos

- [renta_bicicletas] giro raro: solo 7 establecimientos en el DENUE actual
- [renta_bicicletas] solo 9 establecimientos en el historico (11/2020)
- [coworking] giro raro: solo 41 establecimientos en el DENUE actual
- [coworking] solo 25 establecimientos en el historico (11/2020)
