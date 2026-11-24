import { createContext, useCallback, useContext, useEffect, useLayoutEffect, useMemo, useRef, useState, type AnchorHTMLAttributes, type MouseEvent, type ReactNode } from 'react'
import { ArrowUpRight, ChevronRight, Info, X } from 'lucide-react'
import { Count } from '../kit'
import { useApi } from './api'
import { Cargando } from './Cargando'
import { ErrorApi } from './ErrorApi'
import { Fuente } from './Fuente'
import { fmtCompacto, fmtNum, fmtPct, fmtPesos, titulo } from './formato'
import { href, useRuta } from './ruta'
import { SelectorGiro } from './Selectores'
import { Pill } from './ss'
import './desglose.css'

// Panel de desglose: se abre al picar una AGEB del mapa o una tarjeta de zona SIN salir de la vista (la conversación y el scroll
// se quedan donde estaban). Lee GET /api/zona/{cvegeo}/desglose?giro=: todo viene del servidor y cada bloque dice su fuente.
//  · ≥ 1280 px: panel a la derecha que reserva su espacio (no tapa el contenido), sin velo.
//  · 921–1279 px: panel a la derecha sobre el contenido, con velo (un clic fuera lo cierra).
//  · ≤ 920 px: hoja que sube desde abajo, con velo.
// Se cierra con la X, con Esc y con un clic fuera; el foco pasa al panel al abrir y regresa a lo que se picó al cerrar.

// ---------------------------------------------------------------- tipos de la API
interface Contra { ageb: number | null; municipio: number | null; zmvm: number | null }
interface Componente {
  clave: string; etiqueta: string; descripcion: string; aplica: boolean; peso: number; percentil: number | null; aporte: number
  valor: number | null; unidad: string; detalle: string | null; fuente: string; nota?: string
}
interface Cercano { nombre: string | null; actividad: string | null; scian: string; distancia_m: number | null; en_radio: boolean; cvegeo: string; en_la_ageb: boolean }
interface Negocios {
  total_zmvm: number | null; en_radio: number | null; en_ageb: number | null; cercanos: Cercano[]; ponderados: number | null; etiqueta: string; fuente: string
  sin_puntos?: boolean; motivo?: string
}
interface Estacion { sistema: string; linea: string | null; estacion: string; distancia_m: number | null; afluencia_anual: number | null; anio_afluencia: number | null; estado: string | null }
export interface DesgloseZona {
  encontrado: boolean; ageb: string; agebs_zmvm: number; colonia: string | null; municipio: string; cvegeo_mun: string
  giro: { clave: string; nombre: string } | null; giro_pedido: string | null; nota_giro?: string
  score: null | {
    valor: number; de: number; version: string; componentes: Componente[]; suma_aportes: number; pesos_fuente: string; como_leer: string
    lugar: { posicion: number; de: number; mejor_que_pct: number | null; en_top_5: boolean; municipio: { posicion: number; de: number }; fuente: string }
    prob_apertura_pct: number | null; prob_sigue_abierto_pct: number | null; radio_m: number; fuente: string
  }
  competencia: null | { radio_m: number; competidores: Negocios; complementarios: Negocios }
  poblacion: {
    habitantes: number | null; hogares: number | null; densidad_hab_km2: number | null; habitantes_municipio: number | null; agebs_municipio: number; fuente: string
    grupos_edad: { grupo: string; etiqueta: string; personas: number | null; pct_ageb: number | null; pct_municipio: number | null; pct_zmvm: number | null }[]
  }
  ingreso: {
    decil: Contra; ingreso_trim_mediano_mxn: Contra; nse: string | null; prob_nse_pct: Record<string, Contra>; como_leer: string; fuente: string
  }
  flujo: {
    poblacion_diurna: number | null; poblacion_diurna_ageb_media_municipio: number | null; poblacion_diurna_ageb_media_zmvm: number | null
    empleos_500m: number | null; empleos_1km: number | null; negocios_en_ageb: number | null; negocios_500m: number | null; negocios_1km: number | null
    escuelas_1km: number | null; hospitales_1km: number | null; fuente: string
    en_radio_del_giro?: { radio_m: number; empleos: number | null; negocios_de_corredor: number | null; estaciones_1km: number | null; afluencia_metro_1km: number | null }
  }
  transporte: { radio_busqueda_m: number; estaciones: Estacion[]; a_1km: number; fuente: string }
  fuentes: string[]
}

