# Joyería SaaS — Prototipo (React + Vite)

Herramienta operativa multi-sucursal para joyería: POS, inventario, clientes, crédito, reparaciones, transferencias, promociones, reportes y configuración.

Convertido desde el prototipo HTML autónomo (`joyeria-saas-prototipo.html`, conservado como referencia heredada). La fuente de verdad del código es `src/`.

## Versiones

- Node ^20.19.0 o >=22.12.0
- Vite 8.3.x
- React / ReactDOM 18.3.1
- @vitejs/plugin-react 6.1.x

## Comandos

```bash
cp .env.example .env
npm install
npm run dev       # desarrollo con recarga en caliente
npm run build     # producción en dist/ (base relativa "./")
npm run preview   # sirve dist/ localmente
```

The frontend uses FastAPI for local authentication, catalog, inventory, clients,
sales, cash management, POS, credits, repairs, transfers, and physical counts.
Repairs support persisted intake, intake-field updates, validated service-state
transitions, and charging through a real sale; intake and charge retries preserve
their idempotency key after uncertain network failures. Delivery remains read-only
until the backend exposes a delivery endpoint. Transfer and physical-count screens
also provide persisted API-backed operational workflows. Promotions, reports, and
configuration retain isolated demo data until their corresponding slices. Supabase
will be introduced in Phase 9 and used only for authentication.

Si npm falla con `EACCES` en la caché global, usa una caché temporal:

```bash
npm install --cache "$TMPDIR/npm-cache"
```

## Estructura

```
index.html          # entrada Vite, div#root
src/main.jsx        # montaje de React
src/App.jsx         # shell: sesión, carga del modelo y selección de pantalla
src/screens/        # vistas y modales del producto
src/components/     # estados de aplicación y límites compartidos
src/domain/         # reglas de navegación y composición del modelo visual
src/lib/api.js      # cliente HTTP y adaptación única del contrato
src/context/        # sesión, restauración y logout
src/pages/Login.jsx # acceso local
src/styles.css      # tokens y estilos (fuente de verdad visual)
src/assets/         # fuentes locales (.woff2)
dist/               # salida de build (no editar)
```

## Reglas del proyecto

- Especificación de diseño y reglas de negocio: `.interface-design/system.md`.
- Los tokens visuales del CSS son la única fuente de color; no introducir colores crudos.
- No usar `return` seguido de salto de línea antes de `React.createElement` (ASI rompe la vista).
