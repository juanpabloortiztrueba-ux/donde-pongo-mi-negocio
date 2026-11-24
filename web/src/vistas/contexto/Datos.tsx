import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import { ChevronRight, Copy, Check, Download, ExternalLink, Search } from 'lucide-react'
import { apiGet, Cabecera, Cargando, ErrorApi, esCancelado, fijarQuery, fmtNum, Fuente, Kpi, Pill, useApi, useEstado, type VistaProps } from '../../comun'
import { Markdown } from './Markdown'
import { Inline, Opciones, Seccion } from './ui'
import { fecha, fmtBytes, type BusquedaResp, type CarpetasResp, type DescargasResp, type DocResp, type FuentesResp, type NodoCarpeta } from './util'
import './contexto.css'

// Vista «Datos y carpetas»: de dónde sale cada dato (data/FUENTES.md), las carpetas que lee el modelo con visor de Markdown y buscador
// por significado, las descargas y cómo reconstruir todo. Todo sale de /api/fuentes, /api/carpetas, /api/carpetas/doc, /api/carpetas/buscar y /api/descargas.

const DOC_INICIAL = '00_alcance.md'
const corto = (t: string) => (t.split(':')[0] ?? t).replace(/^Etapa /, '')

function antecesores(ruta: string): string[] {
  const p = ruta.split('/').slice(0, -1)
  return p.map((_, i) => p.slice(0, i + 1).join('/'))
}

function Nodo({ n, nivel, abiertos, alternar, activo, abrir }: { n: NodoCarpeta; nivel: number; abiertos: Set<string>; alternar: (r: string) => void; activo: string; abrir: (r: string) => void }) {
  if (n.tipo === 'archivo') {
    return (
      <li>
        <button className="ctx-arbol__arch" data-on={n.ruta === activo || undefined} style={{ paddingLeft: 10 + nivel * 16 }} onClick={() => abrir(n.ruta)} title={n.ruta}>
          <span className="ctx-arbol__nom">{n.titulo || n.nombre}</span>
          <span className="ctx-arbol__n" title="trozos en el índice">{fmtNum(n.trozos)}</span>
        </button>
      </li>
    )
  }
  const abierto = abiertos.has(n.ruta)
  return (
    <li>
      <button className="ctx-arbol__carp" aria-expanded={abierto} style={{ paddingLeft: 4 + nivel * 16 }} onClick={() => alternar(n.ruta)}>
        <ChevronRight size={15} className="ctx-arbol__fl" data-abierto={abierto || undefined} aria-hidden />
        <span className="ctx-arbol__nom"><b>{n.nombre}</b>{n.descripcion && <small>{n.descripcion}</small>}</span>
        <span className="ctx-arbol__n" title="archivos · trozos">{fmtNum(n.archivos)} · {fmtNum(n.trozos)}</span>
      </button>
      {abierto && <ul className="ctx-arbol__lista">{(n.hijos ?? []).map((h) => <Nodo key={h.ruta} n={h} nivel={nivel + 1} abiertos={abiertos} alternar={alternar} activo={activo} abrir={abrir} />)}</ul>}
    </li>
  )
}

function Buscador({ abrir }: { abrir: (ruta: string, seccion?: string) => void }) {
  const [q, setQ] = useState('')
  const [est, setEst] = useState<{ cargando: boolean; datos: BusquedaResp | null; error: Error | null }>({ cargando: false, datos: null, error: null })
  const ac = useRef<AbortController | null>(null)
  useEffect(() => () => ac.current?.abort(), [])
  const buscar = (e: FormEvent) => {
    e.preventDefault()
    const t = q.trim()
    if (!t) return
    ac.current?.abort()
    ac.current = new AbortController()
    setEst({ cargando: true, datos: null, error: null })
    apiGet<BusquedaResp>(`/api/carpetas/buscar?q=${encodeURIComponent(t)}&k=5`, { signal: ac.current.signal })
      .then((datos) => setEst({ cargando: false, datos, error: null }))
      .catch((error) => { if (!esCancelado(error)) setEst({ cargando: false, datos: null, error }) })
  }
  const d = est.datos
  return (
    <div className="ctx-busca">
      <form className="ctx-busca__f" onSubmit={buscar} role="search">
        <Search size={17} aria-hidden />
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Pregunta con tus palabras" aria-label="Buscar en las carpetas" />
        <button type="submit" className="c-boton" disabled={est.cargando || !q.trim()}>{est.cargando ? 'Buscando…' : 'Buscar'}</button>
      </form>
      {est.error && <ErrorApi error={est.error as never} titulo="No pude buscar" />}
      {d && (
        <div className="ctx-busca__res" aria-live="polite">
          <div className="ctx-busca__modo">
            <Pill tono={d.modo === 'vectorial' ? 'verde' : 'amarillo'}>{d.modo === 'vectorial' ? 'Búsqueda por significado' : d.modo === 'lexico' ? 'Búsqueda por palabras' : 'Sin resultados'}</Pill>
            <span className="chico">{d.modo === 'vectorial' ? 'Con embeddings de nomic-embed-text en Ollama.' : d.aviso ?? ''}</span>
          </div>
          {d.resultados.length === 0 && <p className="chico">No encontré trozos parecidos. Prueba con otras palabras.</p>}
          <ol className="ctx-busca__lista">
            {d.resultados.map((r, i) => (
              <li key={i}>
                <button onClick={() => abrir(r.archivo, r.seccion)}>
                  <span className="ctx-busca__ruta">{r.archivo}{r.seccion ? ` › ${r.seccion}` : ''}<em>{r.score != null ? fmtNum(r.score, 2) : ''}</em></span>
                  <span className="ctx-busca__txt"><Inline t={r.texto.replace(/\s+/g, ' ').slice(0, 240) + (r.texto.length > 240 ? '…' : '')} /></span>
                </button>
              </li>
            ))}
          </ol>
          <Fuente>{d.fuente}.</Fuente>
        </div>
      )}
    </div>
  )
}

