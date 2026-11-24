import { useEffect, useId, useMemo, useRef, useState } from 'react'
import { Fuente } from './Fuente'
import { fmtNum } from './formato'

// Gráficas con datos reales en modo plano: solo líneas finas, ejes con marcas es-MX, hover con el valor, trazo que se dibuja
// al montarse y pie «Fuente:». El Chart del kit es una ilustración (sin ejes); para cifras reales usa estas.

export type TonoGrafica = 'naranja' | 'azul' | 'gris' | 'verde'
const VAR_TONO: Record<TonoGrafica, string> = { naranja: 'var(--accent)', azul: 'var(--blue)', gris: 'var(--muted)', verde: 'var(--green)' }
const ORDEN: TonoGrafica[] = ['naranja', 'azul', 'gris', 'verde']

/** Marcas «redondas» entre min y max: [0, 25, 50, 75, 100]. */
export function marcasBonitas(min: number, max: number, n = 4): number[] {
  if (!(max > min)) { max = min + 1 }
  const paso0 = (max - min) / n
  const mag = Math.pow(10, Math.floor(Math.log10(paso0)))
  const paso = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((p) => p >= paso0) ?? 10 * mag
  const a = Math.floor(min / paso + 1e-9) * paso, b = Math.ceil(max / paso - 1e-9) * paso
  const out: number[] = []
  for (let v = a; v <= b + paso / 2; v += paso) out.push(Math.abs(v) < paso * 1e-9 ? 0 : +v.toPrecision(12))
  return out
}

function useAncho<T extends HTMLElement>(): [React.RefObject<T | null>, number] {
  const ref = useRef<T>(null)
  const [w, setW] = useState(0)
  useEffect(() => {
    const el = ref.current; if (!el) return
    setW(el.clientWidth)
    const ro = new ResizeObserver(() => setW(el.clientWidth))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])
  return [ref, w]
}

// ------------------------------------------------------------------------------------------------ líneas
export interface SerieLinea {
  nombre: string
  /** x puede ser número (escala numérica: años, 2020, 2021…) o texto (categorías en orden: «2026-01», «2026-02»…). */
  puntos: { x: string | number; y: number }[]
  tono?: TonoGrafica
}
export interface GraficaLineasProps {
  series: SerieLinea[]
  /** Cómo se escribe un valor de Y en las marcas y el hover. Por defecto fmtNum. Ej.: fmtPct, fmtPesos. */
  formatoY?: (v: number) => string
  /** Cómo se escribe una X en las marcas y el hover (por defecto, tal cual). */
  formatoX?: (x: string | number) => string
  /** Título del eje X (abajo) y del Y (arriba a la izquierda). */
  etiquetaX?: string
  etiquetaY?: string
  /** Rango fijo del eje Y; por defecto se ajusta a los datos (incluye el 0 solo con `incluirCero`). */
  dominioY?: [number, number]
  incluirCero?: boolean
  /** Alto en px (por defecto 280). */
  alto?: number
  /** Fuente de la cifra: obligatoria, sale en el pie. */
  fuente: string
  titulo?: string
}

