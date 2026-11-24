import { useEffect, useState } from 'react'
import { Count } from '../../kit'

/** Cifra que rueda: arranca en 0 al montarse y rueda cada vez que cambia el valor (Count de stageshow). null → «NO ENCONTRADO». */
export function Cifra({ valor, formato, retraso = 0, plano = false }: { valor: number | null | undefined; formato: (n: number) => string; retraso?: number; plano?: boolean }) {
  const [v, setV] = useState(0)
  useEffect(() => {
    if (valor == null || !Number.isFinite(valor)) return
    const t = setTimeout(() => setV(valor), 100 + retraso)
    return () => clearTimeout(t)
  }, [valor, retraso])
  if (valor == null || !Number.isFinite(valor)) return <span className="exp-nd">NO ENCONTRADO</span>
  if (plano) return <>{formato(valor)}</>  // texto con letras (p. ej. «Muy bajo (1)»): Count no lo escribe bien
  return <Count value={v} format={formato} duration={800} stagger={40} />
}
