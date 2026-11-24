import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import { Download, Send, Trash2, X } from 'lucide-react'
import { Collapse, Meter, Roll, Spinner, Toggle } from '../../kit'
import { apiGet, apiPost, Cabecera, Cargando, ErrorApi as ErrorVista, esCancelado, fmtNum, Fuente, Pill, useEstado, type VistaProps } from '../../comun'
import { ErrorApi as ErrorTipo } from '../../comun/api'
import { Datos } from './Datos'
import { Markdown, sinFuentes } from './markdown'
import { Herramientas } from './TablaResultado'
import { borrarHilo, guardarHilo, leerHilo } from './historial'
import { esFueraDeTema, type DatosPregunta, type Herramienta, type RespuestaCrear, type Turno, type VistaTrabajo } from './tipos'
import './preguntar.css'

// Vista Preguntar: caja de pregunta, hilo con los datos que aparecen enseguida, el estado «Pensando» (honesto: segundos y lugar en la
// cola) y la respuesta del modelo con sus fuentes. Plano, como el ejemplo ai-chat de stageshow pero con la app real.

const EJEMPLOS = [
  'Quiero poner una heladería',
  'Farmacia en Iztapalapa',
  'Cafetería de especialidad',
  '¿Qué negocio pongo en Coyoacán?',
  'Quiero abrir una taquería en Monterrey',
]
const EN_CURSO = new Set(['en_cola', 'pensando'])
const uid = () => `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 7)}`
const dormir = (ms: number, s: AbortSignal) => new Promise<void>((ok) => { const t = setTimeout(ok, ms); s.addEventListener('abort', () => { clearTimeout(t); ok() }, { once: true }) })

const desdeVista = (v: VistaTrabajo): Partial<Turno> => ({
  fase: v.estado, id: v.id, respuesta: v.respuesta, modo: v.modo, modelo: v.modelo, latencia_s: v.latencia_s, aviso: v.aviso, error: v.error,
  fuentes: v.fuentes, posicion: v.posicion_en_cola, segundos: v.segundos, t_seg: Date.now(), herramientas: v.herramientas,
  ...(v.fuera_de_tema != null ? { fuera_de_tema: v.fuera_de_tema === true, tipo_fuera_de_tema: v.tipo_fuera_de_tema ?? null } : null),
})

function descargar(t: Turno) {
  const fecha = new Date().toISOString().slice(0, 10)
  const modo = t.modo === 'llm' ? `respuesta del modelo local ${t.modelo ?? ''}`.trim() : t.modo === 'rapido' ? 'respuesta rápida, sin modelo de lenguaje' : 'respuesta armada sin el modelo de lenguaje'
  const md = `# ${t.pregunta}\n\n${t.respuesta ?? ''}\n\n---\n_Dónde pongo mi negocio · ${fecha} · ${modo}._\n`
  const url = URL.createObjectURL(new Blob([md], { type: 'text/markdown;charset=utf-8' }))
  const a = document.createElement('a')
  const giro = t.datos?.giro?.clave ?? 'pregunta'
  a.href = url; a.download = `respuesta-${giro}-${fecha}.md`
  document.body.appendChild(a); a.click(); a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 2000)
}

/** Segundos que lleva la pregunta, contando entre un sondeo y otro. */
function useSegundos(t: Turno) {
  const [, tic] = useState(0)
  useEffect(() => { const id = setInterval(() => tic((n) => n + 1), 500); return () => clearInterval(id) }, [])
  return Math.max(0, Math.floor((t.segundos ?? 0) + (Date.now() - (t.t_seg ?? Date.now())) / 1000))
}

function Pensando({ t, mediana, total, onCancelar }: { t: Turno; mediana: number | null; total?: number; onCancelar: () => void }) {
  const seg = useSegundos(t)
  const enCola = t.fase === 'en_cola'
  const pos = t.posicion ?? 0
  return (
    <div className="pre-pensando" role="status" aria-live="polite">
      <div className="pre-pensando__fila">
        <Spinner size={16} />
        <b>{enCola ? 'Esperando turno' : 'Pensando'}</b>
        <span className="pre-pensando__seg"><Roll>{`${fmtNum(seg)} s`}</Roll></span>
        {enCola && <button className="pre-enlace" onClick={onCancelar}><X size={14} />Cancelar</button>}
      </div>
      {enCola
        ? <p>El modelo contesta una pregunta a la vez. {pos === 1 ? 'Hay 1 pregunta' : `Hay ${fmtNum(pos)} preguntas`} antes de la tuya.</p>
        : <p>El modelo local ({t.modelo ?? 'qwen3:8b'}) lee los datos de abajo y redacta la respuesta en esta computadora, sin internet.</p>}
      {!enCola && mediana != null && (
        <>
          <Meter value={Math.min(0.96, seg / mediana)} />
          <p className="chico">Suele tardar unos {fmtNum(mediana)} s en esta Mac. Mientras, ya puedes revisar el mapa y las zonas que aparecen abajo.</p>
          <Fuente>{`modelo propio, mediana de ${total != null ? `las ${fmtNum(total)} preguntas` : 'las preguntas'} de la evaluación (reports/evaluacion.json)`}</Fuente>
        </>
      )}
    </div>
  )
}

