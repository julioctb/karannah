const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"
).replace(/\/$/, "");
const API_ORIGIN = new URL(API_URL, window.location.origin).origin;

export const AUTH_EXPIRED_EVENT = "joyeria:auth-expired";

export class ApiError extends Error {
  constructor(message, status = 0, details = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function request(
  path,
  { token, body, signal, method = "GET", headers: extraHeaders = {} } = {},
) {
  const isFormData = body instanceof FormData;
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      signal,
      headers: {
        Accept: "application/json",
        ...(body === undefined || isFormData
          ? {}
          : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...extraHeaders,
      },
      ...(body === undefined
        ? {}
        : { body: isFormData ? body : JSON.stringify(body) }),
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new ApiError(
      "No se pudo conectar con la API. Verifica que el backend esté activo.",
    );
  }

  const payload =
    response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : response.status === 403
          ? "No tienes permiso para realizar esta acción."
          : response.status === 409
            ? "La operación entra en conflicto con los datos actuales."
            : response.status === 422
              ? "Revisa la información enviada."
              : "La API no pudo completar la solicitud.";
    if (response.status === 401 && token)
      window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
    throw new ApiError(message, response.status, detail);
  }
  return payload;
}

export function loginLocal(email, password, signal) {
  return request("/auth/local/login", {
    method: "POST",
    body: { email, password },
    signal,
  });
}

export function getMe(token, signal) {
  return request("/me", { token, signal });
}

function mapCategory(row) {
  return {
    id: row.id,
    clave: row.code,
    nombre: row.name,
    grupo: row.group,
    requiereMaterial: row.requires_material,
    activa: row.active,
  };
}

function mapMaterial(row) {
  return { id: row.id, clave: row.code, nombre: row.name, activa: row.active };
}

function mapClient(row) {
  const limiteCredito =
    row.credit_limit === null ? null : Number(row.credit_limit);
  return {
    id: row.id,
    nombre: row.name,
    tipo: row.type,
    telefono: row.phone || "",
    email: row.email || "",
    notas: row.notes || "",
    saldo: Number(row.credit_balance),
    limiteCredito,
    creditoActivo: row.type === "mayoreo" && limiteCredito > 0,
    source: "api",
  };
}

function mapRepair(row) {
  const statuses = {
    recibido: "recibida",
    pendiente_taller: "en_reparacion",
    en_proceso: "en_reparacion",
    terminado: "lista",
    enviado: "en_reparacion",
  };
  return {
    id: row.id,
    codigo: row.folio,
    clienteId: row.client_id,
    cliente: row.client_name,
    pieza: row.product_description,
    servicio: row.service,
    fechaRecepcion: row.received_at,
    fechaEntrega: row.expected_at || "",
    costo: row.quoted_price === null ? null : Number(row.quoted_price),
    pagado: false,
    fechaPago: null,
    entregado: false,
    fechaEntregaReal: null,
    paymentKnown: false,
    deliveryKnown: false,
    estadoServicio: statuses[row.status] || "recibida",
    notas: row.notes || "",
  };
}

function mapSale(row, branchById) {
  const createdAt = new Date(row.created_at);
  const dateParts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Mexico_City",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(createdAt);
  const dateValues = Object.fromEntries(
    dateParts.map(({ type, value }) => [type, value]),
  );
  return {
    id: row.id,
    folio: row.folio,
    fecha: `${dateValues.year}-${dateValues.month}-${dateValues.day}`,
    hora: new Intl.DateTimeFormat("es-MX", {
      timeZone: "America/Mexico_City",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(createdAt),
    cliente: row.client_name || "Público general",
    vendedor: row.seller_name || "No disponible",
    tipoVenta: row.sale_type,
    condicion: row.condition,
    estado: row.status,
    tipoPago: row.payment_method,
    sucursal: branchById.get(row.branch_id)?.name || row.branch_code,
    total: Number(row.total),
    canceladaEn: row.cancelled_at || null,
    motivoCancelacion: row.cancellation_reason || "",
    summaryOnly: true,
    items: [],
  };
}

function mapSaleDetail(row, branchById) {
  const sale = mapSale(row, branchById);
  return {
    ...sale,
    summaryOnly: false,
    items: (row.items || []).map((item) => ({
      id: item.id,
      variantId: item.variant_id,
      sku: item.sku,
      nombre: item.product_name,
      cantidad: item.quantity,
      precioUnitario: Number(item.unit_price),
      subtotal: Number(item.subtotal),
      total: Number(item.total),
    })),
    payments: (row.payments || []).map((payment) => ({
      id: payment.id,
      method: payment.method,
      amount: Number(payment.amount),
      cashSessionId: payment.cash_session_id,
    })),
  };
}

function mapCreditRecoveryReport(row) {
  return {
    branchId: row.branch_id,
    dateFrom: row.date_from,
    dateTo: row.date_to,
    totalClients: row.total_clients,
    totals: {
      clientsWithBalance: row.totals.clients_with_balance,
      currentBalance: Number(row.totals.current_balance),
      periodCharged: Number(row.totals.period_charged),
      periodRecovered: Number(row.totals.period_recovered),
      periodNet: Number(row.totals.period_net),
    },
    rows: (row.rows || []).map((item) => ({
      clientId: item.client_id,
      clientName: item.client_name,
      phone: item.phone || "",
      email: item.email || "",
      creditLimit: item.credit_limit === null ? null : Number(item.credit_limit),
      currentBalance: Number(item.current_balance),
      periodCharged: Number(item.period_charged),
      periodRecovered: Number(item.period_recovered),
      periodNet: Number(item.period_net),
      lastPaymentAt: item.last_payment_at,
    })),
  };
}

function buildPhaseFiveLookups(readModel, branches) {
  const branchById = new Map(branches.map((branch) => [branch.id, branch]));
  const variantById = new Map();
  for (const product of readModel.productos || []) {
    for (const variant of product.variantes || []) {
      variantById.set(variant.id, { product, variant });
    }
  }
  return { branchById, variantById };
}

function mapTransfer(row, readModel, branches) {
  const { branchById, variantById } = buildPhaseFiveLookups(
    readModel,
    branches,
  );
  const origin = branchById.get(row.origin_branch_id);
  const destination = branchById.get(row.destination_branch_id);
  const states = {
    draft: "pendiente",
    sent: "en_transito",
    received: "recibido",
  };
  return {
    id: row.id,
    folio: row.folio,
    status: row.status,
    estado: states[row.status] || row.status,
    originBranchId: row.origin_branch_id,
    originBranchCode: origin?.code || "",
    originBranchName: origin?.name || "",
    destinationBranchId: row.destination_branch_id,
    destinationBranchCode: destination?.code || "",
    destinationBranchName: destination?.name || "",
    origenId: origin?.code || row.origin_branch_id,
    destinoId: destination?.code || row.destination_branch_id,
    createdBy: row.created_by,
    sentBy: row.sent_by,
    receivedBy: row.received_by,
    createdAt: row.created_at,
    sentAt: row.sent_at,
    receivedAt: row.received_at,
    fecha: row.created_at.slice(0, 10),
    productos: (row.lines || []).map((line) => {
      const match = variantById.get(line.variant_id);
      return {
        id: line.id,
        variantId: line.variant_id,
        sku: match?.variant.sku || "",
        nombre: match?.product.nombre || "Producto no disponible",
        cantidad: line.shipped_quantity,
        cantidadRecibida: line.received_quantity,
        faltante: line.shortage_quantity,
      };
    }),
  };
}

function mapPhysicalCount(row, readModel, branches) {
  const { branchById, variantById } = buildPhaseFiveLookups(
    readModel,
    branches,
  );
  const branch = branchById.get(row.branch_id);
  const states = { open: "en_proceso", finalized: "completado" };
  const lineas = (row.lines || []).map((line) => {
    const match = variantById.get(line.variant_id);
    return {
      id: line.id,
      variantId: line.variant_id,
      sku: match?.variant.sku || "",
      nombre: match?.product.nombre || "Producto no disponible",
      categoria: match?.product.categoria || "",
      esperado: line.snapshot_quantity,
      contado: line.observed_quantity,
    };
  });
  const observacionesCompletas = lineas.every((line) => line.contado !== null);
  const totalEsperado = lineas.reduce((total, line) => total + line.esperado, 0);
  const observedTotal = lineas.reduce(
    (total, line) => total + (line.contado ?? 0),
    0,
  );
  const totalContado = observacionesCompletas ? observedTotal : null;
  return {
    id: row.id,
    folio: row.folio,
    branchId: row.branch_id,
    sucursal: branch?.code || row.branch_id,
    branchName: branch?.name || "",
    status: row.status,
    estado: states[row.status] || row.status,
    createdBy: row.created_by,
    finalizedBy: row.finalized_by,
    createdAt: row.created_at,
    finalizedAt: row.finalized_at,
    fecha: row.created_at.slice(0, 10),
    totalEsperado,
    totalContado,
    diferencia: observacionesCompletas
      ? observedTotal - totalEsperado
      : null,
    observacionesCompletas,
    lineas,
  };
}

async function getAllRows(path, token, signal) {
  const pageSize = 500;
  const rows = [];
  let offset = 0;
  while (true) {
    const separator = path.includes("?") ? "&" : "?";
    const page = await request(
      `${path}${separator}limit=${pageSize}&offset=${offset}`,
      { token, signal },
    );
    rows.push(...page);
    if (page.length < pageSize) return rows;
    offset += page.length;
  }
}

export async function getReadModel(token, branches, signal) {
  const [
    categoryRows,
    materialRows,
    subcategoryRows,
    collectionRows,
    productRows,
    stockRows,
    clientRows,
    saleRows,
    repairRows,
  ] = await Promise.all([
    getAllRows("/catalog/categories?include_inactive=true", token, signal),
    getAllRows("/catalog/materials?include_inactive=true", token, signal),
    getAllRows("/catalog/subcategories?include_inactive=true", token, signal),
    getAllRows("/catalog/collections?include_inactive=true", token, signal),
    getAllRows("/catalog/products?include_inactive=true", token, signal),
    getAllRows("/inventory/stock", token, signal),
    getAllRows("/clients", token, signal),
    getAllRows("/sales", token, signal),
    getAllRows("/repairs", token, signal),
  ]);

  const categorias = categoryRows.map(mapCategory);
  const materiales = materialRows.map(mapMaterial);
  const categoryById = new Map(categorias.map((row) => [row.id, row]));
  const materialById = new Map(materiales.map((row) => [row.id, row]));
  const branchById = new Map(branches.map((row) => [row.id, row]));
  const stockByProduct = new Map();
  for (const row of stockRows) {
    stockByProduct.set(
      row.product_id,
      (stockByProduct.get(row.product_id) || 0) + row.quantity,
    );
  }

  const subcategorias = {};
  for (const row of subcategoryRows) {
    const code = categoryById.get(row.category_id)?.clave;
    if (!code) continue;
    if (!subcategorias[code]) subcategorias[code] = [];
    subcategorias[code].push({
      id: row.id,
      nombre: row.name,
      activa: row.active,
      sistema: row.is_system,
    });
  }

  const stockByVariant = new Map();
  const stockByVariantBranch = new Map();
  for (const row of stockRows) {
    stockByVariant.set(
      row.variant_id,
      (stockByVariant.get(row.variant_id) || 0) + row.quantity,
    );
    if (!stockByVariantBranch.has(row.variant_id)) {
      stockByVariantBranch.set(row.variant_id, {});
    }
    stockByVariantBranch.get(row.variant_id)[row.branch_id] = row.quantity;
  }
  const productos = productRows.map((row) => {
    const variantes = row.variants.map((variant) => ({
      id: variant.id,
      sku: variant.sku,
      tipo: row.variant_type,
      talla_o_color: variant.variant_value || "",
      stock: stockByVariant.get(variant.id) || 0,
      stockByBranch: stockByVariantBranch.get(variant.id) || {},
      precio_costo:
        variant.cost_price === null ? null : Number(variant.cost_price),
      precio_menudeo: Number(variant.retail_price),
      precio_mayoreo: Number(variant.wholesale_price),
      estado: variant.active ? "disponible" : "baja",
    }));
    return {
      id: row.id,
      sku: row.sku,
      nombre: row.name,
      categoriaId: row.category_id,
      categoria: categoryById.get(row.category_id)?.clave || "",
      materialId: row.material_id,
      material: row.material_id
        ? materialById.get(row.material_id)?.clave || null
        : null,
      subcategoriaId: row.subcategory_id,
      subcategoria: row.subcategory_name,
      colecciones: row.collection_ids,
      piedra: row.stone,
      notas: row.notes || "",
      imagen: row.image_url
        ? new URL(row.image_url, API_ORIGIN).toString()
        : null,
      precio_costo: row.cost_price === null ? null : Number(row.cost_price),
      precio_menudeo: Number(row.retail_price),
      precio_mayoreo: Number(row.wholesale_price),
      estado: row.active ? row.status : "baja",
      stock: stockByProduct.get(row.id) || 0,
      tiene_variantes: Boolean(row.variant_type),
      tipo_variacion: row.variant_type,
      variantes,
    };
  });

  return {
    categorias,
    materiales,
    subcategorias,
    colecciones: collectionRows.map((row) => ({
      id: row.id,
      nombre: row.name,
      activa: row.active,
    })),
    productos,
    clientes: clientRows.map(mapClient),
    ventas: saleRows.map((row) => mapSale(row, branchById)),
    reparaciones: repairRows.map(mapRepair),
  };
}

export async function createClient(token, data) {
  const row = await request("/clients", {
    token,
    method: "POST",
    body: {
      name: data.nombre,
      phone: data.telefono || null,
      email: data.email || null,
      notes: data.notas || null,
    },
  });
  return mapClient(row);
}

export async function updateClient(token, clientId, data) {
  const row = await request(`/clients/${clientId}`, {
    token,
    method: "PATCH",
    body: {
      name: data.nombre,
      phone: data.telefono || null,
      email: data.email || null,
      notes: data.notas || null,
    },
  });
  return mapClient(row);
}

export async function updateClientCommercialProfile(token, clientId, data) {
  const row = await request(`/clients/${clientId}/commercial-profile`, {
    token,
    method: "PATCH",
    body: {
      type: data.tipo,
      credit_limit: data.creditoActivo ? String(data.limiteCredito) : null,
    },
  });
  return mapClient(row);
}

export function createSubcategory(token, categoryId, name) {
  return request("/catalog/subcategories", {
    token,
    method: "POST",
    body: { category_id: categoryId, name },
  });
}

export function updateSubcategory(token, subcategory) {
  return request(`/catalog/subcategories/${subcategory.id}`, {
    token,
    method: "PATCH",
    body: { name: subcategory.nombre, active: subcategory.activa },
  });
}

export function createCategory(token, category) {
  return request("/catalog/categories", {
    token,
    method: "POST",
    body: {
      code: category.clave,
      name: category.nombre,
      group: category.grupo,
      requires_material: category.requiereMaterial,
    },
  });
}

export function updateCategory(token, category) {
  return request(`/catalog/categories/${category.id}`, {
    token,
    method: "PATCH",
    body: {
      name: category.nombre,
      requires_material: category.requiereMaterial,
      active: category.activa,
    },
  });
}

export function createMaterial(token, material) {
  return request("/catalog/materials", {
    token,
    method: "POST",
    body: { code: material.clave, name: material.nombre },
  });
}

export function updateMaterial(token, material) {
  return request(`/catalog/materials/${material.id}`, {
    token,
    method: "PATCH",
    body: { name: material.nombre, active: material.activa },
  });
}

export function createCollection(token, name) {
  return request("/catalog/collections", {
    token,
    method: "POST",
    body: { name },
  });
}

export function updateCollection(token, collection) {
  return request(`/catalog/collections/${collection.id}`, {
    token,
    method: "PATCH",
    body: { name: collection.nombre, active: collection.activa },
  });
}

export function createProduct(token, product) {
  return request("/catalog/products", { token, method: "POST", body: product });
}

export function updateProduct(token, productId, product) {
  return request(`/catalog/products/${productId}`, {
    token,
    method: "PATCH",
    body: product,
  });
}

export function updateVariant(token, productId, variantId, variant) {
  return request(`/catalog/products/${productId}/variants/${variantId}`, {
    token,
    method: "PATCH",
    body: variant,
  });
}

export function addVariant(token, productId, variant) {
  return request(`/catalog/products/${productId}/variants`, {
    token,
    method: "POST",
    body: variant,
  });
}

export function uploadProductImage(token, productId, file) {
  const body = new FormData();
  body.append("file", file);
  return request(`/catalog/products/${productId}/image`, {
    token,
    method: "PUT",
    body,
  });
}

export function deleteProductImage(token, productId) {
  return request(`/catalog/products/${productId}/image`, {
    token,
    method: "DELETE",
  });
}

export function createInventoryAdjustment(token, adjustment) {
  return request("/inventory/adjustments", {
    token,
    method: "POST",
    body: adjustment,
  });
}

export function getCashTerminals(token, signal) {
  return request("/cash/terminals", { token, signal });
}

export function getCurrentCashSession(token, terminalId, signal) {
  return request(`/cash/sessions/current?terminal_id=${encodeURIComponent(terminalId)}`, {
    token,
    signal,
  });
}

export function openCashSession(token, terminalId, openingAmount) {
  return request("/cash/sessions/open", {
    token,
    method: "POST",
    body: { terminal_id: terminalId, opening_amount: String(openingAmount) },
  });
}

export function closeCashSession(token, sessionId, countedCash) {
  return request(`/cash/sessions/${sessionId}/close`, {
    token,
    method: "POST",
    body: { counted_cash: String(countedCash) },
  });
}

export function quoteSale(token, payload, signal) {
  return request("/sales/quote", {
    token,
    method: "POST",
    body: payload,
    signal,
  });
}

export function checkoutSale(token, payload, idempotencyKey) {
  return request("/sales/checkout", {
    token,
    method: "POST",
    body: payload,
    headers: { "Idempotency-Key": idempotencyKey },
  });
}

export async function getSaleDetail(token, saleId, branches, signal) {
  const row = await request(`/sales/${saleId}`, { token, signal });
  return mapSaleDetail(row, new Map(branches.map((branch) => [branch.id, branch])));
}

export function createDiscountApproval(token, payload) {
  return request("/sales/discount-approvals", {
    token,
    method: "POST",
    body: payload,
  });
}

export function getClientCreditLedger(token, clientId, { limit = 100, offset = 0 } = {}, signal) {
  return request(
    `/clients/${clientId}/credit-ledger?limit=${limit}&offset=${offset}`,
    { token, signal },
  );
}

export function getCreditRecoveryReport(token, options = {}, signal) {
  const params = new URLSearchParams();
  if (options.branchId) params.set("branch_id", options.branchId);
  if (options.dateFrom) params.set("date_from", options.dateFrom);
  if (options.dateTo) params.set("date_to", options.dateTo);
  if (options.limit !== undefined) params.set("limit", String(options.limit));
  if (options.offset !== undefined) params.set("offset", String(options.offset));
  const query = params.toString();
  return request(`/reports/credit-recovery${query ? `?${query}` : ""}`, {
    token,
    signal,
  }).then(mapCreditRecoveryReport);
}

export function createCreditPayment(token, clientId, payload, idempotencyKey) {
  return request(`/clients/${clientId}/credit-payments`, {
    token,
    method: "POST",
    body: payload,
    headers: { "Idempotency-Key": idempotencyKey },
  });
}

export async function cancelSale(token, saleId, payload, idempotencyKey, branches) {
  const row = await request(`/sales/${saleId}/cancel`, {
    token,
    method: "POST",
    body: payload,
    headers: { "Idempotency-Key": idempotencyKey },
  });
  return mapSaleDetail(row, new Map(branches.map((branch) => [branch.id, branch])));
}

export async function getTransfers(token, readModel, branches, signal) {
  const rows = await getAllRows("/inventory/transfers", token, signal);
  return rows.map((row) => mapTransfer(row, readModel, branches));
}

export async function getTransferDetail(
  token,
  transferId,
  readModel,
  branches,
  signal,
) {
  const row = await request(`/inventory/transfers/${transferId}`, {
    token,
    signal,
  });
  return mapTransfer(row, readModel, branches);
}

export async function createTransfer(token, payload, readModel, branches) {
  const row = await request("/inventory/transfers", {
    token,
    method: "POST",
    body: payload,
  });
  return mapTransfer(row, readModel, branches);
}

export async function sendTransfer(
  token,
  transferId,
  payload,
  idempotencyKey,
  readModel,
  branches,
) {
  const row = await request(`/inventory/transfers/${transferId}/send`, {
    token,
    method: "POST",
    body: payload,
    headers: { "Idempotency-Key": idempotencyKey },
  });
  return mapTransfer(row, readModel, branches);
}

export async function receiveTransfer(
  token,
  transferId,
  payload,
  idempotencyKey,
  readModel,
  branches,
) {
  const row = await request(`/inventory/transfers/${transferId}/receive`, {
    token,
    method: "POST",
    body: payload,
    headers: { "Idempotency-Key": idempotencyKey },
  });
  return mapTransfer(row, readModel, branches);
}

export async function getPhysicalCounts(token, readModel, branches, signal) {
  const rows = await getAllRows("/inventory/physical-counts", token, signal);
  return rows.map((row) => mapPhysicalCount(row, readModel, branches));
}

export async function getPhysicalCountDetail(
  token,
  countId,
  readModel,
  branches,
  signal,
) {
  const row = await request(`/inventory/physical-counts/${countId}`, {
    token,
    signal,
  });
  return mapPhysicalCount(row, readModel, branches);
}

export async function createPhysicalCount(token, payload, readModel, branches) {
  const row = await request("/inventory/physical-counts", {
    token,
    method: "POST",
    body: payload,
  });
  return mapPhysicalCount(row, readModel, branches);
}

export async function updatePhysicalCountLines(
  token,
  countId,
  payload,
  readModel,
  branches,
) {
  const row = await request(`/inventory/physical-counts/${countId}/lines`, {
    token,
    method: "PATCH",
    body: payload,
  });
  return mapPhysicalCount(row, readModel, branches);
}

export async function finalizePhysicalCount(
  token,
  countId,
  payload,
  idempotencyKey,
  readModel,
  branches,
) {
  const row = await request(`/inventory/physical-counts/${countId}/finalize`, {
    token,
    method: "POST",
    body: payload,
    headers: { "Idempotency-Key": idempotencyKey },
  });
  return mapPhysicalCount(row, readModel, branches);
}
