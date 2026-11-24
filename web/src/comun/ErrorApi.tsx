import { ErrorApi as ErrorTipo } from './api'

/** Error de la API con botón para reintentar. Si el servidor está apagado lo dice claro. */
export function ErrorApi({ error, reintentar, titulo = 'No pude cargar esto' }: { error: Error | ErrorTipo | null | undefined; reintentar?: () => void; titulo?: string }) {
  if (!error) return null
  const sinServidor = error instanceof ErrorTipo && error.estado === 0
  return (
    <div className="c-error" role="alert">
      <b>{sinServidor ? 'El tablero perdió la conexión con el servidor' : titulo}</b>
      <p>{error.message}</p>
      {reintentar && <button className="c-boton" onClick={reintentar}>Reintentar</button>}
    </div>
  )
}
