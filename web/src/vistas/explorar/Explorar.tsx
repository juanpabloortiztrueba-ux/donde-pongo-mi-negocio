import { useEffect, useMemo, useRef, useState } from 'react'
import { Download } from 'lucide-react'
import { Toggle } from '../../kit'
import {
  Cabecera, Cargando, EnlaceZona, ErrorApi, Fuente, fijarQuery, fmtNum, fmtPct, Kpi, Mapa, SelectorMunicipio, titulo, useApi, useDesglose, useTema,
  type VistaProps,
} from '../../comun'
import { Cifra } from './Cifra'
import { Histograma } from './Histograma'
import { descargarCsv, formatoDe, type Estacion, type FilaMunicipio, type MapaResp, type VarMeta } from './util'
import './explorar.css'

type Orden = { col: 'municipio' | 'n_agebs' | 'poblacion' | 'valor' | 'mediana'; dir: 1 | -1 }

export default function Explorar({ ruta }: VistaProps) {
  const { tema } = useTema()
  const { abierto, abrir } = useDesglose()
  const vars = useApi<{ variables: VarMeta[]; grupos: string[]; fuente: string }>('/api/variables')
  const variable = ruta.query.variable || 'densidad'
  const municipio = ruta.query.municipio || null
  const [estaciones, setEstaciones] = useState(false)
  const [orden, setOrden] = useState<Orden>({ col: 'valor', dir: -1 })
  const q = `/api/mapa?variable=${encodeURIComponent(variable)}${municipio ? `&municipio=${municipio}` : ''}`
  const mapa = useApi<MapaResp>(q)
  const est = useApi<{ estaciones: Estacion[]; fuente: string }>(estaciones ? '/api/transporte' : null)
  const d = mapa.datos
  const m = d?.variable ?? null

  const fVal = useMemo(() => (m ? formatoDe(m) : (v: number) => fmtNum(v)), [m])
  const fAgr = useMemo(() => (m ? formatoDe(m, true) : (v: number) => fmtNum(v)), [m])
  const dominio = useMemo<[number, number]>(() => (d ? [d.dominio[0], d.dominio[1]] : [0, 1]), [d])
  const puntos = useMemo(() => (estaciones && est.datos
    ? est.datos.estaciones.map((e) => ({ lon: e.lon, lat: e.lat, color: tema === 'dark' ? '#6ea2ff' : '#2563eb', etiqueta: `${e.sistema}${e.linea ? ` · línea ${e.linea}` : ''} · ${e.estacion}` }))
    : undefined), [estaciones, est.datos, tema])
  const ordinal = m?.formato === 'ordinal'
  const pasos = useMemo(() => (ordinal && m ? Object.keys(m.etiquetas_ordinal ?? {}).map(Number).sort((a, b) => a - b).map((n) => ({ valor: n, nombre: fVal(n) })) : undefined), [ordinal, m, fVal])
  const etiquetaMapa = m ? `${m.etiqueta} (${m.unidad})` : ''

  const filas = useMemo(() => {
    if (!d) return []
    const f = [...d.municipios]
    const v = (r: FilaMunicipio) => (orden.col === 'municipio' ? r.municipio : r[orden.col]) as string | number | null
    return f.sort((a, b) => {
      const x = v(a), y = v(b)
      if (x == null && y == null) return 0
      if (x == null) return 1
      if (y == null) return -1
      return (typeof x === 'string' ? x.localeCompare(y as string, 'es') : (x as number) - (y as number)) * orden.dir
    })
  }, [d, orden])
  // el municipio elegido queda a la vista dentro de la tabla (que tiene su propio scroll), sin mover la página
  const cajaTabla = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const caja = cajaTabla.current, fila = caja?.querySelector<HTMLElement>('tr[data-sel]')
    if (caja && fila) caja.scrollTop = Math.max(0, fila.getBoundingClientRect().top - caja.getBoundingClientRect().top + caja.scrollTop - caja.clientHeight / 2 + fila.offsetHeight / 2)
    else if (caja) caja.scrollTop = 0
  }, [municipio, filas])
  const maxValor = useMemo(() => Math.max(0, ...(d?.municipios ?? []).map((r) => r.valor ?? 0)), [d])
  const nombreMun = d?.resumen.ambito && municipio ? d.resumen.ambito : null

  const cambiarVariable = (c: string) => fijarQuery({ variable: c })
  const cambiarMunicipio = (c: string | null) => fijarQuery({ municipio: c })
  const ordenar = (col: Orden['col']) => setOrden((o) => (o.col === col ? { col, dir: (-o.dir) as 1 | -1 } : { col, dir: col === 'municipio' ? 1 : -1 }))
  const flecha = (col: Orden['col']) => (orden.col === col ? (orden.dir === 1 ? 'ascending' : 'descending') : 'none') as 'ascending' | 'descending' | 'none'

  const descargar = () => {
    if (!d || !m) return
    const enc = ['cvegeo_mun', 'municipio', 'agebs', 'agebs_con_dato', 'poblacion_2020', `${m.etiqueta} (${m.agregacion_texto}; ${m.unidad})`, `${m.etiqueta}, mediana de AGEB (${m.unidad})`, 'fuente']
    descargarCsv(`explorar_${m.clave}.csv`, [enc, ...filas.map((r) => [r.cvegeo_mun, r.municipio, r.n_agebs, r.n_con_dato, r.poblacion, r.valor, r.mediana, m.fuente])])
  }

  const porGrupo = useMemo(() => {
    const g = new Map<string, VarMeta[]>()
    for (const v of vars.datos?.variables ?? []) { if (!g.has(v.grupo)) g.set(v.grupo, []); g.get(v.grupo)!.push(v) }
    return [...g.entries()]
  }, [vars.datos])

  return (
    <div className="mc-cuerpo exp">
      <Cabecera seccion="Explorar la ZMVM" sub="mapa por AGEB"
        titulo={<>{nombreMun ? `${nombreMun}` : 'La ZMVM'}, AGEB por AGEB: <em>{m ? m.etiqueta.toLocaleLowerCase('es-MX') : 'la variable'}</em></>}>
        Cada polígono es una AGEB (el barrio del Censo). Elige una variable, filtra por municipio y haz clic en una colonia para abrir su desglose.
      </Cabecera>

      {vars.error ? <ErrorApi error={vars.error} reintentar={vars.recargar} titulo="No pude leer la lista de variables" /> : (
        <section className="exp-ctrl" aria-label="Variable y filtros">
          <div className="exp-vars" role="group" aria-label="Variable del mapa">
            {porGrupo.map(([g, vs]) => (
              <div key={g} className="exp-vars__grupo">
                <span className="exp-vars__t">{g}</span>
                <div className="exp-vars__pills">
                  {vs.map((v) => (
                    <button key={v.clave} type="button" className="exp-pill" data-on={v.clave === variable || undefined} aria-pressed={v.clave === variable} onClick={() => cambiarVariable(v.clave)}>{v.etiqueta}</button>
                  ))}
                </div>
              </div>
            ))}
            {!vars.datos && <Cargando forma="texto" filas={2} />}
          </div>
          <label className="c-campo exp-vars__menu">
            <span className="c-campo__t">Variable</span>
            <select className="c-select" value={variable} onChange={(e) => cambiarVariable(e.target.value)} disabled={!vars.datos}>
              {porGrupo.map(([g, vs]) => <optgroup key={g} label={g}>{vs.map((v) => <option key={v.clave} value={v.clave}>{v.etiqueta}</option>)}</optgroup>)}
            </select>
          </label>
          <div className="exp-ctrl__fila">
            <SelectorMunicipio valor={municipio} onCambio={cambiarMunicipio} />
            <button type="button" className="exp-toggle" role="switch" aria-checked={estaciones} onClick={() => setEstaciones((x) => !x)}>
              <Toggle on={estaciones} aria-hidden="true" /><span>Estaciones de transporte{estaciones && est.cargando ? ' (cargando…)' : estaciones && est.datos ? ` (${fmtNum(est.datos.estaciones.length)})` : ''}</span>
            </button>
          </div>
        </section>
      )}

      {m && (
        <section className="exp-desc" aria-label="Qué mide la variable">
          <p><b>{m.etiqueta}</b> <span className="exp-desc__u">{m.unidad}</span></p>
          <p>{m.descripcion}</p>
          <Fuente>{m.fuente}</Fuente>
        </section>
      )}

      <section aria-label="Cifras del mapa">
        {mapa.error ? <ErrorApi error={mapa.error} reintentar={mapa.recargar} titulo="No pude calcular el mapa" /> : !d || !m ? <Cargando forma="kpis" filas={4} /> : (
          <>
            <div className="exp-kpis">
              <Kpi valor={d.resumen.n_con_dato} etiqueta={`AGEB con dato (de ${fmtNum(d.resumen.n_agebs)})`} fuente="Censo 2020 INEGI, Marco Geoestadístico" />
              <Kpi valor={d.resumen.poblacion} etiqueta="habitantes en esas AGEB" fuente="Censo 2020 INEGI" retraso={80} />
              <Kpi valor={d.resumen.valor} formato={fAgr} etiqueta={`${m.etiqueta}, ${m.agregacion_texto}`} fuente={m.fuente} retraso={160} tono="accent" />
              <Kpi valor={d.resumen.mediana} formato={fAgr} etiqueta="AGEB típica (mediana)" fuente={m.fuente} retraso={240} />
            </div>
            <p className="chico exp-extremos">
              Más alto: <EnlaceZona cvegeo={d.resumen.maximo.cvegeo} colonia={d.resumen.maximo.colonia} municipio={d.resumen.maximo.municipio}>{titulo(d.resumen.maximo.colonia)}, {d.resumen.maximo.municipio}</EnlaceZona> ({d.resumen.maximo.valor != null ? fVal(d.resumen.maximo.valor) : 'NO ENCONTRADO'}).
              Más bajo: <EnlaceZona cvegeo={d.resumen.minimo.cvegeo} colonia={d.resumen.minimo.colonia} municipio={d.resumen.minimo.municipio}>{titulo(d.resumen.minimo.colonia)}, {d.resumen.minimo.municipio}</EnlaceZona> ({d.resumen.minimo.valor != null ? fVal(d.resumen.minimo.valor) : 'NO ENCONTRADO'}).
            </p>
          </>
        )}
      </section>

      <section className="exp-mapa" aria-label="Mapa">
        <Mapa valores={d?.valores} dominio={dominio} etiqueta={etiquetaMapa} formatoValor={fVal} municipio={municipio} puntos={puntos} pasosLeyenda={pasos} radioPuntos={3}
          seleccion={abierto?.cvegeo ?? null} volarASeleccion={false} onClic={(cv, p) => abrir(cv, { colonia: p.colonia, municipio: p.municipio })} alto="clamp(440px, 72vh, 760px)" />
        <p className="chico exp-mapa__pie">Haz clic en una colonia para abrir su desglose, con el enlace a su ficha completa. Las AGEB sin dato salen en gris{ordinal ? '; cada color es un nivel de la escala.' : '; la escala va del percentil 2 al 98 para que unas cuantas AGEB extremas no la aplasten.'}</p>
        {m && <Fuente>{m.fuente}. Polígonos: Marco Geoestadístico 2020 INEGI.{estaciones && est.datos ? ` Estaciones: ${est.datos.fuente}.` : ''}</Fuente>}
      </section>

      {d && m && (
        <section aria-label="Distribución">
          <h2 className="seccion-t">Cómo se distribuyen las {fmtNum(d.histograma.n)} AGEB</h2>
          <div className="exp-dist">
            <Histograma cajas={d.histograma.cajas} formato={fVal} mediana={d.resumen.mediana} extremos={d.histograma.valores_en_extremos}
              fuente={`${m.fuente}, ${nombreMun ?? 'toda la ZMVM'}`} unidad={m.etiqueta} clave={`${m.clave}-${municipio ?? ''}`} />
            <ul className="exp-cuant" aria-label="Cuantiles">
              {d.cuantiles.slice(0, -1).map((c, i) => (
                <li key={c.p}>
                  <span>{i === 0 ? 'Mínimo' : `${fmtPct(c.p * 100, 0)} de las AGEB quedan abajo de`}</span>
                  <b><Cifra valor={c.valor} formato={fVal} retraso={i * 60} plano={m.formato === 'ordinal'} /></b>
                </li>
              ))}
              <li><span>Máximo</span><b><Cifra valor={d.cuantiles[d.cuantiles.length - 1].valor} formato={fVal} retraso={300} plano={m.formato === 'ordinal'} /></b></li>
            </ul>
          </div>
        </section>
      )}

      {d && m && (
        <section aria-label="Municipios">
          <div className="exp-tabla__cab">
            <h2 className="seccion-t">Por municipio y alcaldía</h2>
            <button type="button" className="c-boton" onClick={descargar}><Download size={15} aria-hidden="true" />Descargar CSV</button>
          </div>
          <div className="exp-tabla__caja" data-alta ref={cajaTabla}>
            <table className="exp-tabla exp-tabla--mun">
              <thead>
                <tr>
                  <th aria-sort={flecha('municipio')}><button type="button" onClick={() => ordenar('municipio')}>Municipio</button></th>
                  <th className="num" aria-sort={flecha('n_agebs')}><button type="button" onClick={() => ordenar('n_agebs')}>AGEB</button></th>
                  <th className="num" aria-sort={flecha('poblacion')}><button type="button" onClick={() => ordenar('poblacion')}>Habitantes</button></th>
                  <th aria-sort={flecha('valor')}><button type="button" onClick={() => ordenar('valor')}>{m.etiqueta}<small>{m.agregacion_texto}</small></button></th>
                  <th className="num" aria-sort={flecha('mediana')}><button type="button" onClick={() => ordenar('mediana')}>AGEB típica<small>mediana</small></button></th>
                </tr>
              </thead>
              <tbody>
                {filas.map((r) => (
                  <tr key={r.cvegeo_mun} data-sel={r.cvegeo_mun === municipio || undefined}>
                    <th scope="row"><button type="button" className="exp-tabla__mun" title="Filtrar el mapa a este municipio" onClick={() => cambiarMunicipio(r.cvegeo_mun === municipio ? null : r.cvegeo_mun)}>{r.municipio}</button></th>
                    <td className="num">{fmtNum(r.n_agebs)}</td>
                    <td className="num">{fmtNum(r.poblacion)}</td>
                    <td className="exp-tabla__valor">
                      <span className="exp-tabla__n">{r.valor == null ? 'NO ENCONTRADO' : fAgr(r.valor)}</span>
                      <span className="exp-tabla__barra"><i style={{ width: `${r.valor != null && maxValor > 0 ? Math.max(1, (r.valor / maxValor) * 100) : 0}%` }} /></span>
                    </td>
                    <td className="num">{r.mediana == null ? 'NO ENCONTRADO' : fAgr(r.mediana)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="chico exp-tabla__pie">Clic en un municipio para filtrar el mapa a él; otro clic lo quita. «AGEB» es el número de AGEB urbanas del municipio.</p>
          <Fuente>{m.fuente}; habitantes y AGEB: Censo 2020 INEGI.</Fuente>
        </section>
      )}
    </div>
  )
}
