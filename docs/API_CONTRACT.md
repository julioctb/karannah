# Contrato API

Este documento define el contrato entre React y FastAPI. FastAPI es la unica
API de datos. En desarrollo se usa el proveedor de autenticacion local; el
cliente de Supabase del frontend se incorporara en la Fase 9 solo para Auth.

## Convenciones

- Las rutas comienzan con `/api/v1`.
- Los campos del API usan ingles en `snake_case`.
- La interfaz traduce etiquetas al espanol y adapta datos en una sola capa API.
- Sucursales y usuarios usan UUID. Catalogos y documentos usan enteros.
- Los codigos como `T01` y los folios son identificadores visibles, no claves FK.
- Fechas y horas usan ISO 8601 con zona. Los dias comerciales usan
  `America/Mexico_City`.
- Importes monetarios se calculan con `Decimal` y se serializan como strings
  decimales, por ejemplo `"1240.00"`. El frontend no debe usar aritmetica de
  punto flotante para totales.
- Los listados actuales responden arreglos y aceptan `limit` y `offset`.
- Las operaciones que crean ventas o abonos aceptan `Idempotency-Key`; repetir la
  misma clave con el mismo cuerpo devuelve el mismo resultado y cambiar el cuerpo
  produce `409`.

## Autenticacion

Cada solicitud protegida envia:

```http
Authorization: Bearer <access-token>
```

FastAPI valida el token segun `AUTH_PROVIDER`: JWT HMAC emitido por
`POST /auth/local/login` cuando es `local`, o firma, issuer y audience de
Supabase cuando es `supabase`. El `sub` debe coincidir con `user_profiles.id`.
No existe registro publico.

### Login local

- `POST /auth/local/login` solo existe cuando `AUTH_PROVIDER=local`.
- Recibe `email` y `password` y devuelve `access_token`, `token_type`,
  `expires_in` y el perfil con sus sucursales.
- Los usuarios locales son exclusivamente de desarrollo y se sincronizan al
  ejecutar el seed o al iniciar sesion.
- En produccion `AUTH_PROVIDER=local` esta prohibido.

## Identidad y sucursales

- `GET /me` devuelve el perfil canonico y su rol.
- `GET /me/branches` devuelve las sucursales autorizadas.
- El frontend conserva `branch_id` como UUID y muestra `branch_code`.
- `admin` ve todas las sucursales activas; los demas roles solo sus asignaciones.

## Catalogo e inventario

- `GET /catalog/categories`, `/materials`, `/subcategories` y `/collections`
  devuelven los catalogos activos y aceptan `include_inactive=true` para
  administracion.
- `POST`, `PATCH` y `DELETE` sobre categorias, materiales, subcategorias y
  colecciones requieren `admin`. `DELETE` es una desactivacion logica.
- `GET /catalog/products` devuelve productos padre con `variants`; cada variante
  contiene su SKU y precios propios.
- `POST /catalog/products` crea al menos una variante y reserva sus SKU en la
  misma transaccion. `PATCH /catalog/products/{id}` modifica el producto padre.
- `POST /catalog/products/{id}/variants` agrega una unidad vendible y
  `PATCH /catalog/products/{id}/variants/{variant_id}` modifica sus datos. Estas
  escrituras requieren `admin`.
- `DELETE /catalog/products/{id}` desactiva el producto y sus variantes.
- Un producto reactivado restaura sus variantes. No se permite desactivar la
  ultima variante activa ni activar una variante de un producto inactivo.
- `PUT /catalog/products/{id}/image` recibe `multipart/form-data` con el campo
  `file`; valida y normaliza JPEG, PNG o WebP y reemplaza la imagen anterior.
- `DELETE /catalog/products/{id}/image` elimina la referencia y el archivo de
  forma idempotente. Ambas operaciones requieren `admin`.
- `ProductRead.image_url` es una ruta publica bajo `/media/products`. PostgreSQL
  conserva solamente una clave neutral del proveedor; en desarrollo los
  archivos viven en `PRODUCT_MEDIA_ROOT`.
- `GET /inventory/stock` devuelve existencias derivadas del ledger por variante
  y sucursal.
- `GET /inventory/movements` devuelve los movimientos visibles, ordenados de
  mas reciente a mas antiguo.
- `POST /inventory/adjustments` agrega un movimiento `ajuste`; requiere `admin`
  o `encargado` y una sucursal dentro de su alcance. La cantidad debe ser un
  entero distinto de cero y el saldo resultante no puede ser negativo.
- El stock no forma parte del producto y nunca se edita directamente.
- Estados de producto vigentes: `disponible`, `externo`.
- `cost_price` solo se entrega a administradores.
- Formato de SKU: prefijo de categoria, material cuando la categoria lo exige y
  secuencia de cuatro digitos, por ejemplo `AN-OR-0001`.
- Las existencias iniciales no forman parte de `POST /catalog/products`: React
  crea ajustes auditados por variante en la sucursal elegida explicitamente.

### Transferencias

- `POST /inventory/transfers` crea un borrador y responde `201`. Requiere
  `origin_branch_id`, `destination_branch_id` y `lines` unicas con
  `variant_id` y `shipped_quantity` positivo. Las sucursales deben ser
  distintas y las variantes deben existir y estar activas.
- `GET /inventory/transfers` lista solamente documentos cuyas sucursales de
  origen y destino son visibles. `GET /inventory/transfers/{transfer_id}`
  devuelve el detalle bajo la misma regla; un documento fuera del alcance
  responde `404`.
- `POST /inventory/transfers/{transfer_id}/send` recibe opcionalmente `note`,
  requiere `Idempotency-Key`, cambia `draft` a `sent`, debita el origen y crea
  movimientos inmutables `transferencia_salida` referenciados por el folio.
