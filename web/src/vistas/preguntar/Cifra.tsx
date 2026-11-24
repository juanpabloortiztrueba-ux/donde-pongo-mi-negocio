import { useEffect, useState } from 'react'
import { Count } from '../../kit'
import { fmtNum } from '../../comun'

/** Cifra que rueda desde 0 al montarse (Count de stageshow) y otra vez cuando cambia. null o texto → «NO ENCONTRADO». */
export function Cifra({ valor, formato = (n) => fmtNum(n), retraso = 0, duracion = 900 }: {
  valor: number | string | null | undefined; formato?: (n: number) => string; retraso?: number; duracion?: number
}) {
  const n = typeof valor === 'number' && Number.isFinite(valor) ? valor : null
  const [v, setV] = useState(0)
  useEffect(() => {
    if (n == null) return
    const t = setTimeout(() => setV(n), 90 + retraso)
    return () => clearTimeout(t)
  }, [n, retraso])
  if (n == null) return <span className="pre-nd">NO ENCONTRADO</span>
  return <Count value={v} format={formato} duration={duracion} stagger={50} />
}

/** Número o null: el modelo manda «NO ENCONTRADO» como texto cuando falta el dato. */
export const num = (v: unknown): number | null => (typeof v === 'number' && Number.isFinite(v) ? v : null)
