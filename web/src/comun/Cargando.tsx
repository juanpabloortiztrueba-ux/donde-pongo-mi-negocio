import { Bar } from '../kit'

/** Esqueleto con la geometría del contenido que viene (como el ejemplo «loading» de stageshow):
 *  forma «kpis» (fila de cifras), «lista» (filas con avatar y dos líneas), «texto» (párrafos) o «mapa» (lienzo). */
export function Cargando({ forma = 'lista', filas = 5, alto = 420 }: { forma?: 'kpis' | 'lista' | 'texto' | 'mapa'; filas?: number; alto?: number }) {
  if (forma === 'mapa') return <div className="c-carga__mapa" style={{ height: alto }} role="status" aria-label="Cargando" />
  if (forma === 'kpis') {
    return (
      <div className="c-carga" role="status" aria-label="Cargando" style={{ gridTemplateColumns: `repeat(${filas}, minmax(0, 1fr))`, gap: 28 }}>
        {Array.from({ length: filas }, (_, i) => (
          <div key={i} style={{ display: 'grid', gap: 10, paddingTop: 14, borderTop: '1px solid var(--rule-2)' }}>
            <Bar w={110} h={34} r={8} tone={2} /><Bar w={86} h={10} r={5} tone={2} />
          </div>
        ))}
      </div>
    )
  }
  if (forma === 'texto') {
    return (
      <div className="c-carga" role="status" aria-label="Cargando" style={{ maxWidth: 640 }}>
        {Array.from({ length: filas }, (_, i) => <Bar key={i} w={i % 3 === 2 ? '62%' : '100%'} h={11} r={5} tone={2} />)}
      </div>
    )
  }
  return (
    <div className="c-carga" role="status" aria-label="Cargando">
      {Array.from({ length: filas }, (_, i) => (
        <div key={i} className="c-carga__fila">
          <Bar w={30} h={30} r={15} tone={2} />
          <div style={{ display: 'grid', gap: 7 }}><Bar w={150 + (i % 3) * 30} h={10} r={5} tone={2} /><Bar w={96} h={8} r={4} tone={2} /></div>
        </div>
      ))}
    </div>
  )
}
