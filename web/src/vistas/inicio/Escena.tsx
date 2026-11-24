import { useEffect, useMemo, useRef, useState } from 'react'
import { Field, Roll, Stage, Window, type Act } from '../../kit'
import { secuencial, titulo, useTema, type DemoInicio } from '../../comun'
import './inicio.css'

// Escena stageshow del uso: se escribe «Quiero poner una heladería», aparece el mapa con el score de cada AGEB
// y el top 5 rueda. Todo sale de /api/inicio/demo (recomendar_zonas + score_giro), nada escrito a mano.
// Poster = estado final (lo que ve quien pide menos movimiento).

type S = { typed: string; fase: number; rodar: boolean; sel: number | null }
const INICIAL: S = { typed: '', fase: 0, rodar: false, sel: null }
const POSTER: S = { typed: 'Quiero poner una heladería', fase: 2, rodar: true, sel: null }

function proyector(puntos: DemoInicio['puntos'], w: number, h: number) {
  let x0 = 180, x1 = -180, y0 = 90, y1 = -90
  for (const p of puntos) { if (p[0] < x0) x0 = p[0]; if (p[0] > x1) x1 = p[0]; if (p[1] < y0) y0 = p[1]; if (p[1] > y1) y1 = p[1] }
  const k = Math.cos(((y0 + y1) / 2) * Math.PI / 180)
  const sx = w / ((x1 - x0) * k), sy = h / (y1 - y0)
  const s = Math.min(sx, sy)
  const ox = (w - (x1 - x0) * k * s) / 2, oy = (h - (y1 - y0) * s) / 2
  return (lon: number, lat: number): [number, number] => [ox + (lon - x0) * k * s, oy + (y1 - lat) * s]
}

/** Separa los pines que quedan a menos de `min` px (relajación por pares) para que ninguno tape a otro; cada uno conserva su punto real. */
function separar(pts: [number, number][], w: number, h: number, min = 26): [number, number][] {
  const p = pts.map(([x, y], i) => [x + (pts.some(([a, b], j) => j < i && a === x && b === y) ? 0.5 * i : 0), y] as [number, number])
  for (let it = 0; it < 60; it++) {
    let mov = false
    for (let i = 0; i < p.length; i++) for (let j = i + 1; j < p.length; j++) {
      let dx = p[j][0] - p[i][0], dy = p[j][1] - p[i][1]
      let d = Math.hypot(dx, dy)
      if (d >= min) continue
      if (d < 0.01) { dx = Math.cos(i * 2.4 + j); dy = Math.sin(i * 2.4 + j); d = 1 }
      const k = (min - d) / 2 / d
      p[i][0] -= dx * k; p[i][1] -= dy * k; p[j][0] += dx * k; p[j][1] += dy * k
      mov = true
    }
    for (const q of p) { q[0] = Math.min(w - 14, Math.max(14, q[0])); q[1] = Math.min(h - 14, Math.max(14, q[1])) }
    if (!mov) break
  }
  return p
}

function Puntos({ datos, w, h, visible, tema }: { datos: DemoInicio; w: number; h: number; visible: boolean; tema: 'light' | 'dark' }) {
  const caminos = useMemo(() => {
    const proj = proyector(datos.puntos, w, h)
    const grupos: string[][] = Array.from({ length: 8 }, () => [])
    for (const [lon, lat, sc] of datos.puntos) {
      const [x, y] = proj(lon, lat)
      grupos[Math.min(7, Math.floor((sc / 100) * 8))].push(`M${x.toFixed(1)} ${y.toFixed(1)}h2.6v2.6h-2.6z`)
    }
    return grupos
  }, [datos, w, h])
  return (
    <svg className="ini-pts" width={w} height={h} data-on={visible} aria-hidden>
      {caminos.map((d, i) => <path key={i} d={d.join('')} fill={secuencial(i / 7, tema)} />)}
    </svg>
  )
}

const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v))