- `POST /inventory/transfers/{transfer_id}/receive` requiere
  `Idempotency-Key` y una linea por cada variante enviada, con `variant_id` y
  `received_quantity`. Cambia `sent` a `received`, acredita al destino solo la
  cantidad efectivamente recibida y crea movimientos `transferencia_entrada`
  solo cuando esa cantidad es positiva.
- Ambas mutaciones idempotentes devuelven la respuesta almacenada al repetir
  la misma clave y cuerpo, sin duplicar saldos ni ledger. Reutilizar la clave
  dentro del mismo endpoint con otro cuerpo responde `409`.
- Crear, listar, consultar, enviar y recibir requiere rol `admin` o `encargado`
  y visibilidad sobre ambas sucursales.
- Los folios usan `TR-SUC-YEAR-NUMBER`. Una transferencia recorre
  exclusivamente `draft`, `sent` y `received`. Cada linea conserva
  `shipped_quantity`; al recibir persiste `received_quantity` y la diferencia
  exacta en `shortage_quantity`.
- Omitir o agregar lineas, recibir por encima de lo enviado, mutar desde un
  estado incorrecto, enviar sin stock suficiente o provocar stock negativo
  responde `409`. Errores de validacion del cuerpo responden `422`.
- Los documentos no reemplazan a `StockEntry`; `StockBalance` sigue siendo solo
  la proyeccion bloqueable y ambos se actualizan en la misma transaccion.

### Conteos fisicos (vocabulario de Fase 5)

- Los folios de conteo fisico usan `CF-SUC-YEAR-NUMBER`; `CF` identifica el
  documento de conteo de inventario de una sucursal.
- Un conteo fisico recorre exclusivamente `open` y `finalized`.
- Cada linea conserva la captura inicial inmutable en `snapshot_quantity` y la
  cantidad relevada en `observed_quantity`, que permanece ausente hasta que la
  variante sea contada.

## Clientes y credito

- `GET /clients` devuelve `credit_balance` derivado de `credit_entries`.
- `POST /clients` y `PATCH /clients/{id}` estan disponibles para todos los roles
  autenticados. El alta siempre fuerza `type=menudeo`, sin limite de credito.
- `PATCH /clients/{id}/commercial-profile` requiere `admin`; es la unica ruta
  que cambia tipo de cliente y limite de credito.
- Los cargos son positivos y los abonos negativos.
- El saldo no se acepta como campo editable.
- `POST /clients/{id}/credit-payments` registra un abono dentro del ledger y
  requiere `branch_id`, método y `Idempotency-Key`. El efectivo requiere una
  sesión de caja abierta.
- `GET /clients/{id}/credit-ledger` devuelve movimientos paginados, incluyendo
  sucursal, referencia, venta, método y usuario de origen.
- Una nueva deuda mediante checkout solo es válida para clientes `mayoreo` con
  límite de crédito positivo; un cliente `menudeo` no puede generar deuda.

## Reportes

- `GET /reports/credit-recovery` requiere `admin` o `encargado` y devuelve el
  saldo actual de clientes con deuda, cargos y recuperaciones del periodo,
  último abono y totales agregados.
- Acepta `branch_id`, `date_from`, `date_to`, `limit` y `offset`. Las fechas son
  días comerciales en `BUSINESS_TIMEZONE`; los saldos se calculan desde el
  ledger y no desde valores enviados por el frontend.

## Caja

- `GET /cash/terminals` devuelve las terminales activas dentro del alcance del
  usuario.
- `GET /cash/sessions/current?terminal_id=...` devuelve la sesión abierta o
  `null`.
- `POST /cash/sessions/open` abre una sesión; solo puede existir una sesión
  abierta por terminal.
- `POST /cash/sessions/{id}/close` registra el efectivo contado, efectivo
  esperado y diferencia. Solo `encargado` y `admin` pueden cerrar caja.

## Ventas

- `GET /sales` es un listado resumido e incluye `seller_name` cuando el perfil
  del vendedor sigue activo, además de `status` y metadatos de cancelación.
- `GET /sales/{id}` devuelve partidas, pagos, vendedor y snapshots de la venta.
- `POST /sales/quote` recalcula precios, descuentos, impuestos, total y stock
  disponible en el servidor.
- `POST /sales/checkout` vuelve a cotizar bajo bloqueo de inventario y persiste
  venta, partidas, pagos, movimientos de stock y crédito en una transacción.
- El checkout requiere una sesión de caja abierta incluso cuando el pago no es
  efectivo, porque la apertura y el cierre son obligatorios para operar el POS.
- Una venta a credito requiere cliente mayoreo con limite disponible y al menos
  un pago `payment_method=credito`.
- `POST /sales/discount-approvals` genera una autorización ligada a sucursal,
  carrito, porcentaje y expiración; el checkout la consume una sola vez y el
  aprobador debe ser distinto al usuario que cobra.
- `POST /sales/{id}/cancel` requiere `admin` o `encargado`, `Idempotency-Key` y
  motivo. Solo permite cancelar con caja abierta cuando hubo efectivo y agrega
  movimientos compensatorios de inventario, pagos, caja y crédito.

## Errores

- `401`: token ausente, invalido o expirado.
- `403`: perfil inactivo, inexistente o accion no autorizada.
- `404`: recurso inexistente dentro del alcance autorizado.
- `409`: conflicto de negocio o idempotencia.
- `422`: parametros o cuerpo invalidos.

No se deben duplicar estas reglas dentro de componentes React. La capa API del
frontend sera la unica responsable de adaptar este contrato al modelo visual.
