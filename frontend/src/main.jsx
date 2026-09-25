import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  React.createElement(AuthProvider, null, React.createElement(App, null))
);
