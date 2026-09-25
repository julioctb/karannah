export const API_READ_VIEWS = new Set([
  "categories",
  "inventory",
  "pos",
  "sales",
  "clients",
  "credits",
  "repairs",
]);
export const API_WRITE_VIEWS = new Set([
  "categories",
  "inventory",
  "pos",
  "clients",
  "credits",
  "sales",
]);

export function mapCurrentUser(user) {
  const branches = (user.branches || []).map((branch) => ({
    id: branch.code,
    uuid: branch.id,
    nombre: branch.name,
    tipo: branch.code.startsWith("A") ? "almacen" : "tienda",
  }));
  return {
    nombre: user.full_name,
    rol: user.role,
    sucursal: branches[0] || null,
    sucursales: branches,
  };
}

export function buildViewProps({
  connected,
  readModel,
  legacyModel,
  currentUser,
  actions = {},
}) {
  const model = connected ? readModel : legacyModel;
  return {
    ...model,
    ...actions,
    actions,
    sucursales: connected ? currentUser.sucursales : model.sucursales,
    registerClient: actions.registerClient || (() => null),
    updateClientCommercialProfile:
      actions.updateClientCommercialProfile || (() => false),
    currentUser,
    registrarReparacion: () => null,
    actualizarReparacion: () => false,
    cobrarReparacion: () => false,
  };
}