function ModoPill({ t }: { t: Turno }) {
  if (t.modo === 'llm') return <Pill tono="naranja">{`Respuesta del modelo local${t.latencia_s != null ? `, ${fmtNum(t.latencia_s, 0)} s` : ''}`}</Pill>
  if (t.modo === 'rapido') return <Pill tono="gris">Rápida, sin modelo de lenguaje</Pill>
  if (t.modo === 'plantilla') return <Pill tono="amarillo">Armada sin el modelo</Pill>
  return null
}

function Respuesta({ t, cargarHerr, sinHerramientas = false }: { t: Turno; cargarHerr: () => void; sinHerramientas?: boolean }) {
  const [abierto, setAbierto] = useState(!!t.respuesta && t.fase === 'listo' && Date.now() - t.creada > 4000)
  const [herr, setHerr] = useState(false)
  useEffect(() => { const id = requestAnimationFrame(() => setAbierto(true)); return () => cancelAnimationFrame(id) }, [])
  const fuentes = t.fuentes ?? []
  const texto = t.respuesta ?? ''
  return (
    <div className="pre-resp-caja">
      {t.aviso && <div className="pre-aviso" data-tono="amarillo" role="note"><Pill tono="amarillo">Sin modelo</Pill><p>{t.aviso}</p></div>}
      <Collapse open={abierto} reveal="clip">
        <div className="pre-resp">
          <Markdown texto={fuentes.length ? sinFuentes(texto) : texto} />
          {fuentes.length > 0 && (
            <div className="pre-fuentes">
              <h3 className="pre-h">Fuentes</h3>
              <ul>{fuentes.map((f) => <li key={f}>{f}</li>)}</ul>
            </div>
          )}
        </div>
      </Collapse>
      <div className="pre-acciones">
        <ModoPill t={t} />
        <button className="c-boton" onClick={() => descargar(t)}><Download size={15} />Descargar en Markdown</button>
        {!sinHerramientas && <button className="c-boton" aria-expanded={herr} onClick={() => { setHerr((h) => !h); cargarHerr() }}>{herr ? 'Ocultar' : '¿Cómo llegó a esto?'}</button>}
      </div>
      <Collapse open={herr}>
        <div className="pre-como">
          <p className="chico">Estas son las herramientas que consultó el agente, en orden, con lo que pidió y lo que le regresaron. Todas son Python local sobre los datos del proyecto.</p>
          {t.herramientas ? <Herramientas lista={t.herramientas} /> : <Cargando forma="texto" filas={3} />}
        </div>
      </Collapse>
    </div>
  )
}

