import { useEffect, useRef, useState } from 'react'
import { Roll, Stage, Window, type Act } from '../../kit'
import { fmtNum, titulo, useTema } from '../../comun'
import type { EjemploScore } from './util'
import './contexto.css'

// Escena stageshow que arma la suma del score: una AGEB real del top (de /api/modelo/ejemplo) entra término por término,
// cada uno con su percentil dentro de la ZMVM, su peso (leído en vivo de app/motor.py) y lo que aporta; la barra de abajo
// se llena con cada aporte y la cifra rueda hasta el score. Poster = estado final.

type S = { paso: number }
const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v))

export function EscenaScore({ e }: { e: EjemploScore }) {
  const { tema } = useTema()
  const n = e.terminos.length
  const caja = useRef<HTMLDivElement>(null)
  const [cw, setCw] = useState(900)
  useEffect(() => {
    const el = caja.current; if (!el) return
    const medir = () => setCw(Math.floor(el.clientWidth / 4) * 4 || 900)
    medir()
    const ro = new ResizeObserver(medir); ro.observe(el)
    return () => ro.disconnect()
  }, [])
  const W = clamp(cw, 640, 1000), CW = clamp(cw, 300, 420)
  const guion = async (a: Act<S>) => {
    await a.wait(900)
    for (let i = 1; i <= n; i++) { a.put({ paso: i }); await a.wait(950) }
    await a.wait(2400)
  }
  const acum = (paso: number) => (paso <= 0 ? 0 : e.terminos[Math.min(paso, n) - 1].acumulado)
  return (
    <div ref={caja} className="ctx-es-caja">
      <Stage<S> width={W} height={480} compact={{ below: 640, width: CW, height: 650 }} theme={tema} initial={{ paso: 0 }} poster={{ paso: n }} script={guion} play="once">
        {(s, _r, layout) => {
          const compacto = layout === 'compact'
          return (
            <Window title={`score de ${e.nombre_giro.toLowerCase()} · ${titulo(e.colonia)}, ${titulo(e.municipio)}`} className="ctx-es-win">
              <div className="ctx-es" data-compacto={compacto}>
                <div className="ctx-es__cab">
                  <span>Término del score</span><span className="ctx-es__c-pct">Percentil en la ZMVM</span><span className="ctx-es__c-ap">Aporte</span>
                </div>
                {e.terminos.map((t, i) => (
                  <div key={t.clave} className="ctx-es__fila" data-on={s.paso > i || undefined} data-ult={s.paso === i + 1 || undefined}>
                    <div className="ctx-es__nom"><b>{t.nombre}</b><small>peso {fmtNum(t.peso_norm, 2)}</small></div>
                    <div className="ctx-es__pista" aria-hidden><i style={{ width: s.paso > i ? `${t.percentil * 100}%` : '0%' }} /></div>
                    <div className="ctx-es__pct">{s.paso > i ? `p${fmtNum(t.percentil * 100, 0)}` : '—'}</div>
                    <div className="ctx-es__ap"><Roll stagger={30}>{s.paso > i ? `+${fmtNum(t.aporte, 1)}` : '+0.0'}</Roll></div>
                  </div>
                ))}
                <div className="ctx-es__suma" aria-hidden>
                  {e.terminos.map((t, i) => (
                    <i key={t.clave} data-k={i} style={{ width: s.paso > i ? `${t.aporte}%` : '0%' }} />
                  ))}
                </div>
                <div className="ctx-es__tot">
                  <span>{s.paso >= n ? 'Score de la AGEB' : 'Suma hasta ahora'}</span>
                  <span className="ctx-es__score" data-fin={s.paso >= n || undefined}><Roll stagger={40}>{fmtNum(acum(s.paso), 1)}</Roll></span>
                </div>
              </div>
            </Window>
          )
        }}
      </Stage>
    </div>
  )
}
