# Cambios recientes

## 2026-10-07 — Cierre de Fase 7

### Implementado

- `GET /reports/sales-summary` calcula ventas netas por fecha comercial y
  sucursales autorizadas, excluyendo ventas canceladas.
- La pantalla de reportes consume el resumen de ventas desde la API.
- La configuración de empresa persiste en backend con validaciones de RFC,
  correo y teléfono; no depende de `localStorage`.
- El motor de promociones agrega promociones globales de porcentaje para
  ventas de menudeo, seleccionadas explícitamente en POS, no apilables con
  descuento manual y revalidadas en checkout.
- Las ventas guardan atribución y snapshot de promoción aplicada.
- La administración de usuarios lista y edita perfiles existentes por API:
  nombre, rol, estado activo y asignaciones de sucursal.
- La administración de usuarios bloquea autoedición, conserva al menos un admin
  activo y mantiene creación/invitación para la fase de Supabase Auth Admin.

### Verificación

- Backend: `184 passed` con `cd backend && .venv/bin/pytest -q`.
- Backend: `cd backend && .venv/bin/ruff check --no-cache app tests alembic`
  sin errores.
- Frontend: `cd frontend && npm run build` correcto.
- El build mantiene una advertencia no fatal preexistente sobre la anotación
  `@__PURE__` en `src/screens/index.jsx:4522`.
- Revisión nativa F7-05 aprobada y reconocida en lineage
  `review-1b99f5fd54be9089`; F7-04 tuvo revisión nativa declinada para ese
  candidato y fue cubierto por verificación independiente.

### Pendiente

- Promociones por línea/categoría/material/producto, 2x1/3x2 y regalos.
- Creación/invitación de usuarios e integración Supabase Auth Admin en Fase 9.
- Pruebas de concurrencia sobre PostgreSQL real para garantías de último admin
  activo.

## 2026-10-06 — Cierre de Fase 6

### Implementado

- Reparaciones usa estados canónicos backend/frontend: `received`, `in_workshop`
  y `ready`.
- Alta, edición de datos de recepción, transiciones de estado y cobro de
  reparaciones operan mediante API.
- Cada transición agrega historial inmutable con estado anterior, estado nuevo,
  actor, timestamp y nota/razón cuando aplica.
- El cobro de reparaciones crea una venta real con línea de servicio ligada a la
  reparación, sin movimiento de inventario.
- El cobro es idempotente y evita doble cobro mediante vínculo único entre
  reparación, venta y línea de venta.
- La pantalla de reparaciones consume la API para registrar, editar, cambiar
  estado y cobrar; la entrega queda deshabilitada hasta que exista endpoint
  backend.

### Verificación

- Backend: `152 passed` con `cd backend && .venv/bin/pytest -q`.
- Backend: `cd backend && .venv/bin/ruff check --no-cache app tests alembic`
  sin errores.
- Frontend: `cd frontend && npm run build` correcto.
- El build mantiene una advertencia no fatal preexistente sobre la anotación
  `@__PURE__` en `src/screens/index.jsx:4478`.

### Pendiente

- Endpoint backend de entrega de reparación y confirmación operacional de entrega
  con saldo pendiente.
- Pruebas de migración y concurrencia sobre PostgreSQL real.

## 2026-09-28 — Cierre de Fase 5

### Implementado

- Traspasos persistidos con envío atómico, recepción de cantidades reales,
  diferencias por faltantes y movimientos auditados de origen y destino.
- Reintentos de envío y recepción conservan el resultado sin duplicar
  movimientos de inventario.
- Conteos físicos persistidos con fotografía inicial del inventario,
  observaciones editables y finalización mediante movimientos `conteo`.
- El inicio de conteo es idempotente: un reintento no crea documentos, líneas
  de fotografía ni folios adicionales.
- La finalización concilia contra el saldo vigente y sus reintentos no duplican
  movimientos.
- Las pantallas de traspasos y conteos físicos usan documentos obtenidos de la
  API como fuente operativa.

### Verificación