// ---------------------------------------------------------------- estado compartido
export interface AbrirOpciones {
  giro?: string | null; colonia?: string | null; municipio?: string | null
  /** El elemento que se picó: al cerrar, el foco regresa a él. Si no se da, se usa el elemento con foco. */
  origen?: HTMLElement | null
}
interface Abierto { cvegeo: string; giro: string | null; colonia: string | null; municipio: string | null }
interface Ctx { abierto: Abierto | null; abrir: (cvegeo: string, op?: AbrirOpciones) => void; cerrar: () => void }
const Contexto = createContext<Ctx>({ abierto: null, abrir: () => undefined, cerrar: () => undefined })

/** {abierto, abrir(cvegeo, {giro, colonia, municipio, origen}), cerrar()}: `abierto.cvegeo` sirve para marcar esa AGEB en el mapa. */
export const useDesglose = () => useContext(Contexto)

const useMedia = (consulta: string) => {
  const [v, setV] = useState(() => (typeof window !== 'undefined' ? window.matchMedia(consulta).matches : false))
  useEffect(() => {
    const mq = window.matchMedia(consulta)
    const f = () => setV(mq.matches)
    f(); mq.addEventListener('change', f)
    return () => mq.removeEventListener('change', f)
  }, [consulta])
  return v
}

export function DesgloseProvider({ children }: { children: ReactNode }) {
  const [abierto, setAbierto] = useState<Abierto | null>(null)
  const origen = useRef<HTMLElement | null>(null)
  const estaAbierto = useRef(false)
  // al abrir o cerrar, el contenido se reacomoda (el panel reserva su lado): se ancla lo picado para que no se mueva en la pantalla
  const ancla = useRef<{ el: HTMLElement; top: number } | null>(null)
  const giroPreferido = useRef<string | null>(null)   // el giro que se eligió en el panel: vale para las AGEB que se pican después, sin giro
  const ruta = useRuta()

  const anclar = useCallback((el: HTMLElement | null) => {
    const a = el?.closest<HTMLElement>('.c-mapa') ?? el
    ancla.current = a && document.contains(a) ? { el: a, top: a.getBoundingClientRect().top } : null
  }, [])
  const abrir = useCallback((cvegeo: string, op: AbrirOpciones = {}) => {
    const activo = document.activeElement
    origen.current = op.origen ?? (activo && activo !== document.body ? (activo as HTMLElement) : null)
    if (!estaAbierto.current) anclar(origen.current)
    setAbierto({ cvegeo, giro: op.giro || giroPreferido.current, colonia: op.colonia ?? null, municipio: op.municipio ?? null })
  }, [anclar])
  const cerrar = useCallback(() => {
    if (!estaAbierto.current) return
    const o = origen.current
    anclar(o)
    setAbierto(null)
    setTimeout(() => { if (o && document.contains(o)) o.focus({ preventScroll: true }) }, 0)
  }, [anclar])
  const elegirGiro = useCallback((giro: string | null) => { giroPreferido.current = giro; setAbierto((a) => (a ? { ...a, giro } : a)) }, [])
  // otra vista = otra conversación: el panel no la sigue
  useEffect(() => { ancla.current = null; setAbierto(null) }, [ruta.vista, ruta.param])

  const lado = useMedia('(min-width: 1280px)')
  const hay = !!abierto
  useLayoutEffect(() => {
    estaAbierto.current = hay
    const el = document.documentElement
    if (hay) el.dataset.desglose = lado ? 'lado' : 'sobre'; else delete el.dataset.desglose
    const a = ancla.current
    ancla.current = null
    if (a && document.contains(a.el)) {
      el.style.overflowAnchor = 'none'   // el ajuste automático del navegador y el nuestro no se suman
      let n = 0                          // unos cuadros más: el contenido termina de acomodarse (fuentes, tablas) un instante después
      const paso = () => {
        if (!document.contains(a.el)) { el.style.overflowAnchor = ''; return }
        const d = a.el.getBoundingClientRect().top - a.top
        if (Math.abs(d) > 1) window.scrollBy(0, d)
        if (++n < 8) requestAnimationFrame(paso); else el.style.overflowAnchor = ''
      }
      paso()
    }
  }, [hay, lado])
  useEffect(() => () => { delete document.documentElement.dataset.desglose }, [])

  const valor = useMemo(() => ({ abierto, abrir, cerrar }), [abierto, abrir, cerrar])
  return (
    <Contexto.Provider value={valor}>
      {children}
      {abierto && <Panel key="panel" a={abierto} lado={lado} cerrar={cerrar} elegirGiro={elegirGiro} />}
    </Contexto.Provider>
  )
}

