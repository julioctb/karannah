# Plan de implementación por fases

Plataforma real de joyería: **React + FastAPI + PostgreSQL local**, con
integración **Supabase** reservada para la **Fase 9** (última). El desarrollo y
la validación funcionales ocurren **100% en local**, sin credenciales ni tráfico
hacia Supabase.

## Decisiones de arquitectura base

- **Una sola empresa**, con múltiples sucursales. Sin tenant/empresa múltiple.
- **Producto con variantes**: `products` agrupa; cada `product_variants` es la
  unidad vendible con su propio SKU, precio y stock.
- **PostgreSQL local** como entorno principal: permite validar migraciones,
  locks, concurrencia, RLS y transacciones reales.
- **FastAPI es la única vía** de acceso a datos operativos. El frontend **no**
  accede a la base de datos ni usa datos hardcodeados como fuente de verdad.
- **Auth con adaptadores intercambiables**: `local` (JWT firmado con HMAC, uso de
  desarrollo) y `supabase` (validación JWKS RS256/ES256). Misma interfaz de
  `TokenClaims`; cambiar de proveedor en Fase 9 no toca la lógica de dominio.
- Inventario y crédito usan **movimientos inmutables**; los saldos se derivan
  del ledger, nunca se editan directamente.

## Política de esquema y migraciones durante el desarrollo

- Mientras el producto esté en desarrollo y no existan datos reales que
  preservar, los cambios de estructura se corrigen directamente en los modelos
  y en la definición del esquema; no se crearán migraciones incrementales para
  reparar errores de desarrollo.
- Las migraciones actuales se consideran borradores de referencia y no se
  ejecutarán contra una base de datos definitiva durante esta etapa.
- Antes de la primera instalación real se consolidará el esquema completo en
  una única migración inicial, revisada de extremo a extremo, que incluya
  tablas, enums, relaciones, índices, restricciones y reglas necesarias.
- La migración inicial se ejecutará una sola vez para crear la base de datos
  definitiva del entorno operativo.
- Después de esa instalación, cuando ya existan datos que conservar, cualquier
  cambio estructural deberá realizarse mediante migraciones incrementales,
  reversibles cuando sea posible y sin corregir silenciosamente datos pasados.
- Durante esta etapa se mantienen las pruebas automatizadas y las validaciones
  de modelos y servicios con bases aisladas; la ejecución final de Alembic y la
  validación de concurrencia en PostgreSQL quedan para el cierre del desarrollo.

## Modelo de datos previsto (referencia)

- Identidad: `user_profiles`, `user_branch_assignments`, `branches`
- Configuración: `company_settings`, `branch_settings`, `pos_terminals`
- Catálogo: `categories`, `materials`, `subcategories`, `collections`
- Productos: `products`, `product_variants`, `sku_counters`
- Inventario: `inventory_balances`, `inventory_movements`, `inventory_adjustments`
- Clientes: `customers`, `credit_accounts`, `credit_ledger_entries`
- Ventas: `sales`, `sale_items`, `sale_payments`, `discount_approvals`
- Reparaciones: `repair_orders`, `repair_status_history`
- Traspasos: `transfers`, `transfer_lines`
- Conteos: `physical_counts`, `physical_count_lines`
- Promociones: `promotions` y reglas/alcances
- Control: `document_counters`, `idempotency_keys`, `audit_events`

## Fases

### Fase 1 — Traslado y línea base ✅
- [x] Mover la app a `frontend/`.
- [x] Conservar el prototipo HTML en `docs/prototype/`.
- [x] Excluir `node_modules` y `dist` del control de versiones.
- [x] Crear estructura FastAPI, `.env.example`, README y `.gitignore`.
- [x] Confirmar que el frontend mantiene el mismo build.

### Fase 2 — Plataforma local e integración de lecturas ✅
Objetivo: frontend y backend operan juntos **en local**, sin Supabase.

- [x] Conexión asíncrona de FastAPI a Postgres + Alembic.
- [x] Validación de JWT RS256/ES256 vía JWKS (proveedor `supabase`).
- [x] `/api/v1/me`, `/api/v1/me/branches`.
- [x] Perfiles, roles, invitación administrativa y asignaciones de sucursal.
- [x] Inventario, clientes, ventas y reparaciones en modo lectura.
- [x] PostgreSQL local reproducible (config/documentada, `docker` o servicio).
- [x] **Adaptador de auth** con interfaz común y dos implementaciones
      (`local` HMAC / `supabase` JWKS) seleccionadas por `AUTH_PROVIDER`.
- [x] **Login local** (`/auth/local/login`) que emite JWT HMAC para usuarios
      semilla; solo activo cuando `AUTH_PROVIDER=local`.
- [x] Seed de al menos un administrador y un vendedor locales, con sucursales.
- [x] Cliente HTTP centralizado en React (`lib/api.js`): inyecta Bearer, maneja
      `401` con logout y permite reintentar errores de carga; adapta `403`,
      `409` y `422`.