- Backend: `136 passed` con `cd backend && .venv/bin/pytest -q`.
- Backend: `cd backend && .venv/bin/ruff check --no-cache app tests alembic`
  sin errores.
- Frontend: `cd frontend && npm run build` correcto.
- El build mantiene una advertencia no fatal sobre la anotación `@__PURE__` en
  `src/screens/index.jsx:4478`.

## 2026-09-22 — Cierre operativo del siguiente bloque de Fase 4

### Implementado

- Las ventas tienen estado persistido y cancelación idempotente con reversos
  auditables de stock, pagos, caja y crédito.
- El POS genera autorizaciones de descuento para otro usuario y consume el
  identificador durante el checkout.
- Crédito expone historial paginado con referencia, sucursal y movimiento.
- Crédito expone reporte de recuperación con filtros de sucursal y periodo,
  saldos pendientes, cargos, recuperaciones y último abono.
- Ventas y créditos incluyen las acciones nuevas en React con permisos de rol.
- Se agregó la migración `0006_sale_lifecycle_credit_ledger`.

### Verificación

- Backend: `91 passed` con `backend/.venv/bin/pytest -q`.
- Backend: `backend/.venv/bin/ruff check --no-cache app tests alembic` sin errores.
- Frontend: `npm run build` correcto.
- El build mantiene una advertencia no fatal preexistente sobre una anotación
  `@__PURE__` en `src/screens/index.jsx:4477`.

### Pendiente

- Pruebas de migración y concurrencia sobre PostgreSQL real; Docker Desktop no
  tenía el daemon disponible durante esta verificación.
- Fases posteriores y pruebas de concurrencia sobre PostgreSQL real.

## 2026-09-22 — Integración prioritaria de Fase 4

### Implementado

- El POS usa productos y variantes reales del API, cotización server-side y
  checkout transaccional.
- El POS exige una sesión de caja abierta, permite apertura y cierre según rol y
  conserva el carrito si el checkout falla.
- El alta de cliente desde POS espera la respuesta del API y selecciona el
  cliente creado solo después de completar la operación.
- Ventas ahora muestran detalle real con partidas, pagos y vendedor.
- Créditos dejó de usar la tabla demo y muestra saldos derivados de clientes y
  del ledger; registra abonos con método y sesión de caja cuando corresponde.
- Se agregó `Idempotency-Key` obligatorio para abonos y se conserva el mismo
  resultado ante reintentos idénticos.
- El checkout rechaza deuda nueva para clientes menudeo.
- Se eliminaron las implementaciones demo antiguas del POS y de créditos.

### Verificación

- Backend: `88 passed` con `pytest -q`.
- Backend: `ruff check --no-cache app tests alembic` sin errores.
- Frontend: `npm run build` correcto.
- El build mantiene una advertencia no fatal preexistente sobre una anotación
  `@__PURE__` en `src/screens/index.jsx:4477`.

### Fuera de esta entrega

- Estados de venta, cancelaciones y devoluciones.
- Historial paginado de movimientos de crédito y reportes de cobranza.
- Flujo de aprobación iniciado desde el POS para coordinar dos usuarios.
- Pruebas de concurrencia ejecutadas contra PostgreSQL real; Docker no estaba
  disponible durante la verificación.
- Traspasos, conteos, reparaciones operativas, promociones, reportes y
  configuración persistente.

## 2026-09-22 — Confiabilidad de POS y listados

### Implementado

- Checkout y abonos conservan la misma clave de idempotencia cuando un fallo de
  red deja incierto el resultado; los errores de validación permiten iniciar una
  nueva operación.
- POS y créditos permiten elegir la sucursal de operación y consultan terminal,
  caja y existencias dentro de ese alcance.
- `getReadModel` dejó de truncar todos los listados en 500 filas y ahora solicita
  páginas sucesivas hasta completar cada colección.

### Verificación

- Backend: `88 passed` con `pytest -q`.
- Backend: `ruff check --no-cache app tests alembic` sin errores.
- Frontend: `npm run build` correcto.
