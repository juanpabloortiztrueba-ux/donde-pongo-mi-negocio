import { useEffect, useMemo, useRef, useState } from 'react'
import { fmtNum, fmtPct, Fuente } from '../../comun'
import type { CajaHist } from './util'

// Histograma plano con «scrub»: al pasar el cursor, las cajas hasta ahí se pintan fuertes y el pie dice qué parte de las AGEB queda
// por debajo. Las cajas crecen desde la base cada vez que cambia la variable (key). Solo líneas y el color del fondo.

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

export function Histograma({ cajas, formato, mediana, extremos, fuente, unidad, alto = 200, clave }: {
  cajas: CajaHist[]; formato: (v: number) => string; mediana: number | null; extremos: number; fuente: string; unidad: string; alto?: number; clave: string
}) {
  const [ref, w] = useAncho<HTMLDivElement>()
  const [sel, setSel] = useState<number | null>(null)
  const total = useMemo(() => cajas.reduce((a, c) => a + c.n, 0), [cajas])
  const maxN = useMemo(() => Math.max(1, ...cajas.map((c) => c.n)), [cajas])
  const acum = useMemo(() => { let s = 0; return cajas.map((c) => (s += c.n)) }, [cajas])
  const mg = { i: 6, d: 6, a: 22, b: 26 }
  const ancho = Math.max(0, w - mg.i - mg.d), h = alto - mg.a - mg.b
  const bw = cajas.length ? ancho / cajas.length : 0
  const x0 = cajas[0]?.x0 ?? 0, x1 = cajas[cajas.length - 1]?.x1 ?? 1
  const xMed = mediana != null && x1 > x0 ? mg.i + ((mediana - x0) / (x1 - x0)) * ancho : null
  const etiquetaCaja = (c: CajaHist) => c.etiqueta ?? `${formato(c.x0)} a ${formato(c.x1)}`
  const ticks = cajas.length <= 10 ? cajas.map((c, i) => ({ x: mg.i + (i + 0.5) * bw, t: c.etiqueta ?? fmtNum((c.x0 + c.x1) / 2), centro: true }))
    : [0, 0.25, 0.5, 0.75, 1].map((q) => ({ x: mg.i + q * ancho, t: formato(x0 + q * (x1 - x0)), centro: false }))
  const aviso = sel != null ? cajas[sel] : null
  const tipX = sel != null ? mg.i + (sel + 0.5) * bw : 0

  return (
    <div className="exp-hist" ref={ref}>
      {w > 0 && (
        <svg width={w} height={alto} role="img" aria-label={`Histograma de ${unidad}: ${fmtNum(total)} AGEB`} onPointerLeave={() => setSel(null)}
          onPointerMove={(e) => {
            const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
            const i = Math.floor((e.clientX - r.left - mg.i) / bw)
            setSel(i >= 0 && i < cajas.length ? i : null)
          }}>
          <line className="c-graf__eje" x1={mg.i} x2={mg.i + ancho} y1={mg.a + h} y2={mg.a + h} />
          <g key={clave}>
            {cajas.map((c, i) => {
              const alt = Math.max(c.n > 0 ? 1.5 : 0, (c.n / maxN) * h)
              return <rect key={i} className="exp-hist__caja" data-fuera={sel != null && i > sel ? 'true' : undefined}
                x={mg.i + i * bw + 1} width={Math.max(1, bw - 2)} y={mg.a + h - alt} height={alt} rx={1.5} style={{ animationDelay: `${i * 18}ms` }} />
            })}
          </g>
          {xMed != null && sel == null && (
            <g className="exp-hist__med"><line x1={xMed} x2={xMed} y1={mg.a - 8} y2={mg.a + h} /><text x={xMed > mg.i + ancho * 0.7 ? xMed - 5 : xMed + 5} y={mg.a - 10} textAnchor={xMed > mg.i + ancho * 0.7 ? 'end' : 'start'}>mediana {formato(mediana!)}</text></g>
          )}
          {sel != null && <line className="c-graf__guia" x1={tipX} x2={tipX} y1={mg.a} y2={mg.a + h} />}
          {ticks.map((t, i) => <text key={i} x={t.x} y={alto - 8} textAnchor={t.centro ? 'middle' : i === 0 ? 'start' : i === ticks.length - 1 ? 'end' : 'middle'}>{t.t}</text>)}
        </svg>
      )}
      {aviso && w > 0 && (
        <div className="exp-hist__tip" style={{ left: Math.min(Math.max(8, tipX - 110), Math.max(8, w - 228)), top: 0 }}>
          <b>{etiquetaCaja(aviso)}</b>
          <span>{fmtNum(aviso.n)} AGEB · {fmtPct((aviso.n / total) * 100, 1)}</span>
          <span>{fmtPct((acum[sel!] / total) * 100, 0)} de las AGEB están en esta caja o abajo</span>
        </div>
      )}
      <p className="chico exp-hist__nota">
        {sel == null ? `Pasa el cursor para ver cuántas AGEB hay en cada rango.` : ' '}
        {extremos > 0 && <> Las {fmtNum(extremos)} AGEB por debajo del percentil 2 o por encima del 98 se juntan en las cajas de las orillas.</>}
      </p>
      <Fuente>{fuente}</Fuente>
    </div>
  )
}
