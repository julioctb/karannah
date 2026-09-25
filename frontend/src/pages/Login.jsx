import React, { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";

const DEMO_ACCOUNTS = [
  ["Administrador", "admin@joyeria.local", "admin123"],
  ["Encargada T01", "encargada@joyeria.local", "encargada123"],
  ["Vendedora T01", "vendedora@joyeria.local", "vendedora123"],
];

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@joyeria.local");
  const [password, setPassword] = useState("admin123");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(email.trim(), password);
    } catch (nextError) {
      setError(nextError.message);
    } finally {
      setSubmitting(false);
    }
  };

  const selectAccount = (account) => {
    setEmail(account[1]);
    setPassword(account[2]);
    setError("");
  };

  return React.createElement(
    "main",
    { className: "login-page", "data-od-id": "login-page" },
    React.createElement(
      "section",
      { className: "login-intro" },
      React.createElement(
        "div",
        { className: "login-brand" },
        React.createElement(
          "span",
          { className: "login-mark", "aria-hidden": "true" },
          "J",
        ),
        React.createElement("span", null, "Joyería SaaS"),
      ),
      React.createElement(
        "div",
        { className: "login-intro-copy" },
        React.createElement(
          "span",
          { className: "pill pill-accent" },
          "Entorno local",
        ),
        React.createElement(
          "h1",
          null,
          "El mostrador, en orden desde el primer acceso.",
        ),
        React.createElement(
          "p",
          null,
          "Consulta ventas, inventario, clientes y reparaciones con permisos por usuario y sucursal.",
        ),
      ),
      React.createElement("div", {
        className: "login-rule",
        "aria-hidden": "true",
      }),
      React.createElement(
        "p",
        { className: "login-caption" },
        "Acceso seguro al sistema operativo de la joyería.",
      ),
    ),
    React.createElement(
      "section",
      { className: "login-panel" },
      React.createElement(
        "form",
        { className: "login-card card", onSubmit: submit },
        React.createElement(
          "header",
          { className: "login-header" },
          React.createElement(
            "span",
            { className: "mono login-kicker" },
            "ACCESO / LOCAL",
          ),
          React.createElement("h2", null, "Iniciar sesión"),
          React.createElement(
            "p",
            null,
            "Usa una cuenta semilla para entrar al entorno de desarrollo.",
          ),
        ),
        React.createElement(
          "label",
          { className: "login-field", htmlFor: "login-email" },
          React.createElement("span", null, "Correo"),
          React.createElement("input", {
            id: "login-email",
            type: "email",
            autoComplete: "username",
            value: email,
            onChange: (event) => setEmail(event.target.value),
            required: true,
            autoFocus: true,
          }),
        ),
        React.createElement(
          "label",
          { className: "login-field", htmlFor: "login-password" },
          React.createElement("span", null, "Contraseña"),
          React.createElement("input", {
            id: "login-password",
            type: "password",
            autoComplete: "current-password",
            value: password,
            onChange: (event) => setPassword(event.target.value),
            required: true,
          }),
        ),
        React.createElement(
          "div",
          { className: "login-error", role: "alert" },
          error,
        ),
        React.createElement(
          "button",
          {
            className: "btn-primary login-submit",
            type: "submit",
            disabled: submitting,
          },
          submitting ? "Validando…" : "Entrar al sistema",
        ),
        React.createElement(
          "div",
          { className: "login-accounts" },
          React.createElement("span", null, "Cuentas disponibles"),
          DEMO_ACCOUNTS.map((account) =>
            React.createElement(
              "button",
              {
                key: account[1],
                type: "button",
                className: "login-account",
                onClick: () => selectAccount(account),
              },
              React.createElement("strong", null, account[0]),
              React.createElement("span", { className: "mono" }, account[1]),
            ),
          ),
        ),
      ),
    ),
  );
}
