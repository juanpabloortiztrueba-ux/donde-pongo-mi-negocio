import { useMemo, useState, type ReactNode } from 'react'
import { Cabecera, Cargando, ErrorApi, fmtNum, fmtPct, fmtPesos, Fuente, GraficaLineas, Kpi, Pill, useApi, type VistaProps } from '../../comun'
import { EscenaScrub } from './EscenaScrub'
import { Opciones, Seccion } from './ui'
import { fecha, type Indicador, type MacroResp, type SerieMacro } from './util'
import './contexto.css'

// Vista Macro: el entorno económico para quien abre un negocio. Los KPI salen de data/processed/macro.json (último dato, con fecha y serie)
// y las gráficas, de data/processed/macro_series.parquet (scripts/01d_macro_series.py). Las lecturas calculan sus cifras de las series:
// no hay números escritos a mano. Ninguna lectura es consejo de inversión ni de crédito.

const mesMenos = (mes: string, n: number) => {
  const [a, m] = mes.split('-').map(Number)
  const t = a * 12 + (m - 1) - n
  return `${Math.floor(t / 12)}-${String((t % 12) + 1).padStart(2, '0')}`
}
const ultimo = (s?: SerieMacro): [string, number] | null => (s && s.puntos.length ? s.puntos[s.puntos.length - 1] : null)
const en = (s: SerieMacro | undefined, mes: string): number | null => s?.puntos.find((p) => p[0] === mes)?.[1] ?? null
const extremo = (s: SerieMacro | undefined, cual: 'max' | 'min'): [string, number] | null => {
  if (!s || !s.puntos.length) return null
  return s.puntos.reduce((a, p) => (cual === 'max' ? (p[1] > a[1] ? p : a) : (p[1] < a[1] ? p : a)))
}
const pct2 = (v: number | null | undefined) => fmtPct(v, 2)
const pesos2 = (v: number | null | undefined) => fmtPesos(v, 2)
const ND = 'NO ENCONTRADO'
/** Valor de la serie 12 meses antes de su último dato. */
const hace12 = (s: SerieMacro | undefined) => { const u = ultimo(s); return u ? en(s, mesMenos(u[0], 12)) : null }

/** «Hace un año» de una serie: el valor del mismo mes del año anterior, con la forma en que se agregó (cierre, promedio o dato). */
function haceUnAnio(s: SerieMacro | undefined, f: (v: number) => string): string | null {
  const u = ultimo(s)
  if (!s || !u) return null
  const mes = mesMenos(u[0], 12)
  const v = en(s, mes)
  if (v == null) return null
  const como = s.agregacion === 'cierre' ? ' (al cierre del mes)' : s.agregacion === 'promedio' ? ' (promedio del mes)' : ''
  return `${fecha(mes)}: ${f(v)}${como}`
}

function KpiMacro({ ind, serie, etiqueta, formato, retraso, tono }: { ind?: Indicador; serie?: SerieMacro; etiqueta: string; formato: (n: number) => string; retraso: number; tono?: 'accent' }) {
  const fuente = ind?.id_serie ? `${ind.fuente?.startsWith('Banco') ? 'Banxico, SIE' : 'INEGI, BIE'} (serie ${ind.id_serie}), dato del ${fecha(ind.fecha)}` : undefined
  const antes = haceUnAnio(serie, formato)
  return (
    <div className="ctx-kpi">
      <Kpi valor={ind?.valor} etiqueta={etiqueta} fuente={fuente} formato={formato} retraso={retraso} tono={tono} />
      {antes && <p className="ctx-kpi__antes">Hace un año, en {antes}</p>}
    </div>
  )
}

type Rango = 'todo' | '5' | '2'
const RANGOS: { id: Rango; texto: string }[] = [{ id: 'todo', texto: 'Desde 2015' }, { id: '5', texto: 'Últimos 5 años' }, { id: '2', texto: 'Últimos 2 años' }]
const recorta = (s: SerieMacro, r: Rango) => (r === 'todo' ? s.puntos : s.puntos.slice(-(r === '5' ? 60 : 24)))
const pie = (s: SerieMacro) => `${s.fuente.split(';')[0]}; ${s.agregacion === 'cierre' ? 'valor al cierre de cada mes' : s.agregacion === 'promedio' ? 'promedio de cada mes' : 'un dato por mes'}`

function Grafica({ series, formatoY, rango, alto = 260, titulo }: { series: SerieMacro[]; formatoY: (v: number) => string; rango: Rango; alto?: number; titulo?: string }) {
  return (
    <GraficaLineas titulo={titulo} alto={alto} formatoY={formatoY} formatoX={(x) => fecha(String(x))}
      series={series.map((s) => ({ nombre: s.nombre, tono: s.tono, puntos: recorta(s, rango).map(([x, y]) => ({ x, y })) }))}
      fuente={series.map(pie).filter((v, i, a) => a.indexOf(v) === i).join(' · ')} />
  )
}

