import React, { useEffect, useState } from "react";
import { AppError, AppLoading } from "./components/AppState.jsx";
import ReadOnlyBoundary from "./components/ReadOnlyBoundary.jsx";
import { useAuth } from "./context/AuthContext.jsx";
import {
  API_READ_VIEWS,
  API_WRITE_VIEWS,
  buildViewProps,
  mapCurrentUser,
} from "./domain/appModel.js";
import {
  addVariant,
  checkoutSale,
  cancelSale,
  closeCashSession,
  createCategory,
  createClient,
  createCollection,
  createCreditPayment,
  createDiscountApproval,
  createInventoryAdjustment,
  createMaterial,
  createPhysicalCount,
  createProduct,
  createSubcategory,
  createTransfer,
  deleteProductImage,
  finalizePhysicalCount,
  getCashTerminals,
  getCurrentCashSession,
  getClientCreditLedger,
  getCreditRecoveryReport,
  getPhysicalCountDetail,
  getPhysicalCounts,
  getReadModel,
  getSaleDetail,
  getTransferDetail,
  getTransfers,
  openCashSession,
  quoteSale,
  receiveTransfer,
  sendTransfer,
  updateCategory,
  updateClient,
  updateClientCommercialProfile,
  updateCollection,
  updateMaterial,
  updatePhysicalCountLines,
  updateProduct,
  updateSubcategory,
  updateVariant,
  uploadProductImage,
} from "./lib/api.js";
import Login from "./pages/Login.jsx";
import {
  createLegacyReadModel,
  SCREEN_VIEWS,
  Sidebar,
} from "./screens/index.jsx";

const LEGACY_MODEL = createLegacyReadModel();