function TurnoVista({ t, ultimo, mediana, total, onCancelar, parchar }: { t: Turno; ultimo: boolean; mediana: number | null; total?: number; onCancelar: () => void; parchar: (k: string, p: Partial<Turno>) => void }) {
  const [verMapa, setVerMapa] = useState(false)
  const [cargandoMapa, setCargandoMapa] = useState(false)
  const pedido = useRef(false)
  const conMapa = ultimo || verMapa
  const fuera = esFueraDeTema(t)
  const faltaMapa = !fuera && conMapa && !!t.datos?.zonas.length && !t.datos.mapa && !!t.id

  // al reabrir el hilo guardado, el mapa (pesado) se vuelve a pedir al servidor
  useEffect(() => {
    if (!faltaMapa || pedido.current || !t.id) return
    pedido.current = true; setCargandoMapa(true)
    apiGet<VistaTrabajo & { datos: DatosPregunta }>(`/api/preguntas/${t.id}?completo=1`)
      .then((v) => parchar(t.k, { datos: v.datos, herramientas: v.herramientas }))
      .catch((e) => { if (!esCancelado(e)) parchar(t.k, { datos: { ...t.datos!, mapa: null } }) })
      .finally(() => setCargandoMapa(false))
  }, [faltaMapa, t.id, t.k, t.datos, parchar])

  const cargarHerr = useCallback(() => {
    if (t.herramientas || !t.id) return
    apiGet<VistaTrabajo>(`/api/preguntas/${t.id}`).then((v) => parchar(t.k, { herramientas: v.herramientas })).catch(() => parchar(t.k, { herramientas: [] as Herramienta[] }))
  }, [t.herramientas, t.id, t.k, parchar])

  return (
    <article className="pre-turno">
      <div className="pre-q">
        <p>{t.pregunta}</p>
        {t.rapido && <Pill tono="gris">Rápida</Pill>}
      </div>
      {t.fase === 'consultando' && (
        <div className="pre-consulta" role="status">
          <p><Spinner size={15} /> Buscando en los datos del proyecto…</p>
          <Cargando forma="lista" filas={3} />
        </div>
      )}
      {EN_CURSO.has(t.fase) && <Pensando t={t} mediana={mediana} total={total} onCancelar={onCancelar} />}
      {t.fase === 'falla' && <ErrorVista error={new Error(t.error ?? 'No pude contestar.')} titulo="No pude contestar esta pregunta" />}
      {t.datos && !fuera && <Datos datos={t.datos} conMapa={conMapa && !!t.datos.mapa} cargandoMapa={cargandoMapa} onVerMapa={() => { setVerMapa(true); if (!t.datos?.mapa) pedido.current = false }} />}
      {t.fase === 'cancelada' && <p className="chico pre-nota">Cancelaste esta pregunta antes de que el modelo la contestara.</p>}
      {t.fase === 'error' && <ErrorVista error={new Error(t.error ?? 'El modelo falló.')} titulo="El modelo no pudo contestar" />}
      {t.fase === 'listo' && t.respuesta != null && <Respuesta t={t} cargarHerr={cargarHerr} sinHerramientas={fuera} />}
    </article>
  )
}

