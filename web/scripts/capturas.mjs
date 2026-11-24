// Capturas del tablero con playwright-core y el Chrome del sistema (headless).
//   node scripts/capturas.mjs --url http://127.0.0.1:5300 --ruta '#/inicio' --out $TMPDIR/mi-etapa [--anchos 1440,390] [--temas light,dark] [--espera 1500] [--movimiento] [--completa] [--nombre inicio]
// Por defecto usa «movimiento reducido» (las escenas Stage muestran su poster = estado final). Con --movimiento deja correr la animación.
import { chromium } from 'playwright-core'
import fs from 'node:fs'
const a = process.argv.slice(2)
const f = (k, d) => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : d }
const url = f('--url', 'http://127.0.0.1:5300'), ruta = f('--ruta', '#/inicio'), out = f('--out', 'capturas')
const anchos = f('--anchos', '1440,390').split(',').map(Number), temas = f('--temas', 'light,dark').split(',')
const espera = Number(f('--espera', 1500)), movimiento = a.includes('--movimiento'), completa = a.includes('--completa')
const nombre = f('--nombre', ruta.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'inicio')
fs.mkdirSync(out, { recursive: true })
const navegador = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
const errores = []
for (const w of anchos) for (const tema of temas) {
  const h = w >= 900 ? 900 : 844
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: w < 900 ? 2 : 1, colorScheme: tema, reducedMotion: movimiento ? 'no-preference' : 'reduce' })
  const p = await ctx.newPage()
  p.on('pageerror', (e) => errores.push(`[${w}/${tema}] ${e}`)); p.on('console', (m) => { if (m.type() === 'error') errores.push(`[${w}/${tema}] ${m.text()}`) })
  await p.goto(`${url}/${ruta}`, { waitUntil: 'networkidle' })
  await p.waitForTimeout(espera)
  const desborde = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
  const archivo = `${out}/${nombre}_${w}_${tema}.png`
  await p.screenshot({ path: archivo, fullPage: completa })
  console.log(archivo, desborde > 1 ? `DESBORDE HORIZONTAL ${desborde}px` : 'ok')
  await ctx.close()
}
if (errores.length) console.log('ERRORES DE LA PÁGINA:\n' + [...new Set(errores)].join('\n'))
await navegador.close()
