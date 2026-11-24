import { useEffect, useRef, useState } from 'react'
import { fmtNum } from '../../comun'
import type { GiroAuc } from './util'

// AUC por giro: el modelo (naranja) contra una línea base elegida (azul), un giro por renglón, ordenados por el AUC del modelo.
// Es un gráfico de puntos propio en modo plano: al cambiar de línea base los puntos azules se desplazan (transición con causa).
// El eje va de 0.4 a 1.0; 0.5 es el azar. Los giros con menos de 30 AGEB con apertura no entran (métricas inestables).

export type Base = 'comp_ageb' | 'competencia' | 'densidad' | 'actividad' | 'score'
export const BASES: { id: Base; texto: string; col: keyof GiroAuc; largo: string }[] = [
  { id: 'comp_ageb', texto: 'Competencia en la AGEB', col: 'auc_comp_ageb', largo: 'competidores del giro en la propia AGEB (2020)' },
  { id: 'competencia', texto: 'Competencia Huff', col: 'auc_competencia', largo: 'competidores del giro ponderados por distancia (Huff, 2020)' },
  { id: 'densidad', texto: 'Densidad', col: 'auc_densidad', largo: 'densidad de población (hab/km², Censo 2020)' },
  { id: 'actividad', texto: 'Actividad', col: 'auc_actividad', largo: 'negocios de todo tipo a 500 m (2020)' },
  { id: 'score', texto: 'Score combinado', col: 'auc_score', largo: 'el score de score_giro, que castiga la competencia a propósito' },
]
const MIN = 0.4, MAX = 1.0
const FILA = 22

export function PuntosAuc({ giros, base, activo, onActivo }: { giros: GiroAuc[]; base: Base; activo: string | null; onActivo: (g: string | null) => void }) {
  const ref = useRef<HTMLDivElement>(null)
  const [w, setW] = useState(0)
  useEffect(() => {
    const el = ref.current; if (!el) return
    setW(el.clientWidth)
    const ro = new ResizeObserver(() => setW(el.clientWidth)); ro.observe(el)
    return () => ro.disconnect()
  }, [])
  const col = BASES.find((b) => b.id === base)!.col
  const filas = giros.filter((g) => !g.poco_dato && g.auc_modelo != null).sort((a, b) => (b.auc_modelo as number) - (a.auc_modelo as number))
  const etq = w < 520 ? 104 : 168
  const x0 = etq + 10, x1 = Math.max(x0 + 60, w - 14)
  const px = (v: number) => x0 + ((Math.min(MAX, Math.max(MIN, v)) - MIN) / (MAX - MIN)) * (x1 - x0)
  const top = 26, alto = top + filas.length * FILA + 10
  const marcas = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
  return (
    <div ref={ref} className="ctx-pt">
      {w > 0 && (
        <svg width={w} height={alto} role="img" aria-label="AUC por giro: modelo contra línea base">
          {marcas.map((m) => (
            <g key={m}>
              <line x1={px(m)} x2={px(m)} y1={top - 6} y2={alto - 8} className={m === 0.5 ? 'ctx-pt__azar' : 'ctx-pt__rej'} />
              <text x={px(m)} y={14} textAnchor="middle" className="ctx-pt__marca">{fmtNum(m, 1)}</text>
            </g>
          ))}
          <text x={px(0.5) + 4} y={alto - 1} className="ctx-pt__azar-t">0.5 = azar</text>
          {filas.map((g, i) => {
            const y = top + i * FILA + FILA / 2
            const b = g[col] as number | null
            const on = activo === g.giro
            return (
              <g key={g.giro} className="ctx-pt__fila" data-on={on || undefined} onMouseEnter={() => onActivo(g.giro)} onMouseLeave={() => onActivo(null)} onClick={() => onActivo(on ? null : g.giro)}>
                <rect x={0} y={y - FILA / 2} width={w} height={FILA} className="ctx-pt__hit" />
                <text x={etq} y={y + 4} textAnchor="end" className="ctx-pt__etq">{w < 520 && g.nombre.length > 15 ? g.nombre.slice(0, 14) + '…' : g.nombre}</text>
                {b != null && <rect x={0} y={-1} width={1} height={2} className="ctx-pt__vinc" style={{ transform: `translate(${Math.min(px(b), px(g.auc_modelo as number))}px, ${y}px) scale(${Math.abs(px(b) - px(g.auc_modelo as number))}, 1)` }} />}
                {b != null && <circle r={4} className="ctx-pt__base" style={{ transform: `translate(${px(b)}px, ${y}px)` }} />}
                <circle r={5} className="ctx-pt__modelo" style={{ transform: `translate(${px(g.auc_modelo as number)}px, ${y}px)` }} />
                <title>{`${g.nombre}: modelo ${fmtNum(g.auc_modelo, 3)}; ${BASES.find((x) => x.id === base)!.texto.toLowerCase()} ${fmtNum(b, 3)}`}</title>
              </g>
            )
          })}
        </svg>
      )}
    </div>
  )
}
