import { useEffect, useState } from 'react'
import { Count } from '../kit'
import { Fuente } from './Fuente'
import { fmtNum } from './formato'

/** Cifra grande con etiqueta y fuente. El valor «rueda» desde 0 al montarse (Count de stageshow) y cada vez que cambia.
 *  valor=null → «NO ENCONTRADO» (la fuente no tiene el dato). `formato` por defecto: fmtNum. */
export function Kpi({ valor, etiqueta, fuente, formato = (n) => fmtNum(n), tono, retraso = 0 }: {
  valor: number | null | undefined; etiqueta: string; fuente?: string; formato?: (n: number) => string; tono?: 'accent'; retraso?: number
}) {
  const [v, setV] = useState(0)
  useEffect(() => {
    if (valor == null) return
    const t = setTimeout(() => setV(valor), 120 + retraso)
    return () => clearTimeout(t)
  }, [valor, retraso])
  return (
    <div className="c-kpi" data-tono={tono}>
      <div className="c-kpi__valor">{valor == null ? <span className="c-kpi__nd">NO ENCONTRADO</span> : <Count value={v} format={formato} duration={900} stagger={55} />}</div>
      <div className="c-kpi__etq">{etiqueta}</div>
      {fuente && <Fuente>{fuente}</Fuente>}
    </div>
  )
}