/** Enlace de una zona (tarjeta, fila de lista…): un clic normal abre el desglose; con Cmd/Ctrl, Shift o clic medio sigue siendo un enlace a la ficha. */
export function EnlaceZona({ cvegeo, giro, colonia, municipio, children, onClick, ...resto }: {
  cvegeo: string; giro?: string | null; colonia?: string | null; municipio?: string | null; children: ReactNode
} & Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href'>) {
  const { abrir, abierto } = useDesglose()
  const alClic = (e: MouseEvent<HTMLAnchorElement>) => {
    onClick?.(e)
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return
    e.preventDefault()
    abrir(cvegeo, { giro, colonia, municipio, origen: e.currentTarget })
  }
  return (
    <a {...resto} href={href('zona', cvegeo, { giro })} data-zona={cvegeo} aria-haspopup="dialog" aria-expanded={abierto?.cvegeo === cvegeo || undefined} onClick={alClic}>
      {children}
    </a>
  )
}

// ---------------------------------------------------------------- piezas
/** Cifra que rueda desde 0 (Count de stageshow). */
function Rueda({ valor, formato = (n) => fmtNum(n), retraso = 0 }: { valor: number | null | undefined; formato?: (n: number) => string; retraso?: number }) {
  const n = typeof valor === 'number' && Number.isFinite(valor) ? valor : null
  const [v, setV] = useState(0)
  useEffect(() => {
    if (n == null) return
    const t = setTimeout(() => setV(n), 80 + retraso)
    return () => clearTimeout(t)
  }, [n, retraso])
  return n == null ? <span className="dz-nd">NO ENCONTRADO</span> : <Count value={v} format={formato} duration={800} stagger={45} />
}

const ND = 'NO ENCONTRADO'
const pct = (n: number | null | undefined, d = 1) => (n == null ? ND : fmtPct(n, d))

function Bloque({ t, sub, children, fuente }: { t: string; sub?: string; children: ReactNode; fuente?: string }) {
  return (
    <section className="dz-bloque">
      <h3 className="dz-bloque__t">{t}{sub && <small>{sub}</small>}</h3>
      {children}
      {fuente && <Fuente>{fuente}</Fuente>}
    </section>
  )
}

/** Un valor de la AGEB contra el de su municipio y el de la ZMVM: tres barras finas con su cifra. */
function Tres({ etiqueta, nota, v, formato, maximo, i = 0 }: { etiqueta: string; nota?: string; v: Contra; formato: (n: number) => string; maximo?: number; i?: number }) {
  const vals = [v.ageb, v.municipio, v.zmvm]
  const tope = maximo ?? (Math.max(...vals.filter((x): x is number => x != null && Number.isFinite(x)), 0) * 1.05 || 1)
  const filas: [string, number | null, 'a' | 'b' | 'c'][] = [['AGEB', v.ageb, 'a'], ['Municipio', v.municipio, 'b'], ['ZMVM', v.zmvm, 'c']]
  return (
    <div className="dz-tres" style={{ ['--i' as string]: i }}>
      <div className="dz-tres__etq">{etiqueta}{nota && <small>{nota}</small>}</div>
      {filas.map(([n, x, t]) => (
        <div key={t} className="dz-tres__fila" data-t={t} title={`${etiqueta}: ${n} ${x == null ? ND : formato(x)}`}>
          <span className="dz-tres__n">{n}</span>
          <span className="dz-tres__pista"><i style={{ width: `${x == null ? 0 : Math.max(0.8, (x / tope) * 100)}%` }} /></span>
          <b>{x == null ? ND : formato(x)}</b>
        </div>
      ))}
    </div>
  )
}

function Leyenda() {
  return <div className="dz-ley" aria-hidden="true"><span data-t="a">Esta AGEB</span><span data-t="b">Municipio</span><span data-t="c">ZMVM</span></div>
}

