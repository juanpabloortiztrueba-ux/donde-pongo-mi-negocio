import { Cifra, num } from './Cifra'

/** Cifra con su etiqueta y su fuente en una sola unidad: el valor rueda; si falta, dice «NO ENCONTRADO». */
export function Dato({ valor, formato, etiqueta, fuente, titulo, retraso = 0, grande = false, acento = false }: {
  valor: number | string | null | undefined; formato: (n: number) => string; etiqueta: string; fuente: string; titulo?: string; retraso?: number; grande?: boolean; acento?: boolean
}) {
  return (
    <div className="pre-est" title={titulo} data-grande={grande || undefined} data-acento={acento || undefined}>
      <b><Cifra valor={num(valor)} formato={formato} retraso={retraso} /></b>
      <span>{etiqueta}</span>
      <small>{fuente}</small>
    </div>
  )
}
