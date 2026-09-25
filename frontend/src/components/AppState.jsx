import React from "react";

export function AppLoading({ children }) {
  return React.createElement("div", { className: "app-loading" }, children);
}

export function AppError({ message, onRetry, onLogout }) {
  return React.createElement("main", { className: "app-state-page" },
    React.createElement("section", { className: "card app-state-card" },
      React.createElement("span", { className: "pill pill-danger" }, "Sin conexión"),
      React.createElement("h1", null, "No pudimos cargar los datos"),
      React.createElement("p", null, message),
      React.createElement("div", { className: "app-state-actions" },
        React.createElement("button", { className: "btn-primary", onClick: onRetry }, "Reintentar"),
        React.createElement("button", { className: "btn-secondary", onClick: onLogout }, "Cerrar sesión")
      )
    )
  );
}
