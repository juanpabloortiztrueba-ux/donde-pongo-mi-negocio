import { createRoot } from 'react-dom/client'
import './fuentes.css'
import { Marco } from './comun/Marco'

// Esperar las fuentes (máx. 2.5 s) para que Roll/Count midan el texto con la letra real.
Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 2500))]).then(() => createRoot(document.getElementById('root')!).render(<Marco />))
