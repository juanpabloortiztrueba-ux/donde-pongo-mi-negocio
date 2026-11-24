import { fmtNum, Fuente } from '../../comun'

/** Barras de dos series una junto a la otra (esta AGEB contra la ZMVM, 500 m contra 1 km). Plano: solo barras finas sobre el fondo.
 *  Las barras crecen desde 0 al montarse. Cada valor se escribe con `formato` (es-MX). */
export interface FilaComp { etiqueta: string; a: number | null; b: number | null; nota?: string }

export function Comparativa({ filas, nombreA, nombreB, formato = (v) => fmtNum(v, 1), maximo, fuente, titulo }: {
  filas: FilaComp[]; nombreA: string; nombreB: string; formato?: (v: number) => string; maximo?: number; fuente: string; titulo?: string
}) {
  const vals = filas.flatMap((f) => [f.a, f.b]).filter((v): v is number => v != null && Number.isFinite(v))
  if (!vals.length) return <figure className="pre-cmp"><p className="chico">NO ENCONTRADO: la fuente no trae datos para este bloque.</p><Fuente>{fuente}</Fuente></figure>
  const tope = maximo ?? (Math.max(...vals) * 1.05 || 1)
  const w = (v: number | null) => (v == null ? 0 : Math.max(0.6, (v / tope) * 100))
  return (
    <figure className="pre-cmp">
      {titulo && <p className="c-graf__tit">{titulo}</p>}
      <div className="pre-cmp__ley"><span><i data-t="a" />{nombreA}</span><span><i data-t="b" />{nombreB}</span></div>
      <div className="pre-cmp__filas">
        {filas.map((f, i) => (
          <div key={f.etiqueta} className="pre-cmp__fila" style={{ ['--i' as string]: i }}>
            <div className="pre-cmp__etq">{f.etiqueta}{f.nota && <small>{f.nota}</small>}</div>
            <div className="pre-cmp__pista" title={`${f.etiqueta}: ${nombreA} ${f.a == null ? 'NO ENCONTRADO' : formato(f.a)}; ${nombreB} ${f.b == null ? 'NO ENCONTRADO' : formato(f.b)}`}>
              <i data-t="a" style={{ width: `${w(f.a)}%` }} />
              <i data-t="b" style={{ width: `${w(f.b)}%` }} />
            </div>
            <div className="pre-cmp__val"><b>{f.a == null ? 'NO ENCONTRADO' : formato(f.a)}</b><span>{f.b == null ? 'NO ENCONTRADO' : formato(f.b)}</span></div>
          </div>
        ))}
      </div>
      <Fuente>{fuente}</Fuente>
    </figure>
  )
}
