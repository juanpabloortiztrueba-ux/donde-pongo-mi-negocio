import { useMemo, useState } from 'react'
import { Download, Plus, X } from 'lucide-react'
import { Toggle } from '../../kit'
import {
  Cabecera, Cargando, EnlaceZona, ErrorApi, Fuente, fijarQuery, fmtNum, fmtPct, fmtPesos, GraficaBarras, gradienteSecuencial, Mapa, Pill,
  SelectorGiro, SelectorMunicipio, titulo, useApi, useDesglose, useTema, type FilaBarra, type VistaProps,
} from '../../comun'
import { Cifra } from './Cifra'
import { descargarCsv, TONOS_GIRO, type CompararResp, type DenueResp, type GiroComparado, type ScoresResp, type SugerirResp } from './util'
import './explorar.css'

const POR_DEFECTO = ['heladeria', 'cafeteria']
const MAX = 4

function normalizar(texto: string | undefined): string[] {
  const lista = [...new Set((texto ?? '').split(',').map((s) => s.trim()).filter(Boolean))].slice(0, MAX)
  return lista.length >= 2 ? lista : POR_DEFECTO
}

/** Un mapa pequeño: el score del giro por AGEB, sus 5 mejores zonas numeradas y, si se pide, los negocios de la competencia. */
function MapaGiro({ clave, indice, giro, competencia }: { clave: string; indice: number; giro: GiroComparado | undefined; competencia: boolean }) {
  const { tema } = useTema()
  const { abierto, abrir } = useDesglose()
  const sc = useApi<ScoresResp>(`/api/scores/${clave}?componentes=false`)
  const den = useApi<DenueResp>(competencia ? `/api/denue/${clave}?max=1500` : null)
  const valores = useMemo(() => sc.datos?.scores, [sc.datos])
  const resaltar = useMemo(() => giro?.top.slice(0, 5).map((z) => z.ageb), [giro])
  const fmt = useMemo(() => (v: number) => `score ${fmtNum(v, 0)} de 100`, [])
  const puntos = useMemo(() => (competencia && den.datos
    ? den.datos.puntos.map(([lon, lat, n]) => ({ lon, lat, color: tema === 'dark' ? '#6ea2ff' : '#2563eb', etiqueta: titulo(n) || undefined }))
    : undefined), [competencia, den.datos, tema])
  return (
    <figure className="exp-mg" data-tono={TONOS_GIRO[indice]}>
      <figcaption>
        <span className="exp-punto" aria-hidden="true" /><b>{giro?.nombre ?? sc.datos?.nombre ?? clave}</b>
        {competencia && den.datos && <small>{fmtNum(den.datos.mostrados)} de {fmtNum(den.datos.total)} negocios</small>}
        {competencia && den.cargando && !den.datos && <small>cargando negocios…</small>}
      </figcaption>
      {sc.error ? <ErrorApi error={sc.error} reintentar={sc.recargar} titulo="No pude cargar este mapa" /> : (
        <Mapa valores={valores} dominio={[0, 100]} formatoValor={fmt} resaltar={resaltar} puntos={puntos} sinLeyenda interruptorBase={false}
          alto="clamp(300px, 46vh, 380px)" seleccion={abierto?.cvegeo ?? null} volarASeleccion={false}
          onClic={(cv, p) => abrir(cv, { giro: clave, colonia: p.colonia, municipio: p.municipio })} />
      )}
    </figure>
  )
}

type Metrica = { clave: string; etq: string; nota: string; valor: (g: GiroComparado) => number | null; formato: (n: number) => string; fuente: string; mejor?: boolean }

