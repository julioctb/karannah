# Estado de implementación

## Estado verificado

- Backend de lectura implementado con FastAPI, SQLAlchemy async y Alembic.
- Seed con FK activas, sin usuarios ficticios ni IDs enteros impuestos.
- JWT vía JWKS admite RS256 y ES256.
- Usuarios reales por invitación administrativa con `app.provision_user`.
- Contrato API en `docs/API_CONTRACT.md`.
- Adapter de auth local (`AUTH_PROVIDER=local`): JWT HS256 + login `/api/v1/auth/local/login` + usuarios dev con contraseñas plaintext solo para desarrollo. Supabase queda para Fase 9.
- Suite local: 91 pruebas aprobadas. `ruff check` limpio.
- Frontend con cliente API centralizado, sesión persistente, login local y cierre de sesión.
- Catálogo, productos con variantes, clientes y ajustes de inventario tienen API persistente y permisos por rol.
- React ejecuta CRUD administrativo de categorías, materiales, subcategorías,
  colecciones, productos y variantes; todos los roles pueden editar datos básicos
  de clientes y solo administración cambia su perfil comercial.
- Imágenes JPEG, PNG y WebP persistidas localmente mediante un adaptador neutral;
  subida, lectura pública, reemplazo y eliminación validados en PostgreSQL local.
- PostgreSQL 16 reproducible con `compose.yml`; migración
  `0004_product_images`, seed idempotente, login, CRUD e inventario validados.
- Fase 2 cerrada: shell, pantallas, API, autenticación, estados y dominio separados.

## Fase 4 implementada hasta el punto actual

- [x] `GET /sales/{id}` devuelve partidas, pagos y vendedor.
- [x] Cotización y checkout transaccional con bloqueo de inventario.
- [x] Pagos separados, crédito, abonos, límites de descuento y aprobaciones.
- [x] Idempotencia para checkout y abonos.
- [x] Apertura y cierre obligatorio de caja integrado al POS.
- [x] POS conectado al catálogo real, cliente real y medios de pago reales.
- [x] Reintentos del POS y abonos conservan la misma `Idempotency-Key` cuando
  el resultado de la primera solicitud es desconocido.
- [x] POS y abonos permiten seleccionar explícitamente la sucursal y consultan
  la terminal y el stock de esa sucursal.
- [x] La carga inicial del frontend pagina todos los listados en lugar de
  truncarlos silenciosamente en 500 filas.
- [x] Pantalla de créditos conectada a saldos derivados del ledger.
- [x] Historial paginado de crédito con sucursal, referencia y movimientos compensatorios.
- [x] Crédito nuevo limitado a clientes mayoreo con límite disponible.
- [x] Estados `confirmada`/`cancelada` y cancelación con reversos de stock, pagos,
  caja y crédito.
- [x] POS permite generar una aprobación para otro usuario y consumir su
  identificador durante el checkout.
- [x] Reporte de recuperación de crédito server-side con filtros de sucursal y
  periodo, saldos, cargos, recuperaciones y último abono.

## Pendientes posteriores a la Fase 4

1. Ejecutar pruebas de concurrencia sobre PostgreSQL real: sobreventa, folios,
   idempotencia de checkout y abonos concurrentes.
2. Retirar los datasets demo restantes de reportes y pantallas aún no migradas,
   cuando lleguen sus fases correspondientes.
3. Mantener en demostración traspasos, conteos, promociones, reportes y
   configuración hasta sus fases correspondientes.

## Validación con Supabase pendiente (Fase 9)

Requiere credenciales de un proyecto Supabase y no bloquea el desarrollo local:

1. Ejecutar `alembic upgrade head` contra Postgres real.
2. Ejecutar `python -m app.seed` y verificar una segunda ejecución y `--force`.
3. Invitar un administrador con `python -m app.provision_user`.
4. Confirmar login, JWKS, `/api/v1/me` y alcance por sucursal.
5. Confirmar que `anon` y `authenticated` no acceden directamente a tablas.
