import { useEffect, useMemo, useRef, useState } from 'react'
import { Chart, Roll, Stage, Window, chartPoints, type Act } from '../../kit'
import { useTema } from '../../comun'
import type { SerieMacro } from './util'
import { fecha } from './util'
import './contexto.css'

// Escena «chart-scrub» de stageshow con datos reales: el puntero recorre la serie y el encabezado lee el mes que toca
// (la etiqueta y la cifra ruedan; no hay globo sobre la línea). Todo sale de /api/macro; el poster es el último mes.
// Un solo trazo del puntero; el mes bajo el puntero es siempre un mes real (el más cercano), mientras la línea fina sigue al puntero
// y el punto va sobre la curva dibujada.

type S = { dia: number | null; x: number | null }
const H = 150
const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v))

function yEn(path: SVGPathElement | null | undefined, x: number) {
  if (!path) return null
  let lo = 0, hi = path.getTotalLength()
  for (let i = 0; i < 24; i++) { const m = (lo + hi) / 2; if (path.getPointAtLength(m).x < x) lo = m; else hi = m }
  return path.getPointAtLength(hi).y
}

export function EscenaScrub({ serie, formato, titulo }: { serie: SerieMacro; formato: (v: number) => string; titulo: string }) {
  const { tema } = useTema()
  const meses = useMemo(() => serie.puntos.map((p) => p[0]), [serie])
  const vals = useMemo(() => serie.puntos.map((p) => p[1]), [serie])
  // La escena mide su contenedor para que el Stage nunca escale con transform (borroso en Safari): el diseño se ajusta al ancho real.
  const caja = useRef<HTMLDivElement>(null)
  const [cw, setCw] = useState(760)
  useEffect(() => {
    const el = caja.current; if (!el) return
    const medir = () => setCw(Math.floor(el.clientWidth / 4) * 4 || 760)
    medir()
    const ro = new ResizeObserver(medir); ro.observe(el)
    return () => ro.disconnect()
  }, [])
  const W = clamp(cw, 640, 860), CW = clamp(cw, 300, 420)
  const ancho = { wide: W - 2 * 30, compact: CW - 2 * 18 }
  // El Chart del kit dibuja desde cero: se le resta la base para que la línea use todo el alto (los valores mostrados son los reales).
  const lo = Math.min(...vals), hi = Math.max(...vals)
  const base = lo - 0.12 * (hi - lo)
  const datos = useMemo(() => vals.map((v) => v - base), [vals, base])
  const iMax = vals.indexOf(hi), iUlt = vals.length - 1

  const guion = async (a: Act<S>) => {
    await a.wait(900)
    const caja = a.rect('plot')
    const pts = chartPoints({ data: datos, width: caja.width, height: H, dot: false })
    const en = (i: number) => ({ x: caja.x + pts[i]!.x, y: caja.y + pts[i]!.y })
    a.mark('hover')
    await a.move(en(iMax), { duration: 900 })
    a.put({ dia: iMax, x: pts[iMax]!.x })
    await a.wait(1100)
    a.mark('scrub')
    await a.move(en(iUlt), {
      duration: 2600,
      path: (e, from, to) => ({ x: from.x + (to.x - from.x) * e, y: from.y + (to.y - from.y) * e }),
      onMove: (pt) => {
        const x = clamp(pt.x - caja.x, 0, caja.width)
        let cerca = 0
        for (let i = 1; i < pts.length; i++) if (Math.abs(pts[i]!.x - x) < Math.abs(pts[cerca]!.x - x)) cerca = i
        a.put({ dia: cerca, x })
      },
    })
    await a.wait(1800)
    a.mark('leave')
    let fuera = false
    await a.move({ x: caja.x + caja.width + 40, y: caja.y + caja.height + 60 }, {
      duration: 600,
      onMove: (pt) => { if (!fuera && (pt.x > caja.x + caja.width || pt.y > caja.y + caja.height)) { fuera = true; a.put({ dia: null }) } },
    })
    await a.wait(1600)
  }
  const plot = useRef<HTMLDivElement>(null)
  return (
    <div ref={caja} className="ctx-sc">
      <Stage<S> width={W} height={340} compact={{ below: 640, width: CW, height: 340 }} theme={tema} initial={{ dia: null, x: null }} poster={{ dia: iUlt, x: null }}
        script={guion} play="once" cursor={{ at: { wide: { x: W - 120, y: 300 }, compact: { x: CW - 70, y: 300 } }, style: 'real' }}>
        {(s, _r, layout) => {
          const w = layout === 'compact' ? ancho.compact : ancho.wide
          const pts = chartPoints({ data: datos, width: w, height: H, dot: false })
          const dia = s.dia ?? iUlt
          const hx = s.x ?? pts[dia]!.x
          const hy = yEn(plot.current?.querySelector<SVGPathElement>('.ss-chart__line'), hx) ?? pts[dia]!.y
          const encima = s.dia !== null || s.x === null  // en reposo se marca el último mes
          return (
            <Window title={titulo} className="ctx-sc-win">
              <div className="ctx-sc-body" data-compacto={layout === 'compact'}>
                <div className="ctx-sc-lect">
                  <div className="ctx-sc-et"><Roll variant="fade">{s.dia === null ? `Dato más reciente: ${fecha(meses[iUlt])}` : fecha(meses[dia])}</Roll></div>
                  <div className="ctx-sc-val"><Roll stagger={25}>{formato(vals[dia]!)}</Roll></div>
                </div>
                <div ref={plot} className="ctx-sc-plot" data-target="plot" data-cursor="crosshair" style={{ width: w, height: H }}>
                  <Chart data={datos} width={w} height={H} dot={false} />
                  <span className="ctx-sc-hair" data-on={encima || undefined} style={{ left: hx }} />
                  <span className="ctx-sc-dot" data-on={encima || undefined} style={{ left: hx, top: hy }} />
                </div>
                <div className="ctx-sc-eje" style={{ width: w }}><span>{fecha(meses[0])}</span><span>{fecha(meses[iUlt])}</span></div>
              </div>
            </Window>
          )
        }}
      </Stage>
    </div>
  )
}
