import React from "react";

const WRITE_ACTION_PATTERN = /Nuevo producto|Editar|Agregar|Nueva colección|Guardar colección|Nuevo cliente|Registrar cliente|Administrar|Recibir reparación|Registrar reparación|Guardar cambios|Marcar entregada/i;

export default function ReadOnlyBoundary({ children }) {
  const blockWrite = (event) => {
    const button = event.target.closest?.("button");
    if (!button || !WRITE_ACTION_PATTERN.test(button.textContent || "")) return;
    event.preventDefault();
    event.stopPropagation();
    window.alert("Esta pantalla usa datos reales en modo de solo lectura. La operación estará disponible al implementar su endpoint.");
  };
  const blockSubmit = (event) => {
    event.preventDefault();
    event.stopPropagation();
    window.alert("Esta pantalla usa datos reales en modo de solo lectura.");
  };
  return React.createElement("div", { className: "api-read-only", onClickCapture: blockWrite, onSubmitCapture: blockSubmit },
    React.createElement("div", { className: "api-read-only-notice", role: "status" },
      React.createElement("span", { className: "pill pill-accent" }, "API local"),
      React.createElement("span", null, "Consulta conectada al backend. Altas y cambios permanecen bloqueados hasta habilitar escritura persistente.")
    ),
    children
  );
}