export function GraficaLineas({ series, formatoY = (v) => fmtNum(v, Math.abs(v) < 10 ? 2 : 0), formatoX = String, etiquetaX, etiquetaY, dominioY, incluirCero, alto = 280, fuente, titulo }: GraficaLineasProps) {
  const [ref, ancho] = useAncho<HTMLDivElement>()
  const id = useId()
  const [hover, setHover] = useState<number | null>(null)
  const numerica = series.every((s) => s.puntos.every((p) => typeof p.x === 'number'))
  const xs = useMemo(() => {
    const vistos = new Map<string | number, number>()
    series.forEach((s) => s.puntos.forEach((p) => { if (!vistos.has(p.x)) vistos.set(p.x, vistos.size) }))
    const l = [...vistos.keys()]
    return numerica ? (l as number[]).sort((a, b) => a - b) : l
  }, [series, numerica])
  const ys = series.flatMap((s) => s.puntos.map((p) => p.y)).filter(Number.isFinite)
  const mg = { d: 14, a: etiquetaY ? 22 : 8, b: etiquetaX ? 44 : 26 }
  const w0 = Math.max(0, ancho), ancho_i = 8 * (Math.max(...ys.map((y) => formatoY(y).length), 3)) + 14
  const x0 = ancho_i + 6, x1 = Math.max(x0 + 10, w0 - mg.d), y0 = mg.a, y1 = alto - mg.b
  let [lo, hi] = dominioY ?? [Math.min(...ys, incluirCero ? 0 : Infinity), Math.max(...ys, incluirCero ? 0 : -Infinity)]
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) { lo = 0; hi = 1 }
  const marcas = marcasBonitas(lo, hi)
  const dmin = dominioY ? lo : marcas[0], dmax = dominioY ? hi : marcas[marcas.length - 1]
  const px = (x: string | number) => {
    if (xs.length <= 1) return (x0 + x1) / 2
    if (numerica) { const a = xs[0] as number, b = xs[xs.length - 1] as number; return x0 + (((x as number) - a) / (b - a || 1)) * (x1 - x0) }
    return x0 + (xs.indexOf(x) / (xs.length - 1)) * (x1 - x0)
  }
  const py = (y: number) => y1 - ((y - dmin) / (dmax - dmin || 1)) * (y1 - y0)
  // marcas de X: con pocos valores enteros (deciles, años) una por valor; si no, un índice cada k empezando en el primero (separación uniforme)
  const ancho_x = x1 - x0
  const nx = Math.max(2, Math.floor(ancho_x / 80) + 1)
  const pocosEnteros = numerica && xs.length <= 12 && (xs as number[]).every(Number.isInteger) && ancho_x / Math.max(1, xs.length - 1) >= 26
  const marcasX = (() => {
    if (xs.length <= nx || pocosEnteros) return xs
    const k = Math.ceil((xs.length - 1) / (nx - 1))
    const idx: number[] = []
    for (let i = 0; i < xs.length; i += k) idx.push(i)
    if (xs.length - 1 - idx[idx.length - 1] >= k) idx.push(xs.length - 1)
    return idx.map((i) => xs[i])
  })()
  const sinDatos = !ys.length

  const mover = (e: React.PointerEvent<SVGRectElement>) => {
    const r = e.currentTarget.getBoundingClientRect(); const x = e.clientX - r.left + x0
    let mejor = 0, d = Infinity
    xs.forEach((v, i) => { const dd = Math.abs(px(v) - x); if (dd < d) { d = dd; mejor = i } })
    setHover(mejor)
  }
  const hx = hover != null ? xs[hover] : null
  const filasTip = hx == null ? [] : series.map((s, i) => ({ s, i, p: s.puntos.find((p) => p.x === hx) })).filter((f) => f.p)
  const tipX = hx != null ? px(hx) : 0
  const tipAlaIzq = tipX > w0 * 0.6

  return (
    <figure className="c-graf" style={{ margin: 0 }}>
      {titulo && <p className="c-graf__tit">{titulo}</p>}
      {series.length > 1 && (
        <div className="c-graf__leyenda">{series.map((s, i) => <span key={s.nombre} className={`c-graf-t--${s.tono ?? ORDEN[i % ORDEN.length]}`} style={{ color: VAR_TONO[s.tono ?? ORDEN[i % ORDEN.length]] }}><i />{<span style={{ color: 'var(--ink-2)' }}>{s.nombre}</span>}</span>)}</div>
      )}
      <div ref={ref} style={{ position: 'relative' }}>
        {sinDatos ? <p className="chico" style={{ padding: '24px 0' }}>NO ENCONTRADO: la fuente no trae datos para esta gráfica.</p> : w0 > 0 && (
          <svg width={w0} height={alto} role="img" aria-label={titulo ?? series.map((s) => s.nombre).join(', ')}>
            {marcas.filter((m) => m >= dmin - 1e-9 && m <= dmax + 1e-9).map((m) => (
              <g key={m}>
                <line className={m === 0 ? 'c-graf__eje' : 'c-graf__rej'} x1={x0} x2={x1} y1={py(m)} y2={py(m)} />
                <text x={x0 - 8} y={py(m)} textAnchor="end" dominantBaseline="middle">{formatoY(m)}</text>
              </g>
            ))}
            {marcasX.map((m, i) => (
              <text key={String(m)} x={px(m)} y={y1 + 18} textAnchor={i === 0 && marcasX.length > 1 ? 'start' : i === marcasX.length - 1 && marcasX.length > 1 ? 'end' : 'middle'}>{formatoX(m)}</text>
            ))}
            {etiquetaX && <text className="c-graf__eje-t" x={(x0 + x1) / 2} y={alto - 6} textAnchor="middle">{etiquetaX}</text>}
            {etiquetaY && <text className="c-graf__eje-t" x={0} y={9} textAnchor="start">{etiquetaY}</text>}
            {series.map((s, i) => {
              const tono = s.tono ?? ORDEN[i % ORDEN.length]
              const ps = [...s.puntos].filter((p) => Number.isFinite(p.y)).sort((a, b) => px(a.x) - px(b.x))
              const d = ps.map((p, k) => `${k ? 'L' : 'M'}${px(p.x).toFixed(1)} ${py(p.y).toFixed(1)}`).join('')
              return (
                <g key={s.nombre} className={`c-graf-t--${tono}`}>
                  {ps.length > 1 && <path key={id} className="c-graf__linea" d={d} pathLength={1} />}
                  {ps.length === 1 && <circle className="c-graf__pt" cx={px(ps[0].x)} cy={py(ps[0].y)} r={4} />}
                  {hx != null && ps.filter((p) => p.x === hx).map((p) => <circle key="h" className="c-graf__pt" cx={px(p.x)} cy={py(p.y)} r={4.5} />)}
                </g>
              )
            })}
            {hx != null && <line className="c-graf__guia" x1={tipX} x2={tipX} y1={y0} y2={y1} />}
            <rect x={x0} y={y0} width={x1 - x0} height={y1 - y0} fill="transparent" onPointerMove={mover} onPointerLeave={() => setHover(null)} />
          </svg>
        )}
        {hx != null && filasTip.length > 0 && (
          <div className="c-graf__tip" style={{ top: 4, ...(tipAlaIzq ? { right: w0 - tipX + 10 } : { left: tipX + 10 }) }}>
            <b>{formatoX(hx)}</b>
            {filasTip.map(({ s, i, p }) => <span key={s.nombre}><i style={{ background: VAR_TONO[s.tono ?? ORDEN[i % ORDEN.length]] }} />{series.length > 1 ? `${s.nombre}: ` : ''}<strong>{formatoY(p!.y)}</strong></span>)}
          </div>
        )}
      </div>
      <Fuente>{fuente}</Fuente>
    </figure>
  )
}