// ---------------------------------------------------------------- score
function BloqueScore({ d }: { d: DesgloseZona }) {
  const s = d.score!
  const [abierta, setAbierta] = useState<string | null>(null)
  const maxPeso = Math.max(...s.componentes.map((c) => c.peso), 0.01)
  const nombre = (d.giro?.nombre ?? '').toLowerCase()
  const lg = s.lugar
  return (
    <Bloque t={`Score de ${nombre}`} sub="cómo se arma" fuente={`${s.fuente}; ${s.pesos_fuente}; ${lg.fuente}`}>
      <div className="dz-score">
        <div className="dz-score__n"><Rueda valor={s.valor} formato={(n) => fmtNum(n, 1)} /><small>de 100</small></div>
        <div className="dz-score__lugar">
          <Pill tono={lg.en_top_5 ? 'verde' : 'naranja'}>{`Lugar ${fmtNum(lg.posicion)} de ${fmtNum(lg.de)}`}</Pill>
          <span>Mejor que el {pct(lg.mejor_que_pct)} de las AGEB para este giro.</span>
          <span>En {titulo(d.municipio)}: lugar {fmtNum(lg.municipio.posicion)} de {fmtNum(lg.municipio.de)}.</span>
        </div>
      </div>
      <ul className="dz-comp" aria-label="Aporte de cada componente al score">
        {s.componentes.map((c, i) => {
          const abre = abierta === c.clave
          const max = c.peso * 100
          return (
            <li key={c.clave} data-aplica={c.aplica || undefined}>
              <button type="button" className="dz-comp__fila" aria-expanded={abre} aria-controls={`dz-c-${c.clave}`} onClick={() => setAbierta(abre ? null : c.clave)}>
                <ChevronRight size={14} className="dz-comp__flecha" data-abierta={abre} aria-hidden />
                <span className="dz-comp__t"><b>{c.etiqueta}</b><span>{c.aplica ? `peso ${fmtPct(c.peso * 100, 0)}` : 'no aplica a este giro'}</span></span>
                <span className="dz-comp__pts">{c.aplica ? <><b>{fmtNum(c.aporte, 1)}</b> de {fmtNum(max, 0)} pts</> : '—'}</span>
                <span className="dz-comp__pista" style={{ width: `${(c.peso / maxPeso) * 100}%`, ['--i' as string]: i }}>
                  <i style={{ width: `${c.aplica ? c.percentil ?? 0 : 0}%` }} />
                </span>
              </button>
              {abre && (
                <div id={`dz-c-${c.clave}`} className="dz-comp__detalle">
                  <p>{c.descripcion}</p>
                  {c.aplica ? (
                    <ul>
                      <li>Esta AGEB queda en el percentil <b>{c.percentil != null ? fmtNum(c.percentil, 1) : ND}</b> de las {fmtNum(lg.de)} para el giro, y ese percentil vale {fmtNum(max, 0)} pts × {c.percentil != null ? fmtNum(c.percentil / 100, 3) : ND}.</li>
                      <li>Valor medido: <b>{c.valor == null ? ND : c.unidad.startsWith('pesos') ? fmtPesos(c.valor) : fmtNum(c.valor, c.valor < 10 ? 2 : 0)}</b> {c.unidad}{c.detalle ? ` (${c.detalle})` : ''}.</li>
                    </ul>
                  ) : <p>{c.nota ?? ND}</p>}
                  <Fuente>{c.fuente}</Fuente>
                </div>
              )}
            </li>
          )
        })}
      </ul>
      <p className="dz-nota"><Info size={13} aria-hidden /> La barra gris es lo máximo que puede aportar el componente (su peso); lo naranja es lo que logra esta AGEB. Suman {fmtNum(s.suma_aportes, 1)} de 100. {s.como_leer}</p>
      <div className="dz-cifras">
        <div><b>{pct(s.prob_apertura_pct)}</b><span>prob. de apertura del giro en la AGEB</span><small>modelo propio</small></div>
        <div><b>{pct(s.prob_sigue_abierto_pct)}</b><span>prob. de seguir abierto</span><small>modelo propio, poco confiable</small></div>
      </div>
    </Bloque>
  )
}