function Lectura({ titulo, children }: { titulo: string; children: ReactNode }) {
  return (
    <aside className="ctx-lect">
      <b>{titulo}</b>
      {children}
    </aside>
  )
}
const N = ({ children }: { children: ReactNode }) => <strong className="ctx-n">{children}</strong>

export default function Macro(_: VistaProps) {
  const { datos: d, error, cargando, recargar } = useApi<MacroResp>('/api/macro')
  const [rango, setRango] = useState<Rango>('todo')
  const S = useMemo(() => Object.fromEntries((d?.series ?? []).map((s) => [s.clave, s])) as Record<string, SerieMacro | undefined>, [d])
  const I = d?.indicadores ?? {}
  const tasa = S.tasa_objetivo, tiie = S.tiie_28, fix = S.tipo_cambio_fix, inf = S.inpc_general_var_anual, merc = S.inpc_mercancias_var_anual, agro = S.inpc_agropecuarios_var_anual
  const conf = S.confianza_consumidor, cons = S.consumo_privado_var_anual, rem = S.remesas
  const uT = ultimo(tasa), uTi = ultimo(tiie), uF = ultimo(fix), uI = ultimo(inf), uM = ultimo(merc), uA = ultimo(agro), uC = ultimo(conf), uP = ultimo(cons), uR = ultimo(rem)
  const maxT = extremo(tasa, 'max'), minT = extremo(tasa, 'min'), maxF = extremo(fix, 'max'), minF = extremo(fix, 'min')
  const kpiRem = I.remesas
  const fix12 = hace12(fix)

  if (error && !d) return <div className="mc-cuerpo"><Cabecera seccion="Macro" titulo={<>Macro</>} /><ErrorApi error={error} reintentar={recargar} titulo="No pude leer las series macro" /></div>

  return (
    <div className="mc-cuerpo ctx">
      <Cabecera seccion="Macro" sub="Banxico e INEGI" titulo={<>Las tasas, los precios y el dólar <em>que mueven a un negocio</em></>}>
        Series reales desde 2015. Sirven para entender el entorno en el que abre un negocio nuevo; no son una recomendación de inversión ni de crédito.
      </Cabecera>
      {d?.aviso && <p className="ctx-aviso" role="status">{d.aviso}</p>}

      <Seccion kicker="Lo más reciente">
        {cargando && !d ? <Cargando forma="kpis" filas={4} /> : (
          <div className="ctx-kpis">
            <KpiMacro ind={I.tasa_objetivo} serie={tasa} etiqueta="Tasa objetivo de Banxico" formato={pct2} retraso={0} tono="accent" />
            <KpiMacro ind={I.tiie_28} serie={tiie} etiqueta="TIIE a 28 días" formato={pct2} retraso={70} />
            <KpiMacro ind={I.tipo_cambio_fix} serie={fix} etiqueta="Tipo de cambio FIX, pesos por dólar" formato={pesos2} retraso={140} />
            <KpiMacro ind={I.inpc_general_var_anual} serie={inf} etiqueta="Inflación anual (INPC general)" formato={pct2} retraso={210} />
            <KpiMacro ind={I.confianza_consumidor} serie={conf} etiqueta="Confianza del consumidor, puntos" formato={(n) => fmtNum(n, 1)} retraso={280} />
            <KpiMacro ind={I.consumo_privado} serie={cons} etiqueta="Consumo privado, variación anual" formato={pct2} retraso={350} />
            <div className="ctx-kpi">
              <Kpi valor={kpiRem?.valor} etiqueta="Remesas familiares, millones de dólares en el mes" formato={(n) => fmtNum(n, 0)} retraso={420}
                fuente={kpiRem?.id_serie ? `Banxico, SIE (serie ${kpiRem.id_serie}), dato de ${fecha(kpiRem.fecha)}` : undefined} />
              {kpiRem?.acumulado_12_meses_millones_usd != null && <p className="ctx-kpi__antes">En 12 meses suman {fmtNum(kpiRem.acumulado_12_meses_millones_usd, 0)} millones de dólares</p>}
            </div>
            <div className="ctx-kpi">
              <Kpi valor={I.inpc_alimentos_var_anual?.estado === 'NO ENCONTRADO' ? null : (I.inpc_alimentos_var_anual as Indicador | undefined)?.valor} etiqueta="Inflación de alimentos (INPC)" retraso={490}
                fuente={`INEGI y Banxico: no está en sus API (búsqueda del ${fecha(I.inpc_alimentos_var_anual?.consultado)})`} />
              <p className="ctx-kpi__antes">Como aproximación, abajo se usan la inflación de mercancías y la de agropecuarios.</p>
            </div>
          </div>
        )}
        <p className="chico ctx-nota">Cada cifra es el último dato publicado de su serie, con su fecha. «Hace un año» compara con el mismo mes del año anterior.</p>
      </Seccion>

      <Seccion kicker="Lee un mes" titulo={<>Pasa por la línea y <em>lee el mes</em> que toca</>}>
        <div className="ctx-lee">
          <div className="ctx-lee__txt">
            <p>El dólar es el indicador que más rápido le llega a un negocio que compra insumos o equipo importado. Aquí el puntero recorre el tipo de cambio mes por mes, con sus cifras reales: lo que se lee arriba es el promedio de ese mes.</p>
            <p>En las gráficas de abajo haz lo mismo con el ratón o con el dedo: pasa sobre cualquier línea y te dice el valor de ese mes.</p>
            {maxF && minF && <p className="chico">Desde 2015, el FIX mensual tuvo su máximo en {fecha(maxF[0])} ({pesos2(maxF[1])}) y su mínimo en {fecha(minF[0])} ({pesos2(minF[1])}).</p>}
          </div>
          <div className="ctx-lee__esc">
            {fix ? <EscenaScrub serie={fix} formato={pesos2} titulo="Tipo de cambio FIX · promedio mensual" /> : <Cargando forma="mapa" alto={340} />}
            {fix && <Fuente>{pie(fix)}.</Fuente>}
          </div>
        </div>
      </Seccion>

      <Seccion kicker="Las series" titulo={<>Qué significa cada una <em>para quien abre un negocio</em></>}>
        <div className="ctx-rango"><Opciones<Rango> etiqueta="Rango de las gráficas" valor={rango} opciones={RANGOS} onCambio={setRango} /></div>

        <div className="ctx-grupo">
          <div className="ctx-grupo__graf">
            <h4 className="ctx-grupo__t">Crédito <Pill tono="naranja">tasas</Pill></h4>
            {tasa && tiie ? <Grafica series={[tasa, tiie]} formatoY={(v) => `${fmtNum(v, 1)}%`} rango={rango} /> : <Cargando forma="mapa" alto={260} />}
          </div>
          <Lectura titulo="Qué significa para ti">
            <p>La tasa objetivo está en <N>{uT ? pct2(uT[1]) : ND}</N> y hace un año estaba en <N>{pct2(hace12(tasa))}</N>. Su máximo desde 2015 fue <N>{maxT ? pct2(maxT[1]) : ND}</N> ({maxT ? fecha(maxT[0]) : ND}) y su mínimo, <N>{minT ? pct2(minT[1]) : ND}</N> ({minT ? fecha(minT[0]) : ND}).</p>
            <p>La TIIE a 28 días ({pct2(I.tiie_28?.valor)}, al {fecha(I.tiie_28?.fecha)}) es la tasa de referencia con la que suelen fijarse los créditos empresariales a tasa variable. Si baja, financiar inventario o equipo cuesta menos; cada banco suma además su propia sobretasa, que esta serie no trae.</p>
          </Lectura>
        </div>

        <div className="ctx-grupo">
          <div className="ctx-grupo__graf">
            <h4 className="ctx-grupo__t">Costos <Pill tono="azul">inflación</Pill></h4>
            {inf && merc && agro ? <Grafica series={[inf, merc, agro]} formatoY={(v) => `${fmtNum(v, 1)}%`} rango={rango} /> : <Cargando forma="mapa" alto={260} />}
          </div>
          <Lectura titulo="Qué significa para ti">
            <p>Los precios al consumidor suben <N>{uI ? pct2(uI[1]) : ND}</N> al año; las mercancías, <N>{uM ? pct2(uM[1]) : ND}</N>, y los agropecuarios, <N>{uA ? pct2(uA[1]) : ND}</N> ({uI ? fecha(uI[0]) : ND}).</p>
            <p>Es, en promedio, el ritmo al que se encarece lo que un negocio compra a sus proveedores. Si sus precios no avanzan al mismo paso que sus costos, el margen se achica. El índice de alimentos no está disponible; mercancías y agropecuarios son la aproximación más cercana que publican las fuentes.</p>
          </Lectura>
        </div>

        <div className="ctx-grupo">
          <div className="ctx-grupo__graf">
            <h4 className="ctx-grupo__t">Insumos importados <Pill tono="naranja">dólar</Pill></h4>
            {fix ? <Grafica series={[fix]} formatoY={(v) => fmtPesos(v, Number.isInteger(v) ? 0 : Math.round(v * 10) === v * 10 ? 1 : 2)} rango={rango} /> : <Cargando forma="mapa" alto={260} />}
          </div>
          <Lectura titulo="Qué significa para ti">
            <p>Con el FIX en <N>{pesos2(I.tipo_cambio_fix?.valor)}</N> ({fecha(I.tipo_cambio_fix?.fecha)}), un insumo o un equipo que cuesta 100 dólares vale <N>{I.tipo_cambio_fix?.valor != null ? fmtPesos(100 * I.tipo_cambio_fix.valor, 0) : ND}</N>{fix12 != null ? <>; hace un año, con el dólar a {pesos2(fix12)} (promedio del mes), valía {fmtPesos(100 * fix12, 0)}</> : null}.</p>
            <p>Un dólar más caro encarece lo que se compra o se cotiza en dólares (maquinaria, refrigeración, tecnología, algunos empaques); uno más barato lo abarata. Cuánto le pega a un negocio depende de qué parte de sus compras es importada.</p>
          </Lectura>
        </div>

        <div className="ctx-grupo">
          <div className="ctx-grupo__graf">
            <h4 className="ctx-grupo__t">Consumo <Pill tono="azul">gasto de la gente</Pill></h4>
            <div className="ctx-dos">
              {conf ? <Grafica series={[conf]} formatoY={(v) => fmtNum(v, 0)} rango={rango} alto={240} titulo="Confianza del consumidor (puntos)" /> : <Cargando forma="mapa" alto={240} />}
              {cons ? <Grafica series={[cons]} formatoY={(v) => `${fmtNum(v, 0)}%`} rango={rango} alto={240} titulo="Consumo privado, variación anual (%)" /> : <Cargando forma="mapa" alto={240} />}
            </div>
          </div>
          <Lectura titulo="Qué significa para ti">
            <p>La confianza del consumidor está en <N>{uC ? fmtNum(uC[1], 1) : ND}</N> puntos ({uC ? fecha(uC[0]) : ND}); hace un año estaba en <N>{fmtNum(hace12(conf), 1)}</N>. El consumo privado creció <N>{uP ? pct2(uP[1]) : ND}</N> en volumen en {uP ? fecha(uP[0]) : ND}, contra el mismo mes del año anterior.</p>
            <p>Son el pulso de cuánto está dispuesta a gastar la gente en general. No dicen cuánto gasta la de una colonia: eso lo estima el modelo con la ENIGH 2024.</p>
          </Lectura>
        </div>

        <div className="ctx-grupo">
          <div className="ctx-grupo__graf">
            <h4 className="ctx-grupo__t">Remesas <Pill tono="naranja">hogares</Pill></h4>
            {rem ? <Grafica series={[rem]} formatoY={(v) => fmtNum(v, 0)} rango={rango} titulo="Millones de dólares por mes" /> : <Cargando forma="mapa" alto={260} />}
          </div>
          <Lectura titulo="Qué significa para ti">
            <p>En {uR ? fecha(uR[0]) : ND} llegaron <N>{uR ? fmtNum(uR[1], 0) : ND}</N> millones de dólares en remesas{kpiRem?.variacion_anual_pct != null ? <>, <N>{fmtPct(Math.abs(kpiRem.variacion_anual_pct), 2)}</N> {kpiRem.variacion_anual_pct >= 0 ? 'más' : 'menos'} que un año antes</> : null}. En 12 meses suman <N>{kpiRem?.acumulado_12_meses_millones_usd != null ? fmtNum(kpiRem.acumulado_12_meses_millones_usd, 0) : ND}</N> millones.</p>
            <p>Es dinero que reciben hogares con familiares en el exterior y que se gasta sobre todo en consumo local. El dato es nacional: no dice en qué colonias se concentra, así que no mueve el score de ninguna zona.</p>
          </Lectura>
        </div>
        <p className="chico ctx-nota">Las lecturas describen el entorno con los datos de arriba. No son consejo de inversión, de crédito ni una predicción.</p>
      </Seccion>

      <Seccion kicker="De dónde salen">
        <p className="ctx-par">Las series se bajan de Banxico (SIE) y de INEGI (BIE) con <code>scripts/01d_macro_series.py</code> y se guardan en <code>data/processed/macro_series.parquet</code>. Tasa objetivo, TIIE y tipo de cambio son diarias; aquí se muestran por mes (promedio, y para la tasa objetivo el valor al cierre de cada mes). Los últimos valores salen de <code>data/processed/macro.json</code> (consultado el {fecha(d?.meta.generado)}), o de <code>macro_series.parquet</code> cuando esa serie trae un dato más nuevo de la misma serie.</p>
        <Fuente>{d?.fuente ?? 'Banco de México (SIE) e INEGI (BIE)'}. Series: {(d?.series ?? []).filter((s) => !s.clave.includes('indice')).map((s) => `${s.nombre} (${s.id_serie})`).join(', ')}.</Fuente>
      </Seccion>
    </div>
  )
}