- [x] Contexto de sesión en React + pantalla de login + rutas protegidas.
- [x] Reemplazar el admin hardcodeado (`currentUser`, `frontend/src/App.jsx`)
      por datos reales de `/me` y `/me/branches`.
- [x] Separar `App.jsx` en shell, pantallas, cliente API, auth y dominio.
- [x] Conectar catálogo, stock, clientes, ventas y reparaciones a la API,
      **eliminando** cada dataset hardcodeado al migrarlo (sin doble fuente).
- [x] Estados de carga, vacío, error y reintento para las lecturas integradas.

**Criterio de salida:** la app funciona end-to-end en local (login → datos reales
de la API) sin credenciales ni acceso a Supabase.

**Fase completada:** migraciones, seed idempotente, login local y lecturas
validados contra PostgreSQL 16 en Docker. El frontend quedó separado en shell,
pantallas, cliente API, autenticación, componentes de estado y dominio. Las
escrituras pertenecen a las fases siguientes.

### Puerta de decisiones (antes de fases operativas)
1. [x] Stock actual: es ficticio y se eliminará antes de cargar existencias
   reales por sucursal; no se considera inventario de apertura.
2. [x] Costos visibles solo para administradores.
3. [x] Descuentos: vendedor 0%, encargado hasta 10%, administrador sin límite;
   los excesos requieren aprobación de un rol autorizado.
4. [x] Crédito sin vencimiento inicial; se controla por límite y saldo.
5. [x] Apertura y cierre de caja obligatorios para operar el POS.
6. [x] Folios `TIPO-SUC-AÑO-NÚMERO`, con contador independiente por tipo,
   sucursal y año.
7. [x] Todos los datos actuales son ficticios y descartables. El catálogo se
   conserva solo como dataset provisional de desarrollo; ventas, crédito,
   reparaciones y stock demo no se migrarán como datos reales.

### Fase 3 — Catálogo, clientes e inventario (CRUD) ✅
- [x] CRUD API de productos y **variantes** (variante = SKU vendible con precio/stock).
- [x] Generación transaccional de SKU con contador bloqueado, validada con dos
      sesiones paralelas sobre PostgreSQL (50 reservas únicas y secuenciales).
- [x] CRUD API de categorías, materiales, subcategorías y colecciones.
- [x] Desactivación en lugar de borrado cuando existan referencias.
- [x] Clientes siempre como menudeo, sin crédito y saldo cero en el alta.
- [x] Inventario separado por sucursal; ajustes solo vía movimientos auditados.
- [x] Abstracción de almacenamiento de imágenes (backend guarda archivo local;
      el adaptador Supabase Storage queda reservado para Fase 9).

**Criterio de salida:** CRUD persistente; SKU único bajo concurrencia; inventario
modificable únicamente por movimientos auditados.

**Fase completada:** API y formularios React de categorías, materiales,
subcategorías, colecciones, productos, variantes y clientes conectados a
PostgreSQL. Las existencias iniciales exigen una sucursal explícita y todo cambio
de stock crea un movimiento auditado. Las imágenes se validan y persisten en el
almacenamiento local mediante una abstracción reemplazable. La migración
`0004_product_images`, el seed y los flujos de imagen se validaron sobre
PostgreSQL 16 local; la suite contiene 91 pruebas aprobadas.

### Fase 4 — POS, ventas y crédito
- [x] Cotización recalculada íntegramente en el servidor (dinero con `Decimal`).
- [x] Pagos separados y partidas con snapshot.
- [x] Estados de venta persistidos y flujo de cancelación con movimientos compensatorios.
- [x] Checkout transaccional con bloqueo de inventario (sin sobreventa).
- [x] Venta + partidas + pagos + movimientos de stock + crédito en una transacción.
- [x] Claves de idempotencia para checkout y abonos.
- [x] El frontend conserva la clave durante reintentos de checkout y abonos; los
      errores de validación generan una nueva operación.
- [x] Crédito disponible, cargo y abonos con ledger; solo clientes mayoreo pueden
      generar nueva deuda.
- [x] Límites de descuento por rol y aprobación persistida en API.
- [x] Flujo de generación/consumo de aprobación conectado al POS para que un
      vendedor pueda completar un descuento autorizado por otro usuario.
- [x] El POS dejó de usar `VENTAS_DEMO` y sus cálculos monetarios locales; los
      reportes y pantallas demo restantes se mantienen aislados para fases futuras.
- [x] Apertura y cierre de caja integrados al POS, con efectivo esperado y
      diferencia de cierre.
- [x] `GET /sales/{id}` conectado a la vista de detalle con partidas, pagos y
      vendedor.
- [x] Pantalla de créditos conectada a clientes y saldos derivados del ledger.
- [x] POS y abonos operan sobre una sucursal seleccionada explícitamente y la
      carga inicial pagina los listados completos.