export function Escena({ datos }: { datos: DemoInicio }) {
  const { tema } = useTema()
  const top = datos.zonas
  const pregunta = POSTER.typed
  // El Stage del kit escala con transform si su contenedor es más angosto que su diseño (texto diminuto y borroso en Safari).
  // Para que la escala siempre sea 1, el diseño se ajusta al ancho real del contenedor: el layout flex se reacomoda solo.
  const caja = useRef<HTMLDivElement>(null)
  const [cw, setCw] = useState(1040)
  useEffect(() => {
    const el = caja.current; if (!el) return
    const medir = () => setCw(Math.floor(el.clientWidth / 4) * 4 || 1040)
    medir()
    const ro = new ResizeObserver(medir); ro.observe(el)
    return () => ro.disconnect()
  }, [])
  const W = clamp(cw, 640, 1040)
  const CW = clamp(cw, 300, 420)
  const guion = async (a: Act<S>) => {
    await a.wait(900)
    await a.click('campo')
    a.put({ fase: 0 })
    await a.type('typed', pregunta, { interval: 42 })
    await a.wait(500)
    await a.key('Enter')
    a.put({ fase: 1 })
    await a.wait(1300)
    a.put({ fase: 2 })
    await a.wait(450)
    a.put({ rodar: true })
    await a.wait(1400)
    await a.move('fila0', { duration: 900 })
    a.put({ sel: 0 })
    await a.wait(2600)
  }
  return (
    <div ref={caja} className="ini-escena">
    <Stage<S> width={W} height={412} compact={{ below: 640, width: CW, height: 590 }} theme={tema} initial={INICIAL} poster={POSTER} script={guion}
      play="once" cursor={{ at: { wide: { x: 600, y: 420 }, compact: { x: 280, y: 560 } }, style: 'real' }}>
      {(s, _rect, layout) => {
        const compacto = layout === 'compact'
        const mw = compacto ? CW - 28 : clamp(W - 368, 280, 580), mh = compacto ? Math.round(mw * 0.64) : Math.round(mw * 0.586)
        const proj = proyector(datos.puntos, mw, mh)
        const reales = top.map((z) => proj(z.lon, z.lat))
        const pines = separar(reales, mw, mh)
        return (
          <Window url="donde-pongo-mi-negocio  /  preguntar" className="ini-win">
            <div className="ini-esc" data-compacto={compacto}>
              <div className="ini-esc__izq">
                <Field value={s.typed} placeholder="Describe tu negocio…" focused={s.typed.length > 0 && s.fase === 0} box={{ 'data-target': 'campo', 'data-cursor': 'ibeam' } as never} />
                <ol className="ini-top" data-on={s.fase >= 2}>
                  {top.map((z, i) => (
                    <li key={z.ageb} className="ini-top__fila" data-target={`fila${i}`} data-sel={s.sel === i || undefined} style={{ ['--i' as string]: i }}>
                      <span className="ini-top__n">{i + 1}</span>
                      <span className="ini-top__t"><b>{titulo(z.colonia)}</b><small>{titulo(z.municipio)}</small></span>
                      <span className="ini-top__v"><Roll stagger={30}>{String(s.rodar ? Math.round(z.score) : 0)}</Roll></span>
                    </li>
                  ))}
                </ol>
              </div>
              <div className="ini-esc__mapa" style={{ width: mw, height: mh }}>
                <Puntos datos={datos} w={mw} h={mh} visible={s.fase >= 1} tema={tema} />
                <svg className="ini-guias" width={mw} height={mh} data-on={s.fase >= 2} aria-hidden>
                  {pines.map((q, i) => (Math.hypot(q[0] - reales[i][0], q[1] - reales[i][1]) > 3 ? (
                    <g key={i}><line x1={reales[i][0]} y1={reales[i][1]} x2={q[0]} y2={q[1]} /><circle cx={reales[i][0]} cy={reales[i][1]} r={2} /></g>
                  ) : null))}
                </svg>
                {top.map((z, i) => (
                  <span key={z.ageb} className="ini-pin" data-on={s.fase >= 2} data-sel={s.sel === i || undefined} style={{ left: pines[i][0], top: pines[i][1], ['--i' as string]: i }}>{i + 1}</span>
                ))}
                <span className="ini-esc__leyenda" data-on={s.fase >= 1}>Score de heladería por AGEB</span>
              </div>
            </div>
          </Window>
        )
      }}
    </Stage>
    </div>
  )
}
