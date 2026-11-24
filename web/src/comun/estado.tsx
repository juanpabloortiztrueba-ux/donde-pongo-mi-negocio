import { createContext, useContext, type ReactNode } from 'react'
import { useEstadoApi, type Estado, type ErrorApi } from './api'

interface Ctx { estado: Estado | null; error: ErrorApi | null; cargando: boolean }
const EstadoCtx = createContext<Ctx>({ estado: null, error: null, cargando: true })

/** Lo pone el Marco: consulta /api/estado al abrir y la renueva cada 20 s (Ollama puede prenderse o apagarse con el tablero abierto). */
export function EstadoProvider({ children }: { children: ReactNode }) {
  const { datos, error, cargando, recargar } = useEstadoApi()
  // renovación periódica
  useRenovar(recargar)
  return <EstadoCtx.Provider value={{ estado: datos, error, cargando }}>{children}</EstadoCtx.Provider>
}
import { useEffect } from 'react'
function useRenovar(f: () => void) {
  useEffect(() => { const id = setInterval(f, 20000); return () => clearInterval(id) }, [f])
}

/** {estado, error, cargando}: Ollama (prendido, modelos), internet, fechas de corte y KPIs. estado=null mientras carga. */
export const useEstado = () => useContext(EstadoCtx)
