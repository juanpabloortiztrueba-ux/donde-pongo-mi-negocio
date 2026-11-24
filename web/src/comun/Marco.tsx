import { lazy, Suspense, useEffect, useState, type ComponentType } from 'react'
import { BarChart3, Cpu, Database, GitCompare, Home, Map as MapIcon, MapPin, MessageCircle, Menu, Moon, Sun, TrendingUp, X } from 'lucide-react'
import { EstadoProvider, useEstado } from './estado'
import { SECCIONES, TITULOS, href, useRuta, type VistaId, type VistaProps } from './ruta'
import { useTema } from './tema'
import { Cargando } from './Cargando'
import { DesgloseProvider } from './Desglose'
import './escopo.css'
import './theme.css'
import './comun.css'

// Cada vista es un módulo aparte (default export, props VistaProps) que su dueño edita sin tocar este archivo.
const VISTAS: Record<VistaId, ComponentType<VistaProps>> = {
  inicio: lazy(() => import('../vistas/inicio/Inicio')),
  preguntar: lazy(() => import('../vistas/preguntar/Preguntar')),
  explorar: lazy(() => import('../vistas/explorar/Explorar')),
  zona: lazy(() => import('../vistas/preguntar/Ficha')),
  comparar: lazy(() => import('../vistas/explorar/Comparar')),
  macro: lazy(() => import('../vistas/contexto/Macro')),
  modelo: lazy(() => import('../vistas/contexto/Modelo')),
  datos: lazy(() => import('../vistas/contexto/Datos')),
  'ejemplo-mapa': lazy(() => import('./EjemploMapa')),
}
const ICONOS: Record<string, typeof Home> = { inicio: Home, preguntar: MessageCircle, explorar: MapIcon, zona: MapPin, comparar: GitCompare, macro: TrendingUp, modelo: Cpu, datos: Database }

function Marca() {
  return (
    <a className="mc-marca" href={href('inicio')} aria-label="Dónde pongo mi negocio, inicio">
      <svg width="30" height="30" viewBox="0 0 30 30" aria-hidden>
        <circle cx="15" cy="15" r="14" fill="none" stroke="var(--rule-2)" />
        <path d="M15 6.5a6 6 0 0 0-6 6c0 4.4 6 11 6 11s6-6.6 6-11a6 6 0 0 0-6-6Z" fill="var(--accent)" />
        <circle cx="15" cy="12.5" r="2.2" fill="var(--bg)" />
      </svg>
      <span><b>Dónde pongo{' '}<br />mi negocio</b><small>Zona Metropolitana del Valle de México</small></span>
    </a>
  )
}

function Estados() {
  const { estado, error } = useEstado()
  const { tema, alternar } = useTema()
  let ollama: { ok: 'true' | 'false' | 'aviso'; t: string; s: string }
  if (!estado) ollama = { ok: 'aviso', t: error ? 'Sin conexión al servidor' : 'Revisando Ollama…', s: error ? 'Revisa que el tablero siga abierto' : '' }
  else if (!estado.ollama.prendido) ollama = { ok: 'false', t: 'Ollama apagado', s: 'El tablero funciona en modo sin LLM' }
  else if (estado.ollama.faltan.length) ollama = { ok: 'aviso', t: 'Ollama prendido', s: `Faltan modelos: ${estado.ollama.faltan.join(', ')}` }
  else ollama = { ok: 'true', t: 'Ollama prendido', s: estado.ollama.cargados.length ? `Modelo en memoria: ${estado.ollama.cargados[0]}` : 'qwen3:8b y nomic-embed-text listos' }
  return (
    <div className="mc-pie">
      <div className="mc-est"><span className="mc-pto" data-ok={ollama.ok} /><span>{ollama.t}{ollama.s && <small>{ollama.s}</small>}</span></div>
      <div className="mc-est">
        <span className="mc-pto" data-ok={estado ? (estado.internet ? 'true' : 'aviso') : 'aviso'} />
        <span>{estado ? (estado.internet ? 'Internet disponible' : 'Sin internet') : 'Revisando internet…'}<small>{estado && !estado.internet ? 'Todo funciona con datos locales' : 'Solo se usa para el mapa base opcional'}</small></span>
      </div>
      <button className="mc-tema" onClick={alternar} aria-label={tema === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}>
        {tema === 'dark' ? <Sun size={15} /> : <Moon size={15} />}{tema === 'dark' ? 'Tema claro' : 'Tema oscuro'}
      </button>
    </div>
  )
}

function Contenido() {
  const ruta = useRuta()
  const [menu, setMenu] = useState(false)
  useEffect(() => { setMenu(false); window.scrollTo(0, 0); document.title = `${TITULOS[ruta.vista] ?? 'Mapa de prueba'} · Dónde pongo mi negocio` }, [ruta.vista, ruta.param])
  const Vista = VISTAS[ruta.vista]
  return (
    <div className="mc ss-scope">
      <div className="mc-tope">
        <Marca />
        <button className="mc-menu-btn" onClick={() => setMenu((m) => !m)} aria-expanded={menu} aria-controls="mc-nav">{menu ? <X size={16} /> : <Menu size={16} />}{menu ? 'Cerrar' : 'Menú'}</button>
      </div>
      <nav id="mc-nav" className="mc-nav" data-abierto={menu} aria-label="Vistas del tablero">
        <Marca />
        {SECCIONES.map((s, i) => (
          <div className="mc-sec" key={i}>
            {s.titulo && <h2>{s.titulo}</h2>}
            {s.vistas.map((v) => {
              const I = ICONOS[v.id] ?? BarChart3
              return <a key={v.id} className="mc-link" href={href(v.id)} aria-current={ruta.vista === v.id ? 'page' : undefined}><I size={17} />{v.titulo}</a>
            })}
          </div>
        ))}
        <Estados />
      </nav>
      <main className="mc-main">
        <Suspense fallback={<div className="mc-cuerpo"><Cargando forma="texto" filas={4} /></div>}>
          <Vista key={ruta.vista} ruta={ruta} />
        </Suspense>
      </main>
    </div>
  )
}

/** Marco de la app: barra lateral (o menú en el celular), estado de Ollama e internet, tema claro/oscuro y la vista de la ruta. */
export function Marco() {
  return <EstadoProvider><DesgloseProvider><Contenido /></DesgloseProvider></EstadoProvider>
}