// ---------------------------------------------------------------- competencia
function ListaNegocios({ n, radio }: { n: Negocios; radio: number }) {
  return (
    <div className="dz-neg">
      <p className="dz-neg__cab">
        <b>{n.en_radio == null ? ND : fmtNum(n.en_radio)}</b>
        <span>{n.etiqueta.split(':')[0].toLowerCase()} a {fmtNum(radio)} m{n.ponderados != null ? `; ${fmtNum(n.ponderados, 1)} ponderados por distancia` : ''}</span>
      </p>
      {n.cercanos.length > 0 ? (
        <ol>
          {n.cercanos.map((c, i) => (
            <li key={`${c.nombre}-${i}`} data-fuera={!c.en_radio || undefined}>
              <span className="dz-neg__n"><b>{c.nombre ? titulo(c.nombre) : 'Sin nombre'}</b>{c.actividad && <small>{c.actividad}</small>}</span>
              <span className="dz-neg__d">{c.distancia_m == null ? ND : `${fmtNum(c.distancia_m)} m`}{!c.en_radio && <small>fuera del radio</small>}</span>
            </li>
          ))}
        </ol>
      ) : <p className="dz-nd-l">{ND}{n.motivo ? `: ${n.motivo.replace(/^NO ENCONTRADO:\s*/, '')}` : ': no hay negocios de este tipo en el DENUE.'}</p>}
      <Fuente>{n.fuente}</Fuente>
    </div>
  )
}

function BloqueCompetencia({ d }: { d: DesgloseZona }) {
  const c = d.competencia!
  return (
    <Bloque t="Competidores y complementarios" sub={`a ${fmtNum(c.radio_m)} m, el radio de influencia del giro`}>
      <h4 className="dz-sub">Competidores</h4>
      <ListaNegocios n={c.competidores} radio={c.radio_m} />
      <h4 className="dz-sub">Complementarios</h4>
      <ListaNegocios n={c.complementarios} radio={c.radio_m} />
    </Bloque>
  )
}

// ---------------------------------------------------------------- gente, ingreso, transporte y flujo
function BloqueGente({ d }: { d: DesgloseZona }) {
  const p = d.poblacion
  const maximo = Math.max(...p.grupos_edad.flatMap((g) => [g.pct_ageb, g.pct_municipio, g.pct_zmvm]).filter((x): x is number => x != null), 1) * 1.05
  return (
    <Bloque t="Quiénes viven aquí" sub="edades contra su municipio y la ZMVM" fuente={p.fuente}>
      <p className="dz-lineas"><b>{fmtNum(p.habitantes)}</b> habitantes · <b>{fmtNum(p.hogares)}</b> hogares · <b>{fmtNum(p.densidad_hab_km2)}</b> hab/km²</p>
      {p.habitantes === 0 && <p className="dz-nota"><Info size={13} aria-hidden /> El Censo 2020 no registra habitantes en esta AGEB, por eso no hay porcentajes por edad.</p>}
      <Leyenda />
      {p.grupos_edad.map((g, i) => (
        <Tres key={g.grupo} i={i} etiqueta={g.etiqueta} nota={g.personas != null ? `${fmtNum(g.personas)} personas` : undefined} formato={(n) => fmtPct(n, 1)} maximo={maximo}
          v={{ ageb: g.pct_ageb, municipio: g.pct_municipio, zmvm: g.pct_zmvm }} />
      ))}
    </Bloque>
  )
}

function BloqueIngreso({ d }: { d: DesgloseZona }) {
  const g = d.ingreso
  return (
    <Bloque t="Ingreso estimado" sub="decil y nivel socioeconómico" fuente={g.fuente}>
      <p className="dz-lineas">
        {g.nse ? <Pill tono="azul">{`NSE ${g.nse}`}</Pill> : <span className="dz-nd">NSE: {ND}</span>}{' '}
        <b>Decil {g.decil.ageb == null ? ND : fmtNum(g.decil.ageb)}</b> de 10
      </p>
      <Leyenda />
      <Tres etiqueta="Decil de ingreso" nota="1 = el más bajo, 10 = el más alto" v={g.decil} formato={(n) => fmtNum(n)} maximo={10} />
      <Tres etiqueta="Ingreso trimestral mediano por hogar" v={g.ingreso_trim_mediano_mxn} formato={(n) => fmtPesos(n, 0, true)} i={1} />
      {(['bajo', 'medio', 'alto'] as const).map((k, i) => (
        g.prob_nse_pct[k] && <Tres key={k} etiqueta={`Hogares de NSE ${k}`} nota="probabilidad estimada" v={g.prob_nse_pct[k]} formato={(n) => fmtPct(n, 0)} maximo={100} i={i + 2} />
      ))}
      <p className="dz-nota"><Info size={13} aria-hidden /> {g.como_leer}</p>
    </Bloque>
  )
}