- [x] Historial paginado de movimientos de crédito con trazabilidad de sucursal.
- [x] Reporte server-side de recuperación de crédito con filtros de sucursal y
      periodo, saldos pendientes, cargos, recuperaciones y último abono.
**Fase 4 completada funcionalmente.** La consolidación y ejecución de la
migración inicial quedan reservadas para el cierre del desarrollo, según la
política de esquema definida al inicio de este plan.

### Fase 5 — Traspasos y conteos físicos ✅
- [x] Documentos y líneas de traspaso; transferencia atómica origen/destino.
- [x] Diferencias de recepción; sin duplicados por reintentos.
- [x] Fotografía del inventario al iniciar conteo; fin por ajustes auditados.

**Criterio de salida:** movimientos conciliables; ningún reintento duplica stock.

**Fase completada:** traspasos y conteos físicos operan mediante documentos
persistidos y movimientos auditados. Los envíos, recepciones, inicios de conteo
y finalizaciones son seguros ante reintentos; los conteos conservan una
fotografía inicial y concilian las existencias observadas contra el saldo
vigente mediante movimientos `conteo`. Las pantallas de traspasos y conteos
usan la API como única fuente operativa. La verificación integrada aprobó 136
pruebas de backend, Ruff y el build de producción del frontend.

### Fase 6 — Reparaciones ✅
- [x] Unificar estados frontend/backend; alta, precio y fechas.
- [x] Historial de estados inmutable; validación de transiciones.
- [x] Cobro mediante venta real; sin doble cobro; entrega pendiente de endpoint backend.
- [x] Separar reparación terminada / pagada / entregada.

**Fase completada:** reparaciones opera con estados canónicos `received`,
`in_workshop` y `ready`, historial inmutable, alta/edición desde API, cobro
mediante ventas reales y líneas de servicio sin movimiento de inventario. La
pantalla de reparaciones usa la API para alta, edición, transiciones y cobro; la
entrega queda visible como acción no disponible hasta implementar su endpoint
operativo. El backend validó 152 pruebas, Ruff y el build de frontend aprobó con
la advertencia no fatal preexistente sobre `@__PURE__`.

### Fase 7 — Promociones, reportes y administración
- [x] Motor de promociones integrado con cotización/checkout.
- [x] Reportes desde el servidor, por fecha comercial y sucursales autorizadas.
- [x] Configuración persistente (elimina `localStorage`): empresa, sucursales,
      precios, tickets y terminales.
- [x] Admin de perfiles/roles/asignaciones vía adaptador Auth (local ahora,
      Supabase Auth Admin en Fase 9).

**Fase completada:** el reporte de ventas sale de `GET /reports/sales-summary`,
la configuración de empresa persiste en backend, las promociones de porcentaje
se seleccionan explícitamente en POS y se revalidan en checkout, y la pantalla de
usuarios administra perfiles existentes por API sin creación/invitación. Quedan
diferidos alcances deliberados: promociones por línea/categoría/regalo, creación
de usuarios e integración Supabase Auth Admin, y más módulos de configuración
operativa.

**Criterio de salida:** ninguna configuración/reporte/promoción/usuario depende
de arrays locales del navegador para los slices seleccionados de Fase 7.

### Fase 8 — Endurecimiento y preproducción local
- [ ] Pruebas de concurrencia ejecutadas sobre PostgreSQL (sobreventa, SKU,
      folios, idempotencia de abonos).
- [ ] Matriz completa rol × acción × sucursal.
- [ ] Migraciones sobre datos existentes; separación roles migrador/runtime.
- [ ] Ledgers protegidos contra UPDATE/DELETE real.
- [ ] CORS estricto por entorno, logs estructurados, auditoría.
- [ ] Conciliación de inventario, ventas, pagos y cuentas por cobrar.
- [ ] Backup y restauración local comprobados; E2E sin conexiones externas.

**Criterio de salida:** suite completa aprobada en local y restauración
reproducible.

### Fase 9 — Supabase y salida a producción
- [ ] Crear/configurar proyecto Supabase y aplicar migraciones ya certificadas.
- [ ] `@supabase/supabase-js` en el frontend **solo para Auth**.
- [ ] Reemplazar proveedor `local` por `supabase`; validar JWT, JWKS, issuer,
      audience y alcance por sucursal reales.
- [ ] Invitaciones/desactivación vía Supabase Auth Admin.
- [ ] Activar Supabase Storage y mover el adaptador de imágenes.
- [ ] Confirmar que `anon` y `authenticated` no acceden directamente a tablas;
      RLS y permisos correctos.
- [ ] Seed aprobado (sin borrado destructivo); backup/restauración en Supabase.
- [ ] Secretos, logs, alertas y plan de rollback; smoke test completo.

**Criterio de salida:** Auth, API, Postgres y Storage corriendo en Supabase sin
modificar la lógica de dominio desarrollada localmente.