export default function Comparar({ ruta }: VistaProps) {
  const { tema } = useTema()
  const claves = useMemo(() => normalizar(ruta.query.giros), [ruta.query.giros])
  const municipio = ruta.query.mun || null
  const [competencia, setCompetencia] = useState(false)
  const [nse, setNse] = useState<string>('')
  const [ticket, setTicket] = useState<string>('')

  const cmp = useApi<CompararResp>(`/api/comparar?giros=${claves.join(',')}`)
  const giros = cmp.datos?.giros
  const porClave = useMemo(() => new Map((giros ?? []).map((g) => [g.clave, g])), [giros])
  const fuentes = cmp.datos?.fuentes

  const fijar = (lista: string[]) => fijarQuery({ giros: lista.join(',') })
  const cambiar = (i: number, c: string | null) => { if (c) fijar([...new Set(claves.map((x, j) => (j === i ? c : x)))]) }
  const quitar = (i: number) => fijar(claves.filter((_, j) => j !== i))
  const agregar = (c: string | null) => { if (c && !claves.includes(c)) fijar([...claves, c]) }
  const irAComparar = (c: string) => {
    fijar(claves.includes(c) ? claves : claves.length < MAX ? [...claves, c] : [...claves.slice(0, MAX - 1), c])
    document.getElementById('exp-comparar')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const metricas: Metrica[] = useMemo(() => [
    { clave: 'den', etq: 'Negocios del giro en el DENUE', nota: 'competencia directa hoy', valor: (g) => g.negocios_denue, formato: (n) => fmtNum(n), fuente: fuentes?.negocios_denue ?? '' },
    { clave: 'hist', etq: 'Negocios del giro en el DENUE', nota: 'cinco años antes', valor: (g) => g.negocios_denue_hist, formato: (n) => fmtNum(n), fuente: fuentes?.negocios_denue_hist ?? '' },
    { clave: 'ape', etq: 'Aperturas en el periodo', nota: 'aparecieron entre los dos cortes', valor: (g) => g.aperturas, formato: (n) => fmtNum(n), fuente: 'modelo propio: DENUE 11/2020 contra 05/2026' },
    { clave: 'tasa', etq: 'AGEB donde apareció al menos un negocio', nota: 'tasa base', valor: (g) => g.tasa_base_pct, formato: (n) => fmtPct(n, 1), fuente: 'modelo propio: models/metricas_giro.csv' },
    { clave: 'auc', etq: 'AUC del modelo de este giro', nota: '0.5 = azar, 1 = perfecto', valor: (g) => g.auc, formato: (n) => fmtNum(n, 3), fuente: 'modelo propio, validación por municipio' },
    { clave: 'pa', etq: 'Prob. media de apertura por AGEB', nota: 'en 5.5 años', valor: (g) => g.prob_apertura_media_pct, formato: (n) => fmtPct(n, 1), fuente: 'modelo propio', mejor: true },
    { clave: 'ps', etq: 'Prob. media de seguir abierto', nota: 'de un local nuevo', valor: (g) => g.prob_sigue_abierto_media_pct, formato: (n) => fmtPct(n, 1), fuente: 'modelo propio (modelo débil)', mejor: true },
    { clave: 'via', etq: 'Viabilidad media', nota: 'apertura × seguir abierto', valor: (g) => g.viabilidad_media_pct, formato: (n) => fmtPct(n, 1), fuente: 'modelo propio', mejor: true },
    { clave: 'tic', etq: 'Ticket promedio por venta', nota: 'supuesto del proyecto', valor: (g) => g.ticket_promedio_mxn, formato: (n) => fmtPesos(n), fuente: fuentes?.ticket_y_radio ?? '' },
    { clave: 'rad', etq: 'Radio de influencia', nota: 'supuesto del proyecto', valor: (g) => g.radio_influencia_m, formato: (n) => `${fmtNum(n)} m`, fuente: fuentes?.ticket_y_radio ?? '' },
  ], [fuentes])

  const barras: FilaBarra[] = useMemo(() => (giros ?? []).filter((g) => g.viabilidad_media_pct != null).map((g, i) => ({ etiqueta: g.nombre, valor: g.viabilidad_media_pct as number, tono: TONOS_GIRO[i] })), [giros])

  const descargarComparacion = () => {
    if (!giros) return
    descargarCsv('comparar_giros.csv', [
      ['metrica', ...giros.map((g) => g.nombre), 'fuente'],
      ...metricas.map((m) => [`${m.etq} (${m.nota})`, ...giros.map((g) => m.valor(g)), m.fuente]),
      ['Mejor municipio (mayor score medio)', ...giros.map((g) => g.mejor_municipio?.municipio ?? 'NO ENCONTRADO'), 'modelo propio'],
    ])
  }
  const descargarTop = () => {
    if (!giros) return
    descargarCsv('comparar_top10.csv', [
      ['giro', 'posicion', 'colonia', 'municipio', 'ageb', 'score_relativo_0_100', 'prob_apertura_pct', 'prob_sigue_abierto_pct', 'competidores_ponderados', 'nse_estimado', 'fuente'],
      ...giros.flatMap((g) => g.top.map((z) => [g.nombre, z.posicion, z.colonia, z.municipio, z.ageb, z.score, z.prob_apertura_pct, typeof z.prob_sigue_abierto_pct === 'number' ? z.prob_sigue_abierto_pct : null,
        z.competidores_ponderados, z.nse_estimado, 'modelo propio (recomendar_zonas, una zona por colonia)'])),
    ])
  }

  // ---- ¿Qué negocio pongo en mi municipio?
  const qs = new URLSearchParams({ top: '8' })
  if (municipio) qs.set('municipio', municipio)
  if (nse) qs.set('nse', nse)
  if (ticket) qs.set('ticket_max', ticket)
  const sug = useApi<SugerirResp>(`/api/sugerir?${qs}`)
  const barrasSug: FilaBarra[] = useMemo(() => (sug.datos?.giros ?? []).map((g, i) => ({ etiqueta: g.nombre, valor: g.viabilidad_pct, tono: i === 0 ? 'naranja' : 'gris' })), [sug.datos])
  const descargarSug = () => {
    if (!sug.datos?.giros) return
    descargarCsv('que_negocio_pongo.csv', [
      ['giro', 'viabilidad_pct', 'prob_apertura_pct', 'prob_sigue_abierto_pct', 'score_relativo_medio_top10', 'ticket_promedio_mxn', 'fuente'],
      ...sug.datos.giros.map((g) => [g.nombre, g.viabilidad_pct, g.prob_apertura_pct, g.prob_sigue_abierto_pct, g.score_relativo_medio_top10, g.ticket_promedio_mxn, 'modelo propio; ticket: config/giros.yaml (supuesto)']),
    ])
  }

  return (
    <div className="mc-cuerpo exp">
      <Cabecera seccion="Comparar giros" sub="de 2 a 4 giros"
        titulo={<>Qué giro le queda mejor a la ZMVM: <em>compáralos</em> con números absolutos</>}>
        El score de cada giro sirve para ordenar colonias dentro de ese giro. Para elegir entre giros se comparan sus probabilidades de apertura y de seguir abierto.
      </Cabecera>

      <section id="exp-comparar" className="exp-sel" aria-label="Giros a comparar">
        <div className="exp-sel__giros">
          {claves.map((c, i) => (
            <div key={c} className="exp-sel__giro" data-tono={TONOS_GIRO[i]}>
              <span className="exp-punto" aria-hidden="true" />
              <SelectorGiro valor={c} onCambio={(n) => cambiar(i, n)} etiqueta={`Giro ${'ABCD'[i]}`} />
              {claves.length > 2 && <button type="button" className="exp-x" onClick={() => quitar(i)} aria-label={`Quitar ${giros?.find((g) => g.clave === c)?.nombre ?? c}`}><X size={15} /></button>}
            </div>
          ))}
          {claves.length < MAX && <SelectorGiro valor={null} onCambio={agregar} etiqueta="Agregar" vacio="Otro giro…" className="exp-sel__mas" />}
        </div>
        <button type="button" className="exp-toggle" role="switch" aria-checked={competencia} onClick={() => setCompetencia((x) => !x)}>
          <Toggle on={competencia} aria-hidden="true" /><span>Mostrar la competencia en los mapas</span>
        </button>
      </section>

      {cmp.error ? <ErrorApi error={cmp.error} reintentar={cmp.recargar} titulo="No pude comparar estos giros" /> : (
        <>
          <section aria-label="Mapas del score">
            <div className="exp-mapas" data-n={claves.length}>
              {claves.map((c, i) => <MapaGiro key={c} clave={c} indice={i} giro={porClave.get(c)} competencia={competencia} />)}
            </div>
            <div className="exp-leyenda" aria-label="Escala del score">
              <span>0</span><i style={{ background: gradienteSecuencial(tema) }} /><span>100</span>
              <em>score del giro (percentil dentro de cada giro). Los números marcan las 5 mejores zonas de cada uno; haz clic en una colonia para abrir su desglose.</em>
            </div>
            <Fuente>modelo propio (models/scores_giros.parquet, score 0–100 relativo a cada giro){competencia ? `; competencia: ${fuentes?.negocios_denue ?? 'DENUE'}, muestra de hasta 1,500 negocios por giro` : ''}. Polígonos: Marco Geoestadístico 2020 INEGI.</Fuente>
          </section>

          <section aria-label="Tabla comparativa">
            <div className="exp-tabla__cab">
              <h2 className="seccion-t">Giro contra giro</h2>
              <button type="button" className="c-boton" onClick={descargarComparacion} disabled={!giros}><Download size={15} aria-hidden="true" />Descargar CSV</button>
            </div>
            {!giros ? <Cargando forma="lista" filas={6} /> : (
              <div className="exp-tabla__caja">
                <table className="exp-tabla exp-cmp" style={{ ['--n' as string]: giros.length }}>
                  <thead>
                    <tr>
                      <th scope="col">Medida</th>
                      {giros.map((g, i) => <th key={g.clave} scope="col" className="num" data-tono={TONOS_GIRO[i]}><span className="exp-punto" aria-hidden="true" />{g.nombre}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {metricas.map((m) => {
                      const vs = giros.map((g) => m.valor(g))
                      const mx = m.mejor ? Math.max(...vs.filter((v): v is number => v != null)) : null
                      return (
                        <tr key={m.clave}>
                          <th scope="row"><span>{m.etq}</span><small>{m.nota}. Fuente: {m.fuente}</small></th>
                          {giros.map((g, i) => (
                            <td key={g.clave} className="num" data-giro={g.nombre} data-mejor={mx != null && vs[i] === mx && giros.length > 1 ? 'true' : undefined}>
                              <Cifra valor={vs[i]} formato={m.formato} retraso={i * 60} />
                            </td>
                          ))}
                        </tr>
                      )
                    })}
                    <tr>
                      <th scope="row"><span>Municipio con mayor score medio</span><small>entre los que tienen 10 AGEB o más. Fuente: modelo propio</small></th>
                      {giros.map((g) => <td key={g.clave} className="num exp-cmp__txt" data-giro={g.nombre}>{g.mejor_municipio ? <>{g.mejor_municipio.municipio}<small>{fmtPct(g.mejor_municipio.prob_apertura_media_pct, 1)} prob. de apertura</small></> : <span className="exp-nd">NO ENCONTRADO</span>}</td>)}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
            {cmp.datos && (
              <ul className="chico exp-notas">
                <li>{cmp.datos.notas.viabilidad}.</li>
                <li>{cmp.datos.notas.score}.</li>
                <li>Aperturas: {cmp.datos.notas.aperturas}.</li>
              </ul>
            )}
          </section>

          {barras.length > 0 && (
            <section aria-label="Viabilidad">
              <GraficaBarras titulo="Viabilidad media por AGEB (prob. de apertura × prob. de seguir abierto)" filas={barras} formato={(v) => fmtPct(v, 1)} formatoEje={(v) => fmtPct(v, 0)}
                fuente="modelo propio (models/scores_giros.parquet): promedio de las 5,875 AGEB de la ZMVM" alto={Math.max(150, 62 * barras.length)} />
            </section>
          )}

          <section aria-label="Las diez mejores zonas de cada giro">
            <div className="exp-tabla__cab">
              <h2 className="seccion-t">Las 10 mejores zonas de cada giro</h2>
              <button type="button" className="c-boton" onClick={descargarTop} disabled={!giros}><Download size={15} aria-hidden="true" />Descargar CSV</button>
            </div>
            {!giros ? <Cargando forma="lista" filas={5} /> : (
              <div className="exp-tops" data-n={giros.length}>
                {giros.map((g, i) => (
                  <div key={g.clave} className="exp-top" data-tono={TONOS_GIRO[i]}>
                    <h3><span className="exp-punto" aria-hidden="true" />{g.nombre}</h3>
                    <ol>
                      {g.top.map((z) => (
                        <li key={z.ageb}>
                          <EnlaceZona cvegeo={z.ageb} giro={g.clave} colonia={z.colonia} municipio={z.municipio}>
                            <span className="exp-top__n">{z.posicion}</span>
                            <span className="exp-top__t"><b>{titulo(z.colonia)}</b><small>{z.municipio} · prob. de apertura {fmtPct(z.prob_apertura_pct, 0)}</small></span>
                            <span className="exp-top__v">{fmtNum(z.score, 0)}</span>
                          </EnlaceZona>
                        </li>
                      ))}
                    </ol>
                    {g.avisos.aviso_prob_baja && <p className="chico exp-top__aviso">Ojo: {g.avisos.aviso_prob_baja}.</p>}
                  </div>
                ))}
              </div>
            )}
            <Fuente>modelo propio (recomendar_zonas: la mejor AGEB de cada colonia). El número de la derecha es el score 0–100, relativo al giro.</Fuente>
          </section>
        </>
      )}

      <section className="exp-sug" aria-label="¿Qué negocio pongo en mi municipio?">
        <h2 className="exp-sug__t">¿Qué negocio pongo en mi municipio?</h2>
        <p className="exp-sug__expl">
          Aquí no se compara el score: <b>el score es relativo dentro de cada giro</b> (una librería puede sacar 90 y aun así abrir en solo 3 de cada 100 AGEB).
          Los giros se ordenan por <b>viabilidad = probabilidad de apertura × probabilidad de seguir abierto</b>, dos probabilidades absolutas que sí se pueden comparar entre giros.
          Se calcula con las 10 AGEB de mejor score de cada giro en tu filtro.
        </p>
        <div className="exp-sug__ctrl">
          <SelectorMunicipio valor={municipio} onCambio={(c) => fijarQuery({ mun: c })} />
          <div className="exp-seg" role="group" aria-label="Nivel socioeconómico">
            <span className="c-campo__t">Nivel de la zona</span>
            {[['', 'Todos'], ['bajo', 'Bajo'], ['medio', 'Medio'], ['alto', 'Alto']].map(([v, t]) => (
              <button key={v} type="button" data-on={nse === v || undefined} aria-pressed={nse === v} onClick={() => setNse(v)}>{t}</button>
            ))}
          </div>
          <label className="c-campo">
            <span className="c-campo__t">Ticket por venta</span>
            <select className="c-select" value={ticket} onChange={(e) => setTicket(e.target.value)}>
              <option value="">Sin tope</option>
              {[50, 100, 200, 500, 1000].map((t) => <option key={t} value={t}>Hasta {fmtPesos(t)}</option>)}
            </select>
          </label>
        </div>
        {sug.error ? <ErrorApi error={sug.error} reintentar={sug.recargar} titulo="No pude sugerir giros" /> : !sug.datos ? <Cargando forma="lista" filas={5} /> : !sug.datos.encontrado || !sug.datos.giros?.length ? (
          <p className="exp-sug__vacio">{sug.datos.motivo ?? 'NO ENCONTRADO: ningún giro cumple esos filtros.'}</p>
        ) : (
          <>
            <GraficaBarras titulo={`Giros con mayor viabilidad en ${municipio ? (sug.datos.filtros?.municipio as string) ?? 'el municipio' : 'la ZMVM'}`}
              filas={barrasSug} formato={(v) => fmtPct(v, 0)} onClic={(fila) => { const g = sug.datos?.giros?.find((x) => x.nombre === fila.etiqueta); if (g) irAComparar(g.giro) }}
              fuente="modelo propio: prob. de apertura × prob. de seguir abierto, media de las 10 AGEB de mejor score de cada giro" alto={Math.max(180, 46 * barrasSug.length)} />
            <div className="exp-tabla__cab">
              <span className="chico">Un clic en una barra o en «Comparar» suma el giro a la comparación de arriba.</span>
              <button type="button" className="c-boton" onClick={descargarSug}><Download size={15} aria-hidden="true" />Descargar CSV</button>
            </div>
            <div className="exp-tabla__caja">
              <table className="exp-tabla exp-sugtab">
                <thead><tr><th>Giro</th><th className="num">Viabilidad</th><th className="num">Prob. de apertura</th><th className="num">Prob. de seguir abierto</th><th className="num">Score relativo medio</th><th className="num">Ticket (supuesto)</th><th /></tr></thead>
                <tbody>
                  {sug.datos.giros.map((g) => (
                    <tr key={g.giro}>
                      <th scope="row">{g.nombre}{g.aviso && <Pill tono="amarillo">prob. baja</Pill>}</th>
                      <td className="num exp-sugtab__via"><Cifra valor={g.viabilidad_pct} formato={(n) => fmtPct(n, 0)} /></td>
                      <td className="num">{fmtPct(g.prob_apertura_pct, 0)}</td>
                      <td className="num">{fmtPct(g.prob_sigue_abierto_pct, 0)}</td>
                      <td className="num">{fmtNum(g.score_relativo_medio_top10, 1)}</td>
                      <td className="num">{g.ticket_promedio_mxn != null ? fmtPesos(g.ticket_promedio_mxn) : 'NO ENCONTRADO'}</td>
                      <td className="num"><button type="button" className="exp-link" onClick={() => irAComparar(g.giro)}><Plus size={14} aria-hidden="true" />Comparar</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {sug.datos.metodo && <p className="chico exp-sug__metodo">Cómo se calcula: {sug.datos.metodo}.</p>}
            <Fuente>modelo propio (models/scores_giros.parquet y models/metadata.json); ticket por venta: config/giros.yaml, supuesto del proyecto.</Fuente>
          </>
        )}
      </section>
    </div>
  )
}