function BloqueTransporte({ d }: { d: DesgloseZona }) {
  const t = d.transporte
  const f = d.flujo
  const mun = f.poblacion_diurna_ageb_media_municipio, zm = f.poblacion_diurna_ageb_media_zmvm
  return (
    <>
      <Bloque t="Transporte cerca" sub={`las ${fmtNum(t.estaciones.length)} más cercanas; en gris, las que quedan a más de ${fmtNum(t.radio_busqueda_m)} m`} fuente={t.fuente}>
        <p className="dz-lineas"><b>{fmtNum(t.a_1km)}</b> {t.a_1km === 1 ? 'estación' : 'estaciones'} a 1 km</p>
        {t.estaciones.length ? (
          <ol className="dz-est">
            {t.estaciones.map((e) => (
              <li key={`${e.sistema}-${e.linea}-${e.estacion}`} data-lejos={(e.distancia_m ?? 0) > t.radio_busqueda_m || undefined}>
                <span className="dz-est__n"><b>{titulo(e.estacion)}</b><small>{e.sistema}{e.linea ? ` · línea ${e.linea}` : ''}{e.afluencia_anual != null ? ` · ${fmtCompacto(e.afluencia_anual)} entradas al año${e.anio_afluencia ? ` (${e.anio_afluencia})` : ''}` : ' · afluencia: NO ENCONTRADO'}</small></span>
                <span className="dz-est__d">{e.distancia_m == null ? ND : `${fmtNum(e.distancia_m)} m`}</span>
              </li>
            ))}
          </ol>
        ) : <p className="dz-nd-l">{ND}: no hay estaciones registradas cerca.</p>}
      </Bloque>
      <Bloque t="Flujo de gente" sub="población diurna y empleo" fuente={f.fuente}>
        <p className="dz-lineas"><b>{fmtNum(f.poblacion_diurna)}</b> personas trabajan en los negocios de la AGEB (población diurna)</p>
        <Leyenda />
        <Tres etiqueta="Población diurna por AGEB" nota="la de esta AGEB contra el promedio de sus AGEB" formato={(n) => fmtNum(n)} v={{ ageb: f.poblacion_diurna, municipio: mun, zmvm: zm }} />
        <div className="dz-cifras">
          <div><b>{fmtNum(f.empleos_500m)}</b><span>empleos a 500 m</span></div>
          <div><b>{fmtNum(f.empleos_1km)}</b><span>empleos a 1 km</span></div>
          <div><b>{fmtNum(f.negocios_en_ageb)}</b><span>negocios en la AGEB</span></div>
          <div><b>{fmtNum(f.negocios_1km)}</b><span>negocios a 1 km</span></div>
        </div>
        {f.en_radio_del_giro && <p className="dz-nota">En el radio del giro ({fmtNum(f.en_radio_del_giro.radio_m)} m): {fmtNum(f.en_radio_del_giro.empleos)} empleos y {fmtNum(f.en_radio_del_giro.negocios_de_corredor)} negocios de corredor comercial (comercio, restaurantes y servicios), lo que entra al componente de flujo.</p>}
      </Bloque>
    </>
  )
}

// ---------------------------------------------------------------- panel
const ENFOCABLES = 'a[href], button:not([disabled]), select:not([disabled]), input:not([disabled]), textarea, [tabindex]:not([tabindex="-1"])'