// ------------------------------------------------------------------------------------------------ barras
export interface FilaBarra { etiqueta: string; valor: number; tono?: TonoGrafica }
export interface GraficaBarrasProps {
  filas: FilaBarra[]
  /** Rango del eje de valores; por defecto [min(0, mínimo), máximo] ajustado a marcas redondas. */
  dominio?: [number, number]
  /** Cómo se escribe un valor en las marcas y junto a la barra. Por defecto fmtNum. */
  formato?: (v: number) => string
  /** Fuente de la cifra: obligatoria, sale en el pie. */
  fuente: string
  /** 'horizontal' (por defecto, filas con etiqueta larga) o 'vertical' (pocas barras con etiqueta corta). */
  orientacion?: 'horizontal' | 'vertical'
  /** Tono de todas las barras que no traen el suyo (por defecto naranja). */
  tono?: TonoGrafica
  /** Alto de la gráfica vertical (px; por defecto 260). */
  alto?: number
  /** Cómo se escriben las marcas del eje (por defecto, el mismo `formato`). Útil para que las marcas no lleven decimales de más. */
  formatoEje?: (v: number) => string
  /** Línea de referencia vertical (horizontal) con su rótulo, p. ej. un límite: { valor: 180, etiqueta: 'límite de 180 s' }. */
  referencia?: { valor: number; etiqueta: string }
  titulo?: string
  /** Clic en una barra (la fila se vuelve botón). */
  onClic?: (fila: FilaBarra, i: number) => void
}