function Visor({ ruta, abrir, ancla }: { ruta: string; abrir: (r: string) => void; ancla: string | null }) {
  const { datos: doc, error, cargando, recargar } = useApi<DocResp>(`/api/carpetas/doc?ruta=${encodeURIComponent(ruta)}`)
  const cuerpo = useRef<HTMLDivElement>(null)
  useEffect(() => { if (cuerpo.current) cuerpo.current.scrollTop = 0 }, [ruta])
  useEffect(() => {
    if (!ancla || !doc || !cuerpo.current) return
    const hs = Array.from(cuerpo.current.querySelectorAll<HTMLElement>('h2,h3,h4,h5,h6'))
    const h = hs.find((x) => x.textContent?.trim() === ancla) ?? hs.find((x) => (x.textContent ?? '').includes(ancla))
    if (h) cuerpo.current.scrollTo({ top: h.offsetTop - 8, behavior: 'smooth' })
  }, [ancla, doc])
  if (error) return <ErrorApi error={error} reintentar={recargar} titulo="No pude abrir ese archivo" />
  if (cargando || !doc) return <Cargando forma="texto" filas={9} />
  return (
    <article className="ctx-visor">
      <header className="ctx-visor__cab">
        <b>{doc.titulo}</b>
        <span className="chico"><code>carpetas/{doc.ruta}</code> · {fmtBytes(doc.bytes)} · {fmtNum(doc.trozos)} trozos en el índice</span>
      </header>
      <div className="ctx-visor__cuerpo" ref={cuerpo} tabIndex={0}><Markdown md={doc.markdown} ruta={doc.ruta} abrir={abrir} /></div>
    </article>
  )
}

function Copiar({ texto }: { texto: string }) {
  const [ok, setOk] = useState(false)
  const copiar = async () => {
    try { await navigator.clipboard.writeText(texto); setOk(true); setTimeout(() => setOk(false), 1600) } catch { /* sin permiso: se puede seleccionar a mano */ }
  }
  return <button className="c-boton ctx-copiar" onClick={copiar} aria-label="Copiar el comando">{ok ? <Check size={15} /> : <Copy size={15} />}{ok ? 'Copiado' : 'Copiar'}</button>
}