function Panel({ a, lado, cerrar, elegirGiro }: { a: Abierto; lado: boolean; cerrar: () => void; elegirGiro: (g: string | null) => void }) {
  const raiz = useRef<HTMLDivElement>(null)
  const cuerpo = useRef<HTMLDivElement>(null)
  const ruta = `/api/zona/${encodeURIComponent(a.cvegeo)}/desglose${a.giro ? `?giro=${encodeURIComponent(a.giro)}` : ''}`
  const { datos, error, cargando, recargar } = useApi<DesgloseZona>(ruta)
  const d = datos && datos.ageb === a.cvegeo ? datos : null
  const colonia = d ? titulo(d.colonia) : a.colonia ? titulo(a.colonia) : null
  const municipio = d?.municipio ?? a.municipio
  const etiqueta = `Desglose de ${colonia ?? `la AGEB ${a.cvegeo}`}`

  // foco al panel al abrir (y al cambiar de zona), y arriba del cuerpo
  useEffect(() => {
    const id = requestAnimationFrame(() => raiz.current?.focus({ preventScroll: true }))
    if (cuerpo.current) cuerpo.current.scrollTop = 0
    return () => cancelAnimationFrame(id)
  }, [a.cvegeo])

  // Esc cierra; en modo «sobre» y en la hoja el Tab se queda dentro del panel
  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { e.preventDefault(); cerrar(); return }
      if (e.key !== 'Tab' || lado || !raiz.current) return
      const l = [...raiz.current.querySelectorAll<HTMLElement>(ENFOCABLES)].filter((x) => x.offsetParent !== null)
      if (!l.length) { e.preventDefault(); return }
      const primero = l[0], ultimo = l[l.length - 1]
      if (!raiz.current.contains(document.activeElement) || document.activeElement === raiz.current) { e.preventDefault(); (e.shiftKey ? ultimo : primero).focus() }
      else if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus() }
      else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus() }
    }
    document.addEventListener('keydown', tecla)
    return () => document.removeEventListener('keydown', tecla)
  }, [cerrar, lado])

  // clic fuera (con el panel al lado, sin velo): un clic en otra zona o en el mapa no lo cierra, porque cambia o conserva el desglose
  useEffect(() => {
    if (!lado) return
    const fuera = (e: PointerEvent) => {
      const t = e.target as HTMLElement | null
      if (!t || raiz.current?.contains(t) || t.closest('[data-zona], .c-mapa, .c-mapa__num, [role="dialog"]')) return
      cerrar()
    }
    document.addEventListener('pointerdown', fuera)
    return () => document.removeEventListener('pointerdown', fuera)
  }, [lado, cerrar])

  const viejo = !!datos && !d
  return (
    <>
      {!lado && <div className="dz-velo" onClick={cerrar} aria-hidden="true" />}
      <div ref={raiz} className="dz ss-scope" role="dialog" aria-label={etiqueta} aria-modal={!lado} tabIndex={-1} data-modo={lado ? 'lado' : 'sobre'}>
        <div className="dz__asa" aria-hidden="true" />
        <header className="dz__cab">
          <div className="dz__tit">
            <small>Desglose de la zona</small>
            <h2>{colonia ?? `AGEB ${a.cvegeo}`}</h2>
            <p>{municipio ? titulo(municipio) : ND} · AGEB {a.cvegeo}</p>
          </div>
          <button type="button" className="dz__x" onClick={cerrar} aria-label="Cerrar el desglose"><X size={18} aria-hidden /></button>
        </header>
        <div className="dz__ctl">
          <SelectorGiro valor={a.giro} onCambio={elegirGiro} etiqueta="Giro" vacio="Sin giro" />
          <a className="dz__ficha" href={href('zona', a.cvegeo, { giro: a.giro })}>Ver ficha completa<ArrowUpRight size={14} aria-hidden /></a>
        </div>
        <div ref={cuerpo} className="dz__cuerpo" data-actualizando={(cargando && !!d) || viejo || undefined} aria-busy={cargando}>
          {error ? <ErrorApi error={error} reintentar={recargar} titulo="No pude abrir el desglose" /> : !d ? (
            <div className="dz-espera"><Cargando forma="kpis" filas={2} /><Cargando forma="lista" filas={5} /></div>
          ) : (
            <>
              {d.score ? <BloqueScore d={d} /> : (
                <div className="dz-sin-giro" role="note">
                  <Info size={16} aria-hidden />
                  <p><b>{d.nota_giro ?? 'Elige un giro para ver el score.'}</b> Con un giro verás aquí cómo se arma su score, el lugar de esta AGEB entre las {fmtNum(d.agebs_zmvm)} y sus competidores más cercanos. Lo de abajo no depende del giro.</p>
                </div>
              )}
              {d.competencia && <BloqueCompetencia d={d} />}
              <BloqueGente d={d} />
              <BloqueIngreso d={d} />
              <BloqueTransporte d={d} />
              <div className="dz__pie">
                <a className="c-boton" href={href('zona', a.cvegeo, { giro: a.giro })} data-primario="true">Ver ficha completa<ArrowUpRight size={15} aria-hidden /></a>
                <details className="dz-fuentes">
                  <summary>Fuentes de este desglose ({fmtNum(d.fuentes.length)})</summary>
                  <ul>{d.fuentes.map((f) => <li key={f}>{f}</li>)}</ul>
                </details>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