export default function App() {
  const { token, user, restoring, logout } = useAuth();
  const [readModel, setReadModel] = useState(null);
  const [readError, setReadError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [currentView, setCurrentView] = useState("sales");
  const CurrentView = SCREEN_VIEWS[currentView] || SCREEN_VIEWS.sales;

  useEffect(() => {
    if (!token || !user) {
      setReadModel(null);
      setReadError("");
      return undefined;
    }
    const controller = new AbortController();
    setReadError("");
    getReadModel(token, user.branches || [], controller.signal)
      .then(setReadModel)
      .catch((error) => {
        if (error.name !== "AbortError") setReadError(error.message);
      });
    return () => controller.abort();
  }, [token, user?.id, reloadKey]);

  if (restoring)
    return React.createElement(AppLoading, null, "Restaurando sesión…");
  if (!token || !user) return React.createElement(Login, null);
  if (readError && !readModel)
    return React.createElement(AppError, {
      message: readError,
      onRetry: () => setReloadKey((value) => value + 1),
      onLogout: logout,
    });
  if (!readModel)
    return React.createElement(AppLoading, null, "Cargando datos operativos…");

  const currentUser = mapCurrentUser(user);
  const connected = API_READ_VIEWS.has(currentView);
  const writable = API_WRITE_VIEWS.has(currentView);
  const refresh = () => setReloadKey((value) => value + 1);
  const actions = {
    registerClient: async (data) => {
      const client = await createClient(token, data);
      setReadModel((current) => ({
        ...current,
        clientes: [client, ...current.clientes],
      }));
      return client;
    },
    updateClient: async (clientId, data) => {
      const client = await updateClient(token, clientId, data);
      setReadModel((current) => ({
        ...current,
        clientes: current.clientes.map((item) =>
          item.id === client.id ? client : item,
        ),
      }));
      return client;
    },
    updateClientCommercialProfile: async (clientId, data) => {
      const client = await updateClientCommercialProfile(token, clientId, data);
      setReadModel((current) => ({
        ...current,
        clientes: current.clientes.map((item) =>
          item.id === client.id ? client : item,
        ),
      }));
      return true;
    },
    createSubcategory: async (categoryId, name) => {
      const result = await createSubcategory(token, categoryId, name);
      refresh();
      return result;
    },
    updateSubcategory: async (subcategory) => {
      const result = await updateSubcategory(token, subcategory);
      refresh();
      return result;
    },
    createCategory: async (category) => {
      const result = await createCategory(token, category);
      refresh();
      return result;
    },
    updateCategory: async (category) => {
      const result = await updateCategory(token, category);
      refresh();
      return result;
    },
    createMaterial: async (material) => {
      const result = await createMaterial(token, material);
      refresh();
      return result;
    },
    updateMaterial: async (material) => {
      const result = await updateMaterial(token, material);
      refresh();
      return result;
    },
    createCollection: async (name) => {
      const result = await createCollection(token, name);
      refresh();
      return result;
    },
    updateCollection: async (collection) => {
      const result = await updateCollection(token, collection);
      refresh();
      return result;
    },
    createProduct: async (payload) => {
      const result = await createProduct(token, payload);
      refresh();
      return result;
    },
    createInventoryAdjustment: async (payload) => {
      const result = await createInventoryAdjustment(token, payload);
      refresh();
      return result;
    },
    updateProduct: async (productId, payload) => {
      const result = await updateProduct(token, productId, payload);
      refresh();
      return result;
    },
    updateVariant: async (productId, variantId, payload) => {
      const result = await updateVariant(token, productId, variantId, payload);
      refresh();
      return result;
    },
    addVariant: async (productId, payload) => {
      const result = await addVariant(token, productId, payload);
      refresh();
      return result;
    },
    uploadProductImage: async (productId, file) => {
      const result = await uploadProductImage(token, productId, file);
      refresh();
      return result;
    },
    deleteProductImage: async (productId) => {
      await deleteProductImage(token, productId);
      refresh();
    },
    getCashTerminals: (signal) => getCashTerminals(token, signal),
    getCurrentCashSession: (terminalId, signal) =>
      getCurrentCashSession(token, terminalId, signal),
    openCashSession: (terminalId, openingAmount) =>
      openCashSession(token, terminalId, openingAmount),
    closeCashSession: (sessionId, countedCash) =>
      closeCashSession(token, sessionId, countedCash),
    quoteSale: (payload, signal) => quoteSale(token, payload, signal),
    checkoutSale: async (payload, idempotencyKey) => {
      const result = await checkoutSale(token, payload, idempotencyKey);
      refresh();
      return result;
    },
    cancelSale: async (saleId, payload, idempotencyKey) => {
      const result = await cancelSale(
        token,
        saleId,
        payload,
        idempotencyKey,
        user.branches || [],
      );
      refresh();
      return result;
    },
    createDiscountApproval: (payload) => createDiscountApproval(token, payload),
    createCreditPayment: async (clientId, payload, idempotencyKey) => {
      const result = await createCreditPayment(token, clientId, payload, idempotencyKey);
      refresh();
      return result;
    },
    getClientCreditLedger: (clientId, options, signal) =>
      getClientCreditLedger(token, clientId, options, signal),
    getCreditRecoveryReport: (options, signal) =>
      getCreditRecoveryReport(token, options, signal),
    getSaleDetail: (saleId, signal) =>
      getSaleDetail(token, saleId, user.branches || [], signal),
    getTransfers: (signal) =>
      getTransfers(token, readModel, user.branches || [], signal),
    getTransferDetail: (transferId, signal) =>
      getTransferDetail(
        token,
        transferId,
        readModel,
        user.branches || [],
        signal,
      ),
    createTransfer: (payload) =>
      createTransfer(token, payload, readModel, user.branches || []),
    sendTransfer: async (transferId, payload, idempotencyKey) => {
      const result = await sendTransfer(
        token,
        transferId,
        payload,
        idempotencyKey,
        readModel,
        user.branches || [],
      );
      refresh();
      return result;
    },
    receiveTransfer: async (transferId, payload, idempotencyKey) => {
      const result = await receiveTransfer(
        token,
        transferId,
        payload,
        idempotencyKey,
        readModel,
        user.branches || [],
      );
      refresh();
      return result;
    },
    getPhysicalCounts: (signal) =>
      getPhysicalCounts(token, readModel, user.branches || [], signal),
    getPhysicalCountDetail: (countId, signal) =>
      getPhysicalCountDetail(
        token,
        countId,
        readModel,
        user.branches || [],
        signal,
      ),
    createPhysicalCount: (payload, idempotencyKey) =>
      createPhysicalCount(
        token,
        payload,
        idempotencyKey,
        readModel,
        user.branches || [],
      ),
    updatePhysicalCountLines: (countId, payload) =>
      updatePhysicalCountLines(
        token,
        countId,
        payload,
        readModel,
        user.branches || [],
      ),
    finalizePhysicalCount: async (countId, payload, idempotencyKey) => {
      const result = await finalizePhysicalCount(
        token,
        countId,
        payload,
        idempotencyKey,
        readModel,
        user.branches || [],
      );
      refresh();
      return result;
    },
  };
  const view = React.createElement(
    CurrentView,
    buildViewProps({
      connected,
      readModel,
      legacyModel: LEGACY_MODEL,
      currentUser,
      actions,
    }),
  );

  return React.createElement(
    "div",
    { "data-od-id": "app-shell" },
    React.createElement(Sidebar, {
      currentView,
      setView: setCurrentView,
      user: currentUser,
    }),
    React.createElement(
      "div",
      { className: "session-controls" },
      React.createElement("span", { className: "mono" }, user.email),
      React.createElement(
        "button",
        { className: "btn-ghost", type: "button", onClick: logout },
        "Salir",
      ),
    ),
    connected && !writable
      ? React.createElement(ReadOnlyBoundary, null, view)
      : view,
  );
}