export default function Datos({ ruta }: VistaProps) {
  const { estado } = useEstado()
  const fu = useApi<FuentesResp>('/api/fuentes')
  const ca = useApi<CarpetasResp>('/api/carpetas')
  const de = useApi<DescargasResp>('/api/descargas')
  const [grupo, setGrupo] = useState(0)
  const doc = ruta.query.doc || DOC_INICIAL
  const [abiertos, setAbiertos] = useState<Set<string>>(() => new Set(antecesores(doc)))
  const [ancla, setAncla] = useState<string | null>(null)
  const abrir = useCallback((r: string, seccion?: string) => {
    fijarQuery({ doc: r })
    setAncla(seccion ?? null)
    setAbiertos((s) => new Set([...s, ...antecesores(r)]))
  }, [])
  const alternar = useCallback((r: string) => setAbiertos((s) => { const n = new Set(s); if (n.has(r)) n.delete(r); else n.add(r); return n }), [])
  const grupos = useMemo(() => (fu.datos?.secciones ?? []).filter((s) => s.filas.length), [fu.datos])
  const g = grupos[Math.min(grupo, Math.max(0, grupos.length - 1))]
  const cortes = fu.datos?.cortes
  const c = estado?.cortes
  const cmd = fu.datos?.reconstruir

  return (
    <div className="mc-cuerpo ctx">
      <Cabecera seccion="Datos y carpetas" sub="De dónde sale todo" titulo={<>De dónde sale <em>cada dato</em> y qué lee el modelo</>}>
        Una fila por archivo descargado, con su corte y su liga; las carpetas de documentos que consulta el agente; y los comandos para reconstruirlo todo.
      </Cabecera>

      <div className="ctx-kpis ctx-kpis--4">
        <Kpi valor={fu.datos?.n_fuentes} etiqueta="archivos y series descargados" tono="accent" fuente="data/FUENTES.md" />
        <Kpi valor={fu.datos?.bytes_procesados} formato={fmtBytes} etiqueta="de datos procesados en data/processed" retraso={80} fuente="tamaño de los archivos del repositorio" />
        <Kpi valor={ca.datos?.archivos} etiqueta="documentos en carpetas/" retraso={160} fuente="carpetas/ (Markdown)" />
        <Kpi valor={ca.datos?.trozos} etiqueta="trozos indexados para la búsqueda" retraso={240} fuente={`data/index/chunks.parquet${ca.datos?.indice.modelo_embeddings ? `, ${ca.datos.indice.modelo_embeddings}` : ''}`} />
      </div>

      <Seccion id="d-fuentes" kicker="Fuentes" titulo={<>Qué se descargó, <em>de cuándo es</em> y de dónde</>}>
        <dl className="ctx-cortes">
          <div><dt>DENUE actual</dt><dd>{cortes?.denue_actual ?? c?.denue_actual ?? '…'}</dd></div>
          <div><dt>DENUE anterior</dt><dd>{cortes?.denue_hist ?? c?.denue_hist ?? '…'}</dd></div>
          <div><dt>Censo (INEGI)</dt><dd>{cortes?.censo ?? c?.censo ?? '…'}</dd></div>
          <div><dt>ENIGH (INEGI)</dt><dd>{cortes?.enigh ?? c?.enigh ?? '…'}</dd></div>
          <div><dt>Marginación (CONAPO)</dt><dd>{cortes?.conapo ?? c?.conapo ?? '…'}</dd></div>
          <div><dt>Macro consultado</dt><dd>{cortes?.macro_consultado ?? c?.macro_consultado ?? '…'}</dd></div>
        </dl>
        {fu.error ? <ErrorApi error={fu.error} reintentar={fu.recargar} titulo="No pude leer data/FUENTES.md" />
          : !fu.datos ? <Cargando forma="lista" filas={5} /> : (
            <>
              <Opciones etiqueta="Grupo de fuentes" valor={String(Math.min(grupo, grupos.length - 1))} opciones={grupos.map((s, i) => ({ id: String(i), texto: `${corto(s.titulo)} · ${s.filas.length}` }))} onCambio={(v) => setGrupo(Number(v))} />
              {g && (
                <div className="ctx-fuentes" key={g.titulo}>
                  <h4 className="ctx-fuentes__t">{g.titulo}</h4>
                  <div className="ctx-tabla ctx-tabla--fuentes" role="table" aria-label={g.titulo}>
                    <div className="ctx-tabla__cab" role="row"><span>Archivo o serie</span><span>Corte o levantamiento</span><span>Descarga</span><span>Tamaño</span><span>Liga</span></div>
                    {g.filas.map((f, i) => (
                      <div className="ctx-tabla__fila" role="row" key={i} style={{ ['--i' as string]: Math.min(i, 12) }}>
                        <span data-et="Archivo o serie"><b className="ctx-arch">{f.archivo}</b>{f.sha256 && <small title={`sha256 ${f.sha256}`}>sha256 {f.sha256.slice(0, 12)}…</small>}</span>
                        <span data-et="Corte" className="ctx-chico">{f.corte || 'NO ENCONTRADO'}</span>
                        <span data-et="Descarga" className="ctx-num">{f.descarga ? fecha(f.descarga) : 'NO ENCONTRADO'}</span>
                        <span data-et="Tamaño" className="ctx-num">{f.bytes != null ? fmtBytes(f.bytes) : f.tamano || '—'}</span>
                        <span data-et="Liga">{f.url.startsWith('http') ? <a className="ctx-liga" href={f.url} target="_blank" rel="noreferrer" title={f.url}>Abrir <ExternalLink size={13} aria-hidden /></a> : <span className="ctx-chico">{f.url || '—'}</span>}</span>
                      </div>
                    ))}
                  </div>
                  {g.texto.length > 0 && <ul className="ctx-notas">{g.texto.map((t, i) => <li key={i} className="chico">{t.replace(/`/g, '')}</li>)}</ul>}
                </div>
              )}
              <Fuente>{fu.datos.fuente}. Las ligas necesitan internet; los datos ya están descargados en el repositorio.</Fuente>
            </>
          )}
      </Seccion>

      <Seccion id="d-carpetas" kicker="Carpetas que lee el modelo" titulo={<>Los documentos que <em>pidió el profe</em>, con buscador</>}>
        <p className="ctx-par">Estas carpetas son la base de conocimiento del agente: se indexan por significado y, antes de responder, el agente busca aquí. Abre cualquier archivo o busca con tus palabras.</p>
        <Buscador abrir={abrir} />
        <div className="ctx-carp">
          <nav className="ctx-arbol" aria-label="Carpetas">
            {ca.error ? <ErrorApi error={ca.error} reintentar={ca.recargar} titulo="No pude leer carpetas/" />
              : !ca.datos ? <Cargando forma="lista" filas={6} />
                : <ul className="ctx-arbol__lista ctx-arbol__lista--raiz">{ca.datos.nodos.map((n) => <Nodo key={n.ruta} n={n} nivel={0} abiertos={abiertos} alternar={alternar} activo={doc} abrir={abrir} />)}</ul>}
            <p className="ctx-arbol__pie chico">Los números son archivos · trozos de cada carpeta, y trozos por archivo.</p>
          </nav>
          <Visor ruta={doc} abrir={abrir} ancla={ancla} />
        </div>
        <Fuente>{ca.datos?.fuente ?? 'carpetas/ y data/index/chunks.parquet'}.</Fuente>
      </Seccion>

      <Seccion id="d-descargas" kicker="Descargas" titulo={<>Los datos tal como los usa el modelo, <em>en CSV</em></>}>
        <ul className="ctx-desc">
          {(de.datos?.descargas ?? []).map((x) => (
            <li key={x.archivo}>
              <div><b>{x.archivo}</b><p>{x.descripcion}</p><small className="chico">Sale de <code>{x.origen}</code></small></div>
              {x.disponible ? <a className="c-boton" href={x.ruta} download={x.archivo}><Download size={15} aria-hidden /> Descargar</a> : <Pill tono="gris">NO ENCONTRADO</Pill>}
            </li>
          ))}
        </ul>
        {de.error && <ErrorApi error={de.error} reintentar={de.recargar} titulo="No pude listar las descargas" />}
        <Fuente>Censo 2020 INEGI, DENUE corte {c?.denue_actual ?? '…'}, ENIGH {c?.enigh ?? '…'}, CONAPO {c?.conapo ?? '…'} y modelo propio. Los CSV llevan acentos en UTF-8 (Excel los abre bien).</Fuente>
      </Seccion>

      <Seccion id="d-reconstruir" kicker="Reconstruir todo desde cero" titulo={<>Cuatro comandos y <em>se regenera</em> todo</>}>
        {cmd ? (
          <div className="ctx-recon">
            <div className="ctx-recon__cmd"><code>{cmd.comando}</code><Copiar texto={cmd.comando} /></div>
            <ol className="ctx-recon__pasos">
              {cmd.setup && <li><code>make {cmd.setup.objetivo}</code><span>Una sola vez: {cmd.setup.descripcion}.</span></li>}
              {cmd.pasos.map((p) => <li key={p.objetivo}><code>make {p.objetivo}</code><span>{p.descripcion[0].toUpperCase() + p.descripcion.slice(1)}.</span></li>)}
            </ol>
            <p className="ctx-par ctx-par--chico"><code>make datos</code> necesita un archivo <code>.env</code> con las claves de la API de Banxico (<code>BANXICO_TOKEN</code>) y de INEGI (<code>INEGI_TOKEN</code>); se copia de <code>.env.example</code> y nunca se sube al repositorio. <code>make indexar</code> necesita Ollama prendido para los embeddings.
              Para solo usar el tablero no hace falta nada de esto: el repositorio ya trae <code>data/processed</code>, <code>models</code> y <code>data/index</code> ({fmtBytes(fu.datos?.bytes_procesados)} de datos procesados).</p>
            <Fuente>Makefile y data/FUENTES.md.</Fuente>
          </div>
        ) : <Cargando forma="texto" filas={4} />}
      </Seccion>
    </div>
  )
}