export default function Preguntar(_: VistaProps) {
  const { estado } = useEstado()
  const [turnos, setTurnos] = useState<Turno[]>(() => leerHilo())
  const [texto, setTexto] = useState('')
  const [rapido, setRapido] = useState(false)
  const turnosRef = useRef(turnos)
  turnosRef.current = turnos
  const sondeos = useRef(new Map<string, AbortController>())
  const vivos = useRef(new Set<AbortController>())

  const ollamaListo = !!estado && estado.ollama.prendido && !estado.ollama.faltan.includes('qwen3:8b')
  const sinModelo = !!estado && !ollamaListo
  const mediana = estado?.kpis.evaluacion.latencia_mediana_s ?? null
  const total = estado?.kpis.evaluacion.total ?? undefined

  const parchar = useCallback((k: string, p: Partial<Turno>) => setTurnos((ts) => ts.map((t) => (t.k === k ? { ...t, ...p } : t))), [])
  useEffect(() => { guardarHilo(turnos) }, [turnos])
  useEffect(() => () => { vivos.current.forEach((a) => a.abort()); sondeos.current.forEach((a) => a.abort()) }, [])

  // sondeo de lo que sigue en el servidor (también al reabrir el hilo guardado)
  const enCurso = turnos.filter((t) => t.id && EN_CURSO.has(t.fase)).map((t) => t.k + t.id).join('|')
  useEffect(() => {
    for (const t of turnosRef.current) {
      if (!t.id || !EN_CURSO.has(t.fase) || sondeos.current.has(t.k)) continue
      const ac = new AbortController(); sondeos.current.set(t.k, ac)
      ;(async () => {
        while (!ac.signal.aborted) {
          try {
            const v = await apiGet<VistaTrabajo>(`/api/preguntas/${t.id}`, { signal: ac.signal })
            parchar(t.k, desdeVista(v))
            if (!EN_CURSO.has(v.estado)) break
          } catch (e) {
            if (esCancelado(e)) break
            if (e instanceof ErrorTipo && e.estado === 404) { parchar(t.k, { fase: 'falla', error: e.message }); break }
          }
          await dormir(1500, ac.signal)
        }
        sondeos.current.delete(t.k)
      })()
    }
  }, [enCurso, parchar])

  const enviar = useCallback(async (pregunta: string) => {
    const q = pregunta.trim()
    if (q.length < 2) return
    const modoRapido = rapido || sinModelo
    const previos = turnosRef.current.filter((t) => t.fase === 'listo' && t.respuesta).slice(-3)
    const historial = previos.flatMap((t) => [{ role: 'user', content: t.pregunta }, { role: 'assistant', content: (t.respuesta ?? '').slice(0, 1500) }])
    const k = uid()
    setTurnos((ts) => [...ts, { k, pregunta: q, rapido: modoRapido, creada: Date.now(), fase: 'consultando' }])
    setTexto('')
    const ac = new AbortController(); vivos.current.add(ac)
    try {
      const r = await apiPost<RespuestaCrear>('/api/preguntas', { pregunta: q, historial, rapido: modoRapido }, { signal: ac.signal })
      parchar(k, { ...desdeVista(r), datos: r.datos })
    } catch (e) {
      if (!esCancelado(e)) parchar(k, { fase: 'falla', error: e instanceof Error ? e.message : String(e) })
    } finally { vivos.current.delete(ac) }
  }, [rapido, sinModelo, parchar])

  const cancelar = useCallback((t: Turno) => {
    if (!t.id) return
    fetch(`/api/preguntas/${t.id}`, { method: 'DELETE' }).then((r) => r.json()).then((v: VistaTrabajo) => parchar(t.k, { fase: v.estado === 'en_cola' ? 'en_cola' : v.estado })).catch(() => undefined)
  }, [parchar])

  const alEnviar = (e: FormEvent) => { e.preventDefault(); void enviar(texto) }
  const ordenados = useMemo(() => [...turnos].reverse(), [turnos])
  const ocupado = turnos.some((t) => t.fase === 'consultando')

  return (
    <div className="mc-cuerpo pre">
      <Cabecera seccion="Preguntar" sub="agente local" titulo={<>Pregunta en español; te respondo con <em>colonias, cifras y fuentes</em></>}>
        El agente corre en esta computadora (Ollama) y solo puede citar lo que traen los datos del proyecto. Lo que no está, lo dice «NO ENCONTRADO».
      </Cabecera>

      <form className="pre-form" onSubmit={alEnviar}>
        <label className="pre-form__campo">
          <span className="sr-only">Tu pregunta</span>
          <input value={texto} onChange={(e) => setTexto(e.target.value)} maxLength={600} placeholder="Escribe tu negocio: «quiero poner una heladería»" autoComplete="off" enterKeyHint="send" />
        </label>
        <button type="submit" className="c-boton" data-primario="true" disabled={ocupado || texto.trim().length < 2}><Send size={15} />Preguntar</button>
      </form>
      <div className="pre-opciones">
        <div className="pre-ejemplos" aria-label="Ejemplos">
          {EJEMPLOS.map((e) => <button key={e} type="button" className="pre-ejemplo" onClick={() => { setTexto(e); void enviar(e) }} disabled={ocupado}>{e}</button>)}
        </div>
        <button type="button" className="pre-interruptor" role="switch" aria-checked={rapido || sinModelo} disabled={sinModelo}
          onClick={() => setRapido((r) => !r)} title={sinModelo ? 'Ollama está apagado: todas las respuestas salen sin el modelo' : 'Sin LLM: la respuesta sale de una plantilla con los mismos datos, en unos segundos'}>
          <Toggle on={rapido || sinModelo} />
          <span><b>Rápida (sin LLM)</b><small>{sinModelo ? 'Ollama apagado: siempre es rápida' : rapido ? 'Respuesta de plantilla, en segundos' : `El modelo tarda ${mediana != null ? `unos ${fmtNum(mediana)} s` : 'un par de minutos'}`}</small></span>
        </button>
      </div>

      {turnos.length === 0 ? (
        <section className="pre-vacio" aria-label="Cómo funciona">
          <h2 className="seccion-t">Qué pasa cuando preguntas</h2>
          <ol>
            <li><b>Primero, los datos.</b> En unos segundos aparecen el mapa y las 5 zonas, sin esperar al modelo.</li>
            <li><b>Luego, el texto.</b> El modelo local lee esos datos y redacta; puedes ver cuánto lleva y cuántas preguntas van antes.</li>
            <li><b>Al final, las fuentes.</b> Cada cifra dice de dónde sale, y «¿Cómo llegó a esto?» muestra cada herramienta que usó.</li>
          </ol>
          <p className="chico">{!estado ? 'Revisando Ollama…' : ollamaListo ? 'Ollama está prendido: el modelo local contestará.' : 'Ollama está apagado o le falta qwen3:8b: las respuestas saldrán sin el modelo, con los mismos datos.'}</p>
        </section>
      ) : (
        <>
          <div className="pre-hilo-cab">
            <h2 className="seccion-t">Tu conversación</h2>
            <button className="pre-enlace" onClick={() => { vivos.current.forEach((a) => a.abort()); sondeos.current.forEach((a) => a.abort()); sondeos.current.clear(); borrarHilo(); setTurnos([]) }}><Trash2 size={14} />Borrar historial</button>
          </div>
          <div className="pre-hilo">
            {ordenados.map((t, i) => <TurnoVista key={t.k} t={t} ultimo={i === 0} mediana={mediana} total={total} onCancelar={() => cancelar(t)} parchar={parchar} />)}
          </div>
          <p className="chico pre-nota">El historial se guarda en este navegador mientras la pestaña siga abierta.</p>
        </>
      )}
    </div>
  )
}