export function GraficaBarras({ filas, dominio, formato = (v) => fmtNum(v, Math.abs(v) < 10 ? 2 : 0), fuente, orientacion = 'horizontal', tono = 'naranja', alto = 260, titulo, onClic, formatoEje, referencia }: GraficaBarrasProps) {
  const fEje = formatoEje ?? formato
  const [ref, ancho] = useAncho<HTMLDivElement>()
  const vals = filas.map((f) => f.valor).filter(Number.isFinite)
  const lo0 = dominio ? dominio[0] : Math.min(0, ...vals), hi0 = dominio ? dominio[1] : Math.max(0, ...vals)
  // menos marcas cuando la pista es angosta, para que las etiquetas no se encimen
  const nMarcas = Math.max(2, Math.min(5, Math.floor((orientacion === 'horizontal' ? ancho * 0.6 : ancho) / 90)))
  const marcas = marcasBonitas(lo0, hi0, nMarcas).filter((m) => dominio ? m >= lo0 - 1e-9 && m <= hi0 + 1e-9 : true)
  const lo = dominio ? lo0 : marcas[0], hi = dominio ? hi0 : marcas[marcas.length - 1]
  const pos = (v: number) => ((v - lo) / (hi - lo || 1)) * 100
  const cero = pos(Math.min(Math.max(0, lo), hi))
  const [hover, setHover] = useState<number | null>(null)

  if (!vals.length) return <figure className="c-graf" style={{ margin: 0 }}><p className="chico">NO ENCONTRADO: la fuente no trae datos para esta gráfica.</p><Fuente>{fuente}</Fuente></figure>

  if (orientacion === 'horizontal') {
    return (
      <figure className="c-graf" style={{ margin: 0 }}>
        {titulo && <p className="c-graf__tit">{titulo}</p>}
        <div ref={ref} className="c-gb">
          {filas.map((f, i) => {
            const a = pos(Math.min(f.valor, Math.max(lo, Math.min(0, hi)))), b = pos(Math.max(f.valor, Math.max(lo, Math.min(0, hi))))
            const clase = `c-graf-t--${f.tono ?? tono}`
            const Etq = onClic ? 'button' : 'div'
            return (
              <div key={f.etiqueta + i} className="c-gb__fila-sel" title={`${f.etiqueta}: ${formato(f.valor)}`} onClick={onClic ? () => onClic(f, i) : undefined} style={onClic ? { cursor: 'pointer' } : undefined}>
                <Etq className="c-gb__etq" {...(onClic ? { type: 'button', style: { all: 'unset', cursor: 'pointer', fontSize: 13.5, color: 'var(--ink-2)', padding: '7px 0', lineHeight: 1.25, overflowWrap: 'anywhere' } } : {})}>{f.etiqueta}</Etq>
                <div className="c-gb__pista">
                  {marcas.map((m) => <u key={m} data-cero={m === 0} style={{ left: `${pos(m)}%` }} />)}
                  {referencia && referencia.valor >= lo && referencia.valor <= hi && <u className="c-gb__ref" style={{ left: `${pos(referencia.valor)}%` }} aria-hidden="true" />}
                  <i className={`c-gb__barra ${clase}`} data-neg={f.valor < 0} style={{ left: `${a}%`, width: `${Math.max(0.4, b - a)}%`, ['--i' as string]: i }} />
                </div>
                <span className="c-gb__val">{formato(f.valor)}</span>
              </div>
            )
          })}
          <div className="c-gb__ejes" data-ref={referencia ? 'true' : undefined}>
            {marcas.map((m) => <span key={m} style={{ left: `${pos(m)}%` }}>{fEje(m)}</span>)}
            {referencia && referencia.valor >= lo && referencia.valor <= hi && <em className="c-gb__ref-t" style={{ left: `${pos(referencia.valor)}%`, ...(pos(referencia.valor) > 70 ? { transform: 'translateX(-100%)' } : null) }}>{referencia.etiqueta}</em>}
          </div>
        </div>
        <Fuente>{fuente}</Fuente>
      </figure>
    )
  }

  // vertical (SVG)
  const w = Math.max(0, ancho), x0 = 8 * Math.max(...marcas.map((m) => fEje(m).length), 3) + 14, x1 = w - 8, y0 = 8, y1 = alto - 34
  const py = (v: number) => y1 - ((v - lo) / (hi - lo || 1)) * (y1 - y0)
  const paso = (x1 - x0) / filas.length, bw = Math.min(46, paso * 0.58)
  return (
    <figure className="c-graf" style={{ margin: 0 }}>
      {titulo && <p className="c-graf__tit">{titulo}</p>}
      <div ref={ref} style={{ position: 'relative' }}>
        {w > 0 && (
          <svg width={w} height={alto} role="img" aria-label={titulo ?? 'Gráfica de barras'}>
            {marcas.map((m) => (
              <g key={m}>
                <line className={m === 0 ? 'c-graf__eje' : 'c-graf__rej'} x1={x0} x2={x1} y1={py(m)} y2={py(m)} />
                <text x={x0 - 8} y={py(m)} textAnchor="end" dominantBaseline="middle">{fEje(m)}</text>
              </g>
            ))}
            {filas.map((f, i) => {
              const cx = x0 + paso * (i + 0.5), yv = py(f.valor), y00 = py(Math.min(Math.max(0, lo), hi))
              return (
                <g key={f.etiqueta + i} className={`c-graf-t--${f.tono ?? tono}`} onPointerEnter={() => setHover(i)} onPointerLeave={() => setHover(null)} onClick={onClic ? () => onClic(f, i) : undefined} style={onClic ? { cursor: 'pointer' } : undefined}>
                  <rect x={cx - paso / 2} y={y0} width={paso} height={y1 - y0} fill="transparent" />
                  <rect x={cx - bw / 2} y={Math.min(yv, y00)} width={bw} height={Math.max(1, Math.abs(y00 - yv))} rx={2} fill="var(--tono)" opacity={hover == null || hover === i ? 1 : 0.45} />
                  <text x={cx} y={Math.min(yv, y00) - 6} textAnchor="middle" style={{ fill: 'var(--ink)', fontWeight: 600 }}>{formato(f.valor)}</text>
                  <text x={cx} y={y1 + 16} textAnchor="middle">{f.etiqueta.length > Math.floor(paso / 6.5) + 1 ? f.etiqueta.slice(0, Math.max(3, Math.floor(paso / 6.5))) + '…' : f.etiqueta}</text>
                </g>
              )
            })}
          </svg>
        )}
      </div>
      <Fuente>{fuente}</Fuente>
    </figure>
  )
}
