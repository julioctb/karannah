import React from "react";
const PRODUCT_IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const PRODUCT_IMAGE_MAX_BYTES = 5 * 1024 * 1024;

function validateProductImage(file) {
  if (!file) return "Selecciona una imagen.";
  if (!PRODUCT_IMAGE_TYPES.has(file.type))
    return "Solo se aceptan imágenes JPG, PNG o WebP.";
  if (file.size > PRODUCT_IMAGE_MAX_BYTES)
    return "La imagen no puede superar 5 MB.";
  return "";
}

const { useState: useState, useEffect: useEffect } = React,
  SUCURSALES = [
    { id: "T01", nombre: "Centro Histórico", tipo: "tienda" },
    { id: "T02", nombre: "Plaza Universidad", tipo: "tienda" },
    { id: "A01", nombre: "Almacén Principal", tipo: "almacen" },
  ],
  CATEGORIAS = [
    { clave: "AN", nombre: "Anillo", grupo: "joyeria" },
    { clave: "AR", nombre: "Arete", grupo: "joyeria" },
    { clave: "BR", nombre: "Brazalete", grupo: "joyeria" },
    { clave: "CA", nombre: "Cadena", grupo: "joyeria" },
    { clave: "CO", nombre: "Collar", grupo: "joyeria" },
    { clave: "DI", nombre: "Dije", grupo: "joyeria" },
    { clave: "PU", nombre: "Pulsera", grupo: "joyeria" },
    { clave: "JU", nombre: "Juego/Set", grupo: "joyeria" },
    { clave: "ES", nombre: "Estampa", grupo: "nojoyeria" },
    { clave: "AC", nombre: "Accesorio", grupo: "nojoyeria" },
    { clave: "MI", nombre: "Misceláneo", grupo: "nojoyeria" },
  ],
  MATERIALES = [
    { clave: "PL", nombre: "Plata .925" },
    { clave: "OR", nombre: "Oro 14k" },
    { clave: "CH", nombre: "Chapa/Baño" },
    { clave: "AC", nombre: "Acero" },
    { clave: "BI", nombre: "Bisutería" },
    { clave: "OT", nombre: "Otro" },
  ],
  SUBCATEGORIAS_SEED = {
    AC: [
      { id: 1, nombre: "Cuarzos y minerales", activa: !0 },
      { id: 2, nombre: "Ojos turcos y protección", activa: !0 },
      { id: 3, nombre: "Inciensos y sahumerios", activa: !0 },
      { id: 4, nombre: "Geometría sagrada y símbolos", activa: !0 },
      { id: 5, nombre: "Imágenes y figuras religiosas", activa: !0 },
      { id: 6, nombre: "Figuras y animales", activa: !0 },
      { id: 7, nombre: "Móviles, atrapasueños y colgantes", activa: !0 },
      { id: 8, nombre: "Péndulos, runas y tarot", activa: !0 },
      { id: 9, nombre: "Velas y veladoras", activa: !0 },
      { id: 10, nombre: "Decoración esotérica", activa: !0 },
      { id: 11, nombre: "Meditación y rituales", activa: !0 },
      { id: 12, nombre: "Audio", activa: !0 },
      { id: 99, nombre: "Por clasificar", activa: !0, sistema: !0 },
    ],
    MI: [
      { id: 1, nombre: "Velas y veladoras", activa: !0 },
      { id: 2, nombre: "Esencias, sprays y polvos", activa: !0 },
      { id: 3, nombre: "Flores de Bach y herbolaria", activa: !0 },
      { id: 4, nombre: "Aguas y lociones rituales", activa: !0 },
      { id: 5, nombre: "Cuidado personal", activa: !0 },
      { id: 6, nombre: "Aromatización de ambiente", activa: !0 },
      { id: 7, nombre: "Limpieza de joyería", activa: !0 },
      { id: 8, nombre: "Imán y varios", activa: !0 },
      { id: 99, nombre: "Por clasificar", activa: !0, sistema: !0 },
    ],
    ES: [
      { id: 1, nombre: "Estampa religiosa", activa: !0 },
      { id: 99, nombre: "Por clasificar", activa: !0, sistema: !0 },
    ],
  },
  COLECCIONES_SEED = [
    { id: 1, nombre: "Protección", activa: !0 },
    { id: 2, nombre: "Amor", activa: !0 },
    { id: 3, nombre: "Prosperidad", activa: !0 },
    { id: 4, nombre: "Salud", activa: !0 },
    { id: 5, nombre: "Suerte", activa: !0 },
    { id: 6, nombre: "Limpieza", activa: !0 },
    { id: 7, nombre: "Armonía", activa: !0 },
    { id: 8, nombre: "Meditación", activa: !0 },
    { id: 9, nombre: "Día de las madres", activa: !0 },
    { id: 10, nombre: "Bautizos y comuniones", activa: !0 },
  ],
  REGLAS_SUBCATEGORIAS = {
    AC: {
      "Cuarzos y minerales": [
        "cuarzo",
        "amatista",
        "turmalina",
        "obsidiana",
        "jade",
        "onix",
        "ojo de tigre",
        "piedra",
        "mineral",
        "cristal",
        "geoda",
      ],
      "Ojos turcos y protección": [
        "ojo turco",
        "nazar",
        "hamsa",
        "mano de fatima",
        "herradura",
        "trebol",
      ],
      "Inciensos y sahumerios": [
        "incienso",
        "sahumerio",
        "palo santo",
        "copal",
        "mirra",
        "salvia",
      ],
      "Geometría sagrada y símbolos": [
        "geometria",
        "merkaba",
        "flor de la vida",
        "mandala",
        "sri yantra",
        "om",
        "yin yang",
      ],
      "Imágenes y figuras religiosas": [
        "virgen",
        "santo",
        "angel",
        "arcangel",
        "jesus",
        "san",
        "santa",
        "sagrado",
      ],
      "Figuras y animales": [
        "elefante",
        "buda",
        "ganesha",
        "buho",
        "tortuga",
        "dragon",
        "fenix",
        "lobo",
        "aguila",
        "figura",
      ],
      "Móviles, atrapasueños y colgantes": [
        "atrapasueños",
        "movil",
        "colgante",
        "campana",
        "carillon",
      ],
      "Péndulos, runas y tarot": [
        "pendulo",
        "runa",
        "tarot",
        "oraculo",
        "i ching",
      ],
      "Velas y veladoras": ["vela", "veladora", "cirio"],
      "Decoración esotérica": [
        "fuente",
        "lampara",
        "portavela",
        "incensario",
        "altar",
      ],
      "Meditación y rituales": [
        "meditacion",
        "ritual",
        "bol tibetano",
        "tingsha",
        "mala",
      ],
      Audio: ["cd", "musica", "sonido", "audio"],
    },
    MI: {
      "Velas y veladoras": ["vela", "veladora", "cirio"],
      "Esencias, sprays y polvos": [
        "esencia",
        "spray",
        "polvo",
        "aceite esencial",
        "aroma",
      ],
      "Flores de Bach y herbolaria": [
        "bach",
        "herbolaria",
        "hierba",
        "te",
        "infusion",
      ],
      "Aguas y lociones rituales": [
        "agua",
        "locion",
        "colonia",
        "florida",
        "ruda",
      ],
      "Cuidado personal": ["jabon", "shampoo", "crema", "balsamo"],
      "Aromatización de ambiente": ["difusor", "ambientador", "potpourri"],
      "Limpieza de joyería": ["limpiador", "paño", "pulidor", "liquido limpia"],
      "Imán y varios": ["iman", "magnetico", "kit"],
    },
    ES: {},
  },
  sugerirSubcategoria = (e, t) => {
    if (!["ES", "AC", "MI"].includes(t)) return null;
    const a = REGLAS_SUBCATEGORIAS[t] || {},
      l = e.toLowerCase();
    for (const [e, t] of Object.entries(a))
      for (const a of t) if (l.includes(a.toLowerCase())) return e;
    return "Por clasificar";
  },
  skuCounters = {
    AN: 5,
    AR: 2,
    BR: 2,
    CA: 1,
    CO: 2,
    DI: 2,
    PU: 3,
    JU: 1,
    ES: 5,
    AC: 15,
    MI: 10,
  },
  generarSKU = (e, t = null) => {
    const a = CATEGORIAS.find((t) => t.clave === e);
    if (!a) return null;
    skuCounters[e] = (skuCounters[e] || 0) + 1;
    const l = String(skuCounters[e]).padStart(4, "0");
    return "joyeria" === a.grupo && t ? `${e}-${t}-${l}` : `${e}-${l}`;
  },
  PRODUCTOS = [
    {
      id: 1,
      sku: "AN-OR-0001",
      nombre: "Anillo Ojo Turco Oro 14K",
      categoria: "AN",
      material: "OR",
      subcategoria: null,
      colecciones: [1],
      piedra: "Ojo turco",
      precio_costo: 4500,
      precio_menudeo: 6750,
      precio_mayoreo: 5738,
      estado: "disponible",
      stock: 3,
    },
    {
      id: 2,
      sku: "PU-OT-0001",
      nombre: "Pulsera 7 Nudos Roja",
      categoria: "PU",
      material: "OT",
      subcategoria: null,
      colecciones: [1],
      piedra: null,
      precio_costo: 85,
      precio_menudeo: 180,
      precio_mayoreo: 150,
      estado: "disponible",
      stock: 25,
    },
    {
      id: 3,
      sku: "DI-PL-0001",
      nombre: "Dije Elefante de la Suerte",
      categoria: "DI",
      material: "PL",
      subcategoria: null,
      colecciones: [5],
      piedra: null,
      precio_costo: 650,
      precio_menudeo: 1200,
      precio_mayoreo: 980,
      estado: "disponible",
      stock: 8,
    },
    {
      id: 4,
      sku: "AN-OR-0002",
      nombre: "Anillo Compromiso Diamante",
      categoria: "AN",
      material: "OR",
      subcategoria: null,
      colecciones: [2],
      piedra: "Diamante 0.25ct",
      precio_costo: 12500,
      precio_menudeo: 18750,
      precio_mayoreo: 15938,
      estado: "disponible",
      stock: 2,
    },
    {
      id: 5,
      sku: "CO-OR-0001",
      nombre: "Collar Mano de Fátima",
      categoria: "CO",
      material: "OR",
      subcategoria: null,
      colecciones: [1],
      piedra: null,
      precio_costo: 3200,
      precio_menudeo: 4800,
      precio_mayoreo: 4080,
      estado: "disponible",
      stock: 4,
    },
    {
      id: 6,
      sku: "AR-PL-0001",
      nombre: "Aretes Cuarzo Rosa",
      categoria: "AR",
      material: "PL",
      subcategoria: null,
      colecciones: [2],
      piedra: "Cuarzo rosa",
      precio_costo: 420,
      precio_menudeo: 750,
      precio_mayoreo: 638,
      estado: "disponible",
      stock: 6,
    },
    {
      id: 7,
      sku: "BR-AC-0001",
      nombre: "Brazalete Ojo de Tigre",
      categoria: "BR",
      material: "AC",
      subcategoria: null,
      colecciones: [3],
      piedra: "Ojo de tigre",
      precio_costo: 380,
      precio_menudeo: 680,
      precio_mayoreo: 578,
      estado: "disponible",
      stock: 5,
    },
    {
      id: 8,
      sku: "PU-OT-0002",
      nombre: "Pulsera Obsidiana Negra",
      categoria: "PU",
      material: "OT",
      subcategoria: null,
      colecciones: [1],
      piedra: "Obsidiana",
      precio_costo: 150,
      precio_menudeo: 320,
      precio_mayoreo: 272,
      estado: "externo",
      stock: 0,
    },
    {
      id: 9,
      sku: "AC-0001",
      nombre: "Veladora Roja del Amor",
      categoria: "AC",
      material: null,
      subcategoria: "Velas y veladoras",
      colecciones: [2],
      piedra: null,
      precio_costo: 45,
      precio_menudeo: 95,
      precio_mayoreo: 75,
      estado: "disponible",
      stock: 20,
    },
    {
      id: 10,
      sku: "AC-0002",
      nombre: "Incienso Palo Santo x10",
      categoria: "AC",
      material: null,
      subcategoria: "Inciensos y sahumerios",
      colecciones: [6],
      piedra: null,
      precio_costo: 80,
      precio_menudeo: 150,
      precio_mayoreo: 120,
      estado: "disponible",
      stock: 35,
    },
    {
      id: 11,
      sku: "AC-0003",
      nombre: "Cuarzo Rosa en Bruto",
      categoria: "AC",
      material: null,
      subcategoria: "Cuarzos y minerales",
      colecciones: [2],
      piedra: "Cuarzo rosa",
      precio_costo: 120,
      precio_menudeo: 250,
      precio_mayoreo: 200,
      estado: "disponible",
      stock: 15,
    },
    {
      id: 12,
      sku: "AC-0004",
      nombre: "Tarot Rider Waite",
      categoria: "AC",
      material: null,
      subcategoria: "Péndulos, runas y tarot",
      colecciones: [],
      piedra: null,
      precio_costo: 280,
      precio_menudeo: 550,
      precio_mayoreo: 450,
      estado: "disponible",
      stock: 8,
    },
    {
      id: 13,
      sku: "AC-0005",
      nombre: "Atrapasueños Grande",
      categoria: "AC",
      material: null,
      subcategoria: "Móviles, atrapasueños y colgantes",
      colecciones: [1],
      piedra: null,
      precio_costo: 180,
      precio_menudeo: 380,
      precio_mayoreo: 320,
      estado: "disponible",
      stock: 6,
    },
    {
      id: 14,
      sku: "AC-0006",
      nombre: "Figura Buda Meditando",
      categoria: "AC",
      material: null,
      subcategoria: "Figuras y animales",
      colecciones: [7, 8],
      piedra: null,
      precio_costo: 220,
      precio_menudeo: 450,
      precio_mayoreo: 380,
      estado: "disponible",
      stock: 4,
    },
    {
      id: 15,
      sku: "MI-0001",
      nombre: "Aceite Esencial Lavanda",
      categoria: "MI",
      material: null,
      subcategoria: "Esencias, sprays y polvos",
      colecciones: [7],
      piedra: null,
      precio_costo: 95,
      precio_menudeo: 180,
      precio_mayoreo: 150,
      estado: "disponible",
      stock: 12,
    },
    {
      id: 16,
      sku: "MI-0002",
      nombre: "Agua de Florida",
      categoria: "MI",
      material: null,
      subcategoria: "Aguas y lociones rituales",
      colecciones: [6],
      piedra: null,
      precio_costo: 65,
      precio_menudeo: 120,
      precio_mayoreo: 100,
      estado: "disponible",
      stock: 18,
    },
    {
      id: 17,
      sku: "MI-0003",
      nombre: "Jabón de Ruda",
      categoria: "MI",
      material: null,
      subcategoria: "Cuidado personal",
      colecciones: [1, 6],
      piedra: null,
      precio_costo: 35,
      precio_menudeo: 75,
      precio_mayoreo: 60,
      estado: "disponible",
      stock: 25,
    },
    {
      id: 18,
      sku: "ES-0001",
      nombre: "Estampa Virgen de Guadalupe",
      categoria: "ES",
      material: null,
      subcategoria: "Estampa religiosa",
      colecciones: [1],
      piedra: null,
      precio_costo: 8,
      precio_menudeo: 20,
      precio_mayoreo: 15,
      estado: "disponible",
      stock: 50,
    },
  ],
  CLIENTES = [
    {
      id: 1,
      nombre: "María González Pérez",
      tipo: "mayoreo",
      telefono: "55 1234 5678",
      email: "maria.gp@email.com",
      saldo: 45200,
      limiteCredito: 8e4,
    },
    {
      id: 2,
      nombre: "Joyería El Diamante SA",
      tipo: "mayoreo",
      telefono: "55 9876 5432",
      email: "compras@eldiamante.mx",
      saldo: 0,
      limiteCredito: 2e5,
    },
    {
      id: 3,
      nombre: "Roberto Hernández",
      tipo: "menudeo",
      telefono: "55 5555 1234",
      email: "roberto.h@gmail.com",
      saldo: 0,
      limiteCredito: null,
    },
    {
      id: 4,
      nombre: "Ana Martínez",
      tipo: "menudeo",
      telefono: "55 4321 8765",
      email: "ana.mtz@outlook.com",
      saldo: 8500,
      limiteCredito: null,
    },
    {
      id: 5,
      nombre: "Distribuidora Oro Fino",
      tipo: "mayoreo",
      telefono: "33 1122 3344",
      email: "ventas@orofino.mx",
      saldo: 125e3,
      limiteCredito: 15e4,
    },
  ],
  REPARACIONES = [
    {
      id: 1,
      cliente: "María González",
      producto: "Anillo Oro 14K",
      servicio: "Ajuste talla",
      estado: "recibido",
      fecha: "2026-08-10",
      estimada: "2026-08-15",
    },
    {
      id: 2,
      cliente: "Roberto Hernández",
      producto: "Pulsera Tennis",
      servicio: "Cambio piedra",
      estado: "pendiente_taller",
      fecha: "2026-08-08",
      estimada: "2026-08-18",
    },
    {
      id: 3,
      cliente: "Ana Martínez",
      producto: "Collar Veneciano",
      servicio: "Limpieza profunda",
      estado: "en_proceso",
      fecha: "2026-08-05",
      estimada: "2026-08-12",
    },
    {
      id: 4,
      cliente: "Carlos López",
      producto: "Reloj Automático",
      servicio: "Restauración",
      estado: "terminado",
      fecha: "2026-08-01",
      estimada: "2026-08-10",
    },
    {
      id: 5,
      cliente: "Laura Sánchez",
      producto: "Aretes Esmeralda",
      servicio: "Engaste",
      estado: "enviado",
      fecha: "2026-08-06",
      estimada: "2026-08-16",
    },
  ],
  USUARIOS = [
    {
      id: 1,
      nombre: "Ana García",
      email: "ana.garcia@joyeria.mx",
      rol: "admin",
      sucursales: ["T01", "T02", "A01"],
      activo: !0,
      pin: "0000",
    },
    {
      id: 2,
      nombre: "Carlos Mendoza",
      email: "carlos.m@joyeria.mx",
      rol: "encargado",
      sucursales: ["T01"],
      activo: !0,
      pin: "1234",
    },
    {
      id: 3,
      nombre: "Laura Jiménez",
      email: "laura.j@joyeria.mx",
      rol: "encargado",
      sucursales: ["T02"],
      activo: !0,
      pin: "5678",
    },
    {
      id: 4,
      nombre: "Pedro Sánchez",
      email: "pedro.s@joyeria.mx",
      rol: "vendedor",
      sucursales: ["T01", "T02"],
      activo: !0,
      pin: "1111",
    },
    {
      id: 5,
      nombre: "María López",
      email: "maria.l@joyeria.mx",
      rol: "vendedor",
      sucursales: ["T01"],
      activo: !0,
      pin: "2222",
    },
    {
      id: 6,
      nombre: "Juan Ramírez",
      email: "juan.r@joyeria.mx",
      rol: "vendedor",
      sucursales: ["T02"],
      activo: !1,
      pin: "3333",
    },
  ],
  Icons = {
    Inventory: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
        }),
      ),
    POS: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("rect", {
          x: "2",
          y: "5",
          width: "20",
          height: "14",
          rx: "2",
        }),
        React.createElement("path", { d: "M2 10h20" }),
      ),
    Clients: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2",
        }),
        React.createElement("circle", { cx: "9", cy: "7", r: "4" }),
        React.createElement("path", { d: "M23 21v-2a4 4 0 0 0-3-3.87" }),
        React.createElement("path", { d: "M16 3.13a4 4 0 0 1 0 7.75" }),
      ),
    Repair: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
        }),
      ),
    Transfer: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M7 16V4m0 0L3 8m4-4l4 4m6 4v12m0 0l4-4m-4 4l-4-4",
        }),
      ),
    Reports: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", { d: "M18 20V10M12 20V4M6 20v-6" }),
      ),
    Settings: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("circle", { cx: "12", cy: "12", r: "3" }),
        React.createElement("path", {
          d: "M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z",
        }),
      ),
    Search: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("circle", { cx: "11", cy: "11", r: "8" }),
        React.createElement("path", { d: "M21 21l-4.35-4.35" }),
      ),
    Plus: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", { d: "M12 5v14M5 12h14" }),
      ),
    Diamond: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M2.7 10.3a2.4 2.4 0 0 0 0 3.4l8 8c.9.9 2.4.9 3.4 0l8-8a2.4 2.4 0 0 0 0-3.4l-8-8a2.4 2.4 0 0 0-3.4 0l-8 8z",
        }),
      ),
    Logout: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",
        }),
        React.createElement("polyline", { points: "16,17 21,12 16,7" }),
        React.createElement("line", { x1: "21", y1: "12", x2: "9", y2: "12" }),
      ),
    Cart: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("circle", { cx: "9", cy: "21", r: "1" }),
        React.createElement("circle", { cx: "20", cy: "21", r: "1" }),
        React.createElement("path", {
          d: "M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6",
        }),
      ),
    Trash: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("polyline", { points: "3,6 5,6 21,6" }),
        React.createElement("path", {
          d: "M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2",
        }),
      ),
    Check: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("polyline", { points: "20,6 9,17 4,12" }),
      ),
    Tag: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z",
        }),
        React.createElement("line", { x1: "7", y1: "7", x2: "7.01", y2: "7" }),
      ),
    Close: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("line", { x1: "18", y1: "6", x2: "6", y2: "18" }),
        React.createElement("line", { x1: "6", y1: "6", x2: "18", y2: "18" }),
      ),
    Percent: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("line", { x1: "19", y1: "5", x2: "5", y2: "19" }),
        React.createElement("circle", { cx: "6.5", cy: "6.5", r: "2.5" }),
        React.createElement("circle", { cx: "17.5", cy: "17.5", r: "2.5" }),
      ),
    CreditCard: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("rect", {
          x: "1",
          y: "4",
          width: "22",
          height: "16",
          rx: "2",
          ry: "2",
        }),
        React.createElement("line", { x1: "1", y1: "10", x2: "23", y2: "10" }),
      ),
    Users: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",
        }),
        React.createElement("circle", { cx: "9", cy: "7", r: "4" }),
        React.createElement("path", { d: "M22 21v-2a4 4 0 0 0-3-3.87" }),
        React.createElement("path", { d: "M16 3.13a4 4 0 0 1 0 7.75" }),
      ),
    Clipboard: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", {
          d: "M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2",
        }),
        React.createElement("rect", {
          x: "8",
          y: "2",
          width: "8",
          height: "4",
          rx: "1",
          ry: "1",
        }),
        React.createElement("path", { d: "M9 12h6" }),
        React.createElement("path", { d: "M9 16h6" }),
      ),
    Barcode: () =>
      React.createElement(
        "svg",
        { className: "icon", viewBox: "0 0 24 24" },
        React.createElement("path", { d: "M3 5v14" }),
        React.createElement("path", { d: "M6 5v14" }),
        React.createElement("path", { d: "M10 5v14" }),
        React.createElement("path", { d: "M13 5v14" }),
        React.createElement("path", { d: "M17 5v14" }),
        React.createElement("path", { d: "M21 5v14" }),
        React.createElement("path", { d: "M8 5v14" }),
        React.createElement("path", { d: "M15 5v14" }),
        React.createElement("path", { d: "M19 5v14" }),
      ),
  },
  formatMoney = (e) =>
    new Intl.NumberFormat("es-MX", {
      style: "currency",
      currency: "MXN",
    }).format(e),
  estadoPill = (e) =>
    ({
      disponible: "success",
      vendido: "muted",
      externo: "warning",
      baja: "danger",
      recibido: "gold",
      pendiente_taller: "warning",
      enviado: "muted",
      en_proceso: "success",
      terminado: "success",
      entregado: "muted",
    })[e] || "muted";
function LoginScreen({ onLogin: e }) {
  const [t, a] = useState("admin@joyeria.mx"),
    [l, n] = useState("demo"),
    [r, o] = useState("");
  return React.createElement(
    "div",
    {
      style: {
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--bg)",
      },
    },
    React.createElement(
      "div",
      { className: "card", style: { width: 380, padding: 32 } },
      React.createElement(
        "div",
        { style: { textAlign: "center", marginBottom: 32 } },
        React.createElement(
          "div",
          {
            style: {
              width: 48,
              height: 48,
              background: "var(--accent)",
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 16px",
              color: "white",
            },
          },
          React.createElement(Icons.Diamond, null),
        ),
        React.createElement(
          "h1",
          { style: { fontSize: 20, fontWeight: 600, marginBottom: 4 } },
          "Joyería SaaS",
        ),
        React.createElement(
          "p",
          { style: { color: "var(--muted)", fontSize: 13 } },
          "Sistema de Gestión Integral",
        ),
      ),
      React.createElement(
        "form",
        {
          onSubmit: (a) => {
            (a.preventDefault(),
              t
                ? e({
                    email: t,
                    rol: "admin",
                    nombre: "Carlos Mendoza",
                    sucursal: SUCURSALES[0],
                  })
                : o("Ingresa un email válido"));
          },
        },
        React.createElement(
          "div",
          { style: { marginBottom: 16 } },
          React.createElement(
            "label",
            {
              style: {
                display: "block",
                fontSize: 12,
                fontWeight: 500,
                marginBottom: 6,
                color: "var(--muted)",
              },
            },
            "Email",
          ),
          React.createElement("input", {
            type: "email",
            value: t,
            onChange: (e) => a(e.target.value),
            placeholder: "correo@empresa.com",
            style: { width: "100%" },
          }),
        ),
        React.createElement(
          "div",
          { style: { marginBottom: 20 } },
          React.createElement(
            "label",
            {
              style: {
                display: "block",
                fontSize: 12,
                fontWeight: 500,
                marginBottom: 6,
                color: "var(--muted)",
              },
            },
            "Contraseña",
          ),
          React.createElement("input", {
            type: "password",
            value: l,
            onChange: (e) => n(e.target.value),
            placeholder: "••••••••",
            style: { width: "100%" },
          }),
        ),
        r &&
          React.createElement(
            "p",
            {
              style: { color: "var(--danger)", fontSize: 13, marginBottom: 16 },
            },
            r,
          ),
        React.createElement(
          "button",
          {
            type: "submit",
            className: "btn-primary",
            style: { width: "100%" },
          },
          "Iniciar Sesión",
        ),
      ),
      React.createElement(
        "p",
        {
          style: {
            textAlign: "center",
            marginTop: 24,
            fontSize: 12,
            color: "var(--muted)",
          },
        },
        'Demo: haz clic en "Iniciar Sesión" para entrar',
      ),
    ),
  );
}
function Sidebar({ currentView: e, setView: t, user: a }) {
  const l = [
      {
        label: "Catálogo",
        items: [
          { id: "categories", label: "Clasificación", icon: Icons.Tag },
          { id: "inventory", label: "Inventario", icon: Icons.Inventory },
          {
            id: "physicalcount",
            label: "Conteo Físico",
            icon: Icons.Clipboard,
          },
        ],
      },
      {
        label: "Ventas",
        items: [
          { id: "pos", label: "Punto de Venta", icon: Icons.POS },
          { id: "sales", label: "Ventas", icon: Icons.Cart },
          { id: "clients", label: "Clientes", icon: Icons.Clients },
          { id: "credits", label: "Créditos", icon: Icons.CreditCard },
          { id: "promotions", label: "Promociones", icon: Icons.Percent },
        ],
      },
      {
        label: "Servicios",
        items: [
          { id: "repairs", label: "Reparaciones", icon: Icons.Repair },
          { id: "transfers", label: "Traspasos", icon: Icons.Transfer },
        ],
      },
      {
        label: "Sistema",
        items: [
          { id: "reports", label: "Reportes", icon: Icons.Reports },
          { id: "users", label: "Usuarios", icon: Icons.Users },
          { id: "settings", label: "Configuración", icon: Icons.Settings },
        ],
      },
    ],
    n = ({ item: a }) => {
      const l = a.icon,
        n = e === a.id;
      return React.createElement(
        "button",
        {
          onClick: () => t(a.id),
          style: {
            width: "100%",
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "10px 12px",
            borderRadius: 6,
            border: "none",
            background: n ? "var(--accent-light)" : "transparent",
            color: n ? "var(--accent)" : "var(--fg)",
            cursor: "pointer",
            marginBottom: 2,
            fontSize: 13,
            fontWeight: n ? 500 : 400,
            textAlign: "left",
          },
        },
        React.createElement(l, null),
        a.label,
      );
    };
  return React.createElement(
    "aside",
    {
      style: {
        width: "var(--sidebar-width)",
        height: "100vh",
        position: "fixed",
        left: 0,
        top: 0,
        background: "var(--surface)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
      },
    },
    React.createElement(
      "div",
      {
        style: {
          padding: "16px 20px",
          borderBottom: "1px solid var(--border)",
        },
      },
      React.createElement(
        "div",
        { style: { display: "flex", alignItems: "center", gap: 10 } },
        React.createElement(
          "div",
          {
            style: {
              width: 32,
              height: 32,
              background: "var(--accent)",
              borderRadius: 8,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
            },
          },
          React.createElement(Icons.Diamond, null),
        ),
        React.createElement(
          "div",
          null,
          React.createElement(
            "div",
            { style: { fontWeight: 600, fontSize: 14 } },
            "Joyería SaaS",
          ),
          React.createElement(
            "div",
            { style: { fontSize: 11, color: "var(--muted)" } },
            a.sucursal.nombre,
          ),
        ),
      ),
    ),
    React.createElement(
      "nav",
      { style: { flex: 1, padding: "12px 8px", overflowY: "auto" } },
      l.map((e, t) =>
        React.createElement(
          "div",
          { key: t, style: { marginBottom: e.label ? 8 : 0 } },
          e.label &&
            React.createElement(
              "div",
              {
                style: {
                  fontSize: 10,
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  color: "var(--muted)",
                  padding: "12px 12px 6px",
                  marginTop: t > 0 ? 8 : 0,
                },
              },
              e.label,
            ),
          e.items.map((e) => React.createElement(n, { key: e.id, item: e })),
        ),
      ),
    ),
    React.createElement(
      "div",
      { style: { padding: 12, borderTop: "1px solid var(--border)" } },
      React.createElement(
        "div",
        {
          style: {
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "8px 12px",
          },
        },
        React.createElement(
          "div",
          {
            style: {
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: "var(--border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 12,
              fontWeight: 600,
            },
          },
          a.nombre
            .split(" ")
            .map((e) => e[0])
            .join("")
            .slice(0, 2),
        ),
        React.createElement(
          "div",
          { style: { flex: 1, minWidth: 0 } },
          React.createElement(
            "div",
            {
              style: {
                fontSize: 13,
                fontWeight: 500,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              },
            },
            a.nombre,
          ),
          React.createElement(
            "div",
            {
              style: {
                fontSize: 11,
                color: "var(--muted)",
                textTransform: "capitalize",
              },
            },
            a.rol,
          ),
        ),
      ),
    ),
  );
}
function MainLayout({ children: e, title: t, actions: a }) {
  return React.createElement(
    "div",
    { style: { marginLeft: "var(--sidebar-width)", minHeight: "100vh" } },
    React.createElement(
      "header",
      {
        style: {
          height: "var(--header-height)",
          padding: "0 24px",
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          zIndex: 10,
        },
      },
      React.createElement(
        "h1",
        { style: { fontSize: 16, fontWeight: 600 } },
        t,
      ),
      a &&
        React.createElement("div", { style: { display: "flex", gap: 8 } }, a),
    ),
    React.createElement("main", { style: { padding: 24 } }, e),
  );
}
function AdminModalFrame({
  id,
  headingId,
  title,
  subtitle,
  onClose,
  width = 620,
  children,
}) {
  useEffect(() => {
    const handleEscape = (event) => event.key === "Escape" && onClose();
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [onClose]);
  return React.createElement(
    "div",
    {
      "data-od-id": id,
      role: "dialog",
      "aria-modal": "true",
      "aria-labelledby": headingId,
      onMouseDown: (event) => event.target === event.currentTarget && onClose(),
      style: {
        position: "fixed",
        inset: 0,
        padding: 16,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 120,
      },
    },
    React.createElement(
      "div",
      {
        className: "card",
        style: {
          width: `min(${width}px, calc(100vw - 32px))`,
          maxHeight: "90vh",
          overflow: "auto",
          padding: 0,
        },
      },
      React.createElement(
        "div",
        {
          style: {
            minHeight: 64,
            padding: "12px 16px 12px 24px",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 16,
          },
        },
        React.createElement(
          "div",
          null,
          React.createElement(
            "h2",
            {
              id: headingId,
              "data-od-id": headingId,
              style: { fontSize: 17, fontWeight: 600, textWrap: "balance" },
            },
            title,
          ),
          subtitle &&
            React.createElement(
              "p",
              {
                style: {
                  marginTop: 3,
                  color: "var(--muted)",
                  fontSize: 12,
                  textWrap: "pretty",
                },
              },
              subtitle,
            ),
        ),
        React.createElement(
          "button",
          {
            type: "button",
            className: "btn-ghost",
            "aria-label": `Cerrar ${title.toLowerCase()}`,
            onClick: onClose,
            style: {
              minWidth: 44,
              minHeight: 44,
              padding: 0,
              display: "grid",
              placeItems: "center",
            },
          },
          React.createElement(Icons.Close, null),
        ),
      ),
      children,
    ),
  );
}

function ProductEditModal({ product, onClose, onSave }) {
  const [form, setForm] = useState({
    nombre: "",
    precio_costo: "",
    precio_menudeo: "",
    precio_mayoreo: "",
    stock: "",
    estado: "disponible",
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    if (!product) return;
    setForm({
      nombre: product.nombre || "",
      precio_costo: String(product.precio_costo || 0),
      precio_menudeo: String(product.precio_menudeo || ""),
      precio_mayoreo: String(product.precio_mayoreo || ""),
      stock: String(product.stock || 0),
      estado: product.estado || "disponible",
    });
    setErrors({});
  }, [product?.id]);
  if (!product) return null;
  const hasVariants = product.tiene_variantes;
  const update = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: "" }));
  };
  const submit = async (event) => {
    event.preventDefault();
    const nextErrors = {};
    if (!form.nombre.trim())
      nextErrors.nombre = "Escribe el nombre del producto.";
    if (
      !hasVariants &&
      (!form.precio_menudeo || Number(form.precio_menudeo) <= 0)
    )
      nextErrors.precio_menudeo = "Define un precio mayor a cero.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    setSubmitting(true);
    try {
      await onSave({
        ...product,
        nombre: form.nombre.trim(),
        precio_costo: Math.max(0, Number(form.precio_costo) || 0),
        precio_menudeo: Number(form.precio_menudeo),
        precio_mayoreo:
          Number(form.precio_mayoreo) ||
          Math.round(Number(form.precio_menudeo) * 0.85),
        stock: product.stock,
        estado: form.estado,
      });
    } catch (error) {
      setErrors((current) => ({ ...current, submit: error.message }));
    } finally {
      setSubmitting(false);
    }
  };
  const field = (label, key, props = {}) =>
    React.createElement(
      "div",
      {
        className: "client-form-field",
        style: props.full ? { gridColumn: "1 / -1" } : null,
      },
      React.createElement(
        "label",
        { className: "client-form-label", htmlFor: `edit-product-${key}` },
        label,
      ),
      React.createElement("input", {
        id: `edit-product-${key}`,
        "data-od-id": `edit-product-${key}-input`,
        type: props.type || "text",
        min: props.min,
        step: props.step,
        value: form[key],
        onChange: (event) => update(key, event.target.value),
        "aria-invalid": Boolean(errors[key]),
        autoFocus: props.autoFocus,
      }),
      React.createElement(
        "span",
        { className: "client-form-error" },
        errors[key] || "",
      ),
    );
  return React.createElement(
    AdminModalFrame,
    {
      id: "edit-product-modal",
      headingId: "edit-product-heading",
      title: "Editar producto",
      subtitle: `Actualiza la información operativa de ${product.sku}.`,
      onClose,
      width: 660,
    },
    React.createElement(
      "form",
      { onSubmit: submit, noValidate: true },
      React.createElement(
        "div",
        { className: "client-form-grid", style: { padding: 24 } },
        React.createElement(
          "div",
          { className: "client-policy-row", style: { gridColumn: "1 / -1" } },
          React.createElement(
            "span",
            { className: "pill pill-accent mono" },
            product.sku,
          ),
          React.createElement(
            "span",
            null,
            hasVariants
              ? "Los precios se administran por variante."
              : "El precio corresponde al único SKU del producto.",
          ),
        ),
        field("Nombre del producto", "nombre", { full: true, autoFocus: true }),
        !hasVariants &&
          field("Costo", "precio_costo", {
            type: "number",
            min: "0",
            step: "0.01",
          }),
        !hasVariants &&
          field("Precio menudeo", "precio_menudeo", {
            type: "number",
            min: "0.01",
            step: "0.01",
          }),
        !hasVariants &&
          field("Precio mayoreo", "precio_mayoreo", {
            type: "number",
            min: "0",
            step: "0.01",
          }),
        React.createElement(
          "div",
          { className: "client-form-field" },
          React.createElement(
            "span",
            { className: "client-form-label" },
            "Existencias",
          ),
          React.createElement(
            "div",
            { className: "client-policy-row", style: { minHeight: 44 } },
            React.createElement(
              "span",
              { className: "tabular", style: { fontWeight: 600 } },
              product.stock,
            ),
            React.createElement(
              "span",
              null,
              "Usa Ajustar para registrar un movimiento por sucursal",
            ),
          ),
        ),
        React.createElement(
          "div",
          { className: "client-form-field" },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "edit-product-status" },
            "Estado",
          ),
          React.createElement(
            "select",
            {
              id: "edit-product-status",
              "data-od-id": "edit-product-status-select",
              value: form.estado,
              onChange: (event) => update("estado", event.target.value),
            },
            React.createElement(
              "option",
              { value: "disponible" },
              "Disponible",
            ),
            React.createElement("option", { value: "externo" }, "Externo"),
            React.createElement("option", { value: "baja" }, "Baja"),
          ),
        ),
      ),
      errors.submit &&
        React.createElement(
          "div",
          {
            className: "client-form-error",
            role: "alert",
            style: { padding: "0 24px 16px" },
          },
          errors.submit,
        ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          },
        },
        React.createElement(
          "button",
          {
            type: "button",
            className: "btn-secondary",
            onClick: onClose,
            style: { minHeight: 44 },
          },
          "Cancelar",
        ),
        React.createElement(
          "button",
          {
            "data-od-id": "save-product-edit-cta",
            type: "submit",
            className: "btn-primary",
            disabled: submitting,
            style: { minHeight: 44 },
          },
          submitting ? "Guardando…" : "Guardar cambios",
        ),
      ),
    ),
  );
}
function CollectionEditModal({ collection, onClose, onSave }) {
  const [name, setName] = useState("");
  const [active, setActive] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    if (!collection) return;
    setName(collection.nombre || "");
    setActive(collection.activa !== false);
    setError("");
  }, [collection?.id]);
  if (!collection) return null;
  return React.createElement(
    AdminModalFrame,
    {
      id: "edit-collection-modal",
      headingId: "edit-collection-heading",
      title: "Editar colección",
      subtitle: "Actualiza la etiqueta sin alterar los productos asociados.",
      onClose,
      width: 520,
    },
    React.createElement(
      "form",
      {
        onSubmit: async (event) => {
          event.preventDefault();
          if (!name.trim()) {
            setError("Escribe el nombre de la colección.");
            return;
          }
          setSubmitting(true);
          try {
            await onSave({
              ...collection,
              nombre: name.trim(),
              activa: active,
            });
          } catch (saveError) {
            setError(saveError.message);
          } finally {
            setSubmitting(false);
          }
        },
        noValidate: true,
      },
      React.createElement(
        "div",
        { style: { display: "grid", gap: 20, padding: 24 } },
        React.createElement(
          "div",
          { className: "client-form-field" },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "collection-name" },
            "Nombre de la colección",
          ),
          React.createElement("input", {
            id: "collection-name",
            "data-od-id": "collection-name-input",
            value: name,
            onChange: (event) => {
              setName(event.target.value);
              setError("");
            },
            autoFocus: true,
            "aria-invalid": Boolean(error),
          }),
          React.createElement(
            "span",
            { className: "client-form-error" },
            error,
          ),
        ),
        React.createElement(
          "div",
          { className: "client-form-field" },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "collection-status" },
            "Estado",
          ),
          React.createElement(
            "select",
            {
              id: "collection-status",
              "data-od-id": "collection-status-select",
              value: active ? "active" : "inactive",
              onChange: (event) => setActive(event.target.value === "active"),
            },
            React.createElement("option", { value: "active" }, "Activa"),
            React.createElement("option", { value: "inactive" }, "Inactiva"),
          ),
        ),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          },
        },
        React.createElement(
          "button",
          {
            type: "button",
            className: "btn-secondary",
            onClick: onClose,
            style: { minHeight: 44 },
          },
          "Cancelar",
        ),
        React.createElement(
          "button",
          {
            "data-od-id": "save-collection-cta",
            type: "submit",
            className: "btn-primary",
            disabled: submitting,
            style: { minHeight: 44 },
          },
          submitting ? "Guardando…" : "Guardar colección",
        ),
      ),
    ),
  );
}

function CatalogRecordModal({ kind, record, onClose, onSave }) {
  const isCategory = kind === "category";
  const isMaterial = kind === "material";
  const isSubcategory = kind === "subcategory";
  const [form, setForm] = useState({
    clave: "",
    nombre: "",
    grupo: "joyeria",
    requiereMaterial: true,
    activa: true,
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    if (!kind) return;
    setForm({
      clave: record?.clave || "",
      nombre: record?.nombre || "",
      grupo: record?.grupo || "joyeria",
      requiereMaterial: record?.requiereMaterial ?? true,
      activa: record?.activa !== false,
    });
    setError("");
  }, [kind, record?.id]);
  if (!kind) return null;
  const labels = {
    category: "categoría",
    material: "material",
    subcategory: "subcategoría",
  };
  const submit = async (event) => {
    event.preventDefault();
    if (!form.nombre.trim()) {
      setError("Escribe un nombre.");
      return;
    }
    if (!record && !isSubcategory && !form.clave.trim()) {
      setError("Escribe una clave.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await onSave({
        ...record,
        ...form,
        clave: form.clave.trim().toUpperCase(),
        nombre: form.nombre.trim(),
      });
      onClose();
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSubmitting(false);
    }
  };
  return React.createElement(
    AdminModalFrame,
    {
      id: `${kind}-record-modal`,
      headingId: `${kind}-record-heading`,
      title: record
        ? `Editar ${labels[kind]}`
        : `${isMaterial ? "Nuevo" : "Nueva"} ${labels[kind]}`,
      subtitle: record
        ? "Actualiza su nombre o disponibilidad sin cambiar su identidad."
        : isSubcategory
          ? "Organiza los productos de esta categoría sin alterar su SKU."
          : "La clave se utilizará como parte de la clasificación y los SKU.",
      onClose,
      width: 560,
    },
    React.createElement(
      "form",
      { onSubmit: submit, noValidate: true },
      React.createElement(
        "div",
        { className: "client-form-grid", style: { padding: 24 } },
        !isSubcategory &&
          React.createElement(
            "label",
            { className: "client-form-field" },
            React.createElement(
              "span",
              { className: "client-form-label" },
              "Clave",
            ),
            React.createElement("input", {
              className: "mono",
              maxLength: 4,
              disabled: Boolean(record),
              value: form.clave,
              onChange: (event) =>
                setForm((current) => ({
                  ...current,
                  clave: event.target.value,
                })),
            }),
          ),
        React.createElement(
          "label",
          {
            className: "client-form-field",
            style: isSubcategory ? { gridColumn: "1 / -1" } : null,
          },
          React.createElement(
            "span",
            { className: "client-form-label" },
            "Nombre",
          ),
          React.createElement("input", {
            autoFocus: true,
            value: form.nombre,
            onChange: (event) =>
              setForm((current) => ({
                ...current,
                nombre: event.target.value,
              })),
          }),
        ),
        isCategory &&
          React.createElement(
            "label",
            { className: "client-form-field" },
            React.createElement(
              "span",
              { className: "client-form-label" },
              "Grupo",
            ),
            React.createElement(
              "select",
              {
                disabled: Boolean(record),
                value: form.grupo,
                onChange: (event) =>
                  setForm((current) => ({
                    ...current,
                    grupo: event.target.value,
                  })),
              },
              React.createElement("option", { value: "joyeria" }, "Joyería"),
              React.createElement(
                "option",
                { value: "nojoyeria" },
                "No joyería",
              ),
            ),
          ),
        isCategory &&
          React.createElement(
            "label",
            { className: "client-form-field" },
            React.createElement(
              "span",
              { className: "client-form-label" },
              "¿Requiere material?",
            ),
            React.createElement(
              "select",
              {
                value: form.requiereMaterial ? "yes" : "no",
                onChange: (event) =>
                  setForm((current) => ({
                    ...current,
                    requiereMaterial: event.target.value === "yes",
                  })),
              },
              React.createElement("option", { value: "yes" }, "Sí"),
              React.createElement("option", { value: "no" }, "No"),
            ),
          ),
        record &&
          React.createElement(
            "label",
            { className: "client-form-field" },
            React.createElement(
              "span",
              { className: "client-form-label" },
              "Estado",
            ),
            React.createElement(
              "select",
              {
                disabled: isSubcategory && record.sistema,
                value: form.activa ? "active" : "inactive",
                onChange: (event) =>
                  setForm((current) => ({
                    ...current,
                    activa: event.target.value === "active",
                  })),
              },
              React.createElement("option", { value: "active" }, "Activo"),
              React.createElement("option", { value: "inactive" }, "Inactivo"),
            ),
          ),
        error &&
          React.createElement(
            "div",
            {
              className: "client-form-error",
              role: "alert",
              style: { gridColumn: "1 / -1" },
            },
            error,
          ),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          },
        },
        React.createElement(
          "button",
          { type: "button", className: "btn-secondary", onClick: onClose },
          "Cancelar",
        ),
        React.createElement(
          "button",
          { type: "submit", className: "btn-primary", disabled: submitting },
          submitting ? "Guardando…" : "Guardar",
        ),
      ),
    ),
  );
}

function VariantModal({
  product,
  variant,
  branches,
  canDeactivate = true,
  onClose,
  onSave,
}) {
  const creating = Boolean(product && !variant);
  const [form, setForm] = useState({
    valor: "",
    costo: "",
    menudeo: "",
    mayoreo: "",
    activa: true,
    stock: "0",
    branchId: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    if (!product) return;
    setForm({
      valor: variant?.talla_o_color || "",
      costo: String(variant?.precio_costo ?? ""),
      menudeo: String(variant?.precio_menudeo ?? ""),
      mayoreo: String(variant?.precio_mayoreo ?? ""),
      activa: variant?.estado !== "baja",
      stock: "0",
      branchId: "",
    });
    setError("");
  }, [product?.id, variant?.id]);
  if (!product) return null;
  const update = (key, value) =>
    setForm((current) => ({ ...current, [key]: value }));
  const submit = async (event) => {
    event.preventDefault();
    const stock = Number(form.stock);
    if (!form.valor.trim()) return setError("Escribe el valor de la variante.");
    if (!form.menudeo || Number(form.menudeo) <= 0)
      return setError("Define un precio de menudeo mayor a cero.");
    if (
      creating &&
      (form.stock === "" || !Number.isInteger(stock) || stock < 0)
    )
      return setError(
        "Las existencias deben ser un entero mayor o igual a cero.",
      );
    if (creating && stock > 0 && !form.branchId)
      return setError("Selecciona la sucursal para las existencias iniciales.");
    if (
      !creating &&
      variant?.estado !== "baja" &&
      !form.activa &&
      !canDeactivate
    )
      return setError("Debe quedar al menos una variante activa.");
    setSubmitting(true);
    setError("");
    try {
      await onSave({
        variant: {
          variant_value: form.valor.trim(),
          cost_price: String(Number(form.costo) || 0),
          retail_price: String(Number(form.menudeo)),
          wholesale_price: String(
            Number(form.mayoreo) || Math.round(Number(form.menudeo) * 0.85),
          ),
          ...(creating ? {} : { active: form.activa }),
        },
        stock,
        branchId: form.branchId,
      });
      onClose();
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSubmitting(false);
    }
  };
  return React.createElement(
    AdminModalFrame,
    {
      id: "variant-modal",
      headingId: "variant-modal-heading",
      title: creating ? "Agregar variante" : "Editar variante",
      subtitle: `${product.nombre} · ${product.tipo_variacion || "Variante"}`,
      onClose,
      width: 620,
    },
    React.createElement(
      "form",
      { onSubmit: submit, noValidate: true },
      React.createElement(
        "div",
        { className: "client-form-grid", style: { padding: 24 } },
        [
          ["Valor", "valor", "text"],
          ["Costo", "costo", "number"],
          ["Precio menudeo", "menudeo", "number"],
          ["Precio mayoreo", "mayoreo", "number"],
        ].map(([label, key, type]) =>
          React.createElement(
            "label",
            { key, className: "client-form-field" },
            React.createElement(
              "span",
              { className: "client-form-label" },
              label,
            ),
            React.createElement("input", {
              type,
              min: type === "number" ? "0" : undefined,
              step: type === "number" ? "0.01" : undefined,
              value: form[key],
              onChange: (event) => update(key, event.target.value),
            }),
          ),
        ),
        creating &&
          React.createElement(
            "label",
            { className: "client-form-field" },
            React.createElement(
              "span",
              { className: "client-form-label" },
              "Existencias iniciales",
            ),
            React.createElement("input", {
              type: "number",
              min: "0",
              step: "1",
              value: form.stock,
              onChange: (event) => update("stock", event.target.value),
            }),
          ),
        creating &&
          React.createElement(
            "label",
            { className: "client-form-field" },
            React.createElement(
              "span",
              { className: "client-form-label" },
              "Sucursal inicial",
            ),
            React.createElement(
              "select",
              {
                value: form.branchId,
                onChange: (event) => update("branchId", event.target.value),
              },
              React.createElement(
                "option",
                { value: "" },
                "Seleccionar si hay existencias",
              ),
              branches.map((branch) =>
                React.createElement(
                  "option",
                  {
                    key: branch.uuid || branch.id,
                    value: branch.uuid || branch.id,
                  },
                  branch.nombre || branch.name,
                ),
              ),
            ),
          ),
        !creating &&
          React.createElement(
            "label",
            { className: "client-form-field" },
            React.createElement(
              "span",
              { className: "client-form-label" },
              "Estado",
            ),
            React.createElement(
              "select",
              {
                value: form.activa ? "active" : "inactive",
                onChange: (event) =>
                  update("activa", event.target.value === "active"),
              },
              React.createElement("option", { value: "active" }, "Activa"),
              React.createElement(
                "option",
                { value: "inactive", disabled: !canDeactivate },
                "Inactiva",
              ),
            ),
          ),
        error &&
          React.createElement(
            "div",
            {
              className: "client-form-error",
              role: "alert",
              style: { gridColumn: "1 / -1" },
            },
            error,
          ),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          },
        },
        React.createElement(
          "button",
          { type: "button", className: "btn-secondary", onClick: onClose },
          "Cancelar",
        ),
        React.createElement(
          "button",
          { type: "submit", className: "btn-primary", disabled: submitting },
          submitting ? "Guardando…" : "Guardar variante",
        ),
      ),
    ),
  );
}

function PromotionModal({ promotion, onClose, onSave }) {
  const [form, setForm] = useState({
    nombre: "",
    tipo: "descuento",
    valor: "",
    minimo: "",
    regalo: "",
    categoria: "",
    inicio: "",
    fin: "",
    activa: true,
  });
  const [errors, setErrors] = useState({});
  useEffect(() => {
    if (!promotion) return;
    setForm({
      nombre: promotion.nombre || "",
      tipo: promotion.tipo || "descuento",
      valor: promotion.valor ? String(promotion.valor) : "",
      minimo: promotion.minimo ? String(promotion.minimo) : "",
      regalo: promotion.regalo || "",
      categoria: promotion.categoria || "",
      inicio: promotion.inicio || "",
      fin: promotion.fin || "",
      activa: promotion.activa !== false,
    });
    setErrors({});
  }, [promotion?.id, Boolean(promotion)]);
  if (!promotion) return null;
  const update = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: "" }));
  };
  const inputField = (label, key, props = {}) =>
    React.createElement(
      "div",
      {
        className: "client-form-field",
        style: props.full ? { gridColumn: "1 / -1" } : null,
      },
      React.createElement(
        "label",
        { className: "client-form-label", htmlFor: `promotion-${key}` },
        label,
      ),
      React.createElement("input", {
        id: `promotion-${key}`,
        "data-od-id": `promotion-${key}-input`,
        type: props.type || "text",
        inputMode: props.inputMode,
        placeholder: props.placeholder,
        value: form[key],
        onChange: (event) => update(key, event.target.value),
        autoFocus: props.autoFocus,
        "aria-invalid": Boolean(errors[key]),
      }),
      React.createElement(
        "span",
        { className: "client-form-error" },
        errors[key] || "",
      ),
    );
  const submit = (event) => {
    event.preventDefault();
    const nextErrors = {};
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    if (!form.nombre.trim())
      nextErrors.nombre = "Escribe un nombre reconocible.";
    if (!datePattern.test(form.inicio))
      nextErrors.inicio = "Usa el formato AAAA-MM-DD.";
    if (!datePattern.test(form.fin))
      nextErrors.fin = "Usa el formato AAAA-MM-DD.";
    if (!nextErrors.inicio && !nextErrors.fin && form.fin < form.inicio)
      nextErrors.fin = "La fecha final debe ser posterior al inicio.";
    if (
      form.tipo === "descuento" &&
      (Number(form.valor) <= 0 || Number(form.valor) > 100)
    )
      nextErrors.valor = "Define un porcentaje entre 1 y 100.";
    if (form.tipo === "regalo" && Number(form.minimo) <= 0)
      nextErrors.minimo = "Define el monto mínimo de compra.";
    if (form.tipo === "regalo" && !form.regalo.trim())
      nextErrors.regalo = "Escribe el SKU del regalo.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    onSave({
      ...promotion,
      nombre: form.nombre.trim(),
      tipo: form.tipo,
      valor: form.tipo === "descuento" ? Number(form.valor) : null,
      minimo: form.tipo === "regalo" ? Number(form.minimo) : null,
      regalo: form.tipo === "regalo" ? form.regalo.trim().toUpperCase() : null,
      categoria:
        form.tipo === "2x1" || form.tipo === "3x2"
          ? form.categoria || null
          : null,
      inicio: form.inicio,
      fin: form.fin,
      activa: form.activa,
      usada: promotion.usada || 0,
    });
  };
  return React.createElement(
    AdminModalFrame,
    {
      id: "promotion-modal",
      headingId: "promotion-heading",
      title: promotion.id ? "Editar promoción" : "Nueva promoción",
      subtitle: "Configura la regla, su alcance y el periodo de vigencia.",
      onClose,
      width: 680,
    },
    React.createElement(
      "form",
      { onSubmit: submit, noValidate: true },
      React.createElement(
        "div",
        { className: "client-form-grid", style: { padding: 24 } },
        inputField("Nombre de la promoción", "nombre", {
          full: true,
          autoFocus: true,
        }),
        React.createElement(
          "div",
          { className: "client-form-field" },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "promotion-type" },
            "Tipo",
          ),
          React.createElement(
            "select",
            {
              id: "promotion-type",
              "data-od-id": "promotion-type-select",
              value: form.tipo,
              onChange: (event) => update("tipo", event.target.value),
            },
            React.createElement(
              "option",
              { value: "descuento" },
              "Porcentaje de descuento",
            ),
            React.createElement("option", { value: "2x1" }, "2 × 1"),
            React.createElement("option", { value: "3x2" }, "3 × 2"),
            React.createElement(
              "option",
              { value: "regalo" },
              "Regalo por monto",
            ),
          ),
        ),
        React.createElement(
          "div",
          { className: "client-form-field" },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "promotion-active" },
            "Estado",
          ),
          React.createElement(
            "select",
            {
              id: "promotion-active",
              "data-od-id": "promotion-status-select",
              value: form.activa ? "active" : "inactive",
              onChange: (event) =>
                update("activa", event.target.value === "active"),
            },
            React.createElement("option", { value: "active" }, "Activa"),
            React.createElement("option", { value: "inactive" }, "Inactiva"),
          ),
        ),
        form.tipo === "descuento" &&
          inputField("Descuento (%)", "valor", {
            type: "number",
            inputMode: "decimal",
          }),
        (form.tipo === "2x1" || form.tipo === "3x2") &&
          React.createElement(
            "div",
            { className: "client-form-field" },
            React.createElement(
              "label",
              { className: "client-form-label", htmlFor: "promotion-category" },
              "Categoría",
            ),
            React.createElement(
              "select",
              {
                id: "promotion-category",
                "data-od-id": "promotion-category-select",
                value: form.categoria,
                onChange: (event) => update("categoria", event.target.value),
              },
              React.createElement(
                "option",
                { value: "" },
                "Todos los productos",
              ),
              CATEGORIAS.map((category) =>
                React.createElement(
                  "option",
                  { key: category.clave, value: category.clave },
                  `${category.clave} · ${category.nombre}`,
                ),
              ),
            ),
          ),
        form.tipo === "regalo" &&
          inputField("Compra mínima", "minimo", {
            type: "number",
            inputMode: "decimal",
          }),
        form.tipo === "regalo" &&
          inputField("SKU del regalo", "regalo", {
            placeholder: "Ej. AC-0001",
          }),
        inputField("Inicia", "inicio", { placeholder: "AAAA-MM-DD" }),
        inputField("Termina", "fin", { placeholder: "AAAA-MM-DD" }),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          },
        },
        React.createElement(
          "button",
          {
            type: "button",
            className: "btn-secondary",
            onClick: onClose,
            style: { minHeight: 44 },
          },
          "Cancelar",
        ),
        React.createElement(
          "button",
          {
            "data-od-id": "save-promotion-cta",
            type: "submit",
            className: "btn-primary",
            style: { minHeight: 44 },
          },
          promotion.id ? "Guardar cambios" : "Crear promoción",
        ),
      ),
    ),
  );
}

function BranchModal({ branch, onClose, onSave }) {
  const [form, setForm] = useState({
    nombre: "",
    tipo: "tienda",
    direccion: "",
    telefono: "",
  });
  const [errors, setErrors] = useState({});
  useEffect(() => {
    if (!branch) return;
    setForm({
      nombre: branch.nombre || "",
      tipo: branch.tipo || "tienda",
      direccion: branch.direccion || "",
      telefono: branch.telefono || "",
    });
    setErrors({});
  }, [branch?.id, Boolean(branch)]);
  if (!branch) return null;
  const update = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: "" }));
  };
  const submit = (event) => {
    event.preventDefault();
    const nextErrors = {};
    if (!form.nombre.trim())
      nextErrors.nombre = "Escribe el nombre de la sucursal.";
    if (!form.direccion.trim())
      nextErrors.direccion = "Escribe la dirección de operación.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    onSave({
      ...branch,
      nombre: form.nombre.trim(),
      tipo: form.tipo,
      direccion: form.direccion.trim(),
      telefono: form.telefono.trim(),
    });
  };
  return React.createElement(
    AdminModalFrame,
    {
      id: "branch-modal",
      headingId: "branch-heading",
      title: branch.id ? "Editar sucursal" : "Nueva sucursal",
      subtitle: branch.id
        ? `Actualiza la ubicación ${branch.id}.`
        : "El identificador se asignará automáticamente al guardar.",
      onClose,
      width: 620,
    },
    React.createElement(
      "form",
      { onSubmit: submit, noValidate: true },
      React.createElement(
        "div",
        { className: "client-form-grid", style: { padding: 24 } },
        React.createElement(
          "div",
          { className: "client-form-field", style: { gridColumn: "1 / -1" } },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "branch-name" },
            "Nombre",
          ),
          React.createElement("input", {
            id: "branch-name",
            "data-od-id": "branch-name-input",
            value: form.nombre,
            onChange: (event) => update("nombre", event.target.value),
            autoFocus: true,
            "aria-invalid": Boolean(errors.nombre),
          }),
          React.createElement(
            "span",
            { className: "client-form-error" },
            errors.nombre || "",
          ),
        ),
        React.createElement(
          "div",
          { className: "client-form-field" },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "branch-type" },
            "Tipo",
          ),
          React.createElement(
            "select",
            {
              id: "branch-type",
              "data-od-id": "branch-type-select",
              value: form.tipo,
              onChange: (event) => update("tipo", event.target.value),
            },
            React.createElement("option", { value: "tienda" }, "Tienda"),
            React.createElement("option", { value: "almacen" }, "Almacén"),
          ),
        ),
        React.createElement(
          "div",
          { className: "client-form-field" },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "branch-phone" },
            "Teléfono",
          ),
          React.createElement("input", {
            id: "branch-phone",
            "data-od-id": "branch-phone-input",
            type: "tel",
            placeholder: "55 1234 5678",
            value: form.telefono,
            onChange: (event) => update("telefono", event.target.value),
          }),
        ),
        React.createElement(
          "div",
          { className: "client-form-field", style: { gridColumn: "1 / -1" } },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "branch-address" },
            "Dirección",
          ),
          React.createElement("textarea", {
            id: "branch-address",
            "data-od-id": "branch-address-input",
            value: form.direccion,
            onChange: (event) => update("direccion", event.target.value),
            style: { minHeight: 80 },
            "aria-invalid": Boolean(errors.direccion),
          }),
          React.createElement(
            "span",
            { className: "client-form-error" },
            errors.direccion || "",
          ),
        ),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          },
        },
        React.createElement(
          "button",
          {
            type: "button",
            className: "btn-secondary",
            onClick: onClose,
            style: { minHeight: 44 },
          },
          "Cancelar",
        ),
        React.createElement(
          "button",
          {
            "data-od-id": "save-branch-cta",
            type: "submit",
            className: "btn-primary",
            style: { minHeight: 44 },
          },
          branch.id ? "Guardar cambios" : "Crear sucursal",
        ),
      ),
    ),
  );
}

const REPORT_DEFINITIONS = [
  {
    id: "sales",
    title: "Ventas por Periodo",
    desc: "Análisis de ventas diario, semanal y mensual",
  },
  {
    id: "inventory",
    title: "Inventario Valorizado",
    desc: "Valor total del inventario disponible",
  },
  {
    id: "products",
    title: "Top Productos",
    desc: "Productos más vendidos por unidades",
  },
  {
    id: "clients",
    title: "Clientes Activos",
    desc: "Clientes registrados con compras en el periodo",
  },
  {
    id: "receivables",
    title: "Cuentas por Cobrar",
    desc: "Estado general de saldos pendientes",
  },
  {
    id: "repairs",
    title: "Reparaciones",
    desc: "Órdenes por estado y fecha de entrega",
  },
];

function buildReportPreview(reportId, fromDate, toDate, branchId) {
  const branchName = SUCURSALES.find(
    (branch) => branch.id === branchId,
  )?.nombre;
  const sales = VENTAS_DEMO.filter(
    (sale) =>
      (!fromDate || sale.fecha >= fromDate) &&
      (!toDate || sale.fecha <= toDate) &&
      (!branchName || sale.sucursal === branchName),
  );
  if (reportId === "sales")
    return [
      {
        label: "Importe vendido",
        value: formatMoney(
          sales.reduce((sum, sale) => sum + getSaleTotal(sale), 0),
        ),
      },
      { label: "Operaciones", value: String(sales.length) },
      {
        label: "Ventas a crédito",
        value: String(
          sales.filter((sale) => sale.condicion === "credito").length,
        ),
      },
    ];
  if (reportId === "inventory")
    return [
      {
        label: "Costo del inventario",
        value: formatMoney(
          PRODUCTOS.reduce(
            (sum, product) => sum + product.precio_costo * product.stock,
            0,
          ),
        ),
      },
      {
        label: "Piezas en existencia",
        value: String(
          PRODUCTOS.reduce((sum, product) => sum + product.stock, 0),
        ),
      },
      {
        label: "Productos activos",
        value: String(
          PRODUCTOS.filter((product) => product.estado !== "baja").length,
        ),
      },
    ];
  if (reportId === "products") {
    const units = {};
    sales.forEach((sale) =>
      sale.items.forEach((item) => {
        units[item.nombre] = (units[item.nombre] || 0) + item.cantidad;
      }),
    );
    const ranking = Object.entries(units).sort(
      (left, right) => right[1] - left[1],
    );
    return [
      { label: "Producto líder", value: ranking[0]?.[0] || "Sin ventas" },
      { label: "Unidades del líder", value: String(ranking[0]?.[1] || 0) },
      { label: "Productos vendidos", value: String(ranking.length) },
    ];
  }
  if (reportId === "clients") {
    const registered = new Set(
      sales
        .filter((sale) => sale.cliente !== "Público general")
        .map((sale) => sale.cliente),
    );
    return [
      { label: "Clientes con compras", value: String(registered.size) },
      { label: "Clientes registrados", value: String(CLIENTES.length) },
      {
        label: "Ventas a público general",
        value: String(
          sales.filter((sale) => sale.cliente === "Público general").length,
        ),
      },
    ];
  }
  if (reportId === "receivables")
    return [
      {
        label: "Saldo pendiente",
        value: formatMoney(
          CLIENTES.reduce((sum, client) => sum + (client.saldo || 0), 0),
        ),
      },
      {
        label: "Clientes con saldo",
        value: String(CLIENTES.filter((client) => client.saldo > 0).length),
      },
      {
        label: "Líneas registradas",
        value: String(CLIENTES.filter((client) => client.limiteCredito).length),
      },
    ];
  const repairs = REPARACIONES.filter(
    (repair) =>
      (!fromDate || repair.fecha >= fromDate) &&
      (!toDate || repair.fecha <= toDate),
  );
  return [
    { label: "Reparaciones recibidas", value: String(repairs.length) },
    {
      label: "Terminadas",
      value: String(
        repairs.filter(
          (repair) =>
            repair.estado === "terminado" || repair.estado === "entregado",
        ).length,
      ),
    },
    {
      label: "Pendientes",
      value: String(
        repairs.filter(
          (repair) =>
            repair.estado !== "terminado" && repair.estado !== "entregado",
        ).length,
      ),
    },
  ];
}

function ReportModal({ report, onClose }) {
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [branchId, setBranchId] = useState("");
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    if (report) {
      setFromDate("");
      setToDate("");
      setBranchId("");
      setPreview(null);
      setError("");
    }
  }, [report?.id]);
  if (!report) return null;
  const generate = (event) => {
    event.preventDefault();
    const pattern = /^\d{4}-\d{2}-\d{2}$/;
    if (
      (fromDate && !pattern.test(fromDate)) ||
      (toDate && !pattern.test(toDate))
    ) {
      setError("Escribe las fechas con el formato AAAA-MM-DD.");
      return;
    }
    if (fromDate && toDate && fromDate > toDate) {
      setError("La fecha inicial debe ser anterior a la fecha final.");
      return;
    }
    setError("");
    setPreview(buildReportPreview(report.id, fromDate, toDate, branchId));
  };
  return React.createElement(
    AdminModalFrame,
    {
      id: "report-modal",
      headingId: "report-heading",
      title: report.title,
      subtitle: report.desc,
      onClose,
      width: 720,
    },
    React.createElement(
      "form",
      { onSubmit: generate, noValidate: true },
      React.createElement(
        "div",
        { style: { display: "grid", gap: 20, padding: 24 } },
        React.createElement(
          "div",
          { className: "client-policy-row" },
          React.createElement(
            "span",
            { className: "pill pill-muted" },
            "Demostración",
          ),
          React.createElement(
            "span",
            null,
            "La vista previa utiliza únicamente los datos disponibles dentro de este prototipo.",
          ),
        ),
        React.createElement(
          "div",
          { className: "client-form-grid" },
          React.createElement(
            "div",
            { className: "client-form-field" },
            React.createElement(
              "label",
              { className: "client-form-label", htmlFor: "report-from" },
              "Desde",
            ),
            React.createElement("input", {
              id: "report-from",
              "data-od-id": "report-from-input",
              placeholder: "AAAA-MM-DD",
              value: fromDate,
              onChange: (event) => {
                setFromDate(event.target.value);
                setPreview(null);
              },
            }),
          ),
          React.createElement(
            "div",
            { className: "client-form-field" },
            React.createElement(
              "label",
              { className: "client-form-label", htmlFor: "report-to" },
              "Hasta",
            ),
            React.createElement("input", {
              id: "report-to",
              "data-od-id": "report-to-input",
              placeholder: "AAAA-MM-DD",
              value: toDate,
              onChange: (event) => {
                setToDate(event.target.value);
                setPreview(null);
              },
            }),
          ),
          React.createElement(
            "div",
            { className: "client-form-field", style: { gridColumn: "1 / -1" } },
            React.createElement(
              "label",
              { className: "client-form-label", htmlFor: "report-branch" },
              "Sucursal",
            ),
            React.createElement(
              "select",
              {
                id: "report-branch",
                "data-od-id": "report-branch-select",
                value: branchId,
                onChange: (event) => {
                  setBranchId(event.target.value);
                  setPreview(null);
                },
              },
              React.createElement(
                "option",
                { value: "" },
                "Todas las sucursales",
              ),
              SUCURSALES.map((branch) =>
                React.createElement(
                  "option",
                  { key: branch.id, value: branch.id },
                  branch.nombre,
                ),
              ),
            ),
          ),
        ),
        error &&
          React.createElement(
            "div",
            { className: "client-form-error", role: "alert" },
            error,
          ),
        preview &&
          React.createElement(
            "div",
            {
              "data-od-id": "report-preview",
              style: {
                display: "grid",
                gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                gap: 12,
              },
            },
            preview.map((metric) =>
              React.createElement(
                "div",
                {
                  key: metric.label,
                  className: "card",
                  style: { padding: 16, background: "var(--bg)" },
                },
                React.createElement(
                  "div",
                  {
                    style: {
                      color: "var(--muted)",
                      fontSize: 11,
                      marginBottom: 6,
                    },
                  },
                  metric.label,
                ),
                React.createElement(
                  "div",
                  {
                    className: "tabular",
                    style: { fontWeight: 600, overflowWrap: "anywhere" },
                  },
                  metric.value,
                ),
              ),
            ),
          ),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          },
        },
        React.createElement(
          "button",
          {
            type: "button",
            className: "btn-secondary",
            onClick: onClose,
            style: { minHeight: 44 },
          },
          "Cerrar",
        ),
        React.createElement(
          "button",
          {
            "data-od-id": "generate-report-cta",
            type: "submit",
            className: "btn-primary",
            style: { minHeight: 44 },
          },
          preview ? "Actualizar reporte" : "Generar reporte",
        ),
      ),
    ),
  );
}

function InventoryAdjustmentModal({ product, branches, onClose, onSave }) {
  const [variantId, setVariantId] = useState("");
  const [branchId, setBranchId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [reference, setReference] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!product) return;
    setVariantId(
      String(
        product.variantes?.find((variant) => variant.estado !== "baja")?.id ||
          "",
      ),
    );
    setBranchId(String(branches[0]?.uuid || branches[0]?.id || ""));
    setQuantity("");
    setReference("");
    setNote("");
    setError("");
  }, [product?.id]);

  if (!product) return null;
  const submit = async (event) => {
    event.preventDefault();
    const parsedQuantity = Number(quantity);
    if (
      !variantId ||
      !branchId ||
      !Number.isInteger(parsedQuantity) ||
      parsedQuantity === 0
    ) {
      setError(
        "Selecciona variante y sucursal, e ingresa una cantidad entera distinta de cero.",
      );
      return;
    }
    if (!note.trim()) {
      setError("Describe el motivo del ajuste.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await onSave({
        variant_id: Number(variantId),
        branch_id: branchId,
        quantity: parsedQuantity,
        reference: reference.trim() || null,
        note: note.trim(),
      });
      onClose();
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSubmitting(false);
    }
  };

  return React.createElement(
    AdminModalFrame,
    {
      id: "inventory-adjustment-modal",
      headingId: "inventory-adjustment-heading",
      title: "Ajustar inventario",
      subtitle: `${product.nombre} · el movimiento quedará auditado.`,
      onClose,
      width: 560,
    },
    React.createElement(
      "form",
      { onSubmit: submit, noValidate: true },
      React.createElement(
        "div",
        { style: { display: "grid", gap: 16, padding: 24 } },
        React.createElement(
          "label",
          { className: "client-form-field" },
          React.createElement(
            "span",
            { className: "client-form-label" },
            "Variante / SKU",
          ),
          React.createElement(
            "select",
            {
              value: variantId,
              onChange: (event) => setVariantId(event.target.value),
            },
            (product.variantes || [])
              .filter((variant) => variant.estado !== "baja")
              .map((variant) =>
                React.createElement(
                  "option",
                  { key: variant.id, value: variant.id },
                  `${variant.sku}${variant.talla_o_color ? ` · ${variant.talla_o_color}` : ""}`,
                ),
              ),
          ),
        ),
        React.createElement(
          "label",
          { className: "client-form-field" },
          React.createElement(
            "span",
            { className: "client-form-label" },
            "Sucursal",
          ),
          React.createElement(
            "select",
            {
              value: branchId,
              onChange: (event) => setBranchId(event.target.value),
            },
            branches.map((branch) =>
              React.createElement(
                "option",
                {
                  key: branch.uuid || branch.id,
                  value: branch.uuid || branch.id,
                },
                branch.nombre || branch.name,
              ),
            ),
          ),
        ),
        React.createElement(
          "label",
          { className: "client-form-field" },
          React.createElement(
            "span",
            { className: "client-form-label" },
            "Cantidad (+ entrada / - salida)",
          ),
          React.createElement("input", {
            type: "number",
            step: "1",
            value: quantity,
            onChange: (event) => setQuantity(event.target.value),
            placeholder: "Ej. 2 o -1",
          }),
        ),
        React.createElement(
          "label",
          { className: "client-form-field" },
          React.createElement(
            "span",
            { className: "client-form-label" },
            "Referencia (opcional)",
          ),
          React.createElement("input", {
            value: reference,
            maxLength: 60,
            onChange: (event) => setReference(event.target.value),
          }),
        ),
        React.createElement(
          "label",
          { className: "client-form-field" },
          React.createElement(
            "span",
            { className: "client-form-label" },
            "Motivo",
          ),
          React.createElement("input", {
            value: note,
            maxLength: 255,
            onChange: (event) => setNote(event.target.value),
            placeholder: "Ej. Diferencia confirmada en conteo",
          }),
        ),
        error &&
          React.createElement(
            "div",
            { className: "client-form-error", role: "alert" },
            error,
          ),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          },
        },
        React.createElement(
          "button",
          { type: "button", className: "btn-secondary", onClick: onClose },
          "Cancelar",
        ),
        React.createElement(
          "button",
          { type: "submit", className: "btn-primary", disabled: submitting },
          submitting ? "Registrando…" : "Registrar ajuste",
        ),
      ),
    ),
  );
}

function InventoryView({
  productos: PRODUCTOS = [],
  categorias: CATEGORIAS = [],
  materiales: MATERIALES = [],
  subcategorias: SUBCATEGORIAS_SEED = {},
  colecciones: COLECCIONES_SEED = [],
  sucursales = [],
  currentUser,
  actions = {},
}) {
  const [e, t] = useState(""),
    [a, l] = useState("all"),
    [n, r] = useState("all"),
    [o, c] = useState(PRODUCTOS),
    [i, s] = useState(!1),
    [m, d] = useState(""),
    [u, p] = useState({
      categoria: "",
      material: "",
      nombre: "",
      subcategoria: "",
      subcategoriaSugerida: "",
      precio_costo: "",
      precio_menudeo: "",
      precio_mayoreo: "",
      stock: "1",
      branchId: "",
      piedra: "",
      imagen: null,
    }),
    [g, y] = useState(null),
    [R, E] = useState({}),
    [v, b] = useState(!1),
    [f, h] = useState("Talla"),
    [C, S] = useState([
      { id: 1, valor: "", stock: "1", precio_menudeo: "", precio_mayoreo: "" },
    ]),
    [x, k] = useState(null),
    [editProduct, setEditProduct] = useState(null),
    w = (e) => CATEGORIAS.find((t) => t.clave === e)?.grupo,
    requiresMaterial = (e) =>
      Boolean(CATEGORIAS.find((t) => t.clave === e)?.requiereMaterial),
    I = (e) => CATEGORIAS.find((t) => t.clave === e)?.nombre || e,
    B = (e) => MATERIALES.find((t) => t.clave === e)?.nombre || e,
    A = u.categoria && requiresMaterial(u.categoria),
    T = u.categoria && "nojoyeria" === w(u.categoria),
    M = u.categoria
      ? `${u.categoria}-${A ? u.material + "-" : ""}${String((skuCounters[u.categoria] || 0) + 1).padStart(4, "0")}`
      : "",
    j = {
      Talla: "Ej. 6",
      Color: "Ej. Dorado",
      Medida: "Ej. 45 cm",
      Presentación: "Ej. 30 ml",
    }[f],
    P = m ? CATEGORIAS.filter((e) => e.grupo === m && e.activa !== false) : [],
    activeJewelryCategoryCount = CATEGORIAS.filter(
      (category) => category.grupo === "joyeria" && category.activa !== false,
    ).length,
    activeNonJewelryCategoryCount = CATEGORIAS.filter(
      (category) => category.grupo === "nojoyeria" && category.activa !== false,
    ).length,
    W =
      T && SUBCATEGORIAS_SEED[u.categoria]
        ? SUBCATEGORIAS_SEED[u.categoria].filter((e) => e.activa)
        : [],
    _ = (e, t, a) => {
      S((l) =>
        l.map((l) => {
          if (l.id !== e) return l;
          if ("precio_menudeo" === t) {
            const e = parseFloat(a) || 0;
            return {
              ...l,
              precio_menudeo: a,
              precio_mayoreo: e > 0 ? String(Math.round(0.85 * e)) : "",
            };
          }
          return { ...l, [t]: a };
        }),
      );
    },
    D = () => {
      (s(!1),
        d(""),
        p({
          categoria: "",
          material: "",
          nombre: "",
          subcategoria: "",
          subcategoriaSugerida: "",
          precio_costo: "",
          precio_menudeo: "",
          precio_mayoreo: "",
          stock: "1",
          branchId: "",
          piedra: "",
          imagen: null,
        }),
        y(null),
        b(!1),
        h("Talla"),
        S([
          {
            id: 1,
            valor: "",
            stock: "1",
            precio_menudeo: "",
            precio_mayoreo: "",
          },
        ]),
        E({}));
    },
    O = o.filter((t) => {
      const l = e.toLowerCase(),
        r =
          t.nombre.toLowerCase().includes(l) ||
          t.sku.toLowerCase().includes(l) ||
          (t.variantes || []).some(
            (e) =>
              e.sku.toLowerCase().includes(l) ||
              e.talla_o_color.toLowerCase().includes(l),
          ),
        o = "all" === a || w(t.categoria) === a,
        c = "all" === n || t.estado === n;
      return r && o && c;
    });
  const [savingProduct, setSavingProduct] = useState(false);
  const [adjustmentProduct, setAdjustmentProduct] = useState(null);
  const [variantModal, setVariantModal] = useState(null);
  const [imageSaving, setImageSaving] = useState(false);
  const [imageError, setImageError] = useState("");
  const [inventoryError, setInventoryError] = useState("");
  const canManageProducts = currentUser?.rol === "admin";
  const canAdjustInventory = ["admin", "encargado"].includes(currentUser?.rol);
  useEffect(() => c(PRODUCTOS), [PRODUCTOS]);
  return React.createElement(
    MainLayout,
    {
      title: "Inventario",
      actions:
        canManageProducts &&
        React.createElement(
          "button",
          {
            "data-od-id": "new-product-cta",
            className: "btn-primary",
            onClick: () => s(!0),
            style: {
              minHeight: 44,
              display: "flex",
              alignItems: "center",
              gap: 6,
            },
          },
          React.createElement(Icons.Plus, null),
          " Nuevo Producto",
        ),
    },
    inventoryError &&
      React.createElement(
        "div",
        {
          className: "client-form-error",
          role: "alert",
          style: { marginBottom: 16 },
        },
        inventoryError,
      ),
    React.createElement(
      "div",
      { className: "card", "data-od-id": "inventory-table" },
      React.createElement(
        "div",
        {
          style: {
            padding: 16,
            borderBottom: "1px solid var(--border)",
            display: "flex",
            gap: 12,
          },
        },
        React.createElement(
          "div",
          { style: { position: "relative", flex: 1 } },
          React.createElement("input", {
            type: "text",
            placeholder: "Buscar por SKU, nombre...",
            value: e,
            onChange: (e) => t(e.target.value),
            style: { width: "100%", paddingLeft: 36 },
          }),
          React.createElement(
            "div",
            {
              style: {
                position: "absolute",
                left: 10,
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--muted)",
              },
            },
            React.createElement(Icons.Search, null),
          ),
        ),
        React.createElement(
          "select",
          {
            value: a,
            onChange: (e) => l(e.target.value),
            style: { width: 140 },
          },
          React.createElement("option", { value: "all" }, "Todos"),
          React.createElement("option", { value: "joyeria" }, "Joyería"),
          React.createElement("option", { value: "nojoyeria" }, "No Joyería"),
        ),
        React.createElement(
          "select",
          {
            value: n,
            onChange: (e) => r(e.target.value),
            style: { width: 140 },
          },
          React.createElement("option", { value: "all" }, "Todos los estados"),
          React.createElement("option", { value: "disponible" }, "Disponible"),
          React.createElement("option", { value: "vendido" }, "Vendido"),
          React.createElement("option", { value: "externo" }, "Externo"),
          React.createElement("option", { value: "baja" }, "Baja"),
        ),
      ),
      React.createElement(
        "table",
        null,
        React.createElement(
          "thead",
          null,
          React.createElement(
            "tr",
            null,
            React.createElement("th", { style: { width: 50 } }),
            React.createElement("th", null, "SKU"),
            React.createElement("th", null, "Producto"),
            React.createElement("th", null, "Categoría"),
            React.createElement("th", null, "Material"),
            React.createElement("th", null, "Subcategoría"),
            React.createElement(
              "th",
              { style: { textAlign: "right" } },
              "Menudeo",
            ),
            React.createElement("th", null, "Estado"),
            React.createElement(
              "th",
              { style: { textAlign: "center" } },
              "Stock",
            ),
            React.createElement("th", { style: { width: 60 } }),
          ),
        ),
        React.createElement(
          "tbody",
          null,
          O.map((e) =>
            React.createElement(
              "tr",
              { key: e.id },
              React.createElement(
                "td",
                { style: { padding: "6px 12px" } },
                e.imagen
                  ? React.createElement("img", {
                      src: e.imagen,
                      alt: e.nombre,
                      style: {
                        width: 40,
                        height: 40,
                        objectFit: "cover",
                        borderRadius: 6,
                      },
                    })
                  : React.createElement(
                      "div",
                      {
                        style: {
                          width: 40,
                          height: 40,
                          borderRadius: 6,
                          background:
                            "joyeria" === w(e.categoria)
                              ? "var(--gold-bg)"
                              : "var(--border)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color:
                            "joyeria" === w(e.categoria)
                              ? "var(--gold)"
                              : "var(--muted)",
                        },
                      },
                      React.createElement(Icons.Diamond, null),
                    ),
              ),
              React.createElement(
                "td",
                { className: "mono", style: { color: "var(--accent)" } },
                e.sku,
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "div",
                  { style: { fontWeight: 500 } },
                  e.nombre,
                ),
                e.piedra &&
                  React.createElement(
                    "div",
                    { style: { fontSize: 12, color: "var(--muted)" } },
                    e.piedra,
                  ),
                e.tiene_variantes &&
                  React.createElement(
                    "div",
                    { style: { marginTop: 4 } },
                    React.createElement(
                      "span",
                      { className: "pill pill-accent" },
                      e.variantes.length,
                      " variaciones",
                    ),
                  ),
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "span",
                  {
                    className:
                      "pill " +
                      ("joyeria" === w(e.categoria)
                        ? "pill-gold"
                        : "pill-accent"),
                    style: { marginRight: 6 },
                  },
                  e.categoria,
                ),
                React.createElement(
                  "span",
                  { style: { fontSize: 12 } },
                  I(e.categoria),
                ),
              ),
              React.createElement(
                "td",
                { style: { color: e.material ? "inherit" : "var(--muted)" } },
                e.material ? B(e.material) : "—",
              ),
              React.createElement(
                "td",
                {
                  style: {
                    color: e.subcategoria ? "inherit" : "var(--muted)",
                    fontSize: 12,
                  },
                },
                e.subcategoria || "—",
              ),
              React.createElement(
                "td",
                { style: { textAlign: "right" }, className: "tabular" },
                e.tiene_variantes &&
                  React.createElement(
                    "span",
                    { style: { color: "var(--muted)", marginRight: 4 } },
                    "Desde",
                  ),
                formatMoney(e.precio_menudeo),
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "span",
                  { className: `pill pill-${estadoPill(e.estado)}` },
                  e.estado,
                ),
              ),
              React.createElement(
                "td",
                { style: { textAlign: "center" }, className: "tabular" },
                e.stock,
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "button",
                  {
                    className: "btn-ghost",
                    onClick: () => k(e),
                    style: { padding: "4px 8px", fontSize: 11 },
                  },
                  "Ver",
                ),
                canAdjustInventory &&
                  e.estado !== "baja" &&
                  e.variantes?.some((variant) => variant.estado !== "baja") &&
                  React.createElement(
                    "button",
                    {
                      className: "btn-ghost",
                      onClick: () => setAdjustmentProduct(e),
                      style: { padding: "4px 8px", fontSize: 11 },
                    },
                    "Ajustar",
                  ),
              ),
            ),
          ),
        ),
      ),
    ),
    x &&
      React.createElement(
        "div",
        {
          "data-od-id": "product-detail-modal",
          style: {
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          },
        },
        React.createElement(
          "div",
          {
            className: "card",
            style: {
              width: x.tiene_variantes ? 820 : 500,
              maxWidth: "calc(100vw - 32px)",
              maxHeight: "90vh",
              overflow: "auto",
              padding: 0,
            },
          },
          React.createElement(
            "div",
            {
              style: {
                padding: "16px 24px",
                borderBottom: "1px solid var(--border)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              },
            },
            React.createElement(
              "h3",
              { style: { fontSize: 16, fontWeight: 600 } },
              "Detalle del Producto",
            ),
            React.createElement(
              "button",
              { className: "btn-ghost", onClick: () => k(null) },
              React.createElement(Icons.Close, null),
            ),
          ),
          React.createElement(
            "div",
            { style: { padding: 24 } },
            React.createElement(
              "div",
              { style: { display: "flex", gap: 16, marginBottom: 20 } },
              React.createElement(
                "div",
                { style: { position: "relative" } },
                x.imagen
                  ? React.createElement("img", {
                      src: x.imagen,
                      alt: x.nombre,
                      style: {
                        width: 100,
                        height: 100,
                        objectFit: "cover",
                        borderRadius: 8,
                        border: "1px solid var(--border)",
                      },
                    })
                  : React.createElement(
                      "div",
                      {
                        style: {
                          width: 100,
                          height: 100,
                          borderRadius: 8,
                          background:
                            "joyeria" === w(x.categoria)
                              ? "var(--gold-bg)"
                              : "var(--bg)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color:
                            "joyeria" === w(x.categoria)
                              ? "var(--gold)"
                              : "var(--muted)",
                          border: "1px solid var(--border)",
                        },
                      },
                      React.createElement(Icons.Diamond, null),
                    ),
                canManageProducts &&
                  React.createElement(
                    "label",
                    {
                      title: x.imagen ? "Reemplazar imagen" : "Agregar imagen",
                      style: {
                        position: "absolute",
                        bottom: -8,
                        right: -8,
                        width: 28,
                        height: 28,
                        borderRadius: "50%",
                        background: "var(--accent)",
                        color: "white",
                        border: "none",
                        cursor: imageSaving ? "wait" : "pointer",
                        opacity: imageSaving ? 0.6 : 1,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 12,
                        boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
                      },
                    },
                    React.createElement(Icons.Plus, null),
                    React.createElement("input", {
                      type: "file",
                      accept: "image/jpeg,image/png,image/webp",
                      disabled: imageSaving,
                      onChange: async (event) => {
                        const file = event.target.files?.[0];
                        event.target.value = "";
                        const validationError = validateProductImage(file);
                        if (validationError) {
                          setImageError(validationError);
                          return;
                        }
                        const previousImage = x.imagen;
                        const preview = URL.createObjectURL(file);
                        setImageError("");
                        setImageSaving(true);
                        k((current) => ({ ...current, imagen: preview }));
                        try {
                          await actions.uploadProductImage(x.id, file);
                          c((current) =>
                            current.map((product) =>
                              product.id === x.id
                                ? { ...product, imagen: preview }
                                : product,
                            ),
                          );
                        } catch (error) {
                          URL.revokeObjectURL(preview);
                          k((current) => ({
                            ...current,
                            imagen: previousImage,
                          }));
                          setImageError(error.message);
                        } finally {
                          setImageSaving(false);
                        }
                      },
                      style: { display: "none" },
                    }),
                  ),
                canManageProducts &&
                  x.imagen &&
                  React.createElement(
                    "button",
                    {
                      type: "button",
                      title: "Eliminar imagen",
                      disabled: imageSaving,
                      onClick: async () => {
                        setImageError("");
                        setImageSaving(true);
                        try {
                          await actions.deleteProductImage(x.id);
                          c((current) =>
                            current.map((product) =>
                              product.id === x.id
                                ? { ...product, imagen: null }
                                : product,
                            ),
                          );
                          k((current) => ({ ...current, imagen: null }));
                        } catch (error) {
                          setImageError(error.message);
                        } finally {
                          setImageSaving(false);
                        }
                      },
                      style: {
                        position: "absolute",
                        bottom: -8,
                        left: -8,
                        width: 28,
                        height: 28,
                        padding: 0,
                        display: "grid",
                        placeItems: "center",
                        color: "white",
                        background: "var(--danger)",
                        borderRadius: "50%",
                      },
                    },
                    React.createElement(Icons.Trash, null),
                  ),
              ),
              React.createElement(
                "div",
                {
                  style: {
                    flex: 1,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  },
                },
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "div",
                    {
                      className: "mono",
                      style: {
                        fontSize: 18,
                        color: "var(--accent)",
                        fontWeight: 600,
                      },
                    },
                    x.sku,
                  ),
                  React.createElement(
                    "div",
                    { style: { fontSize: 16, fontWeight: 500, marginTop: 4 } },
                    x.nombre,
                  ),
                  x.piedra &&
                    React.createElement(
                      "div",
                      {
                        style: {
                          fontSize: 13,
                          color: "var(--muted)",
                          marginTop: 2,
                        },
                      },
                      x.piedra,
                    ),
                ),
                React.createElement(
                  "span",
                  { className: `pill pill-${estadoPill(x.estado)}` },
                  x.estado,
                ),
              ),
            ),
            imageSaving &&
              React.createElement(
                "div",
                {
                  style: {
                    marginTop: -12,
                    marginBottom: 16,
                    color: "var(--muted)",
                    fontSize: 11,
                  },
                },
                "Actualizando imagen…",
              ),
            imageError &&
              React.createElement(
                "div",
                {
                  className: "client-form-error",
                  role: "alert",
                  style: { marginTop: -12, marginBottom: 16 },
                },
                imageError,
              ),
            React.createElement(
              "div",
              {
                style: {
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 16,
                  marginBottom: 20,
                },
              },
              React.createElement(
                "div",
                {
                  style: {
                    padding: 12,
                    background: "var(--bg)",
                    borderRadius: 6,
                  },
                },
                React.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 11,
                      color: "var(--muted)",
                      marginBottom: 4,
                    },
                  },
                  "Categoría",
                ),
                React.createElement(
                  "div",
                  { style: { display: "flex", alignItems: "center", gap: 6 } },
                  React.createElement(
                    "span",
                    {
                      className:
                        "pill " +
                        ("joyeria" === w(x.categoria)
                          ? "pill-gold"
                          : "pill-accent"),
                    },
                    x.categoria,
                  ),
                  React.createElement(
                    "span",
                    { style: { fontSize: 13 } },
                    I(x.categoria),
                  ),
                ),
              ),
              React.createElement(
                "div",
                {
                  style: {
                    padding: 12,
                    background: "var(--bg)",
                    borderRadius: 6,
                  },
                },
                React.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 11,
                      color: "var(--muted)",
                      marginBottom: 4,
                    },
                  },
                  requiresMaterial(x.categoria) ? "Material" : "Subcategoría",
                ),
                React.createElement(
                  "div",
                  { style: { fontSize: 13 } },
                  requiresMaterial(x.categoria)
                    ? x.material
                      ? B(x.material)
                      : "—"
                    : x.subcategoria || "—",
                ),
              ),
            ),
            React.createElement(
              "div",
              {
                style: {
                  padding: 16,
                  background: "var(--bg)",
                  borderRadius: 8,
                  marginBottom: 20,
                },
              },
              React.createElement(
                "div",
                {
                  style: {
                    fontSize: 11,
                    color: "var(--muted)",
                    marginBottom: 12,
                  },
                },
                "Precios",
              ),
              React.createElement(
                "div",
                {
                  style: {
                    display: "grid",
                    gridTemplateColumns: "repeat(3, 1fr)",
                    gap: 16,
                  },
                },
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "div",
                    { style: { fontSize: 11, color: "var(--muted)" } },
                    "Costo",
                  ),
                  React.createElement(
                    "div",
                    { style: { fontSize: 16, fontWeight: 500 } },
                    formatMoney(x.precio_costo),
                  ),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "div",
                    { style: { fontSize: 11, color: "var(--muted)" } },
                    "Menudeo",
                  ),
                  React.createElement(
                    "div",
                    {
                      style: {
                        fontSize: 16,
                        fontWeight: 600,
                        color: "var(--accent)",
                      },
                    },
                    x.tiene_variantes ? "Desde " : "",
                    formatMoney(x.precio_menudeo),
                  ),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "div",
                    { style: { fontSize: 11, color: "var(--muted)" } },
                    "Mayoreo",
                  ),
                  React.createElement(
                    "div",
                    { style: { fontSize: 16, fontWeight: 500 } },
                    formatMoney(x.precio_mayoreo),
                  ),
                ),
              ),
              x.precio_costo > 0 &&
                React.createElement(
                  "div",
                  {
                    style: {
                      marginTop: 12,
                      fontSize: 11,
                      color: "var(--success)",
                    },
                  },
                  "Margen: ",
                  Math.round(100 * (1 - x.precio_costo / x.precio_menudeo)),
                  "%",
                ),
            ),
            x.tiene_variantes &&
              React.createElement(
                "section",
                {
                  "data-od-id": "product-variation-summary",
                  "aria-labelledby": "variation-summary-title",
                },
                React.createElement(
                  "div",
                  {
                    id: "variation-summary-title",
                    style: {
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 12,
                      alignItems: "baseline",
                      marginBottom: 8,
                    },
                  },
                  React.createElement(
                    "div",
                    { style: { fontSize: 12, fontWeight: 600 } },
                    "Variaciones por ",
                    x.tipo_variacion.toLowerCase(),
                  ),
                  React.createElement(
                    "div",
                    {
                      style: { display: "flex", alignItems: "center", gap: 8 },
                    },
                    React.createElement(
                      "span",
                      { style: { fontSize: 11, color: "var(--muted)" } },
                      x.variantes.length,
                      " registradas",
                    ),
                    canManageProducts &&
                      x.estado !== "baja" &&
                      React.createElement(
                        "button",
                        {
                          type: "button",
                          className: "btn-secondary",
                          onClick: () =>
                            setVariantModal({ product: x, variant: null }),
                          style: { padding: "4px 8px", fontSize: 11 },
                        },
                        React.createElement(Icons.Plus, null),
                        " Agregar",
                      ),
                  ),
                ),
                React.createElement(
                  "div",
                  { className: "variation-summary" },
                  React.createElement(
                    "div",
                    {
                      className: "variation-summary-row header",
                      "aria-hidden": "true",
                    },
                    React.createElement("span", null, x.tipo_variacion),
                    React.createElement("span", null, "SKU"),
                    React.createElement("span", null, "Menudeo"),
                    React.createElement("span", null, "Mayoreo"),
                    React.createElement("span", null, "Stock"),
                    React.createElement("span", null, "Estado / acción"),
                  ),
                  x.variantes.map((e, t) =>
                    React.createElement(
                      "div",
                      {
                        className: "variation-summary-row",
                        key: e.id,
                        "data-od-id": `product-variation-${t + 1}`,
                        style: e.estado === "baja" ? { opacity: 0.68 } : null,
                      },
                      React.createElement("strong", null, e.talla_o_color),
                      React.createElement("span", { className: "mono" }, e.sku),
                      React.createElement(
                        "span",
                        { className: "tabular" },
                        formatMoney(e.precio_menudeo),
                      ),
                      React.createElement(
                        "span",
                        { className: "tabular" },
                        formatMoney(e.precio_mayoreo),
                      ),
                      React.createElement(
                        "span",
                        { className: "tabular" },
                        e.stock,
                      ),
                      React.createElement(
                        "span",
                        {
                          style: {
                            display: "flex",
                            alignItems: "center",
                            gap: 4,
                          },
                        },
                        React.createElement(
                          "span",
                          {
                            className:
                              "pill pill-" +
                              (e.estado === "baja" ? "danger" : "success"),
                          },
                          e.estado === "baja" ? "Inactiva" : "Activa",
                        ),
                        canManageProducts &&
                          React.createElement(
                            "button",
                            {
                              type: "button",
                              className: "btn-ghost",
                              onClick: () =>
                                setVariantModal({ product: x, variant: e }),
                              style: { padding: "4px 6px", fontSize: 11 },
                            },
                            e.estado === "baja" ? "Reactivar" : "Editar",
                          ),
                      ),
                    ),
                  ),
                ),
              ),
            React.createElement(
              "div",
              {
                style: {
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 16,
                },
              },
              React.createElement(
                "div",
                {
                  style: {
                    padding: 12,
                    background: "var(--bg)",
                    borderRadius: 6,
                  },
                },
                React.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 11,
                      color: "var(--muted)",
                      marginBottom: 4,
                    },
                  },
                  "Existencias",
                ),
                React.createElement(
                  "div",
                  { style: { fontSize: 20, fontWeight: 600 } },
                  x.stock,
                ),
              ),
              React.createElement(
                "div",
                {
                  style: {
                    padding: 12,
                    background: "var(--bg)",
                    borderRadius: 6,
                  },
                },
                React.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 11,
                      color: "var(--muted)",
                      marginBottom: 4,
                    },
                  },
                  "Colecciones",
                ),
                React.createElement(
                  "div",
                  { style: { display: "flex", flexWrap: "wrap", gap: 4 } },
                  (x.colecciones || []).length > 0
                    ? x.colecciones.map((e) => {
                        const t = COLECCIONES_SEED.find((t) => t.id === e);
                        return t
                          ? React.createElement(
                              "span",
                              {
                                key: e,
                                className: "pill pill-muted",
                                style: { fontSize: 10 },
                              },
                              t.nombre,
                            )
                          : null;
                      })
                    : React.createElement(
                        "span",
                        { style: { fontSize: 12, color: "var(--muted)" } },
                        "Sin asignar",
                      ),
                ),
              ),
            ),
          ),
          React.createElement(
            "div",
            {
              style: {
                padding: "16px 24px",
                borderTop: "1px solid var(--border)",
                display: "flex",
                justifyContent: "flex-end",
                gap: 8,
              },
            },
            React.createElement(
              "button",
              { className: "btn-ghost", onClick: () => k(null) },
              "Cerrar",
            ),
            canManageProducts &&
              React.createElement(
                "button",
                {
                  "data-od-id": "edit-product-cta",
                  className: "btn-primary",
                  onClick: () => {
                    (setEditProduct(x), k(null));
                  },
                },
                "Editar",
              ),
          ),
        ),
      ),
    React.createElement(ProductEditModal, {
      product: canManageProducts ? editProduct : null,
      onClose: () => setEditProduct(null),
      onSave: async (updated) => {
        const active = updated.estado !== "baja";
        await actions.updateProduct(updated.id, {
          name: updated.nombre,
          status: updated.estado === "externo" ? "externo" : "disponible",
          active,
        });
        const primaryVariant = updated.variantes?.[0];
        if (primaryVariant && !updated.tiene_variantes) {
          await actions.updateVariant(updated.id, primaryVariant.id, {
            cost_price: updated.precio_costo,
            retail_price: updated.precio_menudeo,
            wholesale_price: updated.precio_mayoreo,
            active,
          });
        }
        setEditProduct(null);
      },
    }),
    React.createElement(VariantModal, {
      product: canManageProducts ? variantModal?.product : null,
      variant: variantModal?.variant || null,
      branches: sucursales,
      canDeactivate:
        !variantModal?.variant ||
        variantModal.variant.estado === "baja" ||
        variantModal.product.variantes.filter(
          (variant) => variant.estado !== "baja",
        ).length > 1,
      onClose: () => setVariantModal(null),
      onSave: async ({ variant, stock, branchId }) => {
        const product = variantModal.product;
        if (variantModal.variant) {
          await actions.updateVariant(
            product.id,
            variantModal.variant.id,
            variant,
          );
          k(null);
          return;
        }
        const updated = await actions.addVariant(product.id, variant);
        if (stock > 0) {
          const createdVariant = updated.variants.find(
            (item) => item.variant_value === variant.variant_value,
          );
          if (!createdVariant)
            throw new Error("No se pudo identificar la variante creada.");
          await actions.createInventoryAdjustment({
            variant_id: createdVariant.id,
            branch_id: branchId,
            quantity: stock,
            reference: "ALTA-VARIANTE",
            note: "Existencias iniciales de la variante",
          });
        }
        k(null);
      },
    }),
    React.createElement(InventoryAdjustmentModal, {
      product: adjustmentProduct,
      branches: sucursales,
      onClose: () => setAdjustmentProduct(null),
      onSave: actions.createInventoryAdjustment,
    }),
    i &&
      React.createElement(
        "div",
        {
          "data-od-id": "new-product-modal",
          style: {
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          },
        },
        React.createElement(
          "div",
          { className: "card capture-modal" },
          React.createElement(
            "div",
            {
              style: {
                padding: "16px 24px",
                borderBottom: "1px solid var(--border)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              },
            },
            React.createElement(
              "h3",
              {
                "data-od-id": "new-product-heading",
                style: { fontSize: 16, fontWeight: 600 },
              },
              "Nuevo producto",
            ),
            React.createElement(
              "button",
              { className: "btn-ghost", onClick: D },
              React.createElement(Icons.Close, null),
            ),
          ),
          React.createElement(
            "div",
            { style: { padding: 24 } },
            React.createElement(
              "div",
              { style: { marginBottom: 20 } },
              React.createElement(
                "label",
                {
                  style: {
                    display: "block",
                    fontSize: 12,
                    fontWeight: 500,
                    marginBottom: 8,
                    color: "var(--muted)",
                  },
                },
                "1. Tipo de producto ",
                React.createElement(
                  "span",
                  { style: { color: "var(--danger)" } },
                  "*",
                ),
              ),
              React.createElement(
                "div",
                {
                  style: {
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 12,
                  },
                },
                React.createElement(
                  "button",
                  {
                    type: "button",
                    onClick: () => {
                      (d("joyeria"),
                        p((e) => ({
                          ...e,
                          categoria: "",
                          material: "",
                          subcategoria: "",
                        })));
                    },
                    style: {
                      padding: 20,
                      borderRadius: 8,
                      border:
                        "joyeria" === m
                          ? "2px solid var(--gold)"
                          : "1px solid var(--border)",
                      background:
                        "joyeria" === m ? "var(--gold-bg)" : "var(--surface)",
                      cursor: "pointer",
                      textAlign: "center",
                    },
                  },
                  React.createElement(
                    "div",
                    {
                      style: {
                        width: 36,
                        height: 36,
                        margin: "0 auto 8px",
                        display: "grid",
                        placeItems: "center",
                        color: "joyeria" === m ? "var(--gold)" : "var(--muted)",
                      },
                    },
                    React.createElement(Icons.Diamond, null),
                  ),
                  React.createElement(
                    "div",
                    {
                      style: {
                        fontWeight: 600,
                        color: "joyeria" === m ? "var(--gold)" : "inherit",
                      },
                    },
                    "Joyería",
                  ),
                  React.createElement(
                    "div",
                    {
                      style: {
                        fontSize: 11,
                        color: "var(--muted)",
                        marginTop: 4,
                      },
                    },
                    `${activeJewelryCategoryCount} categorías activas · material según categoría`,
                  ),
                ),
                React.createElement(
                  "button",
                  {
                    type: "button",
                    onClick: () => {
                      (d("nojoyeria"),
                        p((e) => ({
                          ...e,
                          categoria: "",
                          material: "",
                          subcategoria: "",
                        })));
                    },
                    style: {
                      padding: 20,
                      borderRadius: 8,
                      border:
                        "nojoyeria" === m
                          ? "2px solid var(--accent)"
                          : "1px solid var(--border)",
                      background:
                        "nojoyeria" === m
                          ? "var(--accent-light)"
                          : "var(--surface)",
                      cursor: "pointer",
                      textAlign: "center",
                    },
                  },
                  React.createElement(
                    "div",
                    {
                      style: {
                        width: 36,
                        height: 36,
                        margin: "0 auto 8px",
                        display: "grid",
                        placeItems: "center",
                        color:
                          "nojoyeria" === m ? "var(--accent)" : "var(--muted)",
                      },
                    },
                    React.createElement(Icons.Tag, null),
                  ),
                  React.createElement(
                    "div",
                    {
                      style: {
                        fontWeight: 600,
                        color: "nojoyeria" === m ? "var(--accent)" : "inherit",
                      },
                    },
                    "No Joyería",
                  ),
                  React.createElement(
                    "div",
                    {
                      style: {
                        fontSize: 11,
                        color: "var(--muted)",
                        marginTop: 4,
                      },
                    },
                    `${activeNonJewelryCategoryCount} categorías activas · con subcategorías`,
                  ),
                ),
              ),
            ),
            m &&
              React.createElement(
                "div",
                { style: { marginBottom: 20 } },
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 8,
                      color: "var(--muted)",
                    },
                  },
                  "2. Categoría ",
                  React.createElement(
                    "span",
                    { style: { color: "var(--danger)" } },
                    "*",
                  ),
                ),
                React.createElement(
                  "div",
                  {
                    style: {
                      display: "grid",
                      gridTemplateColumns:
                        "joyeria" === m ? "repeat(4, 1fr)" : "repeat(3, 1fr)",
                      gap: 8,
                    },
                  },
                  P.map((e) =>
                    React.createElement(
                      "button",
                      {
                        key: e.clave,
                        type: "button",
                        onClick: () =>
                          p((t) => ({
                            ...t,
                            categoria: e.clave,
                            material: "",
                            subcategoria: "",
                            subcategoriaSugerida: "",
                          })),
                        className:
                          u.categoria === e.clave
                            ? "btn-primary"
                            : "btn-secondary",
                        style: {
                          padding: "10px 6px",
                          fontSize: 12,
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "center",
                          gap: 4,
                          border:
                            u.categoria === e.clave
                              ? "2px solid var(--accent)"
                              : "1px solid var(--border)",
                        },
                      },
                      React.createElement(
                        "span",
                        { style: { fontWeight: 600, fontSize: 14 } },
                        e.clave,
                      ),
                      React.createElement(
                        "span",
                        { style: { fontSize: 11, opacity: 0.8 } },
                        e.nombre,
                      ),
                    ),
                  ),
                ),
                R.categoria &&
                  React.createElement(
                    "div",
                    {
                      style: {
                        color: "var(--danger)",
                        fontSize: 11,
                        marginTop: 4,
                      },
                    },
                    R.categoria,
                  ),
              ),
            A &&
              React.createElement(
                "div",
                {
                  style: {
                    marginBottom: 20,
                    padding: 16,
                    background: "var(--gold-bg)",
                    borderRadius: 8,
                  },
                },
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 8,
                      color: "var(--gold)",
                    },
                  },
                  "3. Material ",
                  React.createElement(
                    "span",
                    { style: { color: "var(--danger)" } },
                    "*",
                  ),
                ),
                React.createElement(
                  "div",
                  {
                    style: {
                      display: "grid",
                      gridTemplateColumns: "repeat(4, 1fr)",
                      gap: 6,
                    },
                  },
                  MATERIALES.filter((e) => e.activa !== false).map((e) =>
                    React.createElement(
                      "button",
                      {
                        key: e.clave,
                        type: "button",
                        onClick: () => p((t) => ({ ...t, material: e.clave })),
                        className:
                          u.material === e.clave ? "btn-primary" : "btn-ghost",
                        style: {
                          padding: "6px 8px",
                          fontSize: 11,
                          border: "1px solid var(--border)",
                        },
                      },
                      React.createElement(
                        "span",
                        { className: "mono" },
                        e.clave,
                      ),
                      " ",
                      e.nombre.split(" ")[0],
                    ),
                  ),
                ),
                R.material &&
                  React.createElement(
                    "div",
                    {
                      style: {
                        color: "var(--danger)",
                        fontSize: 11,
                        marginTop: 4,
                      },
                    },
                    R.material,
                  ),
              ),
            u.categoria &&
              (!A || u.material) &&
              React.createElement(
                "div",
                { style: { marginBottom: 20 } },
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  A ? "4" : "3",
                  ". Nombre del producto ",
                  React.createElement(
                    "span",
                    { style: { color: "var(--danger)" } },
                    "*",
                  ),
                ),
                React.createElement("input", {
                  type: "text",
                  placeholder:
                    "Ej: Anillo Ojo Turco, Veladora Roja del Amor...",
                  value: u.nombre,
                  onChange: (e) => {
                    return (
                      (t = e.target.value),
                      void p((e) => {
                        const a = T ? sugerirSubcategoria(t, e.categoria) : "";
                        return {
                          ...e,
                          nombre: t,
                          subcategoriaSugerida: a,
                          subcategoria: a || e.subcategoria,
                        };
                      })
                    );
                    var t;
                  },
                  style: { width: "100%" },
                  autoFocus: !0,
                }),
                R.nombre &&
                  React.createElement(
                    "div",
                    {
                      style: {
                        color: "var(--danger)",
                        fontSize: 11,
                        marginTop: 4,
                      },
                    },
                    R.nombre,
                  ),
                u.nombre &&
                  React.createElement(
                    "div",
                    {
                      style: {
                        marginTop: 8,
                        padding: 8,
                        background: "var(--bg)",
                        borderRadius: 4,
                        fontSize: 12,
                      },
                    },
                    React.createElement(
                      "span",
                      { style: { color: "var(--muted)" } },
                      "SKU generado: ",
                    ),
                    React.createElement(
                      "span",
                      {
                        className: "mono",
                        style: { color: "var(--accent)", fontWeight: 500 },
                      },
                      M,
                    ),
                  ),
              ),
            T &&
              u.nombre &&
              React.createElement(
                "div",
                {
                  style: {
                    marginBottom: 20,
                    padding: 16,
                    background: "var(--accent-light)",
                    borderRadius: 8,
                  },
                },
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 8,
                    },
                  },
                  "Subcategoría",
                  u.subcategoriaSugerida &&
                    "Por clasificar" !== u.subcategoriaSugerida &&
                    React.createElement(
                      "span",
                      {
                        className: "pill pill-success",
                        style: { marginLeft: 8, fontSize: 10 },
                      },
                      "Sugerida",
                    ),
                ),
                React.createElement(
                  "select",
                  {
                    value: u.subcategoria,
                    onChange: (e) =>
                      p((t) => ({ ...t, subcategoria: e.target.value })),
                    style: { width: "100%" },
                  },
                  React.createElement(
                    "option",
                    { value: "" },
                    "Seleccionar subcategoría...",
                  ),
                  W.map((e) =>
                    React.createElement(
                      "option",
                      { key: e.id, value: e.nombre },
                      e.nombre,
                      " ",
                      e.sistema ? "(sistema)" : "",
                    ),
                  ),
                ),
                "Por clasificar" === u.subcategoriaSugerida &&
                  React.createElement(
                    "div",
                    {
                      style: {
                        marginTop: 6,
                        fontSize: 11,
                        color: "var(--warning)",
                      },
                    },
                    'No se encontró sugerencia. Se asignará "Por clasificar" si no seleccionas una.',
                  ),
              ),
            u.nombre &&
              React.createElement(
                React.Fragment,
                null,
                React.createElement(
                  "div",
                  { style: { marginBottom: 20 } },
                  React.createElement(
                    "button",
                    {
                      type: "button",
                      role: "switch",
                      "aria-checked": v,
                      className: "variation-option",
                      "data-od-id": "variation-capture-option",
                      onClick: () => {
                        const e = !v;
                        (e &&
                          1 === C.length &&
                          !C[0].precio_menudeo &&
                          S([
                            {
                              ...C[0],
                              stock: u.stock || "1",
                              precio_menudeo: u.precio_menudeo,
                              precio_mayoreo: u.precio_mayoreo,
                            },
                          ]),
                          b(e),
                          E((e) => ({ ...e, variaciones: null })));
                      },
                    },
                    React.createElement(
                      "span",
                      { className: "variation-option-copy" },
                      React.createElement(
                        "strong",
                        null,
                        "Este producto tiene variaciones",
                      ),
                      React.createElement(
                        "span",
                        null,
                        "Captura tallas, colores, medidas o presentaciones con stock y precio propios.",
                      ),
                    ),
                    React.createElement("span", {
                      className: "variation-switch",
                      "aria-hidden": "true",
                    }),
                  ),
                ),
                React.createElement(
                  "div",
                  {
                    style: {
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: 16,
                      marginBottom: 20,
                    },
                  },
                  React.createElement(
                    "div",
                    null,
                    React.createElement(
                      "label",
                      {
                        style: {
                          display: "block",
                          fontSize: 12,
                          fontWeight: 500,
                          marginBottom: 6,
                          color: "var(--muted)",
                        },
                      },
                      "Precio costo ",
                      React.createElement(
                        "span",
                        { style: { fontSize: 10 } },
                        "(producto padre)",
                      ),
                    ),
                    React.createElement("input", {
                      type: "number",
                      min: "0",
                      placeholder: "0.00",
                      value: u.precio_costo,
                      onChange: (e) =>
                        p((t) => ({ ...t, precio_costo: e.target.value })),
                      style: { width: "100%" },
                    }),
                  ),
                  React.createElement(
                    "div",
                    null,
                    React.createElement(
                      "label",
                      {
                        style: {
                          display: "block",
                          fontSize: 12,
                          fontWeight: 500,
                          marginBottom: 6,
                          color: "var(--muted)",
                        },
                      },
                      "Piedra o material secundario ",
                      React.createElement(
                        "span",
                        { style: { fontSize: 10 } },
                        "(opcional)",
                      ),
                    ),
                    React.createElement("input", {
                      type: "text",
                      placeholder: "Ej. Cuarzo rosa, diamante",
                      value: u.piedra,
                      onChange: (e) =>
                        p((t) => ({ ...t, piedra: e.target.value })),
                      style: { width: "100%" },
                    }),
                  ),
                ),
                v
                  ? React.createElement(
                      "section",
                      {
                        className: "variation-panel",
                        "data-od-id": "variation-capture-panel",
                        "aria-labelledby": "variation-capture-title",
                      },
                      React.createElement(
                        "div",
                        {
                          style: {
                            display: "flex",
                            justifyContent: "space-between",
                            gap: 16,
                            alignItems: "flex-start",
                            marginBottom: 14,
                          },
                        },
                        React.createElement(
                          "div",
                          null,
                          React.createElement(
                            "h4",
                            {
                              id: "variation-capture-title",
                              style: { fontSize: 13, fontWeight: 600 },
                            },
                            "Captura de variaciones",
                          ),
                          React.createElement(
                            "p",
                            {
                              style: {
                                marginTop: 2,
                                fontSize: 11,
                                color: "var(--muted)",
                              },
                            },
                            "El SKU padre agrupa las opciones y cada variación recibe un sufijo correlativo.",
                          ),
                        ),
                        React.createElement(
                          "span",
                          { className: "pill pill-muted" },
                          C.length,
                          " ",
                          1 === C.length ? "variación" : "variaciones",
                        ),
                      ),
                      React.createElement(
                        "div",
                        { style: { marginBottom: 12 } },
                        React.createElement(
                          "div",
                          {
                            style: {
                              marginBottom: 6,
                              fontSize: 10,
                              fontWeight: 600,
                              color: "var(--muted)",
                              textTransform: "uppercase",
                              letterSpacing: "0.04em",
                            },
                          },
                          "Atributo",
                        ),
                        React.createElement(
                          "div",
                          {
                            className: "variation-type-group",
                            role: "group",
                            "aria-label": "Tipo de variación",
                          },
                          ["Talla", "Color", "Medida", "Presentación"].map(
                            (e) =>
                              React.createElement(
                                "button",
                                {
                                  key: e,
                                  type: "button",
                                  className:
                                    "btn-secondary variation-type-button",
                                  "data-od-id": `variation-type-${"Presentación" === e ? "presentation" : e.toLowerCase()}`,
                                  "aria-pressed": f === e,
                                  onClick: () => h(e),
                                },
                                e,
                              ),
                          ),
                        ),
                      ),
                      React.createElement(
                        "div",
                        null,
                        C.map((e, t) =>
                          React.createElement(
                            "div",
                            {
                              className: "variation-row",
                              key: e.id,
                              "data-od-id": `variation-row-${t + 1}`,
                            },
                            React.createElement(
                              "div",
                              { className: "variation-field" },
                              React.createElement("label", null, "SKU"),
                              React.createElement(
                                "div",
                                { className: "variation-sku mono" },
                                M,
                                "-",
                                String(t + 1).padStart(2, "0"),
                              ),
                            ),
                            React.createElement(
                              "div",
                              { className: "variation-field" },
                              React.createElement("label", null, f),
                              React.createElement("input", {
                                type: "text",
                                value: e.valor,
                                onChange: (t) =>
                                  _(e.id, "valor", t.target.value),
                                placeholder: j,
                                "aria-label": `${f} de la variación ${t + 1}`,
                              }),
                            ),
                            React.createElement(
                              "div",
                              { className: "variation-field" },
                              React.createElement("label", null, "Stock"),
                              React.createElement("input", {
                                type: "number",
                                min: "0",
                                step: "1",
                                value: e.stock,
                                onChange: (t) =>
                                  _(e.id, "stock", t.target.value),
                                "aria-label": `Existencias de la variación ${t + 1}`,
                              }),
                            ),
                            React.createElement(
                              "div",
                              { className: "variation-field" },
                              React.createElement("label", null, "Menudeo"),
                              React.createElement("input", {
                                type: "number",
                                min: "0",
                                placeholder: "0.00",
                                value: e.precio_menudeo,
                                onChange: (t) =>
                                  _(e.id, "precio_menudeo", t.target.value),
                                "aria-label": `Precio menudeo de la variación ${t + 1}`,
                              }),
                            ),
                            React.createElement(
                              "div",
                              { className: "variation-field" },
                              React.createElement("label", null, "Mayoreo"),
                              React.createElement("input", {
                                type: "number",
                                min: "0",
                                placeholder: "85%",
                                value: e.precio_mayoreo,
                                onChange: (t) =>
                                  _(e.id, "precio_mayoreo", t.target.value),
                                "aria-label": `Precio mayoreo de la variación ${t + 1}`,
                              }),
                            ),
                            React.createElement(
                              "button",
                              {
                                type: "button",
                                className: "btn-ghost variation-remove",
                                onClick: () => {
                                  return (
                                    (t = e.id),
                                    void (
                                      1 !== C.length &&
                                      S((e) => e.filter((e) => e.id !== t))
                                    )
                                  );
                                  var t;
                                },
                                disabled: 1 === C.length,
                                "aria-label": `Eliminar variación ${t + 1}`,
                              },
                              React.createElement(Icons.Trash, null),
                            ),
                          ),
                        ),
                      ),
                      R.variaciones &&
                        React.createElement(
                          "div",
                          {
                            role: "alert",
                            style: {
                              color: "var(--danger)",
                              fontSize: 11,
                              marginTop: 10,
                            },
                          },
                          R.variaciones,
                        ),
                      React.createElement(
                        "button",
                        {
                          type: "button",
                          className: "btn-secondary",
                          "data-od-id": "add-variation-button",
                          onClick: () => {
                            if (C.length >= 99) return;
                            const e = C[C.length - 1] || {},
                              t = Math.max(...C.map((e) => e.id), 0) + 1;
                            S((a) => [
                              ...a,
                              {
                                id: t,
                                valor: "",
                                stock: "1",
                                precio_menudeo:
                                  e.precio_menudeo || u.precio_menudeo || "",
                                precio_mayoreo:
                                  e.precio_mayoreo || u.precio_mayoreo || "",
                              },
                            ]);
                          },
                          disabled: C.length >= 99,
                          style: {
                            minHeight: 44,
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 6,
                            marginTop: 12,
                          },
                        },
                        React.createElement(Icons.Plus, null),
                        " Agregar variación",
                      ),
                    )
                  : React.createElement(
                      "div",
                      {
                        style: {
                          display: "grid",
                          gridTemplateColumns: "repeat(3, 1fr)",
                          gap: 16,
                          marginBottom: 20,
                        },
                      },
                      React.createElement(
                        "div",
                        null,
                        React.createElement(
                          "label",
                          {
                            style: {
                              display: "block",
                              fontSize: 12,
                              fontWeight: 500,
                              marginBottom: 6,
                              color: "var(--muted)",
                            },
                          },
                          "Precio menudeo ",
                          React.createElement(
                            "span",
                            { style: { color: "var(--danger)" } },
                            "*",
                          ),
                        ),
                        React.createElement("input", {
                          type: "number",
                          min: "0",
                          step: "1",
                          placeholder: "0.00",
                          value: u.precio_menudeo,
                          onChange: (e) =>
                            ((e) => {
                              const t = parseFloat(e) || 0,
                                a = Math.round(0.85 * t);
                              p((t) => ({
                                ...t,
                                precio_menudeo: e,
                                precio_mayoreo: a > 0 ? String(a) : "",
                              }));
                            })(e.target.value),
                          style: { width: "100%" },
                        }),
                        R.precio_menudeo &&
                          React.createElement(
                            "div",
                            {
                              style: {
                                color: "var(--danger)",
                                fontSize: 11,
                                marginTop: 4,
                              },
                            },
                            R.precio_menudeo,
                          ),
                      ),
                      React.createElement(
                        "div",
                        null,
                        React.createElement(
                          "label",
                          {
                            style: {
                              display: "block",
                              fontSize: 12,
                              fontWeight: 500,
                              marginBottom: 6,
                              color: "var(--muted)",
                            },
                          },
                          "Precio mayoreo ",
                          React.createElement(
                            "span",
                            { style: { fontSize: 10 } },
                            "(85%)",
                          ),
                        ),
                        React.createElement("input", {
                          type: "number",
                          min: "0",
                          placeholder: "Automático",
                          value: u.precio_mayoreo,
                          onChange: (e) =>
                            p((t) => ({
                              ...t,
                              precio_mayoreo: e.target.value,
                            })),
                          style: { width: "100%" },
                        }),
                      ),
                      React.createElement(
                        "div",
                        null,
                        React.createElement(
                          "label",
                          {
                            style: {
                              display: "block",
                              fontSize: 12,
                              fontWeight: 500,
                              marginBottom: 6,
                              color: "var(--muted)",
                            },
                          },
                          "Existencias ",
                          React.createElement(
                            "span",
                            { style: { color: "var(--danger)" } },
                            "*",
                          ),
                        ),
                        React.createElement("input", {
                          type: "number",
                          min: "0",
                          value: u.stock,
                          onChange: (e) =>
                            p((t) => ({ ...t, stock: e.target.value })),
                          style: { width: "100%" },
                        }),
                        R.stock &&
                          React.createElement(
                            "div",
                            {
                              style: {
                                color: "var(--danger)",
                                fontSize: 11,
                                marginTop: 4,
                              },
                            },
                            R.stock,
                          ),
                      ),
                    ),
                React.createElement(
                  "div",
                  { style: { marginBottom: 20 } },
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Sucursal para existencias iniciales",
                  ),
                  React.createElement(
                    "select",
                    {
                      value: u.branchId,
                      onChange: (event) =>
                        p((current) => ({
                          ...current,
                          branchId: event.target.value,
                        })),
                      style: { width: "100%" },
                      "aria-invalid": Boolean(R.branchId),
                    },
                    React.createElement(
                      "option",
                      { value: "" },
                      "Seleccionar si registrarás existencias",
                    ),
                    sucursales.map((branch) =>
                      React.createElement(
                        "option",
                        {
                          key: branch.uuid || branch.id,
                          value: branch.uuid || branch.id,
                        },
                        branch.nombre || branch.name,
                      ),
                    ),
                  ),
                  R.branchId &&
                    React.createElement(
                      "div",
                      {
                        style: {
                          marginTop: 4,
                          color: "var(--danger)",
                          fontSize: 11,
                        },
                      },
                      R.branchId,
                    ),
                ),
                React.createElement(
                  "div",
                  { style: { marginBottom: 20 } },
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 8,
                        color: "var(--muted)",
                      },
                    },
                    "Imagen del producto ",
                    React.createElement(
                      "span",
                      { style: { fontSize: 10 } },
                      "(opcional)",
                    ),
                  ),
                  React.createElement(
                    "div",
                    {
                      style: {
                        display: "flex",
                        gap: 16,
                        alignItems: "flex-start",
                      },
                    },
                    g
                      ? React.createElement(
                          "div",
                          { style: { position: "relative" } },
                          React.createElement("img", {
                            src: g,
                            alt: `Vista previa de ${u.nombre || "producto"}`,
                            style: {
                              width: 100,
                              height: 100,
                              objectFit: "cover",
                              borderRadius: 8,
                              border: "1px solid var(--border)",
                            },
                          }),
                          React.createElement(
                            "button",
                            {
                              type: "button",
                              onClick: () => {
                                (y(null), p((e) => ({ ...e, imagen: null })));
                              },
                              style: {
                                position: "absolute",
                                top: -8,
                                right: -8,
                                width: 24,
                                height: 24,
                                borderRadius: "50%",
                                background: "var(--danger)",
                                color: "white",
                                border: "none",
                                cursor: "pointer",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                fontSize: 14,
                              },
                            },
                            "x",
                          ),
                        )
                      : React.createElement(
                          "label",
                          {
                            style: {
                              width: 100,
                              height: 100,
                              border: "2px dashed var(--border)",
                              borderRadius: 8,
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                              justifyContent: "center",
                              cursor: "pointer",
                              background: "var(--bg)",
                              transition: "border-color 0.2s",
                            },
                          },
                          React.createElement(Icons.Plus, null),
                          React.createElement(
                            "span",
                            {
                              style: {
                                fontSize: 10,
                                color: "var(--muted)",
                                marginTop: 4,
                              },
                            },
                            "Agregar",
                          ),
                          React.createElement("input", {
                            type: "file",
                            accept: "image/jpeg,image/png,image/webp",
                            onChange: (event) => {
                              const file = event.target.files?.[0];
                              event.target.value = "";
                              const validationError =
                                validateProductImage(file);
                              if (validationError) {
                                E((current) => ({
                                  ...current,
                                  imagen: validationError,
                                }));
                                return;
                              }
                              const reader = new FileReader();
                              reader.onloadend = () => y(reader.result);
                              reader.readAsDataURL(file);
                              p((current) => ({ ...current, imagen: file }));
                              E((current) => ({ ...current, imagen: "" }));
                            },
                            style: { display: "none" },
                          }),
                        ),
                    React.createElement(
                      "div",
                      {
                        style: { fontSize: 11, color: "var(--muted)", flex: 1 },
                      },
                      React.createElement(
                        "div",
                        { style: { marginBottom: 4 } },
                        "Formatos: JPG, PNG, WebP",
                      ),
                      React.createElement(
                        "div",
                        null,
                        "Máximo 5 MB. También puedes agregarla después desde el detalle.",
                      ),
                      R.imagen &&
                        React.createElement(
                          "div",
                          {
                            role: "alert",
                            style: { marginTop: 6, color: "var(--danger)" },
                          },
                          R.imagen,
                        ),
                    ),
                  ),
                ),
              ),
          ),
          React.createElement(
            "div",
            {
              style: {
                padding: "16px 24px",
                borderTop: "1px solid var(--border)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                background: "var(--bg)",
              },
            },
            React.createElement(
              "div",
              {
                role: R.submit ? "alert" : undefined,
                style: {
                  fontSize: 11,
                  color: R.submit ? "var(--danger)" : "var(--muted)",
                },
              },
              R.submit || "Las colecciones se asignan después, en lote.",
            ),
            React.createElement(
              "div",
              { style: { display: "flex", gap: 8 } },
              React.createElement(
                "button",
                { className: "btn-ghost", onClick: D },
                "Cancelar",
              ),
              React.createElement(
                "button",
                {
                  className: "btn-primary",
                  "data-od-id": "save-product-button",
                  onClick: async () => {
                    if (
                      !(() => {
                        const e = {};
                        if (!u.categoria)
                          e.categoria = "Selecciona una categoría";
                        if (A && !u.material)
                          e.material = "Selecciona un material";
                        if (!u.nombre.trim())
                          e.nombre = "Escribe el nombre del producto";
                        const stocks = v
                          ? C.map((item) => Number(item.stock))
                          : [Number(u.stock)];
                        if (v) {
                          const t = C.map((e) =>
                            e.valor.trim().toLowerCase(),
                          ).filter(Boolean);
                          C.some(
                            (item) =>
                              !item.valor.trim() ||
                              item.stock === "" ||
                              !Number.isInteger(Number(item.stock)) ||
                              Number(item.stock) < 0 ||
                              !item.precio_menudeo ||
                              Number(item.precio_menudeo) <= 0,
                          )
                            ? (e.variaciones =
                                "Completa cada valor con existencias enteras y un precio válido")
                            : new Set(t).size !== t.length &&
                              (e.variaciones =
                                "Cada variación debe tener un valor distinto");
                        } else {
                          if (
                            !u.precio_menudeo ||
                            Number(u.precio_menudeo) <= 0
                          )
                            e.precio_menudeo = "Ingresa el precio";
                          if (
                            u.stock === "" ||
                            !Number.isInteger(Number(u.stock)) ||
                            Number(u.stock) < 0
                          )
                            e.stock =
                              "Ingresa una cantidad entera mayor o igual a cero";
                        }
                        if (stocks.some((stock) => stock > 0) && !u.branchId)
                          e.branchId =
                            "Selecciona la sucursal para las existencias iniciales";
                        return (E(e), 0 === Object.keys(e).length);
                      })()
                    )
                      return;
                    const category = CATEGORIAS.find(
                      (category) => category.clave === u.categoria,
                    );
                    const material = MATERIALES.find(
                      (material) => material.clave === u.material,
                    );
                    const subcategoryName = T
                      ? u.subcategoria || "Por clasificar"
                      : null;
                    const subcategory = subcategoryName
                      ? W.find((item) => item.nombre === subcategoryName)
                      : null;
                    const sourceVariants = v
                      ? C.map((item) => ({
                          variant_value: item.valor.trim(),
                          stock: Number(item.stock),
                          cost_price: parseFloat(u.precio_costo) || 0,
                          retail_price: parseFloat(item.precio_menudeo),
                          wholesale_price:
                            parseFloat(item.precio_mayoreo) ||
                            Math.round(0.85 * parseFloat(item.precio_menudeo)),
                        }))
                      : [
                          {
                            variant_value: null,
                            stock: Number(u.stock),
                            cost_price: parseFloat(u.precio_costo) || 0,
                            retail_price: parseFloat(u.precio_menudeo),
                            wholesale_price:
                              parseFloat(u.precio_mayoreo) ||
                              Math.round(0.85 * parseFloat(u.precio_menudeo)),
                          },
                        ];
                    setSavingProduct(true);
                    setInventoryError("");
                    let created = null;
                    try {
                      created = await actions.createProduct({
                        name: u.nombre.trim(),
                        category_id: category.id,
                        material_id: A ? material.id : null,
                        subcategory_id: subcategory?.id || null,
                        stone: u.piedra.trim() || null,
                        status: "disponible",
                        variant_type: v ? f : null,
                        collection_ids: [],
                        variants: sourceVariants.map(
                          ({ stock, ...variant }) => variant,
                        ),
                      });
                      if (u.imagen)
                        await actions.uploadProductImage(created.id, u.imagen);
                      if (u.branchId) {
                        await Promise.all(
                          created.variants.map((variant, index) => {
                            const quantity = sourceVariants[index].stock;
                            if (!quantity) return Promise.resolve();
                            return actions.createInventoryAdjustment({
                              variant_id: variant.id,
                              branch_id: u.branchId,
                              quantity,
                              reference: "ALTA-PRODUCTO",
                              note: "Existencias iniciales del producto",
                            });
                          }),
                        );
                      }
                      D();
                    } catch (error) {
                      if (created) {
                        D();
                        setInventoryError(
                          `El producto fue creado, pero una operación posterior falló: ${error.message}`,
                        );
                      } else {
                        E((current) => ({ ...current, submit: error.message }));
                      }
                    } finally {
                      setSavingProduct(false);
                    }
                  },
                  disabled:
                    savingProduct || !u.nombre || (!v && !u.precio_menudeo),
                  style: { minHeight: 44 },
                },
                savingProduct ? "Guardando…" : "Guardar Producto",
              ),
            ),
          ),
        ),
      ),
  );
}
const canManageClientCommercialProfile = (e) => "admin" === e?.rol;
function NewClientModal({
  open: e,
  origin: t = "clients",
  onClose: a,
  onRegister: l,
}) {
  const [n, r] = useState({ nombre: "", telefono: "", email: "", notas: "" }),
    [o, c] = useState({}),
    i = () => {
      (r({ nombre: "", telefono: "", email: "", notas: "" }), c({}));
    },
    s = () => {
      (i(), a());
    };
  const [submitting, setSubmitting] = useState(false);
  if (
    (useEffect(() => {
      if (!e) return;
      i();
      const t = (e) => {
        "Escape" === e.key && s();
      };
      return (
        document.addEventListener("keydown", t),
        () => document.removeEventListener("keydown", t)
      );
    }, [e]),
    !e)
  )
    return null;
  const m = (e, t) => {
    (r((a) => ({ ...a, [e]: t })), o[e] && c((t) => ({ ...t, [e]: "" })));
  };
  return React.createElement(
    "div",
    {
      "data-od-id": "pos" === t ? "pos-new-client-modal" : "new-client-modal",
      role: "dialog",
      "aria-modal": "true",
      "aria-labelledby": "new-client-heading",
      style: {
        position: "fixed",
        inset: 0,
        padding: 16,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 110,
      },
    },
    React.createElement(
      "div",
      { className: "card client-form-modal" },
      React.createElement(
        "div",
        {
          style: {
            minHeight: 64,
            padding: "12px 16px 12px 24px",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 16,
          },
        },
        React.createElement(
          "div",
          null,
          React.createElement(
            "h2",
            {
              "data-od-id": "new-client-heading",
              id: "new-client-heading",
              style: { fontSize: 17, fontWeight: 600 },
            },
            "Registrar nuevo cliente",
          ),
          React.createElement(
            "p",
            { style: { marginTop: 3, color: "var(--muted)", fontSize: 12 } },
            "pos" === t
              ? "Se registrará como menudeo y se seleccionará en esta venta."
              : "Todo cliente nuevo comienza como cliente de menudeo.",
          ),
        ),
        React.createElement(
          "button",
          {
            "data-od-id": "close-new-client-control",
            type: "button",
            className: "btn-ghost",
            "aria-label": "Cerrar registro de cliente",
            onClick: s,
            style: {
              minWidth: 44,
              minHeight: 44,
              padding: 0,
              display: "grid",
              placeItems: "center",
            },
          },
          React.createElement(Icons.Close, null),
        ),
      ),
      React.createElement(
        "form",
        {
          "data-od-id": "new-client-form",
          onSubmit: async (event) => {
            event.preventDefault();
            const errors = {};
            const email = n.email.trim();
            const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
            if (!n.nombre.trim()) errors.nombre = "Escribe el nombre completo.";
            if (email && !validEmail)
              errors.email = "Introduce un correo válido.";
            c(errors);
            if (Object.keys(errors).length > 0) return;
            setSubmitting(true);
            try {
              await l({
                nombre: n.nombre.trim(),
                telefono: n.telefono.trim(),
                email: email.toLowerCase(),
                notas: n.notas.trim(),
              });
              i();
            } catch (error) {
              c((current) => ({ ...current, submit: error.message }));
            } finally {
              setSubmitting(false);
            }
          },
          noValidate: !0,
        },
        React.createElement(
          "div",
          { className: "client-form-grid", style: { padding: 24 } },
          React.createElement(
            "div",
            {
              className: "client-policy-row",
              "data-od-id": "new-client-policy",
            },
            React.createElement(
              "span",
              { className: "pill pill-muted" },
              "Menudeo",
            ),
            React.createElement(
              "span",
              null,
              "Solo administración puede convertirlo a mayoreo y configurar una línea de crédito desde el panel Clientes.",
            ),
          ),
          React.createElement(
            "div",
            { className: "client-form-field client-form-field-full" },
            React.createElement(
              "label",
              { className: "client-form-label", htmlFor: "client-name" },
              "Nombre completo o razón social",
            ),
            React.createElement("input", {
              "data-od-id": "client-name-input",
              id: "client-name",
              type: "text",
              autoComplete: "name",
              placeholder: "Ej. Elena Ramírez",
              value: n.nombre,
              onChange: (e) => m("nombre", e.target.value),
              "aria-invalid": Boolean(o.nombre),
              "aria-describedby": o.nombre ? "client-name-error" : void 0,
              autoFocus: !0,
            }),
            React.createElement(
              "span",
              { id: "client-name-error", className: "client-form-error" },
              o.nombre || "",
            ),
          ),
          React.createElement(
            "div",
            { className: "client-form-field" },
            React.createElement(
              "label",
              { className: "client-form-label", htmlFor: "client-phone" },
              "Teléfono (opcional)",
            ),
            React.createElement("input", {
              "data-od-id": "client-phone-input",
              id: "client-phone",
              type: "tel",
              autoComplete: "tel",
              placeholder: "55 1234 5678",
              value: n.telefono,
              onChange: (e) => m("telefono", e.target.value),
              "aria-invalid": Boolean(o.telefono),
              "aria-describedby": o.telefono ? "client-phone-error" : void 0,
            }),
            React.createElement(
              "span",
              { id: "client-phone-error", className: "client-form-error" },
              o.telefono || "",
            ),
          ),
          React.createElement(
            "div",
            { className: "client-form-field" },
            React.createElement(
              "label",
              { className: "client-form-label", htmlFor: "client-email" },
              "Correo electrónico (opcional)",
            ),
            React.createElement("input", {
              "data-od-id": "client-email-input",
              id: "client-email",
              type: "email",
              autoComplete: "email",
              placeholder: "cliente@correo.mx",
              value: n.email,
              onChange: (e) => m("email", e.target.value),
              "aria-invalid": Boolean(o.email),
              "aria-describedby": o.email ? "client-email-error" : void 0,
            }),
            React.createElement(
              "span",
              { id: "client-email-error", className: "client-form-error" },
              o.email || "",
            ),
          ),
          React.createElement(
            "div",
            { className: "client-form-field client-form-field-full" },
            React.createElement(
              "label",
              { className: "client-form-label", htmlFor: "client-notes" },
              "Notas (opcional)",
            ),
            React.createElement("textarea", {
              id: "client-notes",
              rows: 3,
              maxLength: 1000,
              placeholder: "Preferencias o referencias útiles para el equipo",
              value: n.notas,
              onChange: (event) => m("notas", event.target.value),
            }),
          ),
          o.submit &&
            React.createElement(
              "div",
              {
                className: "client-form-error",
                role: "alert",
                style: { gridColumn: "1 / -1" },
              },
              o.submit,
            ),
        ),
        React.createElement(
          "div",
          {
            style: {
              padding: "16px 24px",
              borderTop: "1px solid var(--border)",
              display: "flex",
              justifyContent: "flex-end",
              gap: 8,
            },
          },
          React.createElement(
            "button",
            {
              "data-od-id": "cancel-new-client-control",
              type: "button",
              className: "btn-secondary",
              onClick: s,
              style: { minHeight: 44 },
            },
            "Cancelar",
          ),
          React.createElement(
            "button",
            {
              "data-od-id": "register-client-cta",
              type: "submit",
              className: "btn-primary",
              disabled: submitting,
              style: { minHeight: 44 },
            },
            submitting ? "Registrando…" : "Registrar cliente",
          ),
        ),
      ),
    ),
  );
}
function ClientEditModal({ client, onClose, onSave }) {
  const [form, setForm] = useState({
    nombre: "",
    telefono: "",
    email: "",
    notas: "",
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!client) return;
    setForm({
      nombre: client.nombre || "",
      telefono: client.telefono || "",
      email: client.email || "",
      notas: client.notas || "",
    });
    setErrors({});
  }, [client?.id]);

  if (!client) return null;
  const update = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: "", submit: "" }));
  };
  const submit = async (event) => {
    event.preventDefault();
    const nextErrors = {};
    const email = form.email.trim();
    if (!form.nombre.trim()) nextErrors.nombre = "Escribe el nombre completo.";
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      nextErrors.email = "Introduce un correo válido.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    setSubmitting(true);
    try {
      await onSave(client.id, {
        nombre: form.nombre.trim(),
        telefono: form.telefono.trim(),
        email: email.toLowerCase(),
        notas: form.notas.trim(),
      });
      onClose();
    } catch (error) {
      setErrors((current) => ({ ...current, submit: error.message }));
    } finally {
      setSubmitting(false);
    }
  };
  const field = (label, key, type = "text") =>
    React.createElement(
      "label",
      { className: "client-form-field" },
      React.createElement("span", { className: "client-form-label" }, label),
      React.createElement("input", {
        type,
        value: form[key],
        onChange: (event) => update(key, event.target.value),
        "aria-invalid": Boolean(errors[key]),
      }),
      React.createElement(
        "span",
        { className: "client-form-error" },
        errors[key] || "",
      ),
    );

  return React.createElement(
    AdminModalFrame,
    {
      id: "edit-client-modal",
      headingId: "edit-client-heading",
      title: "Editar cliente",
      subtitle: "Actualiza sus datos de contacto y notas operativas.",
      onClose,
      width: 620,
    },
    React.createElement(
      "form",
      { onSubmit: submit, noValidate: true },
      React.createElement(
        "div",
        { className: "client-form-grid", style: { padding: 24 } },
        React.createElement(
          "div",
          { className: "client-form-field client-form-field-full" },
          React.createElement(
            "label",
            { className: "client-form-label", htmlFor: "edit-client-name" },
            "Nombre completo o razón social",
          ),
          React.createElement("input", {
            id: "edit-client-name",
            autoFocus: true,
            value: form.nombre,
            onChange: (event) => update("nombre", event.target.value),
            "aria-invalid": Boolean(errors.nombre),
          }),
          React.createElement(
            "span",
            { className: "client-form-error" },
            errors.nombre || "",
          ),
        ),
        field("Teléfono (opcional)", "telefono", "tel"),
        field("Correo electrónico (opcional)", "email", "email"),
        React.createElement(
          "label",
          { className: "client-form-field client-form-field-full" },
          React.createElement(
            "span",
            { className: "client-form-label" },
            "Notas (opcional)",
          ),
          React.createElement("textarea", {
            rows: 4,
            maxLength: 1000,
            value: form.notas,
            onChange: (event) => update("notas", event.target.value),
          }),
        ),
        errors.submit &&
          React.createElement(
            "div",
            {
              className: "client-form-error client-form-field-full",
              role: "alert",
            },
            errors.submit,
          ),
      ),
      React.createElement(
        "div",
        { className: "modal-footer" },
        React.createElement(
          "button",
          { type: "button", className: "btn-secondary", onClick: onClose },
          "Cancelar",
        ),
        React.createElement(
          "button",
          { type: "submit", className: "btn-primary", disabled: submitting },
          submitting ? "Guardando…" : "Guardar cambios",
        ),
      ),
    ),
  );
}
function ClientCommercialModal({
  client: e,
  open: t,
  currentUser: a,
  onClose: l,
  onSave: n,
}) {
  const [r, o] = useState({
      tipo: "menudeo",
      creditoActivo: !1,
      limiteCredito: "",
    }),
    [c, i] = useState({}),
    s = canManageClientCommercialProfile(a);
  const [submitting, setSubmitting] = useState(false);
  if (
    (useEffect(() => {
      if (!t || !e) return;
      (o({
        tipo: "mayoreo" === e.tipo ? "mayoreo" : "menudeo",
        creditoActivo: Boolean(e.creditoActivo),
        limiteCredito: e.limiteCredito || "",
      }),
        i({}));
      const a = (e) => {
        "Escape" === e.key && l();
      };
      return (
        document.addEventListener("keydown", a),
        () => document.removeEventListener("keydown", a)
      );
    }, [t, e?.id]),
    !t || !e || !s)
  )
    return null;
  const m = (e) => {
    (o((t) => ({
      ...t,
      tipo: e,
      ...("menudeo" === e ? { creditoActivo: !1, limiteCredito: "" } : {}),
    })),
      i({}));
  };
  return React.createElement(
    "div",
    {
      "data-od-id": "client-commercial-modal",
      role: "dialog",
      "aria-modal": "true",
      "aria-labelledby": "client-commercial-heading",
      style: {
        position: "fixed",
        inset: 0,
        padding: 16,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 110,
      },
    },
    React.createElement(
      "div",
      { className: "card client-form-modal" },
      React.createElement(
        "div",
        {
          style: {
            minHeight: 64,
            padding: "12px 16px 12px 24px",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 16,
          },
        },
        React.createElement(
          "div",
          null,
          React.createElement(
            "h2",
            {
              "data-od-id": "client-commercial-heading",
              id: "client-commercial-heading",
              style: { fontSize: 17, fontWeight: 600 },
            },
            "Condiciones comerciales",
          ),
          React.createElement(
            "p",
            { style: { marginTop: 3, color: "var(--muted)", fontSize: 12 } },
            "Configuración exclusiva de administración.",
          ),
        ),
        React.createElement(
          "button",
          {
            "data-od-id": "close-client-commercial-control",
            type: "button",
            className: "btn-ghost",
            "aria-label": "Cerrar condiciones comerciales",
            onClick: l,
            style: {
              minWidth: 44,
              minHeight: 44,
              padding: 0,
              display: "grid",
              placeItems: "center",
            },
          },
          React.createElement(Icons.Close, null),
        ),
      ),
      React.createElement(
        "form",
        {
          "data-od-id": "client-commercial-form",
          onSubmit: async (e) => {
            e.preventDefault();
            const t = {};
            ("mayoreo" === r.tipo &&
              r.creditoActivo &&
              (!r.limiteCredito || Number(r.limiteCredito) <= 0) &&
              (t.limiteCredito = "Define un límite mayor a cero."),
              i(t),
              Object.keys(t).length > 0);
            if (Object.keys(t).length > 0) return;
            setSubmitting(true);
            try {
              await n({
                tipo: r.tipo,
                creditoActivo: "mayoreo" === r.tipo && r.creditoActivo,
                limiteCredito:
                  "mayoreo" === r.tipo && r.creditoActivo
                    ? Number(r.limiteCredito)
                    : null,
              });
            } catch (error) {
              i((current) => ({ ...current, submit: error.message }));
            } finally {
              setSubmitting(false);
            }
          },
          noValidate: !0,
        },
        c.submit &&
          React.createElement(
            "div",
            {
              className: "client-form-error",
              role: "alert",
              style: { padding: "0 24px" },
            },
            c.submit,
          ),
        React.createElement(
          "div",
          { style: { display: "grid", gap: 20, padding: 24 } },
          React.createElement(
            "div",
            { className: "client-admin-summary" },
            React.createElement(
              "div",
              { style: { minWidth: 0 } },
              React.createElement(
                "div",
                { style: { fontWeight: 600 } },
                e.nombre,
              ),
              React.createElement(
                "div",
                {
                  style: {
                    marginTop: 3,
                    color: "var(--muted)",
                    fontSize: 12,
                    overflowWrap: "anywhere",
                  },
                },
                e.email,
              ),
            ),
            React.createElement(
              "span",
              {
                className:
                  "pill pill-" + ("mayoreo" === r.tipo ? "gold" : "muted"),
              },
              r.tipo,
            ),
          ),
          React.createElement(
            "div",
            { className: "client-commercial-section" },
            React.createElement(
              "span",
              { className: "client-form-label", id: "commercial-type-label" },
              "Clasificación del cliente",
            ),
            React.createElement(
              "div",
              {
                className: "client-type-group",
                role: "group",
                "aria-labelledby": "commercial-type-label",
              },
              React.createElement(
                "button",
                {
                  "data-od-id": "commercial-type-retail-control",
                  type: "button",
                  className: "btn-secondary client-type-button",
                  "aria-pressed": "menudeo" === r.tipo,
                  onClick: () => m("menudeo"),
                },
                "Menudeo",
              ),
              React.createElement(
                "button",
                {
                  "data-od-id": "commercial-type-wholesale-control",
                  type: "button",
                  className: "btn-secondary client-type-button",
                  "aria-pressed": "mayoreo" === r.tipo,
                  onClick: () => m("mayoreo"),
                },
                "Mayoreo",
              ),
            ),
            React.createElement(
              "span",
              { className: "client-commercial-note" },
              "menudeo" === r.tipo
                ? "El perfil de menudeo no puede utilizar crédito."
                : "El precio de mayoreo se aplicará en el POS.",
            ),
          ),
          "mayoreo" === r.tipo &&
            React.createElement(
              "div",
              { className: "client-commercial-section" },
              React.createElement(
                "span",
                {
                  className: "client-form-label",
                  id: "commercial-credit-label",
                },
                "¿Cuenta con línea de crédito?",
              ),
              React.createElement(
                "div",
                {
                  className: "client-type-group",
                  role: "group",
                  "aria-labelledby": "commercial-credit-label",
                },
                React.createElement(
                  "button",
                  {
                    "data-od-id": "commercial-credit-disabled-control",
                    type: "button",
                    className: "btn-secondary client-type-button",
                    "aria-pressed": !r.creditoActivo,
                    onClick: () => {
                      (o((e) => ({
                        ...e,
                        creditoActivo: !1,
                        limiteCredito: "",
                      })),
                        i({}));
                    },
                  },
                  "Sin crédito",
                ),
                React.createElement(
                  "button",
                  {
                    "data-od-id": "commercial-credit-enabled-control",
                    type: "button",
                    className: "btn-secondary client-type-button",
                    "aria-pressed": r.creditoActivo,
                    onClick: () => o((e) => ({ ...e, creditoActivo: !0 })),
                  },
                  "Con crédito",
                ),
              ),
              !r.creditoActivo &&
                React.createElement(
                  "span",
                  { className: "client-commercial-note" },
                  "Podrá comprar a precio mayoreo, pero no utilizar ventas a crédito.",
                ),
            ),
          "mayoreo" === r.tipo &&
            r.creditoActivo &&
            React.createElement(
              "div",
              { className: "client-form-field" },
              React.createElement(
                "label",
                {
                  className: "client-form-label",
                  htmlFor: "commercial-credit-limit",
                },
                "Límite de crédito",
              ),
              React.createElement("input", {
                "data-od-id": "commercial-credit-limit-input",
                id: "commercial-credit-limit",
                type: "number",
                inputMode: "decimal",
                min: "1",
                step: "1000",
                placeholder: "0.00",
                value: r.limiteCredito,
                onChange: (e) => {
                  (o((t) => ({ ...t, limiteCredito: e.target.value })),
                    c.limiteCredito && i({}));
                },
                "aria-invalid": Boolean(c.limiteCredito),
                "aria-describedby": c.limiteCredito
                  ? "commercial-credit-limit-error"
                  : "commercial-credit-limit-note",
              }),
              React.createElement(
                "span",
                {
                  id: "commercial-credit-limit-note",
                  className: "client-credit-note",
                },
                "Este límite controla la disponibilidad de ventas a crédito en el POS.",
              ),
              React.createElement(
                "span",
                {
                  id: "commercial-credit-limit-error",
                  className: "client-form-error",
                },
                c.limiteCredito || "",
              ),
            ),
        ),
        React.createElement(
          "div",
          {
            style: {
              padding: "16px 24px",
              borderTop: "1px solid var(--border)",
              display: "flex",
              justifyContent: "flex-end",
              gap: 8,
            },
          },
          React.createElement(
            "button",
            {
              "data-od-id": "cancel-client-commercial-control",
              type: "button",
              className: "btn-secondary",
              onClick: l,
              style: { minHeight: 44 },
            },
            "Cancelar",
          ),
          React.createElement(
            "button",
            {
              "data-od-id": "save-client-commercial-cta",
              type: "submit",
              className: "btn-primary",
              disabled: submitting,
              style: { minHeight: 44 },
            },
            submitting ? "Guardando…" : "Guardar cambios",
          ),
        ),
      ),
    ),
  );
}
function ClientSelectorModal({
  open,
  clientes,
  selectedClient,
  onClose,
  onSelect,
}) {
  const [search, setSearch] = useState("");
  useEffect(() => {
    if (!open) return void 0;
    setSearch("");
    const handleEscape = (event) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [open]);
  if (!open) return null;
  const term = search.trim().toLocaleLowerCase("es-MX");
  const filteredClients = clientes.filter((client) =>
    [client.nombre, client.telefono, client.email]
      .filter(Boolean)
      .some((value) => value.toLocaleLowerCase("es-MX").includes(term)),
  );
  return /* @__PURE__ */ React.createElement(
    "div",
    {
      className: "modal-backdrop",
      "data-od-id": "pos-client-selector-modal",
      role: "dialog",
      "aria-modal": "true",
      "aria-labelledby": "pos-client-selector-heading",
    },
    /* @__PURE__ */ React.createElement(
      "div",
      { className: "card client-selector-modal" },
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "modal-header" },
        /* @__PURE__ */ React.createElement(
          "div",
          null,
          /* @__PURE__ */ React.createElement(
            "h2",
            {
              id: "pos-client-selector-heading",
              "data-od-id": "pos-client-selector-heading",
              className: "modal-title",
            },
            "Seleccionar cliente",
          ),
          /* @__PURE__ */ React.createElement(
            "p",
            { className: "modal-subtitle" },
            "Busca por nombre, tel\xE9fono o correo.",
          ),
        ),
        /* @__PURE__ */ React.createElement(
          "button",
          {
            "data-od-id": "close-pos-client-selector-control",
            type: "button",
            className: "btn-ghost modal-close",
            "aria-label": "Cerrar selector de cliente",
            onClick: onClose,
          },
          /* @__PURE__ */ React.createElement(Icons.Close, null),
        ),
      ),
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "client-selector-search" },
        /* @__PURE__ */ React.createElement(Icons.Search, null),
        /* @__PURE__ */ React.createElement("input", {
          "data-od-id": "pos-client-search-input",
          type: "search",
          value: search,
          onChange: (event) => setSearch(event.target.value),
          placeholder: "Buscar cliente...",
          "aria-label": "Buscar cliente",
          autoFocus: true,
        }),
      ),
      /* @__PURE__ */ React.createElement(
        "div",
        {
          className: "client-selector-list",
          role: "listbox",
          "aria-label": "Clientes disponibles",
        },
        /* @__PURE__ */ React.createElement(
          "button",
          {
            "data-od-id": "pos-public-general-option",
            type: "button",
            className: "client-selector-option",
            role: "option",
            "aria-selected": !selectedClient,
            onClick: () => onSelect(null),
          },
          /* @__PURE__ */ React.createElement(
            "span",
            { className: "client-option-main" },
            /* @__PURE__ */ React.createElement(
              "strong",
              null,
              "P\xFAblico general",
            ),
            /* @__PURE__ */ React.createElement(
              "small",
              null,
              "Venta sin cliente registrado",
            ),
          ),
          !selectedClient &&
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "client-option-check", "aria-hidden": "true" },
              "\u2713",
            ),
        ),
        filteredClients.map((client) => {
          const isSelected = selectedClient?.id === client.id;
          const availableCredit = client.creditoActivo
            ? Math.max(0, (client.limiteCredito || 0) - (client.saldo || 0))
            : null;
          return /* @__PURE__ */ React.createElement(
            "button",
            {
              key: client.id,
              "data-od-id": `pos-client-option-${client.id}`,
              type: "button",
              className: "client-selector-option",
              role: "option",
              "aria-selected": isSelected,
              onClick: () => onSelect(client),
            },
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "client-option-main" },
              /* @__PURE__ */ React.createElement(
                "span",
                { className: "client-option-title" },
                /* @__PURE__ */ React.createElement(
                  "strong",
                  null,
                  client.nombre,
                ),
                /* @__PURE__ */ React.createElement(
                  "span",
                  {
                    className: `pill pill-${client.tipo === "mayoreo" ? "gold" : "muted"}`,
                  },
                  client.tipo,
                ),
              ),
              /* @__PURE__ */ React.createElement(
                "small",
                null,
                client.telefono || client.email || "Sin datos de contacto",
              ),
              client.creditoActivo &&
                /* @__PURE__ */ React.createElement(
                  "small",
                  null,
                  "Cr\xE9dito disponible: ",
                  formatMoney(availableCredit),
                ),
            ),
            isSelected &&
              /* @__PURE__ */ React.createElement(
                "span",
                { className: "client-option-check", "aria-hidden": "true" },
                "\u2713",
              ),
          );
        }),
        filteredClients.length === 0 &&
          /* @__PURE__ */ React.createElement(
            "div",
            {
              className: "client-selector-empty",
              "data-od-id": "pos-client-search-empty",
            },
            "No encontramos clientes con esa b\xFAsqueda.",
          ),
      ),
    ),
  );
}
function getLocalISODate(date = /* @__PURE__ */ new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
function formatRepairDate(value) {
  if (!value) return "Sin fecha";
  return new Intl.DateTimeFormat("es-MX", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  })
    .format(/* @__PURE__ */ new Date(`${value}T12:00:00`))
    .replace(".", "");
}
function normalizeRepairSeed(repair) {
  const client = CLIENTES.find(
    (item) =>
      item.nombre.startsWith(repair.cliente) ||
      repair.cliente.startsWith(item.nombre),
  );
  return {
    id: repair.id,
    codigo: `RP-${String(repair.id).padStart(4, "0")}`,
    clienteId: client?.id || null,
    cliente: client?.nombre || repair.cliente,
    pieza: repair.producto,
    servicio: repair.servicio,
    fechaRecepcion: repair.fecha,
    fechaEntrega: repair.estimada,
    costo: null,
    pagado: false,
    fechaPago: null,
    entregado: false,
    fechaEntregaReal: null,
    estadoServicio:
      repair.estado === "terminado"
        ? "lista"
        : repair.estado === "en_proceso"
          ? "en_reparacion"
          : "recibida",
    notas: "",
  };
}
function getRepairUrgency(repair, today = getLocalISODate()) {
  if (repair.entregado)
    return {
      key: "entregada",
      label: "Entregada",
      tone: "success",
      days: null,
    };
  const dayMs = 24 * 60 * 60 * 1e3;
  const difference = Math.round(
    /* @__PURE__ */ (new Date(`${repair.fechaEntrega}T12:00:00`) -
      /* @__PURE__ */ new Date(`${today}T12:00:00`)) /
      dayMs,
  );
  if (difference < 0)
    return {
      key: "vencida",
      label: `Vencida hace ${Math.abs(difference)} d\xEDa${Math.abs(difference) === 1 ? "" : "s"}`,
      tone: "danger",
      days: difference,
    };
  if (difference === 0)
    return { key: "hoy", label: "Entrega hoy", tone: "warning", days: 0 };
  if (difference <= 3)
    return {
      key: "proxima",
      label: `Entrega en ${difference} d\xEDa${difference === 1 ? "" : "s"}`,
      tone: "warning",
      days: difference,
    };
  return {
    key: "programada",
    label: "Programada",
    tone: "muted",
    days: difference,
  };
}
function getRepairPaymentLabel(repair) {
  if (repair.paymentKnown === false)
    return { label: "Pago no disponible", tone: "muted" };
  if (repair.pagado) return { label: "Pagada", tone: "success" };
  if (repair.costo > 0) return { label: "Por cobrar", tone: "warning" };
  return { label: "Costo pendiente", tone: "muted" };
}
function repairToPosItem(repair) {
  const availableForSale =
    repair.paymentKnown !== false &&
    Boolean(repair.costo > 0 && !repair.pagado && !repair.entregado);
  const saleStatus = repair.entregado
    ? "Entregada"
    : repair.pagado
      ? "Ya pagada"
      : repair.costo > 0
        ? "Lista para cobrar"
        : "Costo pendiente";
  return {
    id: `repair-${repair.id}`,
    repairId: repair.id,
    clienteId: repair.clienteId,
    sku: repair.codigo,
    nombre: `${repair.pieza} \xB7 ${repair.cliente}`,
    categoria: "RP",
    precio_costo: repair.costo || 0,
    precio_menudeo: repair.costo || 0,
    precio_mayoreo: repair.costo || 0,
    estado: "disponible",
    stock: 1,
    isRepair: true,
    availableForSale,
    saleStatus,
  };
}
function RepairDatePicker({ value, onChange }) {
  const [open, setOpen] = useState(false);
  const initialDate = value
    ? /* @__PURE__ */ new Date(`${value}T12:00:00`)
    : /* @__PURE__ */ new Date(`${getLocalISODate()}T12:00:00`);
  const [viewDate, setViewDate] = useState(
    new Date(initialDate.getFullYear(), initialDate.getMonth(), 1),
  );
  useEffect(() => {
    if (!open) return void 0;
    const handleEscape = (event) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [open]);
  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();
  const monthLabel = new Intl.DateTimeFormat("es-MX", {
    month: "long",
    year: "numeric",
  }).format(viewDate);
  const firstDayOffset = (new Date(year, month, 1).getDay() + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = Array.from({ length: 42 }, (_, index) => {
    const day = index - firstDayOffset + 1;
    if (day < 1 || day > daysInMonth) return null;
    const iso = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    return { day, iso, disabled: iso < getLocalISODate() };
  });
  return /* @__PURE__ */ React.createElement(
    "div",
    { className: "repair-date-picker", "data-od-id": "repair-date-picker" },
    /* @__PURE__ */ React.createElement(
      "button",
      {
        "data-od-id": "repair-date-trigger",
        type: "button",
        className: "btn-secondary repair-date-trigger",
        "aria-haspopup": "dialog",
        "aria-expanded": open,
        onClick: () => setOpen((current) => !current),
      },
      /* @__PURE__ */ React.createElement(
        "span",
        null,
        value ? formatRepairDate(value) : "Seleccionar fecha",
      ),
      /* @__PURE__ */ React.createElement(
        "span",
        { className: "repair-calendar-glyph", "aria-hidden": "true" },
        "\u25A6",
      ),
    ),
    open &&
      /* @__PURE__ */ React.createElement(
        "div",
        {
          className: "repair-calendar",
          role: "dialog",
          "aria-label": "Calendario de entrega estimada",
        },
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "repair-calendar-header" },
          /* @__PURE__ */ React.createElement(
            "button",
            {
              type: "button",
              className: "btn-ghost",
              "aria-label": "Mes anterior",
              onClick: () => setViewDate(new Date(year, month - 1, 1)),
            },
            "\u2039",
          ),
          /* @__PURE__ */ React.createElement("strong", null, monthLabel),
          /* @__PURE__ */ React.createElement(
            "button",
            {
              type: "button",
              className: "btn-ghost",
              "aria-label": "Mes siguiente",
              onClick: () => setViewDate(new Date(year, month + 1, 1)),
            },
            "\u203A",
          ),
        ),
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "repair-calendar-weekdays", "aria-hidden": "true" },
          ["L", "M", "M", "J", "V", "S", "D"].map((day, index) =>
            /* @__PURE__ */ React.createElement(
              "span",
              { key: `${day}-${index}` },
              day,
            ),
          ),
        ),
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "repair-calendar-grid" },
          cells.map((cell, index) =>
            cell
              ? /* @__PURE__ */ React.createElement(
                  "button",
                  {
                    key: cell.iso,
                    "data-od-id": `repair-calendar-day-${cell.iso}`,
                    type: "button",
                    className: "repair-calendar-day",
                    "aria-pressed": value === cell.iso,
                    disabled: cell.disabled,
                    onClick: () => {
                      onChange(cell.iso);
                      setOpen(false);
                    },
                  },
                  cell.day,
                )
              : /* @__PURE__ */ React.createElement("span", {
                  key: `empty-${index}`,
                }),
          ),
        ),
      ),
  );
}
function NewRepairModal({ open, clientes, onClose, onCreate }) {
  const [clientSearch, setClientSearch] = useState("");
  const [selectedClient, setSelectedClient] = useState(null);
  const [piece, setPiece] = useState("");
  const [service, setService] = useState("");
  const [estimatedDate, setEstimatedDate] = useState("");
  const [cost, setCost] = useState("");
  const [errors, setErrors] = useState({});
  useEffect(() => {
    if (!open) return void 0;
    setClientSearch("");
    setSelectedClient(null);
    setPiece("");
    setService("");
    setEstimatedDate("");
    setCost("");
    setErrors({});
    const handleEscape = (event) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [open]);
  if (!open) return null;
  const term = clientSearch.trim().toLocaleLowerCase("es-MX");
  const clientResults = term
    ? clientes
        .filter((client) =>
          [client.nombre, client.telefono, client.email]
            .filter(Boolean)
            .some((value) => value.toLocaleLowerCase("es-MX").includes(term)),
        )
        .slice(0, 6)
    : [];
  const chooseClient = (client) => {
    setSelectedClient(client);
    setClientSearch(client.nombre);
    setErrors((current) => ({ ...current, client: "" }));
  };
  const submitRepair = (event) => {
    event.preventDefault();
    const exactClient =
      selectedClient ||
      clientes.find(
        (client) => client.nombre.toLocaleLowerCase("es-MX") === term,
      );
    const nextErrors = {};
    if (!exactClient)
      nextErrors.client = "Selecciona un cliente de los resultados.";
    if (!piece.trim()) nextErrors.piece = "Describe la pieza recibida.";
    if (!service.trim()) nextErrors.service = "Indica el servicio solicitado.";
    if (!estimatedDate)
      nextErrors.estimatedDate =
        "Selecciona la entrega estimada en el calendario.";
    const parsedCost = cost === "" ? null : Number(cost);
    if (
      parsedCost !== null &&
      (!Number.isFinite(parsedCost) || parsedCost <= 0)
    )
      nextErrors.cost =
        "Ingresa un costo mayor que cero o d\xE9jalo pendiente.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;
    onCreate({
      clienteId: exactClient.id,
      cliente: exactClient.nombre,
      pieza: piece.trim(),
      servicio: service.trim(),
      fechaEntrega: estimatedDate,
      costo: parsedCost,
    });
  };
  return /* @__PURE__ */ React.createElement(
    "div",
    {
      className: "modal-backdrop",
      "data-od-id": "new-repair-modal",
      role: "dialog",
      "aria-modal": "true",
      "aria-labelledby": "new-repair-heading",
    },
    /* @__PURE__ */ React.createElement(
      "div",
      { className: "card repair-form-modal" },
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "modal-header" },
        /* @__PURE__ */ React.createElement(
          "div",
          null,
          /* @__PURE__ */ React.createElement(
            "h2",
            {
              id: "new-repair-heading",
              "data-od-id": "new-repair-heading",
              className: "modal-title",
            },
            "Recibir reparaci\xF3n",
          ),
          /* @__PURE__ */ React.createElement(
            "p",
            { className: "modal-subtitle" },
            "Registra lo esencial; el costo puede completarse despu\xE9s.",
          ),
        ),
        /* @__PURE__ */ React.createElement(
          "button",
          {
            "data-od-id": "close-new-repair-control",
            type: "button",
            className: "btn-ghost modal-close",
            "aria-label": "Cerrar recepci\xF3n de reparaci\xF3n",
            onClick: onClose,
          },
          /* @__PURE__ */ React.createElement(Icons.Close, null),
        ),
      ),
      /* @__PURE__ */ React.createElement(
        "form",
        { onSubmit: submitRepair },
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "repair-form-grid" },
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-field repair-field-full repair-client-field" },
            /* @__PURE__ */ React.createElement(
              "label",
              { htmlFor: "repair-client-search" },
              "Cliente *",
            ),
            /* @__PURE__ */ React.createElement(
              "div",
              { className: "repair-client-search-control" },
              /* @__PURE__ */ React.createElement(Icons.Search, null),
              /* @__PURE__ */ React.createElement("input", {
                id: "repair-client-search",
                "data-od-id": "repair-client-search-input",
                type: "search",
                value: clientSearch,
                onChange: (event) => {
                  setClientSearch(event.target.value);
                  if (
                    selectedClient &&
                    event.target.value !== selectedClient.nombre
                  )
                    setSelectedClient(null);
                },
                placeholder: "Buscar por nombre, tel\xE9fono o correo...",
                autoComplete: "off",
                autoFocus: true,
              }),
            ),
            term &&
              !selectedClient &&
              /* @__PURE__ */ React.createElement(
                "div",
                {
                  className: "repair-client-results",
                  role: "listbox",
                  "aria-label": "Resultados de clientes",
                },
                clientResults.map((client) =>
                  /* @__PURE__ */ React.createElement(
                    "button",
                    {
                      key: client.id,
                      "data-od-id": `repair-client-option-${client.id}`,
                      type: "button",
                      className: "repair-client-option",
                      onClick: () => chooseClient(client),
                    },
                    /* @__PURE__ */ React.createElement(
                      "span",
                      null,
                      /* @__PURE__ */ React.createElement(
                        "strong",
                        null,
                        client.nombre,
                      ),
                      /* @__PURE__ */ React.createElement(
                        "small",
                        null,
                        client.telefono || client.email,
                      ),
                    ),
                    /* @__PURE__ */ React.createElement(
                      "span",
                      {
                        className: `pill pill-${client.tipo === "mayoreo" ? "gold" : "muted"}`,
                      },
                      client.tipo,
                    ),
                  ),
                ),
                clientResults.length === 0 &&
                  /* @__PURE__ */ React.createElement(
                    "div",
                    { className: "repair-client-empty" },
                    "No encontramos clientes con esa b\xFAsqueda.",
                  ),
              ),
            selectedClient &&
              /* @__PURE__ */ React.createElement(
                "div",
                { className: "repair-client-confirmed" },
                /* @__PURE__ */ React.createElement(
                  "span",
                  { "aria-hidden": "true" },
                  "\u2713",
                ),
                " ",
                selectedClient.nombre,
              ),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "repair-form-error" },
              errors.client,
            ),
          ),
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-field" },
            /* @__PURE__ */ React.createElement(
              "label",
              { htmlFor: "repair-piece" },
              "Pieza recibida *",
            ),
            /* @__PURE__ */ React.createElement("input", {
              id: "repair-piece",
              "data-od-id": "repair-piece-input",
              value: piece,
              onChange: (event) => setPiece(event.target.value),
              placeholder: "Ej. Anillo de oro 14K",
            }),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "repair-form-error" },
              errors.piece,
            ),
          ),
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-field" },
            /* @__PURE__ */ React.createElement(
              "label",
              { htmlFor: "repair-service" },
              "Servicio solicitado *",
            ),
            /* @__PURE__ */ React.createElement("input", {
              id: "repair-service",
              "data-od-id": "repair-service-input",
              value: service,
              onChange: (event) => setService(event.target.value),
              placeholder: "Ej. Ajuste de talla",
            }),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "repair-form-error" },
              errors.service,
            ),
          ),
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-field" },
            /* @__PURE__ */ React.createElement(
              "label",
              null,
              "Entrega estimada *",
            ),
            /* @__PURE__ */ React.createElement(RepairDatePicker, {
              value: estimatedDate,
              onChange: (value) => {
                setEstimatedDate(value);
                setErrors((current) => ({ ...current, estimatedDate: "" }));
              },
            }),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "repair-form-error" },
              errors.estimatedDate,
            ),
          ),
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-field" },
            /* @__PURE__ */ React.createElement(
              "label",
              { htmlFor: "repair-cost" },
              "Costo (opcional)",
            ),
            /* @__PURE__ */ React.createElement(
              "div",
              { className: "repair-money-control" },
              /* @__PURE__ */ React.createElement(
                "span",
                { "aria-hidden": "true" },
                "$",
              ),
              /* @__PURE__ */ React.createElement("input", {
                id: "repair-cost",
                "data-od-id": "repair-cost-input",
                type: "number",
                min: "0",
                step: "0.01",
                value: cost,
                onChange: (event) => setCost(event.target.value),
                placeholder: "Pendiente",
              }),
            ),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "repair-field-help" },
              "Puedes capturarlo desde el detalle m\xE1s adelante.",
            ),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "repair-form-error" },
              errors.cost,
            ),
          ),
        ),
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "modal-footer" },
          /* @__PURE__ */ React.createElement(
            "button",
            { type: "button", className: "btn-secondary", onClick: onClose },
            "Cancelar",
          ),
          /* @__PURE__ */ React.createElement(
            "button",
            {
              "data-od-id": "save-new-repair-cta",
              type: "submit",
              className: "btn-primary",
            },
            "Registrar reparaci\xF3n",
          ),
        ),
      ),
    ),
  );
}
function RepairDetailModal({ repair, open, onClose, onUpdate }) {
  const [cost, setCost] = useState("");
  const [serviceStatus, setServiceStatus] = useState("recibida");
  const [costError, setCostError] = useState("");
  useEffect(() => {
    if (!open || !repair) return void 0;
    setCost(repair.costo || "");
    setServiceStatus(repair.estadoServicio || "recibida");
    setCostError("");
    const handleEscape = (event) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [open, repair?.id, repair?.costo, repair?.estadoServicio]);
  if (!open || !repair) return null;
  const urgency = getRepairUrgency(repair);
  const payment = getRepairPaymentLabel(repair);
  const saveChanges = (event) => {
    event.preventDefault();
    const parsedCost = cost === "" ? null : Number(cost);
    if (
      parsedCost !== null &&
      (!Number.isFinite(parsedCost) || parsedCost <= 0)
    ) {
      setCostError("Ingresa un costo mayor que cero o d\xE9jalo pendiente.");
      return;
    }
    onUpdate(repair.id, { costo: parsedCost, estadoServicio: serviceStatus });
    onClose();
  };
  return /* @__PURE__ */ React.createElement(
    "div",
    {
      className: "modal-backdrop",
      "data-od-id": "repair-detail-modal",
      role: "dialog",
      "aria-modal": "true",
      "aria-labelledby": "repair-detail-heading",
    },
    /* @__PURE__ */ React.createElement(
      "div",
      { className: "card repair-detail-modal" },
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "modal-header" },
        /* @__PURE__ */ React.createElement(
          "div",
          null,
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-detail-code" },
            repair.codigo,
          ),
          /* @__PURE__ */ React.createElement(
            "h2",
            {
              id: "repair-detail-heading",
              "data-od-id": "repair-detail-heading",
              className: "modal-title",
            },
            "Detalle de reparaci\xF3n",
          ),
        ),
        /* @__PURE__ */ React.createElement(
          "button",
          {
            "data-od-id": "close-repair-detail-control",
            type: "button",
            className: "btn-ghost modal-close",
            "aria-label": "Cerrar detalle de reparaci\xF3n",
            onClick: onClose,
          },
          /* @__PURE__ */ React.createElement(Icons.Close, null),
        ),
      ),
      /* @__PURE__ */ React.createElement(
        "form",
        { onSubmit: saveChanges },
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "repair-detail-body" },
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-detail-summary" },
            /* @__PURE__ */ React.createElement(
              "div",
              null,
              /* @__PURE__ */ React.createElement("span", null, "Cliente"),
              /* @__PURE__ */ React.createElement(
                "strong",
                null,
                repair.cliente,
              ),
            ),
            /* @__PURE__ */ React.createElement(
              "div",
              null,
              /* @__PURE__ */ React.createElement("span", null, "Pieza"),
              /* @__PURE__ */ React.createElement("strong", null, repair.pieza),
            ),
            /* @__PURE__ */ React.createElement(
              "div",
              null,
              /* @__PURE__ */ React.createElement(
                "span",
                null,
                "Servicio solicitado",
              ),
              /* @__PURE__ */ React.createElement(
                "strong",
                null,
                repair.servicio,
              ),
            ),
            /* @__PURE__ */ React.createElement(
              "div",
              null,
              /* @__PURE__ */ React.createElement(
                "span",
                null,
                "Entrega estimada",
              ),
              /* @__PURE__ */ React.createElement(
                "strong",
                null,
                formatRepairDate(repair.fechaEntrega),
              ),
            ),
          ),
          /* @__PURE__ */ React.createElement(
            "div",
            {
              className: "repair-status-line",
              "data-od-id": "repair-detail-statuses",
            },
            /* @__PURE__ */ React.createElement(
              "span",
              { className: `pill pill-${urgency.tone}` },
              urgency.label,
            ),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: `pill pill-${payment.tone}` },
              payment.label,
            ),
            /* @__PURE__ */ React.createElement(
              "span",
              {
                className: `pill pill-${repair.entregado ? "success" : "muted"}`,
              },
              repair.entregado ? "Entregada" : "Pendiente de entrega",
            ),
          ),
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-detail-edit-grid" },
            /* @__PURE__ */ React.createElement(
              "div",
              { className: "repair-field" },
              /* @__PURE__ */ React.createElement(
                "label",
                { htmlFor: "repair-detail-cost" },
                "Costo de reparaci\xF3n",
              ),
              /* @__PURE__ */ React.createElement(
                "div",
                { className: "repair-money-control" },
                /* @__PURE__ */ React.createElement(
                  "span",
                  { "aria-hidden": "true" },
                  "$",
                ),
                /* @__PURE__ */ React.createElement("input", {
                  id: "repair-detail-cost",
                  "data-od-id": "repair-detail-cost-input",
                  type: "number",
                  min: "0",
                  step: "0.01",
                  value: cost,
                  onChange: (event) => setCost(event.target.value),
                  placeholder: "Pendiente",
                  disabled: repair.pagado,
                }),
              ),
              /* @__PURE__ */ React.createElement(
                "span",
                { className: "repair-field-help" },
                repair.pagado
                  ? "El costo queda bloqueado despu\xE9s del cobro."
                  : `Se cobrar\xE1 en POS con el c\xF3digo ${repair.codigo}.`,
              ),
              /* @__PURE__ */ React.createElement(
                "span",
                { className: "repair-form-error" },
                costError,
              ),
            ),
            /* @__PURE__ */ React.createElement(
              "div",
              { className: "repair-field" },
              /* @__PURE__ */ React.createElement(
                "label",
                { htmlFor: "repair-service-status" },
                "Estado del servicio",
              ),
              /* @__PURE__ */ React.createElement(
                "select",
                {
                  id: "repair-service-status",
                  "data-od-id": "repair-service-status-select",
                  value: serviceStatus,
                  onChange: (event) => setServiceStatus(event.target.value),
                  disabled: repair.entregado,
                },
                /* @__PURE__ */ React.createElement(
                  "option",
                  { value: "recibida" },
                  "Recibida",
                ),
                /* @__PURE__ */ React.createElement(
                  "option",
                  { value: "en_reparacion" },
                  "En reparaci\xF3n",
                ),
                /* @__PURE__ */ React.createElement(
                  "option",
                  { value: "lista" },
                  "Lista para entregar",
                ),
              ),
            ),
          ),
          repair.pagado &&
            !repair.entregado &&
            /* @__PURE__ */ React.createElement(
              "div",
              { className: "repair-ready-strip" },
              /* @__PURE__ */ React.createElement(
                "div",
                null,
                /* @__PURE__ */ React.createElement(
                  "strong",
                  null,
                  "Pago confirmado",
                ),
                /* @__PURE__ */ React.createElement(
                  "span",
                  null,
                  "La pieza ya puede marcarse como entregada.",
                ),
              ),
              /* @__PURE__ */ React.createElement(
                "button",
                {
                  "data-od-id": "mark-repair-delivered-control",
                  type: "button",
                  className: "btn-secondary",
                  onClick: () => {
                    onUpdate(repair.id, {
                      entregado: true,
                      fechaEntregaReal: getLocalISODate(),
                    });
                    onClose();
                  },
                },
                "Marcar entregada",
              ),
            ),
        ),
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "modal-footer" },
          /* @__PURE__ */ React.createElement(
            "button",
            { type: "button", className: "btn-secondary", onClick: onClose },
            "Cancelar",
          ),
          /* @__PURE__ */ React.createElement(
            "button",
            {
              "data-od-id": "save-repair-detail-cta",
              type: "submit",
              className: "btn-primary",
            },
            "Guardar cambios",
          ),
        ),
      ),
    ),
  );
}
function RepairsView({
  clientes,
  reparaciones,
  registrarReparacion,
  actualizarReparacion,
}) {
  const [showNewRepair, setShowNewRepair] = useState(false);
  const [selectedRepairId, setSelectedRepairId] = useState(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const selectedRepair =
    reparaciones.find((repair) => repair.id === selectedRepairId) || null;
  const attentionRepairs = reparaciones
    .filter(
      (repair) =>
        ["vencida", "hoy", "proxima"].includes(getRepairUrgency(repair).key) &&
        !repair.entregado,
    )
    .sort((a, b) => a.fechaEntrega.localeCompare(b.fechaEntrega));
  const overdueCount = attentionRepairs.filter(
    (repair) => getRepairUrgency(repair).key === "vencida",
  ).length;
  const upcomingCount = attentionRepairs.length - overdueCount;
  const unpaidCount = reparaciones.filter(
    (repair) =>
      repair.paymentKnown !== false && repair.costo > 0 && !repair.pagado,
  ).length;
  const readyForDeliveryCount = reparaciones.filter(
    (repair) =>
      repair.deliveryKnown !== false && repair.pagado && !repair.entregado,
  ).length;
  const term = search.trim().toLocaleLowerCase("es-MX");
  const filteredRepairs = reparaciones.filter((repair) => {
    const matchesSearch = [
      repair.codigo,
      repair.cliente,
      repair.pieza,
      repair.servicio,
    ].some((value) => value.toLocaleLowerCase("es-MX").includes(term));
    const matchesFilter =
      filter === "all" ||
      (filter === "attention" &&
        ["vencida", "hoy", "proxima"].includes(getRepairUrgency(repair).key) &&
        !repair.entregado) ||
      (filter === "no_cost" && !repair.costo) ||
      (filter === "paid" && repair.pagado && !repair.entregado) ||
      (filter === "delivered" && repair.entregado);
    return matchesSearch && matchesFilter;
  });
  const registerAndOpen = (data) => {
    const created = registrarReparacion(data);
    setShowNewRepair(false);
    setSelectedRepairId(created.id);
  };
  return /* @__PURE__ */ React.createElement(
    MainLayout,
    {
      title: "Reparaciones",
      actions: /* @__PURE__ */ React.createElement(
        "button",
        {
          "data-od-id": "new-repair-cta",
          type: "button",
          className: "btn-primary",
          onClick: () => setShowNewRepair(true),
          style: {
            minHeight: 44,
            display: "flex",
            alignItems: "center",
            gap: 6,
          },
        },
        /* @__PURE__ */ React.createElement(Icons.Plus, null),
        " Recibir reparaci\xF3n",
      ),
    },
    /* @__PURE__ */ React.createElement(
      "section",
      {
        className: "repair-attention",
        "data-od-id": "repair-attention-region",
      },
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "repair-attention-header" },
        /* @__PURE__ */ React.createElement(
          "div",
          null,
          /* @__PURE__ */ React.createElement(
            "h2",
            null,
            "Atenci\xF3n de entregas",
          ),
          /* @__PURE__ */ React.createElement(
            "p",
            null,
            "Piezas vencidas o con entrega prevista en los pr\xF3ximos tres d\xEDas.",
          ),
        ),
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "repair-metrics", "data-od-id": "repair-metrics" },
          /* @__PURE__ */ React.createElement(
            "span",
            null,
            /* @__PURE__ */ React.createElement(
              "strong",
              { className: "tabular" },
              overdueCount,
            ),
            " vencidas",
          ),
          /* @__PURE__ */ React.createElement(
            "span",
            null,
            /* @__PURE__ */ React.createElement(
              "strong",
              { className: "tabular" },
              upcomingCount,
            ),
            " pr\xF3ximas",
          ),
          /* @__PURE__ */ React.createElement(
            "span",
            null,
            /* @__PURE__ */ React.createElement(
              "strong",
              { className: "tabular" },
              unpaidCount,
            ),
            " por cobrar",
          ),
          /* @__PURE__ */ React.createElement(
            "span",
            null,
            /* @__PURE__ */ React.createElement(
              "strong",
              { className: "tabular" },
              readyForDeliveryCount,
            ),
            " por entregar",
          ),
        ),
      ),
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "repair-attention-list" },
        attentionRepairs.map((repair) => {
          const urgency = getRepairUrgency(repair);
          const payment = getRepairPaymentLabel(repair);
          return /* @__PURE__ */ React.createElement(
            "button",
            {
              key: repair.id,
              "data-od-id": `repair-attention-${repair.id}`,
              type: "button",
              className: "repair-attention-row",
              onClick: () => setSelectedRepairId(repair.id),
            },
            /* @__PURE__ */ React.createElement("span", {
              className: `repair-due-mark repair-due-${urgency.tone}`,
              "aria-hidden": "true",
            }),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "repair-attention-code" },
              repair.codigo,
            ),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: "repair-attention-main" },
              /* @__PURE__ */ React.createElement("strong", null, repair.pieza),
              /* @__PURE__ */ React.createElement(
                "small",
                null,
                repair.cliente,
                " \xB7 ",
                repair.servicio,
              ),
            ),
            /* @__PURE__ */ React.createElement(
              "span",
              { className: `pill pill-${payment.tone}` },
              payment.label,
            ),
            /* @__PURE__ */ React.createElement(
              "span",
              {
                className: `repair-attention-date repair-date-${urgency.tone}`,
              },
              /* @__PURE__ */ React.createElement(
                "strong",
                null,
                urgency.label,
              ),
              /* @__PURE__ */ React.createElement(
                "small",
                null,
                formatRepairDate(repair.fechaEntrega),
              ),
            ),
          );
        }),
        attentionRepairs.length === 0 &&
          /* @__PURE__ */ React.createElement(
            "div",
            { className: "repair-attention-empty" },
            "No hay entregas vencidas ni pr\xF3ximas.",
          ),
      ),
    ),
    /* @__PURE__ */ React.createElement(
      "section",
      {
        className: "card repair-list-card",
        "data-od-id": "repair-list-region",
      },
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "repair-list-toolbar" },
        /* @__PURE__ */ React.createElement(
          "div",
          null,
          /* @__PURE__ */ React.createElement(
            "h2",
            null,
            "Listado de reparaciones",
          ),
          /* @__PURE__ */ React.createElement(
            "p",
            null,
            "Busca por c\xF3digo, cliente, pieza o servicio.",
          ),
        ),
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "repair-list-search" },
          /* @__PURE__ */ React.createElement(Icons.Search, null),
          /* @__PURE__ */ React.createElement("input", {
            "data-od-id": "repair-search-input",
            type: "search",
            value: search,
            onChange: (event) => setSearch(event.target.value),
            placeholder: "Buscar reparaci\xF3n...",
            "aria-label": "Buscar reparaciones",
          }),
        ),
      ),
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "repair-filter-tabs", "data-od-id": "repair-filter-tabs" },
        [
          { key: "all", label: "Todas" },
          { key: "attention", label: "Atenci\xF3n" },
          { key: "no_cost", label: "Sin costo" },
          { key: "paid", label: "Pagadas" },
          { key: "delivered", label: "Entregadas" },
        ].map((option) =>
          /* @__PURE__ */ React.createElement(
            "button",
            {
              key: option.key,
              type: "button",
              className:
                filter === option.key
                  ? "btn-secondary repair-filter-active"
                  : "btn-ghost",
              "aria-pressed": filter === option.key,
              onClick: () => setFilter(option.key),
            },
            option.label,
          ),
        ),
      ),
      /* @__PURE__ */ React.createElement(
        "div",
        { className: "repair-table-wrap" },
        /* @__PURE__ */ React.createElement(
          "table",
          null,
          /* @__PURE__ */ React.createElement(
            "thead",
            null,
            /* @__PURE__ */ React.createElement(
              "tr",
              null,
              /* @__PURE__ */ React.createElement("th", null, "C\xF3digo"),
              /* @__PURE__ */ React.createElement(
                "th",
                null,
                "Pieza y cliente",
              ),
              /* @__PURE__ */ React.createElement("th", null, "Servicio"),
              /* @__PURE__ */ React.createElement("th", null, "Entrega"),
              /* @__PURE__ */ React.createElement(
                "th",
                { style: { textAlign: "right" } },
                "Costo",
              ),
              /* @__PURE__ */ React.createElement("th", null, "Pago"),
              /* @__PURE__ */ React.createElement(
                "th",
                null,
                "Entrega f\xEDsica",
              ),
            ),
          ),
          /* @__PURE__ */ React.createElement(
            "tbody",
            null,
            filteredRepairs.map((repair) => {
              const urgency = getRepairUrgency(repair);
              const payment = getRepairPaymentLabel(repair);
              return /* @__PURE__ */ React.createElement(
                "tr",
                {
                  key: repair.id,
                  "data-od-id": `repair-row-${repair.id}`,
                  className: "repair-table-row",
                  tabIndex: "0",
                  onClick: () => setSelectedRepairId(repair.id),
                  onKeyDown: (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      setSelectedRepairId(repair.id);
                    }
                  },
                },
                /* @__PURE__ */ React.createElement(
                  "td",
                  { className: "mono repair-code-cell" },
                  repair.codigo,
                ),
                /* @__PURE__ */ React.createElement(
                  "td",
                  null,
                  /* @__PURE__ */ React.createElement(
                    "strong",
                    null,
                    repair.pieza,
                  ),
                  /* @__PURE__ */ React.createElement(
                    "small",
                    null,
                    repair.cliente,
                  ),
                ),
                /* @__PURE__ */ React.createElement(
                  "td",
                  null,
                  repair.servicio,
                ),
                /* @__PURE__ */ React.createElement(
                  "td",
                  null,
                  /* @__PURE__ */ React.createElement(
                    "span",
                    { className: `pill pill-${urgency.tone}` },
                    urgency.label,
                  ),
                  /* @__PURE__ */ React.createElement(
                    "small",
                    null,
                    formatRepairDate(repair.fechaEntrega),
                  ),
                ),
                /* @__PURE__ */ React.createElement(
                  "td",
                  {
                    className: "tabular",
                    style: { textAlign: "right", fontWeight: 600 },
                  },
                  repair.costo ? formatMoney(repair.costo) : "Pendiente",
                ),
                /* @__PURE__ */ React.createElement(
                  "td",
                  null,
                  /* @__PURE__ */ React.createElement(
                    "span",
                    { className: `pill pill-${payment.tone}` },
                    payment.label,
                  ),
                ),
                /* @__PURE__ */ React.createElement(
                  "td",
                  null,
                  /* @__PURE__ */ React.createElement(
                    "span",
                    {
                      className: `pill pill-${repair.deliveryKnown === false ? "muted" : repair.entregado ? "success" : "muted"}`,
                    },
                    repair.deliveryKnown === false
                      ? "No disponible"
                      : repair.entregado
                        ? "Entregada"
                        : "Pendiente",
                  ),
                ),
              );
            }),
            filteredRepairs.length === 0 &&
              /* @__PURE__ */ React.createElement(
                "tr",
                null,
                /* @__PURE__ */ React.createElement(
                  "td",
                  { colSpan: "7", className: "repair-table-empty" },
                  "No hay reparaciones con estos criterios.",
                ),
              ),
          ),
        ),
      ),
    ),
    /* @__PURE__ */ React.createElement(NewRepairModal, {
      open: showNewRepair,
      clientes,
      onClose: () => setShowNewRepair(false),
      onCreate: registerAndOpen,
    }),
    /* @__PURE__ */ React.createElement(RepairDetailModal, {
      repair: selectedRepair,
      open: Boolean(selectedRepair),
      onClose: () => setSelectedRepairId(null),
      onUpdate: actualizarReparacion,
    }),
  );
}
function POSView({
  productos = [],
  categorias = [],
  clientes = [],
  sucursales = [],
  currentUser,
  actions = {},
}) {
  const h = React.createElement;
  const branchOptions = sucursales.length ? sucursales : currentUser?.sucursales || [];
  const defaultBranchId = currentUser?.sucursal?.uuid || branchOptions[0]?.uuid;
  const [selectedBranchId, setSelectedBranchId] = useState(defaultBranchId);
  const branchId = selectedBranchId || defaultBranchId;
  const [search, setSearch] = useState("");
  const [cart, setCart] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [showClientSelector, setShowClientSelector] = useState(false);
  const [showNewClient, setShowNewClient] = useState(false);
  const [discountPercent, setDiscountPercent] = useState("0");
  const [discountApprovalId, setDiscountApprovalId] = useState("");
  const [approvalLoading, setApprovalLoading] = useState(false);
  const [approvalError, setApprovalError] = useState("");
  const [approvalSuccess, setApprovalSuccess] = useState("");
  const [quote, setQuote] = useState(null);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [quoteError, setQuoteError] = useState("");
  const [terminals, setTerminals] = useState([]);
  const [terminal, setTerminal] = useState(null);
  const [session, setSession] = useState(null);
  const [openingAmount, setOpeningAmount] = useState("0");
  const [countedCash, setCountedCash] = useState("");
  const [terminalError, setTerminalError] = useState("");
  const [sessionError, setSessionError] = useState("");
  const [openingSession, setOpeningSession] = useState(false);
  const [closingSession, setClosingSession] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState("efectivo");
  const [checkoutError, setCheckoutError] = useState("");
  const [checkoutSuccess, setCheckoutSuccess] = useState("");
  const [checkingOut, setCheckingOut] = useState(false);
  const [checkoutIdempotencyKey, setCheckoutIdempotencyKey] = useState(null);
  const saleType = selectedClient?.tipo === "mayoreo" ? "mayoreo" : "menudeo";
  const canCloseSession = ["admin", "encargado"].includes(currentUser?.rol);
  const creditEligible = Boolean(
    selectedClient?.tipo === "mayoreo" && selectedClient?.creditoActivo,
  );

  const catalog = productos.flatMap((product) => {
    if (product.active === false || product.estado === "baja") return [];
    const category = categorias.find(
      (item) => item.id === product.categoriaId || item.clave === product.categoria,
    );
    return (product.variantes || product.variants || [])
      .filter((variant) => variant.active !== false && variant.estado !== "baja")
      .map((variant) => {
        const branchStock = variant.stockByBranch ?? variant.stock_by_branch;
        const rawStock = branchStock
          ? branchStock[branchId] ?? 0
          : variant.branch_stock ?? variant.branchStock ?? variant.stock;
        const stock =
          rawStock === null || rawStock === undefined || Number.isNaN(Number(rawStock))
            ? null
            : Number(rawStock);
        return {
          variant_id: variant.id,
          product_id: product.id,
          nombre: product.nombre || product.name,
          sku: variant.sku || product.sku,
          variant_value: variant.talla_o_color ?? variant.variant_value ?? "",
          categoria: product.categoria || category?.clave || "",
          categoryGroup: category?.grupo,
          stock,
          precio_menudeo: variant.precio_menudeo ?? variant.retail_price,
          precio_mayoreo: variant.precio_mayoreo ?? variant.wholesale_price,
        };
      });
  });
  const filteredCatalog = catalog.filter((item) => {
    const term = search.trim().toLocaleLowerCase("es-MX");
    return !term || [item.nombre, item.sku, item.variant_value].some((value) =>
      String(value || "").toLocaleLowerCase("es-MX").includes(term),
    );
  });
  const quoteLines = new Map((quote?.lines || []).map((line) => [line.variant_id, line]));
  const openSession = Boolean(session && session.status !== "cerrada");
  const quoteTotal = quote ? Number(quote.total) : null;
  const discountValue = Number(discountPercent || 0);
  const canApproveDiscount = ["admin", "encargado"].includes(currentUser?.rol);

  useEffect(() => {
    if (!branchOptions.some((branch) => branch.uuid === selectedBranchId)) {
      setSelectedBranchId(defaultBranchId);
    }
  }, [branchOptions, defaultBranchId, selectedBranchId]);

  useEffect(() => {
    if (!branchId || typeof actions.getCashTerminals !== "function") {
      setTerminals([]);
      setTerminal(null);
      setTerminalError(branchId ? "La caja no está disponible." : "No hay sucursal asignada.");
      return undefined;
    }
    const controller = new AbortController();
    let active = true;
    setTerminalError("");
    setTerminals([]);
    setTerminal(null);
    setSession(null);
    actions
      .getCashTerminals(controller.signal)
      .then((rows) => {
        if (!active) return;
        const branchTerminals = (Array.isArray(rows) ? rows : []).filter(
          (item) => String(item.branch_id) === String(branchId) && item.active !== false,
        );
        setTerminals(branchTerminals);
        setTerminal(branchTerminals[0] || null);
        if (!branchTerminals.length) setTerminalError("No hay terminal activa en esta sucursal.");
      })
      .catch((error) => {
        if (active && error.name !== "AbortError")
          setTerminalError(error.message || "No se pudieron cargar las terminales.");
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [branchId]);

  useEffect(() => {
    if (!terminal || typeof actions.getCurrentCashSession !== "function") {
      setSession(null);
      return undefined;
    }
    const controller = new AbortController();
    let active = true;
    setSession(null);
    setSessionError("");
    actions
      .getCurrentCashSession(terminal.id, controller.signal)
      .then((current) => {
        if (active) setSession(current);
      })
      .catch((error) => {
        if (active && error.name !== "AbortError")
          setSessionError(error.message || "No se pudo consultar la sesión de caja.");
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [terminal?.id]);

  useEffect(() => {
    if (paymentMethod === "credito" && !creditEligible) setPaymentMethod("efectivo");
  }, [paymentMethod, creditEligible]);

  useEffect(() => {
    if (!branchId || !cart.length || typeof actions.quoteSale !== "function") {
      setQuote(null);
      setQuoteError(cart.length ? "La cotización no está disponible." : "");
      setQuoteLoading(false);
      return undefined;
    }
    const controller = new AbortController();
    let active = true;
    const discount = discountPercent === "" ? 0 : Number(discountPercent);
    setQuote(null);
    setQuoteError("");
    setQuoteLoading(true);
    actions
      .quoteSale(
        {
          branch_id: branchId,
          sale_type: saleType,
          items: cart.map((item) => ({
            variant_id: item.variant_id,
            quantity: item.quantity,
          })),
          discount_percent: Number.isFinite(discount) ? discount : 0,
        },
        controller.signal,
      )
      .then((result) => {
        if (active) setQuote(result);
      })
      .catch((error) => {
        if (active && error.name !== "AbortError")
          setQuoteError(error.message || "No se pudo cotizar la venta.");
      })
      .finally(() => {
        if (active) setQuoteLoading(false);
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [branchId, cart, saleType, discountPercent]);

  useEffect(() => {
    setCheckoutIdempotencyKey(null);
    setDiscountApprovalId("");
    setApprovalError("");
    setApprovalSuccess("");
  }, [branchId, cart, saleType, discountPercent, paymentMethod, session?.id, selectedClient?.id]);

  const generateDiscountApproval = async () => {
    if (!quote || !discountValue || typeof actions.createDiscountApproval !== "function") return;
    setApprovalLoading(true);
    setApprovalError("");
    setApprovalSuccess("");
    try {
      const approval = await actions.createDiscountApproval({
        branch_id: branchId,
        sale_type: saleType,
        items: cart.map((item) => ({ variant_id: item.variant_id, quantity: item.quantity })),
        discount_percent: discountValue,
      });
      setDiscountApprovalId(approval.id);
      setApprovalSuccess("Autorización generada. Comparte el identificador con quien cobrará la venta.");
    } catch (error) {
      setApprovalError(error.message || "No se pudo generar la autorización.");
    } finally {
      setApprovalLoading(false);
    }
  };

  const addToCart = (item) => {
    if (item.stock !== null && item.stock <= 0) return;
    setCart((current) => {
      const existing = current.find((row) => row.variant_id === item.variant_id);
      return existing
        ? current.map((row) =>
            row.variant_id === item.variant_id
              ? { ...row, quantity: row.quantity + 1 }
              : row,
          )
        : [...current, { ...item, quantity: 1 }];
    });
    setCheckoutError("");
    setCheckoutSuccess("");
  };
  const changeQuantity = (variantId, amount) => {
    setCart((current) =>
      current
        .map((item) =>
          item.variant_id === variantId
            ? { ...item, quantity: item.quantity + amount }
            : item,
        )
        .filter((item) => item.quantity > 0),
    );
    setCheckoutSuccess("");
  };
  const openSessionNow = async (event) => {
    event.preventDefault();
    if (!terminal || typeof actions.openCashSession !== "function") return;
    setOpeningSession(true);
    setSessionError("");
    try {
      const opened = await actions.openCashSession(
        terminal.id,
        Number(openingAmount === "" ? 0 : openingAmount),
      );
      setSession(opened);
    } catch (error) {
      setSessionError(error.message || "No se pudo abrir la sesión de caja.");
    } finally {
      setOpeningSession(false);
    }
  };
  const closeSessionNow = async (event) => {
    event.preventDefault();
    if (!session || typeof actions.closeCashSession !== "function") return;
    const counted = Number(countedCash);
    if (!Number.isFinite(counted) || counted < 0) {
      setSessionError("Escribe el efectivo contado para cerrar la caja.");
      return;
    }
    setClosingSession(true);
    setSessionError("");
    try {
      const closed = await actions.closeCashSession(session.id, counted);
      setSession(closed);
      setCountedCash("");
    } catch (error) {
      setSessionError(error.message || "No se pudo cerrar la sesión de caja.");
    } finally {
      setClosingSession(false);
    }
  };
  const checkout = async () => {
    if (!branchId || !openSession || !quote) {
      setCheckoutError("Abre una sesión de caja y espera la cotización antes de cobrar.");
      return;
    }
    if (paymentMethod === "credito" && !creditEligible) {
      setCheckoutError("El crédito requiere un cliente con crédito habilitado.");
      return;
    }
    if (typeof actions.checkoutSale !== "function") {
      setCheckoutError("El cobro no está disponible.");
      return;
    }
    setCheckingOut(true);
    setCheckoutError("");
    setCheckoutSuccess("");
    const idempotencyKey = checkoutIdempotencyKey || crypto.randomUUID();
    setCheckoutIdempotencyKey(idempotencyKey);
    try {
      await actions.checkoutSale(
        {
          branch_id: branchId,
          sale_type: saleType,
          items: cart.map((item) => ({
            variant_id: item.variant_id,
            quantity: item.quantity,
          })),
           discount_percent: Number(discountPercent || 0),
           discount_approval_id: discountApprovalId || null,
           client_id: selectedClient?.id || null,
          cash_session_id: session.id,
          payments: [{ method: paymentMethod, amount: quote.total }],
        },
        idempotencyKey,
      );
      setCart([]);
      setQuote(null);
      setCheckoutIdempotencyKey(null);
      setCheckoutSuccess("Venta registrada correctamente.");
    } catch (error) {
      if (error.status >= 400 && error.status < 500) setCheckoutIdempotencyKey(null);
      setCheckoutError(error.message || "No se pudo registrar la venta.");
    } finally {
      setCheckingOut(false);
    }
  };

  const clientSection = h(
    "div",
    { className: "pos-client-selector", "data-od-id": "pos-client-selector" },
    h(
      "button",
      {
        "data-od-id": "pos-client-picker-control",
        type: "button",
        className: "btn-secondary pos-client-picker",
        "aria-haspopup": "dialog",
        "aria-expanded": showClientSelector,
        onClick: () => setShowClientSelector(true),
      },
      h("span", { className: "pos-client-picker-label" }, "Cliente de esta venta"),
      h("span", { className: "pos-client-picker-value" }, selectedClient?.nombre || "Público general"),
      h("span", { className: "pos-client-picker-caret", "aria-hidden": "true" }, "⌄"),
    ),
    h(
      "button",
      {
        "data-od-id": "pos-new-client-control",
        type: "button",
        className: "btn-secondary pos-client-add",
        onClick: () => setShowNewClient(true),
      },
      h(Icons.Plus, null),
      " Nuevo",
    ),
  );
  return h(
    MainLayout,
    { title: "Punto de Venta" },
    h(
      "div",
      {
        style: {
          display: "grid",
          gridTemplateColumns: "minmax(0, 1fr) minmax(320px, 400px)",
          gap: 24,
          minHeight: "calc(100vh - var(--header-height) - 48px)",
        },
      },
      h(
        "section",
        { className: "card", style: { display: "flex", flexDirection: "column", minHeight: 520 } },
        h(
          "div",
          { style: { padding: 16, borderBottom: "1px solid var(--border)" } },
           h("input", {
            "data-od-id": "pos-product-search-input",
            type: "search",
            placeholder: "Buscar producto, variante o SKU...",
            value: search,
            onChange: (event) => setSearch(event.target.value),
            style: { width: "100%" },
            "aria-label": "Buscar producto",
          }),
        ),
        h(
          "div",
          { style: { flex: 1, overflow: "auto", padding: 16 } },
          filteredCatalog.length
            ? h(
                "div",
                {
                  style: {
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(190px, 1fr))",
                    gap: 12,
                  },
                },
                filteredCatalog.map((item) => {
                  const unavailable = item.stock !== null && item.stock <= 0;
                  return h(
                    "button",
                    {
                      key: item.variant_id,
                      type: "button",
                      "data-od-id": `pos-catalog-item-${item.variant_id}`,
                      className: "pos-catalog-item",
                      disabled: unavailable,
                      onClick: () => addToCart(item),
                      style: {
                        padding: 16,
                        textAlign: "left",
                        border: "1px solid var(--border)",
                        borderRadius: 8,
                        background: "var(--surface)",
                        cursor: unavailable ? "not-allowed" : "pointer",
                        opacity: unavailable ? 0.55 : 1,
                      },
                    },
                    h(
                      "div",
                      { style: { display: "flex", gap: 6, alignItems: "center", marginBottom: 5 } },
                      item.categoria &&
                        h(
                          "span",
                          { className: `pill ${item.categoryGroup === "joyeria" ? "pill-gold" : "pill-muted"}` },
                          item.categoria,
                        ),
                      h("strong", null, item.nombre),
                    ),
                    h("div", { className: "mono", style: { fontSize: 11, color: "var(--muted)" } }, item.sku),
                    item.variant_value &&
                      h("div", { style: { fontSize: 12, color: "var(--muted)", marginTop: 6 } }, item.variant_value),
                    h(
                      "div",
                      { style: { display: "flex", justifyContent: "space-between", marginTop: 12, gap: 8 } },
                      h("strong", null, formatMoney(saleType === "mayoreo" ? item.precio_mayoreo : item.precio_menudeo)),
                      h(
                        "span",
                        { style: { fontSize: 12, color: unavailable ? "var(--danger)" : "var(--muted)" } },
                        item.stock === null ? "Stock no disponible" : `Stock: ${item.stock}`,
                      ),
                    ),
                  );
                }),
              )
            : h("div", { style: { padding: 40, textAlign: "center", color: "var(--muted)" } }, "No hay productos disponibles."),
        ),
      ),
      h(
        "section",
        { className: "card", style: { display: "flex", flexDirection: "column" } },
        h(
          "div",
          { style: { padding: 16, borderBottom: "1px solid var(--border)" } },
          h("h2", { style: { fontSize: 17, marginBottom: 12 } }, "Venta"),
          clientSection,
          selectedClient &&
            h(
              "div",
              { style: { marginTop: 8, padding: "7px 10px", background: "var(--gold-bg)", borderRadius: 6, fontSize: 12 } },
              saleType === "mayoreo" ? "Precio mayoreo aplicado" : "Precio menudeo aplicado",
              selectedClient.creditoActivo && " · Crédito habilitado",
            ),
        ),
        h(
          "div",
          { style: { padding: 16, borderBottom: "1px solid var(--border)" } },
          h("div", { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } }, "Caja"),
          branchOptions.length > 1 &&
            h(
              "label",
              { htmlFor: "pos-branch-select", style: { display: "block", marginBottom: 8 } },
              h("span", { style: { display: "block", fontSize: 12, marginBottom: 6 } }, "Sucursal de operación"),
              h(
                "select",
                {
                  id: "pos-branch-select",
                  "data-od-id": "pos-branch-select",
                  value: branchId || "",
                  onChange: (event) => {
                    setSelectedBranchId(event.target.value);
                    setSession(null);
                    setTerminal(null);
                    setCheckoutError("");
                  },
                  style: { width: "100%" },
                },
                branchOptions.map((branch) =>
                  h("option", { key: branch.uuid, value: branch.uuid }, `${branch.id} · ${branch.nombre}`),
                ),
              ),
            ),
          terminal
            ? terminals.length > 1
              ? h(
                  "select",
                  {
                    "data-od-id": "pos-terminal-select",
                    value: terminal.id,
                    onChange: (event) => setTerminal(terminals.find((item) => item.id === event.target.value) || null),
                    style: { width: "100%", marginBottom: 8 },
                  },
                  terminals.map((item) => h("option", { key: item.id, value: item.id }, `${item.code} · ${item.name}`)),
                )
              : h("div", { style: { marginBottom: 8, fontWeight: 500 } }, `${terminal.code} · ${terminal.name}`)
            : h("div", { style: { color: "var(--muted)", marginBottom: 8 } }, "Sin terminal seleccionada"),
          terminalError && h("div", { className: "client-form-error", role: "alert" }, terminalError),
          openSession
            ? h(
                "div",
                { "data-od-id": "pos-cash-session-open" },
                h("div", { className: "pill pill-success", style: { marginBottom: 8 } }, "Sesión abierta"),
                canCloseSession &&
                  h(
                    "form",
                    { onSubmit: closeSessionNow, "data-od-id": "pos-close-cash-session-form" },
                    h("label", { htmlFor: "pos-counted-cash", style: { display: "block", fontSize: 12, marginBottom: 6 } }, "Efectivo contado al cierre"),
                    h(
                      "div",
                      { style: { display: "flex", gap: 8 } },
                      h("input", { id: "pos-counted-cash", type: "number", min: "0", step: "0.01", inputMode: "decimal", value: countedCash, onChange: (event) => setCountedCash(event.target.value), style: { minWidth: 0, flex: 1 }, required: true }),
                      h("button", { className: "btn-secondary", type: "submit", disabled: closingSession }, closingSession ? "Cerrando…" : "Cerrar caja"),
                    ),
                  ),
              )
            : h(
                "form",
                { onSubmit: openSessionNow, "data-od-id": "pos-open-cash-session-form" },
                h("label", { htmlFor: "pos-opening-amount", style: { display: "block", fontSize: 12, marginBottom: 6 } }, "Monto inicial"),
                h(
                  "div",
                  { style: { display: "flex", gap: 8 } },
                  h("input", {
                    id: "pos-opening-amount",
                    type: "number",
                    min: "0",
                    step: "0.01",
                    inputMode: "decimal",
                    value: openingAmount,
                    onChange: (event) => setOpeningAmount(event.target.value),
                    style: { minWidth: 0, flex: 1 },
                  }),
                  h("button", { className: "btn-primary", type: "submit", disabled: openingSession || !terminal }, openingSession ? "Abriendo…" : "Abrir caja"),
                ),
              ),
          sessionError && h("div", { className: "client-form-error", role: "alert", style: { marginTop: 8 } }, sessionError),
        ),
        h(
          "div",
          { style: { flex: 1, overflow: "auto", padding: 16 } },
          cart.length
            ? cart.map((item) => {
                const line = quoteLines.get(item.variant_id);
                return h(
                  "div",
                  { key: item.variant_id, style: { padding: "10px 0", borderBottom: "1px solid var(--border)" } },
                  h(
                    "div",
                    { style: { display: "flex", gap: 8, alignItems: "flex-start" } },
                    h(
                      "div",
                      { style: { flex: 1 } },
                      h("strong", null, item.nombre),
                      h("div", { style: { fontSize: 12, color: "var(--muted)" } }, item.variant_value || item.sku),
                      h("div", { style: { fontSize: 12, color: "var(--muted)" } }, `${item.quantity} × ${line ? formatMoney(line.unit_price) : quoteLoading ? "Calculando…" : "—"}`),
                    ),
                    h("strong", { className: "tabular" }, line ? formatMoney(line.total) : quoteLoading ? "…" : "—"),
                    h(
                      "button",
                      { type: "button", className: "btn-ghost", onClick: () => setCart((current) => current.filter((row) => row.variant_id !== item.variant_id)), "aria-label": `Quitar ${item.nombre}`, style: { padding: 4, color: "var(--danger)" } },
                      h(Icons.Trash, null),
                    ),
                  ),
                  h(
                    "div",
                    { style: { display: "flex", alignItems: "center", gap: 6, marginTop: 6 } },
                    h("button", { type: "button", className: "btn-ghost", onClick: () => changeQuantity(item.variant_id, -1), "aria-label": "Reducir cantidad" }, "−"),
                    h("span", { className: "tabular", "aria-label": "Cantidad" }, item.quantity),
                    h("button", { type: "button", className: "btn-ghost", onClick: () => changeQuantity(item.variant_id, 1), "aria-label": "Aumentar cantidad" }, "+"),
                  ),
                );
              })
            : h("div", { style: { padding: 40, textAlign: "center", color: "var(--muted)" } }, h(Icons.Cart, null), h("p", { style: { marginTop: 12 } }, "Carrito vacío")),
        ),
        h(
          "div",
          { style: { padding: 16, borderTop: "1px solid var(--border)", background: "var(--bg)" } },
          h(
            "div",
            { style: { marginBottom: 12 } },
            h("label", { htmlFor: "pos-general-discount", style: { display: "block", fontSize: 12, marginBottom: 6 } }, "Descuento general (%)"),
            h("input", {
              id: "pos-general-discount",
              "data-od-id": "pos-general-discount-input",
              type: "number",
              min: "0",
              max: "100",
              step: "0.01",
              value: discountPercent,
              onChange: (event) => setDiscountPercent(event.target.value),
              disabled: !cart.length,
             style: { width: "100%" },
           }),
           discountValue > 0 &&
             h(
               "div",
               { className: "pos-approval-card", "data-od-id": "pos-discount-approval" },
               h(
                 "div",
                 { style: { fontWeight: 600, marginBottom: 5 } },
                 quote?.approval_required
                   ? "Este descuento requiere autorización."
                   : "¿Necesitas autorizar este descuento para otro usuario?",
               ),
               h(
                 "div",
                 { style: { color: "var(--muted)", fontSize: 12, marginBottom: 8 } },
                 "La autorización queda ligada a esta sucursal, carrito y porcentaje.",
               ),
               canApproveDiscount &&
                 h(
                   "button",
                   {
                     type: "button",
                     className: "btn-secondary",
                     onClick: generateDiscountApproval,
                     disabled: approvalLoading || !quote || Boolean(quoteError),
                   },
                   approvalLoading ? "Generando…" : "Generar autorización",
                 ),
               h("label", { htmlFor: "pos-discount-approval-id", style: { display: "block", fontSize: 12, marginTop: 10 } }, "Identificador de autorización"),
               h("input", {
                 id: "pos-discount-approval-id",
                 "data-od-id": "pos-discount-approval-input",
                 value: discountApprovalId,
                 onChange: (event) => {
                   setDiscountApprovalId(event.target.value.trim());
                   setApprovalError("");
                   setApprovalSuccess("");
                 },
                 placeholder: "UUID proporcionado por el aprobador",
                 autoComplete: "off",
               }),
               approvalError && h("div", { className: "client-form-error", role: "alert", style: { marginTop: 8 } }, approvalError),
               approvalSuccess && h("div", { className: "client-form-success", role: "status", style: { marginTop: 8 } }, approvalSuccess),
             ),
         ),
          quoteError && h("div", { className: "client-form-error", role: "alert", style: { marginBottom: 10 } }, quoteError),
          h(
            "div",
            { style: { fontSize: 13, marginBottom: 12 } },
            h("div", { style: { display: "flex", justifyContent: "space-between" } }, h("span", null, "Subtotal"), h("span", { className: "tabular" }, quote ? formatMoney(quote.subtotal) : "—")),
            h("div", { style: { display: "flex", justifyContent: "space-between", color: "var(--success)" } }, h("span", null, "Descuento"), h("span", { className: "tabular" }, quote ? `-${formatMoney(quote.discount)}` : "—")),
            h("div", { style: { display: "flex", justifyContent: "space-between", color: "var(--muted)" } }, h("span", null, "Impuesto"), h("span", { className: "tabular" }, quote ? formatMoney(quote.tax) : "—")),
          ),
          h(
            "div",
            { style: { display: "flex", justifyContent: "space-between", alignItems: "baseline", borderTop: "1px solid var(--border)", paddingTop: 10, marginBottom: 12 } },
            h("strong", { style: { fontSize: 18 } }, "Total"),
            h("strong", { style: { fontSize: 24, fontVariantNumeric: "tabular-nums" } }, quoteLoading ? "Calculando…" : quoteTotal === null ? "—" : formatMoney(quoteTotal)),
          ),
          h(
            "div",
            { style: { display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 8 } },
            [
              ["efectivo", "Efectivo"],
              ["tarjeta", "Tarjeta"],
              ["transferencia", "Transferencia"],
              ["credito", "Crédito"],
            ].map(([value, label]) =>
              h(
                "button",
                {
                  key: value,
                  type: "button",
                  className: paymentMethod === value ? "btn-primary" : "btn-secondary",
                  disabled: value === "credito" && !creditEligible,
                  onClick: () => setPaymentMethod(value),
                  title: value === "credito" && !creditEligible ? "Selecciona un cliente con crédito habilitado" : undefined,
                },
                label,
              ),
            ),
          ),
          checkoutError && h("div", { className: "client-form-error", role: "alert", style: { marginTop: 10 } }, checkoutError),
          checkoutSuccess && h("div", { className: "client-form-success", role: "status", style: { marginTop: 10 } }, checkoutSuccess),
          h(
            "button",
            {
              "data-od-id": "confirm-pos-sale-cta",
              type: "button",
              className: "btn-primary",
              style: { width: "100%", marginTop: 12, padding: 14 },
              disabled: !cart.length || !openSession || !quote || quoteLoading || Boolean(quoteError) || checkingOut,
              onClick: checkout,
            },
            checkingOut ? "Registrando…" : "Confirmar Venta",
          ),
        ),
      ),
    ),
    h(ClientSelectorModal, {
      open: showClientSelector,
      clientes,
      selectedClient,
      onClose: () => setShowClientSelector(false),
      onSelect: (client) => {
        setSelectedClient(client);
        setShowClientSelector(false);
      },
    }),
    h(NewClientModal, {
      open: showNewClient,
      origin: "pos",
      onClose: () => setShowNewClient(false),
      onRegister: async (data) => {
        if (typeof actions.registerClient !== "function") throw new Error("El registro de clientes no está disponible.");
        const client = await actions.registerClient(data);
        setSelectedClient(client);
        setShowNewClient(false);
      },
    }),
  );
}
function ClientsView({
  clientes: e,
  registerClient: t,
  updateClient: updateClientAction,
  updateClientCommercialProfile: a,
  currentUser: l,
}) {
  const [n, r] = useState(""),
    [o, c] = useState(!1),
    [i, s] = useState(null),
    m = canManageClientCommercialProfile(l),
    d = n.trim().toLowerCase(),
    u = e.filter(
      (e) =>
        e.nombre.toLowerCase().includes(d) ||
        e.email.toLowerCase().includes(d) ||
        e.telefono.toLowerCase().includes(d),
    );
  const [editClient, setEditClient] = useState(null);
  return React.createElement(
    MainLayout,
    {
      title: "Clientes",
      actions: React.createElement(
        "button",
        {
          "data-od-id": "new-client-cta",
          className: "btn-primary",
          onClick: () => c(!0),
          style: {
            minHeight: 44,
            display: "flex",
            alignItems: "center",
            gap: 6,
          },
        },
        React.createElement(Icons.Plus, null),
        " Nuevo Cliente",
      ),
    },
    React.createElement(
      "div",
      { className: "card", "data-od-id": "clients-table-region" },
      React.createElement(
        "div",
        {
          style: {
            padding: 16,
            borderBottom: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
          },
        },
        React.createElement(
          "div",
          { style: { position: "relative", maxWidth: 400, flex: 1 } },
          React.createElement("input", {
            "data-od-id": "client-search-input",
            type: "search",
            "aria-label": "Buscar clientes",
            placeholder: "Buscar por nombre, teléfono o correo...",
            value: n,
            onChange: (e) => r(e.target.value),
            style: { width: "100%", minHeight: 44, paddingLeft: 36 },
          }),
          React.createElement(
            "div",
            {
              "aria-hidden": "true",
              style: {
                position: "absolute",
                left: 10,
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--muted)",
              },
            },
            React.createElement(Icons.Search, null),
          ),
        ),
        m &&
          React.createElement(
            "span",
            { className: "pill pill-accent" },
            "Gestión administrativa",
          ),
      ),
      React.createElement(
        "div",
        { style: { overflowX: "auto" } },
        React.createElement(
          "table",
          null,
          React.createElement(
            "thead",
            null,
            React.createElement(
              "tr",
              null,
              React.createElement("th", null, "Cliente"),
              React.createElement("th", null, "Tipo"),
              React.createElement("th", null, "Teléfono"),
              React.createElement("th", null, "Email"),
              React.createElement(
                "th",
                { style: { textAlign: "right" } },
                "Saldo Pendiente",
              ),
              React.createElement(
                "th",
                { style: { textAlign: "right" } },
                "Crédito",
              ),
              React.createElement(
                "th",
                { style: { textAlign: "right" } },
                "Disponible",
              ),
              React.createElement(
                "th",
                { style: { textAlign: "right" } },
                "Acciones",
              ),
            ),
          ),
          React.createElement(
            "tbody",
            null,
            u.map((e) => {
              const t =
                  e.creditoActivo && e.limiteCredito
                    ? e.limiteCredito - e.saldo
                    : null,
                a = null !== t && t < 0;
              return React.createElement(
                "tr",
                { key: e.id },
                React.createElement(
                  "td",
                  { style: { fontWeight: 500 } },
                  e.nombre,
                  e.notas &&
                    React.createElement(
                      "div",
                      {
                        style: {
                          marginTop: 3,
                          color: "var(--muted)",
                          fontSize: 11,
                          fontWeight: 400,
                        },
                      },
                      e.notas,
                    ),
                ),
                React.createElement(
                  "td",
                  null,
                  React.createElement(
                    "span",
                    {
                      className:
                        "pill pill-" +
                        ("mayoreo" === e.tipo ? "gold" : "muted"),
                    },
                    e.tipo,
                  ),
                ),
                React.createElement(
                  "td",
                  { className: "mono" },
                  e.telefono || "—",
                ),
                React.createElement(
                  "td",
                  { style: { color: "var(--muted)" } },
                  e.email || "—",
                ),
                React.createElement(
                  "td",
                  {
                    style: {
                      textAlign: "right",
                      color: e.saldo > 0 ? "var(--danger)" : "var(--muted)",
                    },
                    className: "tabular",
                  },
                  e.saldo > 0 ? formatMoney(e.saldo) : "—",
                ),
                React.createElement(
                  "td",
                  { style: { textAlign: "right" }, className: "tabular" },
                  e.creditoActivo && e.limiteCredito
                    ? formatMoney(e.limiteCredito)
                    : React.createElement(
                        "span",
                        { style: { color: "var(--muted)" } },
                        "Sin crédito",
                      ),
                ),
                React.createElement(
                  "td",
                  { style: { textAlign: "right" }, className: "tabular" },
                  null !== t
                    ? React.createElement(
                        "span",
                        {
                          style: {
                            color: a ? "var(--danger)" : "var(--success)",
                            fontWeight: 500,
                          },
                        },
                        a
                          ? "(" + formatMoney(Math.abs(t)) + ")"
                          : formatMoney(t),
                      )
                    : React.createElement(
                        "span",
                        { style: { color: "var(--muted)" } },
                        "—",
                      ),
                ),
                React.createElement(
                  "td",
                  { style: { textAlign: "right", whiteSpace: "nowrap" } },
                  React.createElement(
                    "button",
                    {
                      type: "button",
                      className: "btn-ghost client-admin-action",
                      "aria-label": "Editar datos de " + e.nombre,
                      onClick: () => setEditClient(e),
                    },
                    "Editar",
                  ),
                  m &&
                    React.createElement(
                      "button",
                      {
                        "data-od-id": "manage-client-" + e.id,
                        type: "button",
                        className: "btn-secondary client-admin-action",
                        "aria-label":
                          "Administrar condiciones comerciales de " + e.nombre,
                        onClick: () => s(e),
                      },
                      "Comercial",
                    ),
                ),
              );
            }),
            0 === u.length &&
              React.createElement(
                "tr",
                null,
                React.createElement(
                  "td",
                  {
                    colSpan: 8,
                    style: {
                      padding: 40,
                      textAlign: "center",
                      color: "var(--muted)",
                    },
                  },
                  "No se encontraron clientes con esa búsqueda.",
                ),
              ),
          ),
        ),
      ),
    ),
    React.createElement(NewClientModal, {
      open: o,
      origin: "clients",
      onClose: () => c(!1),
      onRegister: (e) => {
        return t(e).then((client) => {
          c(!1);
          return client;
        });
      },
    }),
    React.createElement(ClientCommercialModal, {
      client: i,
      open: Boolean(i),
      currentUser: l,
      onClose: () => s(null),
      onSave: async (e) => {
        const saved = await a(i.id, e, l);
        if (saved) s(null);
        return saved;
      },
    }),
    React.createElement(ClientEditModal, {
      client: editClient,
      onClose: () => setEditClient(null),
      onSave: updateClientAction,
    }),
  );
}
function TransfersView() {
  const [e, t] = useState([
      {
        id: 1,
        folio: "TR-001",
        productos: [
          {
            sku: "AN-OR-0002",
            nombre: "Anillo Compromiso Diamante",
            cantidad: 1,
          },
        ],
        origenId: "T01",
        destinoId: "T02",
        estado: "pendiente",
        fecha: "2026-08-12",
        notas: "",
      },
      {
        id: 2,
        folio: "TR-002",
        productos: [
          { sku: "AR-PL-0001", nombre: "Aretes Cuarzo Rosa", cantidad: 3 },
        ],
        origenId: "A01",
        destinoId: "T01",
        estado: "en_transito",
        fecha: "2026-08-11",
        notas: "Envío por paquetería",
      },
      {
        id: 3,
        folio: "TR-003",
        productos: [
          { sku: "CO-OR-0001", nombre: "Collar Mano de Fátima", cantidad: 2 },
          {
            sku: "DI-PL-0001",
            nombre: "Dije Elefante de la Suerte",
            cantidad: 5,
          },
        ],
        origenId: "T02",
        destinoId: "T01",
        estado: "recibido",
        fecha: "2026-08-10",
        notas: "",
      },
    ]),
    [a, l] = useState(!1),
    [n, r] = useState(""),
    [o, c] = useState(""),
    [i, s] = useState([]),
    [m, d] = useState("all"),
    [u, p] = useState(""),
    g = (e) => SUCURSALES.find((t) => t.id === e)?.nombre || e,
    y = (e) => {
      const t = {
        pendiente: {
          color: "warning",
          label: "Pendiente",
          next: "Enviar",
          nextEstado: "en_transito",
        },
        en_transito: {
          color: "gold",
          label: "En Tránsito",
          next: "Recibir",
          nextEstado: "recibido",
        },
        recibido: { color: "success", label: "Recibido", next: null },
        cancelado: { color: "danger", label: "Cancelado", next: null },
      };
      return t[e] || t.pendiente;
    },
    R = (a, l) => {
      t(e.map((e) => (e.id === a ? { ...e, estado: l } : e)));
    },
    E = n
      ? PRODUCTOS.filter(
          (e) => "disponible" === e.estado && e.stock > 0,
        ).filter((e) => {
          if (!u.trim()) return !0;
          const t = u.toLowerCase();
          return (
            e.nombre.toLowerCase().includes(t) ||
            e.sku.toLowerCase().includes(t)
          );
        })
      : [],
    v = (e) => {
      const t = i.find((t) => t.sku === e.sku);
      s(
        t
          ? i.filter((t) => t.sku !== e.sku)
          : [...i, { ...e, cantidadTraspaso: 1 }],
      );
    },
    b = (e, t) => {
      s(
        i.map((a) =>
          a.sku === e ? { ...a, cantidadTraspaso: Math.min(t, a.stock) } : a,
        ),
      );
    },
    f = e.filter((e) => "all" === m || e.estado === m);
  return React.createElement(
    MainLayout,
    {
      title: "Traspasos entre Sucursales",
      actions: React.createElement(
        "button",
        {
          className: "btn-primary",
          onClick: () => l(!0),
          style: { display: "flex", alignItems: "center", gap: 6 },
        },
        React.createElement(Icons.Plus, null),
        " Nuevo Traspaso",
      ),
    },
    React.createElement(
      "div",
      {
        style: {
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 16,
          marginBottom: 24,
        },
      },
      React.createElement(
        "div",
        { className: "card", style: { padding: 20 } },
        React.createElement(
          "div",
          { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } },
          "Pendientes",
        ),
        React.createElement(
          "div",
          { style: { fontSize: 24, fontWeight: 600, color: "var(--warning)" } },
          e.filter((e) => "pendiente" === e.estado).length,
        ),
      ),
      React.createElement(
        "div",
        { className: "card", style: { padding: 20 } },
        React.createElement(
          "div",
          { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } },
          "En Tránsito",
        ),
        React.createElement(
          "div",
          { style: { fontSize: 24, fontWeight: 600, color: "var(--gold)" } },
          e.filter((e) => "en_transito" === e.estado).length,
        ),
      ),
      React.createElement(
        "div",
        { className: "card", style: { padding: 20 } },
        React.createElement(
          "div",
          { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } },
          "Recibidos (mes)",
        ),
        React.createElement(
          "div",
          { style: { fontSize: 24, fontWeight: 600, color: "var(--success)" } },
          e.filter((e) => "recibido" === e.estado).length,
        ),
      ),
      React.createElement(
        "div",
        { className: "card", style: { padding: 20 } },
        React.createElement(
          "div",
          { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } },
          "Total Piezas Movidas",
        ),
        React.createElement(
          "div",
          { style: { fontSize: 24, fontWeight: 600 } },
          e
            .filter((e) => "recibido" === e.estado)
            .reduce(
              (e, t) => e + t.productos.reduce((e, t) => e + t.cantidad, 0),
              0,
            ),
        ),
      ),
    ),
    React.createElement(
      "div",
      { className: "card" },
      React.createElement(
        "div",
        {
          style: {
            padding: 16,
            borderBottom: "1px solid var(--border)",
            display: "flex",
            gap: 8,
          },
        },
        ["all", "pendiente", "en_transito", "recibido"].map((e) =>
          React.createElement(
            "button",
            {
              key: e,
              className: m === e ? "btn-primary" : "btn-secondary",
              onClick: () => d(e),
              style: { padding: "6px 12px", fontSize: 12 },
            },
            "all" === e ? "Todos" : y(e).label,
          ),
        ),
      ),
      React.createElement(
        "table",
        null,
        React.createElement(
          "thead",
          null,
          React.createElement(
            "tr",
            null,
            React.createElement("th", null, "Folio"),
            React.createElement("th", null, "Productos"),
            React.createElement("th", null, "Origen → Destino"),
            React.createElement("th", null, "Estado"),
            React.createElement("th", null, "Fecha"),
            React.createElement("th", null),
          ),
        ),
        React.createElement(
          "tbody",
          null,
          f.map((e) => {
            const t = y(e.estado);
            return React.createElement(
              "tr",
              { key: e.id },
              React.createElement(
                "td",
                {
                  className: "mono",
                  style: { color: "var(--accent)", fontWeight: 500 },
                },
                e.folio,
              ),
              React.createElement(
                "td",
                null,
                e.productos.map((e, t) =>
                  React.createElement(
                    "div",
                    { key: t, style: { fontSize: 12 } },
                    React.createElement(
                      "span",
                      { style: { fontWeight: 500 } },
                      e.cantidad,
                      "×",
                    ),
                    " ",
                    e.nombre,
                    React.createElement(
                      "span",
                      {
                        className: "mono",
                        style: { color: "var(--muted)", marginLeft: 6 },
                      },
                      e.sku,
                    ),
                  ),
                ),
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "div",
                  { style: { display: "flex", alignItems: "center", gap: 8 } },
                  React.createElement(
                    "span",
                    { className: "pill pill-muted" },
                    e.origenId,
                  ),
                  React.createElement(
                    "span",
                    { style: { color: "var(--muted)" } },
                    "→",
                  ),
                  React.createElement(
                    "span",
                    { className: "pill pill-muted" },
                    e.destinoId,
                  ),
                ),
                React.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 11,
                      color: "var(--muted)",
                      marginTop: 2,
                    },
                  },
                  g(e.origenId),
                  " → ",
                  g(e.destinoId),
                ),
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "span",
                  { className: `pill pill-${t.color}` },
                  t.label,
                ),
              ),
              React.createElement(
                "td",
                {
                  className: "tabular",
                  style: { color: "var(--muted)", fontSize: 12 },
                },
                e.fecha,
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "div",
                  { style: { display: "flex", gap: 4 } },
                  t.next &&
                    React.createElement(
                      "button",
                      {
                        className: "btn-primary",
                        style: { padding: "4px 12px", fontSize: 11 },
                        onClick: () => R(e.id, t.nextEstado),
                      },
                      t.next,
                    ),
                  "pendiente" === e.estado &&
                    React.createElement(
                      "button",
                      {
                        className: "btn-ghost",
                        style: {
                          padding: "4px 8px",
                          fontSize: 11,
                          color: "var(--danger)",
                        },
                        onClick: () => R(e.id, "cancelado"),
                      },
                      "Cancelar",
                    ),
                ),
              ),
            );
          }),
        ),
      ),
    ),
    a &&
      React.createElement(
        "div",
        {
          style: {
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          },
        },
        React.createElement(
          "div",
          {
            className: "card",
            style: {
              width: 900,
              maxHeight: "90vh",
              overflow: "auto",
              padding: 24,
            },
          },
          React.createElement(
            "div",
            {
              style: {
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 20,
              },
            },
            React.createElement(
              "h3",
              { style: { fontSize: 16, fontWeight: 600 } },
              "Nuevo Traspaso",
            ),
            React.createElement(
              "button",
              {
                className: "btn-ghost",
                onClick: () => {
                  (l(!1), s([]), p(""));
                },
              },
              React.createElement(Icons.Close, null),
            ),
          ),
          React.createElement(
            "div",
            {
              style: {
                display: "grid",
                gridTemplateColumns: "1fr auto 1fr",
                gap: 16,
                marginBottom: 20,
              },
            },
            React.createElement(
              "div",
              null,
              React.createElement(
                "label",
                {
                  style: {
                    display: "block",
                    fontSize: 12,
                    fontWeight: 500,
                    marginBottom: 6,
                    color: "var(--muted)",
                  },
                },
                "Sucursal Origen *",
              ),
              React.createElement(
                "select",
                {
                  value: n,
                  onChange: (e) => {
                    (r(e.target.value), s([]), p(""));
                  },
                  style: { width: "100%" },
                },
                React.createElement("option", { value: "" }, "Seleccionar..."),
                SUCURSALES.filter((e) => e.id !== o).map((e) =>
                  React.createElement(
                    "option",
                    { key: e.id, value: e.id },
                    e.nombre,
                    " (",
                    e.id,
                    ")",
                  ),
                ),
              ),
            ),
            React.createElement(
              "div",
              {
                style: {
                  display: "flex",
                  alignItems: "flex-end",
                  paddingBottom: 8,
                  color: "var(--muted)",
                },
              },
              "→",
            ),
            React.createElement(
              "div",
              null,
              React.createElement(
                "label",
                {
                  style: {
                    display: "block",
                    fontSize: 12,
                    fontWeight: 500,
                    marginBottom: 6,
                    color: "var(--muted)",
                  },
                },
                "Sucursal Destino *",
              ),
              React.createElement(
                "select",
                {
                  value: o,
                  onChange: (e) => c(e.target.value),
                  style: { width: "100%" },
                },
                React.createElement("option", { value: "" }, "Seleccionar..."),
                SUCURSALES.filter((e) => e.id !== n).map((e) =>
                  React.createElement(
                    "option",
                    { key: e.id, value: e.id },
                    e.nombre,
                    " (",
                    e.id,
                    ")",
                  ),
                ),
              ),
            ),
          ),
          n &&
            React.createElement(
              "div",
              {
                style: {
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 20,
                },
              },
              React.createElement(
                "div",
                null,
                React.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 8,
                      color: "var(--muted)",
                    },
                  },
                  "Productos disponibles en ",
                  g(n),
                ),
                React.createElement(
                  "div",
                  { style: { position: "relative", marginBottom: 12 } },
                  React.createElement("input", {
                    type: "text",
                    placeholder: "Buscar por nombre o SKU...",
                    value: u,
                    onChange: (e) => p(e.target.value),
                    style: { width: "100%", paddingLeft: 36 },
                  }),
                  React.createElement(
                    "span",
                    {
                      style: {
                        position: "absolute",
                        left: 12,
                        top: "50%",
                        transform: "translateY(-50%)",
                        color: "var(--muted)",
                        display: "flex",
                      },
                    },
                    React.createElement(Icons.Search, null),
                  ),
                  u &&
                    React.createElement(
                      "button",
                      {
                        className: "btn-ghost",
                        onClick: () => p(""),
                        style: {
                          position: "absolute",
                          right: 8,
                          top: "50%",
                          transform: "translateY(-50%)",
                          padding: 4,
                        },
                      },
                      React.createElement(Icons.Close, null),
                    ),
                ),
                React.createElement(
                  "div",
                  {
                    style: {
                      border: "1px solid var(--border)",
                      borderRadius: 6,
                      maxHeight: 300,
                      overflow: "auto",
                    },
                  },
                  E.length > 0
                    ? React.createElement(
                        "table",
                        { style: { marginBottom: 0 } },
                        React.createElement(
                          "thead",
                          null,
                          React.createElement(
                            "tr",
                            null,
                            React.createElement("th", { style: { width: 40 } }),
                            React.createElement("th", null, "SKU"),
                            React.createElement("th", null, "Producto"),
                            React.createElement(
                              "th",
                              { style: { textAlign: "center" } },
                              "Stock",
                            ),
                          ),
                        ),
                        React.createElement(
                          "tbody",
                          null,
                          E.map((e) => {
                            const t = i.find((t) => t.sku === e.sku);
                            return React.createElement(
                              "tr",
                              {
                                key: e.sku,
                                style: {
                                  background: t
                                    ? "var(--accent-light)"
                                    : "transparent",
                                  cursor: "pointer",
                                },
                                onClick: () => v(e),
                              },
                              React.createElement(
                                "td",
                                { style: { textAlign: "center" } },
                                React.createElement("input", {
                                  type: "checkbox",
                                  checked: !!t,
                                  onChange: () => {},
                                  style: { pointerEvents: "none" },
                                }),
                              ),
                              React.createElement(
                                "td",
                                { className: "mono", style: { fontSize: 11 } },
                                e.sku,
                              ),
                              React.createElement(
                                "td",
                                { style: { fontSize: 13 } },
                                e.nombre,
                              ),
                              React.createElement(
                                "td",
                                {
                                  style: { textAlign: "center" },
                                  className: "tabular",
                                },
                                e.stock,
                              ),
                            );
                          }),
                        ),
                      )
                    : React.createElement(
                        "div",
                        {
                          style: {
                            padding: 24,
                            textAlign: "center",
                            color: "var(--muted)",
                            fontSize: 13,
                          },
                        },
                        u
                          ? `No se encontraron productos para "${u}"`
                          : "No hay productos disponibles",
                      ),
                ),
                React.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 11,
                      color: "var(--muted)",
                      marginTop: 6,
                    },
                  },
                  E.length,
                  " producto(s) encontrado(s)",
                ),
              ),
              React.createElement(
                "div",
                null,
                React.createElement(
                  "div",
                  {
                    style: {
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 8,
                    },
                  },
                  React.createElement(
                    "div",
                    {
                      style: {
                        fontSize: 12,
                        fontWeight: 500,
                        color: "var(--muted)",
                      },
                    },
                    "Productos a traspasar",
                  ),
                  i.length > 0 &&
                    React.createElement(
                      "span",
                      { className: "pill pill-accent" },
                      i.length,
                      " seleccionado(s)",
                    ),
                ),
                React.createElement(
                  "div",
                  {
                    style: {
                      border: "1px solid var(--border)",
                      borderRadius: 6,
                      minHeight: 300,
                      maxHeight: 300,
                      overflow: "auto",
                      background: "var(--bg)",
                    },
                  },
                  i.length > 0
                    ? React.createElement(
                        "div",
                        { style: { padding: 12 } },
                        i.map((e, t) =>
                          React.createElement(
                            "div",
                            {
                              key: e.sku,
                              style: {
                                display: "flex",
                                alignItems: "center",
                                gap: 12,
                                padding: "10px 12px",
                                marginBottom: t < i.length - 1 ? 8 : 0,
                                background: "var(--surface)",
                                borderRadius: 6,
                                border: "1px solid var(--border)",
                              },
                            },
                            React.createElement(
                              "div",
                              { style: { flex: 1, minWidth: 0 } },
                              React.createElement(
                                "div",
                                {
                                  style: {
                                    fontWeight: 500,
                                    fontSize: 13,
                                    whiteSpace: "nowrap",
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                  },
                                },
                                e.nombre,
                              ),
                              React.createElement(
                                "div",
                                {
                                  className: "mono",
                                  style: {
                                    fontSize: 11,
                                    color: "var(--muted)",
                                  },
                                },
                                e.sku,
                              ),
                            ),
                            React.createElement(
                              "div",
                              {
                                style: {
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 6,
                                },
                              },
                              React.createElement(
                                "button",
                                {
                                  className: "btn-ghost",
                                  onClick: () =>
                                    b(
                                      e.sku,
                                      Math.max(1, e.cantidadTraspaso - 1),
                                    ),
                                  style: {
                                    padding: "2px 6px",
                                    fontSize: 14,
                                    fontWeight: 600,
                                  },
                                },
                                "−",
                              ),
                              React.createElement("input", {
                                type: "number",
                                min: "1",
                                max: e.stock,
                                value: e.cantidadTraspaso,
                                onChange: (t) =>
                                  b(e.sku, parseInt(t.target.value) || 1),
                                style: {
                                  width: 50,
                                  textAlign: "center",
                                  padding: "4px 2px",
                                },
                              }),
                              React.createElement(
                                "button",
                                {
                                  className: "btn-ghost",
                                  onClick: () =>
                                    b(
                                      e.sku,
                                      Math.min(e.stock, e.cantidadTraspaso + 1),
                                    ),
                                  style: {
                                    padding: "2px 6px",
                                    fontSize: 14,
                                    fontWeight: 600,
                                  },
                                },
                                "+",
                              ),
                              React.createElement(
                                "span",
                                {
                                  style: {
                                    fontSize: 11,
                                    color: "var(--muted)",
                                    width: 40,
                                  },
                                },
                                "/ ",
                                e.stock,
                              ),
                            ),
                            React.createElement(
                              "button",
                              {
                                className: "btn-ghost",
                                onClick: () => v(e),
                                style: { padding: 4, color: "var(--danger)" },
                              },
                              React.createElement(Icons.Trash, null),
                            ),
                          ),
                        ),
                      )
                    : React.createElement(
                        "div",
                        {
                          style: {
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            height: "100%",
                            padding: 24,
                            color: "var(--muted)",
                            textAlign: "center",
                          },
                        },
                        React.createElement(
                          "span",
                          {
                            style: {
                              opacity: 0.3,
                              marginBottom: 8,
                              transform: "scale(2)",
                            },
                          },
                          React.createElement(Icons.Transfer, null),
                        ),
                        React.createElement(
                          "div",
                          { style: { fontSize: 13, marginBottom: 4 } },
                          "Sin productos seleccionados",
                        ),
                        React.createElement(
                          "div",
                          { style: { fontSize: 11 } },
                          "Selecciona productos de la lista izquierda",
                        ),
                      ),
                ),
                i.length > 0 &&
                  React.createElement(
                    "div",
                    {
                      style: {
                        marginTop: 12,
                        padding: 12,
                        background: "var(--accent-light)",
                        borderRadius: 6,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      },
                    },
                    React.createElement(
                      "span",
                      { style: { fontSize: 13, fontWeight: 500 } },
                      "Total a traspasar:",
                    ),
                    React.createElement(
                      "span",
                      {
                        style: {
                          fontSize: 16,
                          fontWeight: 600,
                          color: "var(--accent)",
                        },
                      },
                      i.reduce((e, t) => e + t.cantidadTraspaso, 0),
                      " pieza(s)",
                    ),
                  ),
              ),
            ),
          React.createElement(
            "div",
            {
              style: {
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              },
            },
            React.createElement(
              "div",
              { style: { fontSize: 13 } },
              i.length > 0 &&
                React.createElement(
                  "span",
                  null,
                  React.createElement(
                    "strong",
                    null,
                    i.reduce((e, t) => e + t.cantidadTraspaso, 0),
                  ),
                  " piezas de ",
                  React.createElement("strong", null, i.length),
                  " productos",
                ),
            ),
            React.createElement(
              "div",
              { style: { display: "flex", gap: 8 } },
              React.createElement(
                "button",
                {
                  className: "btn-secondary",
                  onClick: () => {
                    (l(!1), s([]));
                  },
                },
                "Cancelar",
              ),
              React.createElement(
                "button",
                {
                  className: "btn-primary",
                  onClick: () => {
                    if (!n || !o || 0 === i.length) return;
                    const a = {
                      id: e.length + 1,
                      folio: `TR-${String(e.length + 1).padStart(3, "0")}`,
                      productos: i.map((e) => ({
                        sku: e.sku,
                        nombre: e.nombre,
                        cantidad: e.cantidadTraspaso,
                      })),
                      origenId: n,
                      destinoId: o,
                      estado: "pendiente",
                      fecha: new Date().toISOString().split("T")[0],
                      notas: "",
                    };
                    (t([a, ...e]), l(!1), r(""), c(""), s([]), p(""));
                  },
                  disabled: !n || !o || 0 === i.length,
                },
                "Crear Traspaso",
              ),
            ),
          ),
        ),
      ),
  );
}
function CreditsView({ clientes = [], sucursales = [], currentUser, actions = {} }) {
  const h = React.createElement;
  const branchOptions = sucursales.length ? sucursales : currentUser?.sucursales || [];
  const defaultBranchId = currentUser?.sucursal?.uuid || branchOptions[0]?.uuid;
  const [selectedBranchId, setSelectedBranchId] = useState(defaultBranchId);
  const branchId = selectedBranchId || defaultBranchId;
  const [selectedClient, setSelectedClient] = useState(null);
  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState("efectivo");
  const [terminal, setTerminal] = useState(null);
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [paymentIdempotencyKey, setPaymentIdempotencyKey] = useState(null);
  const [ledgerClient, setLedgerClient] = useState(null);
  const [ledgerRows, setLedgerRows] = useState([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerError, setLedgerError] = useState("");
  const currentMonthRange = getCurrentSalesMonthRange();
  const [reportBranchId, setReportBranchId] = useState("");
  const [reportFrom, setReportFrom] = useState(currentMonthRange.from);
  const [reportTo, setReportTo] = useState(currentMonthRange.to);
  const [creditReport, setCreditReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState("");
  const outstanding = clientes.filter((client) => Number(client.saldo || 0) > 0);
  const totalBalance = outstanding.reduce((sum, client) => sum + Number(client.saldo || 0), 0);

  useEffect(() => {
    if (!branchOptions.some((branch) => branch.uuid === selectedBranchId)) {
      setSelectedBranchId(defaultBranchId);
    }
  }, [branchOptions, defaultBranchId, selectedBranchId]);

  useEffect(() => {
    if (!branchId || typeof actions.getCashTerminals !== "function") return undefined;
    const controller = new AbortController();
    actions.getCashTerminals(controller.signal).then((rows) => {
      const branchTerminal = (rows || []).find(
        (row) => String(row.branch_id) === String(branchId) && row.active !== false,
      );
      setTerminal(branchTerminal || null);
      if (!branchTerminal || typeof actions.getCurrentCashSession !== "function") return;
      return actions.getCurrentCashSession(branchTerminal.id, controller.signal).then(setSession);
    }).catch((requestError) => {
      if (requestError.name !== "AbortError") setError(requestError.message);
    });
    return () => controller.abort();
  }, [branchId]);

  useEffect(() => {
    if (typeof actions.getCreditRecoveryReport !== "function") return undefined;
    const controller = new AbortController();
    setReportLoading(true);
    setReportError("");
    actions
      .getCreditRecoveryReport(
        {
          branchId: reportBranchId || undefined,
          dateFrom: reportFrom || undefined,
          dateTo: reportTo || undefined,
          limit: 500,
        },
        controller.signal,
      )
      .then(setCreditReport)
      .catch((requestError) => {
        if (requestError.name !== "AbortError") {
          setCreditReport(null);
          setReportError(requestError.message || "No se pudo cargar el reporte de crédito.");
        }
      })
      .finally(() => setReportLoading(false));
    return () => controller.abort();
  }, [reportBranchId, reportFrom, reportTo]);

  useEffect(() => {
    setPaymentIdempotencyKey(null);
  }, [selectedClient?.id, amount, method, branchId, session?.id]);

  const submitPayment = async (event) => {
    event.preventDefault();
    if (!selectedClient) return;
    const parsedAmount = Number(amount);
    if (!Number.isFinite(parsedAmount) || parsedAmount <= 0) {
      setError("Escribe un importe válido.");
      return;
    }
    if (parsedAmount > Number(selectedClient.saldo || 0)) {
      setError("El abono no puede superar el saldo pendiente.");
      return;
    }
    if (method === "efectivo" && !session) {
      setError("Abre una sesión de caja antes de registrar un abono en efectivo.");
      return;
    }
    setSubmitting(true);
    setError("");
    setSuccess("");
    const idempotencyKey = paymentIdempotencyKey || crypto.randomUUID();
    setPaymentIdempotencyKey(idempotencyKey);
    try {
      await actions.createCreditPayment(
        selectedClient.id,
        {
          branch_id: branchId,
          amount: String(parsedAmount),
          method,
          ...(method === "efectivo" ? { cash_session_id: session.id } : {}),
        },
        idempotencyKey,
      );
      setSuccess("Abono registrado correctamente.");
      setAmount("");
      setSelectedClient(null);
      setPaymentIdempotencyKey(null);
    } catch (requestError) {
      if (requestError.status >= 400 && requestError.status < 500) {
        setPaymentIdempotencyKey(null);
      }
      setError(requestError.message || "No se pudo registrar el abono.");
    } finally {
      setSubmitting(false);
    }
  };
  const openLedger = async (client) => {
    if (typeof actions.getClientCreditLedger !== "function") return;
    setLedgerClient(client);
    setLedgerRows([]);
    setLedgerError("");
    setLedgerLoading(true);
    try {
      setLedgerRows(await actions.getClientCreditLedger(client.id));
    } catch (requestError) {
      setLedgerError(requestError.message || "No se pudo cargar el historial de crédito.");
    } finally {
      setLedgerLoading(false);
    }
  };
  const ledgerContent = ledgerLoading
    ? h("div", { style: { padding: 24 }, role: "status" }, "Cargando historial…")
    : ledgerError
      ? h("div", { className: "client-form-error", role: "alert", style: { margin: 24 } }, ledgerError)
      : h(
          "div",
          { style: { overflowX: "auto", padding: 16 } },
          h(
            "table",
            null,
            h(
              "thead",
              null,
              h(
                "tr",
                null,
                h("th", null, "Fecha"),
                h("th", null, "Movimiento"),
                h("th", null, "Referencia"),
                h("th", null, "Sucursal"),
                h("th", { style: { textAlign: "right" } }, "Importe"),
              ),
            ),
            h(
              "tbody",
              null,
              ledgerRows.map((row) =>
                h(
                  "tr",
                  { key: row.id },
                  h("td", null, new Date(row.created_at).toLocaleString("es-MX")),
                  h(
                    "td",
                    null,
                    { venta_credito: "Venta a crédito", abono: "Abono", ajuste: "Ajuste" }[
                      row.movement_type
                    ] || row.movement_type,
                  ),
                  h("td", { className: "mono" }, row.reference || "—"),
                  h("td", null, row.branch_code || "—"),
                  h(
                    "td",
                    {
                      className: "tabular",
                      style: {
                        textAlign: "right",
                        color: Number(row.quantity) > 0 ? "var(--danger)" : "var(--success)",
                      },
                    },
                    `${Number(row.quantity) > 0 ? "+" : ""}${formatMoney(row.quantity)}`,
                  ),
                ),
              ),
              ledgerRows.length === 0 &&
                h(
                  "tr",
                  null,
                  h(
                    "td",
                    { colSpan: 5, style: { padding: 24, textAlign: "center", color: "var(--muted)" } },
                    "Sin movimientos.",
                  ),
                ),
            ),
          ),
        );
  const reportContent = reportLoading
    ? h("div", { className: "api-read-only-notice", role: "status" }, "Cargando reporte…")
    : reportError
      ? h("div", { className: "client-form-error", role: "alert" }, reportError)
      : creditReport &&
        h(
          "div",
          { className: "credit-report-content" },
          h(
            "div",
            { className: "sales-summary-strip", "data-od-id": "credit-report-summary" },
            h("div", { className: "sales-summary-item" }, h("div", { className: "sales-summary-label" }, "Saldo actual"), h("div", { className: "sales-summary-value" }, formatMoney(creditReport.totals.currentBalance))),
            h("div", { className: "sales-summary-item" }, h("div", { className: "sales-summary-label" }, "Cargos del periodo"), h("div", { className: "sales-summary-value" }, formatMoney(creditReport.totals.periodCharged))),
            h("div", { className: "sales-summary-item" }, h("div", { className: "sales-summary-label" }, "Recuperado"), h("div", { className: "sales-summary-value", style: { color: "var(--success)" } }, formatMoney(creditReport.totals.periodRecovered))),
            h("div", { className: "sales-summary-item" }, h("div", { className: "sales-summary-label" }, "Clientes con saldo"), h("div", { className: "sales-summary-value" }, creditReport.totalClients)),
          ),
          h(
            "div",
            { className: "credit-report-table-wrap" },
            h(
              "table",
              null,
              h("thead", null, h("tr", null, h("th", null, "Cliente"), h("th", { style: { textAlign: "right" } }, "Saldo"), h("th", { style: { textAlign: "right" } }, "Cargo"), h("th", { style: { textAlign: "right" } }, "Recuperado"), h("th", { style: { textAlign: "right" } }, "Neto"), h("th", null, "Último abono"))),
              h(
                "tbody",
                null,
                creditReport.rows.map((row) => h(
                  "tr",
                  { key: row.clientId },
                  h("td", null, h("strong", null, row.clientName), h("div", { style: { color: "var(--muted)", fontSize: 12 } }, row.phone || row.email || "Sin contacto")),
                  h("td", { className: "tabular", style: { textAlign: "right", fontWeight: 600 } }, formatMoney(row.currentBalance)),
                  h("td", { className: "tabular", style: { textAlign: "right" } }, formatMoney(row.periodCharged)),
                  h("td", { className: "tabular", style: { textAlign: "right", color: "var(--success)" } }, formatMoney(row.periodRecovered)),
                  h("td", { className: "tabular", style: { textAlign: "right" } }, formatMoney(row.periodNet)),
                  h("td", null, row.lastPaymentAt ? new Date(row.lastPaymentAt).toLocaleDateString("es-MX") : "Sin abonos"),
                )),
                creditReport.rows.length === 0 && h("tr", null, h("td", { colSpan: 6, style: { padding: 32, textAlign: "center", color: "var(--muted)" } }, "No hay clientes con saldo en el alcance seleccionado.")),
              ),
            ),
          ),
        );

  return h(
    MainLayout,
    { title: "Créditos y cuentas por cobrar" },
    h(
      "div",
      { className: "sales-summary-strip", "data-od-id": "credit-summary" },
      h("div", { className: "sales-summary-item" }, h("div", { className: "sales-summary-label" }, "Saldo pendiente"), h("div", { className: "sales-summary-value" }, formatMoney(totalBalance))),
      h("div", { className: "sales-summary-item" }, h("div", { className: "sales-summary-label" }, "Clientes con saldo"), h("div", { className: "sales-summary-value" }, outstanding.length)),
      h("div", { className: "sales-summary-item" }, h("div", { className: "sales-summary-label" }, "Caja"), h("div", { className: "sales-summary-value" }, session ? "Abierta" : "No abierta")),
    ),
    error && h("div", { className: "client-form-error", role: "alert", style: { marginBottom: 16 } }, error),
    success && h("div", { className: "client-form-success", role: "status", style: { marginBottom: 16 } }, success),
    h(
      "div",
      { className: "card", "data-od-id": "credit-recovery-report", style: { marginBottom: 16 } },
      h(
        "div",
        { style: { padding: 16, borderBottom: "1px solid var(--border)" } },
        h("strong", null, "Reporte de recuperación de crédito"),
        h("div", { style: { color: "var(--muted)", fontSize: 12, marginTop: 4 } }, "El saldo es actual; cargos y recuperaciones corresponden al periodo seleccionado."),
        h(
          "div",
          { className: "credit-report-filters" },
          branchOptions.length > 1 && h("label", null, h("span", null, "Sucursal"), h("select", { value: reportBranchId, onChange: (event) => setReportBranchId(event.target.value) }, h("option", { value: "" }, "Todas las sucursales"), branchOptions.map((branch) => h("option", { key: branch.uuid, value: branch.uuid }, `${branch.id} · ${branch.nombre}`)))),
          h("label", null, h("span", null, "Desde"), h("input", { type: "date", value: reportFrom, onChange: (event) => setReportFrom(event.target.value) })),
          h("label", null, h("span", null, "Hasta"), h("input", { type: "date", value: reportTo, onChange: (event) => setReportTo(event.target.value) })),
        ),
      ),
      h("div", { style: { padding: 16 } }, reportContent),
    ),
    h(
      "div",
      { className: "card", "data-od-id": "credits-api-table" },
      h(
        "div",
        { style: { padding: 16, borderBottom: "1px solid var(--border)" } },
        h("strong", null, "Saldos derivados del ledger"),
        h("div", { style: { color: "var(--muted)", fontSize: 12, marginTop: 4 } }, "Los vencimientos no se aplican en esta fase; el saldo se calcula en el servidor."),
        branchOptions.length > 1 &&
          h(
            "label",
            { htmlFor: "credits-branch-select", style: { display: "block", marginTop: 12 } },
            h("span", { style: { display: "block", fontSize: 12, marginBottom: 6 } }, "Sucursal del abono"),
            h(
              "select",
              {
                id: "credits-branch-select",
                "data-od-id": "credits-branch-select",
                value: branchId || "",
                onChange: (event) => {
                  setSelectedBranchId(event.target.value);
                  setSession(null);
                  setTerminal(null);
                },
                style: { width: "100%" },
              },
              branchOptions.map((branch) =>
                h("option", { key: branch.uuid, value: branch.uuid }, `${branch.id} · ${branch.nombre}`),
              ),
            ),
          ),
      ),
      h(
        "div",
        { style: { overflowX: "auto" } },
        h(
          "table",
          null,
          h("thead", null, h("tr", null, h("th", null, "Cliente"), h("th", null, "Tipo"), h("th", { style: { textAlign: "right" } }, "Saldo"), h("th", { style: { textAlign: "right" } }, "Límite"), h("th", { style: { textAlign: "right" } }, "Acciones"))),
          h(
            "tbody",
            null,
            clientes.map((client) => h(
              "tr",
              { key: client.id },
              h("td", null, h("strong", null, client.nombre), h("div", { style: { color: "var(--muted)", fontSize: 12 } }, client.telefono || client.email || "Sin contacto")),
              h("td", null, client.tipo),
              h("td", { className: "tabular", style: { textAlign: "right", fontWeight: 600 } }, formatMoney(client.saldo || 0)),
              h("td", { className: "tabular", style: { textAlign: "right" } }, client.limiteCredito == null ? "Sin crédito" : formatMoney(client.limiteCredito)),
               h("td", { style: { textAlign: "right", whiteSpace: "nowrap" } },
                 h("button", { type: "button", className: "btn-ghost", onClick: () => openLedger(client) }, "Historial"),
                 Number(client.saldo || 0) > 0 && h("button", { type: "button", className: "btn-secondary", onClick: () => { setSelectedClient(client); setError(""); setSuccess(""); } }, "Registrar abono"),
               ),
            )),
            clientes.length === 0 && h("tr", null, h("td", { colSpan: 5, style: { padding: 40, textAlign: "center", color: "var(--muted)" } }, "No hay clientes registrados.")),
          ),
        ),
      ),
    ),
    selectedClient && h(
      "div",
      { className: "modal-backdrop", role: "dialog", "aria-modal": "true", "aria-labelledby": "credit-payment-heading" },
      h(
        "form",
        { className: "card client-form-modal", onSubmit: submitPayment },
        h("div", { className: "modal-header" }, h("div", null, h("h2", { id: "credit-payment-heading", className: "modal-title" }, "Registrar abono"), h("p", { className: "modal-subtitle" }, selectedClient.nombre)), h("button", { type: "button", className: "btn-ghost modal-close", onClick: () => setSelectedClient(null), "aria-label": "Cerrar" }, h(Icons.Close, null))),
        h("div", { style: { display: "grid", gap: 12, padding: 24 } },
          h("label", { className: "client-form-label", htmlFor: "credit-payment-amount" }, "Importe"),
          h("input", { id: "credit-payment-amount", type: "number", min: "0.01", max: selectedClient.saldo, step: "0.01", value: amount, onChange: (event) => setAmount(event.target.value), required: true }),
          h("label", { className: "client-form-label", htmlFor: "credit-payment-method" }, "Método"),
          h("select", { id: "credit-payment-method", value: method, onChange: (event) => setMethod(event.target.value) }, h("option", { value: "efectivo" }, "Efectivo"), h("option", { value: "tarjeta" }, "Tarjeta"), h("option", { value: "transferencia" }, "Transferencia")),
          method === "efectivo" && h("div", { style: { color: "var(--muted)", fontSize: 12 } }, session ? "Se aplicará a la sesión de caja abierta." : "No hay una sesión de caja abierta."),
        ),
        h("div", { style: { padding: "16px 24px", borderTop: "1px solid var(--border)", display: "flex", justifyContent: "flex-end", gap: 8 } }, h("button", { type: "button", className: "btn-secondary", onClick: () => setSelectedClient(null) }, "Cancelar"), h("button", { type: "submit", className: "btn-primary", disabled: submitting }, submitting ? "Registrando…" : "Registrar abono")),
      ),
    ),
    ledgerClient && h(
      "div",
      { className: "modal-backdrop", role: "dialog", "aria-modal": "true", "aria-labelledby": "credit-ledger-heading" },
      h(
        "div",
        { className: "card client-form-modal" },
        h("div", { className: "modal-header" }, h("div", null, h("h2", { id: "credit-ledger-heading", className: "modal-title" }, "Historial de crédito"), h("p", { className: "modal-subtitle" }, ledgerClient.nombre)), h("button", { type: "button", className: "btn-ghost modal-close", onClick: () => setLedgerClient(null), "aria-label": "Cerrar" }, h(Icons.Close, null))),
        ledgerContent,
      ),
    ),
  );
}
function PromotionsView() {
  const [e, t] = useState([
      {
        id: 1,
        nombre: "2x1 en Pulseras de Hilo",
        tipo: "2x1",
        categoria: "PU",
        activa: !0,
        inicio: "2026-08-01",
        fin: "2026-08-31",
        usada: 45,
      },
      {
        id: 2,
        nombre: "15% en Joyería de Oro",
        tipo: "descuento",
        valor: 15,
        material: "OR",
        activa: !0,
        inicio: "2026-08-10",
        fin: "2026-08-20",
        usada: 12,
      },
      {
        id: 3,
        nombre: "20% Día de las Madres",
        tipo: "descuento",
        valor: 20,
        activa: !1,
        inicio: "2026-05-01",
        fin: "2026-05-10",
        usada: 89,
      },
      {
        id: 4,
        nombre: "Vela gratis +$500",
        tipo: "regalo",
        minimo: 500,
        regalo: "VE-0001",
        activa: !0,
        inicio: "2026-08-01",
        fin: "2026-08-31",
        usada: 23,
      },
    ]),
    [promotionDraft, setPromotionDraft] = useState(null),
    a = (e) =>
      ({ "2x1": "2×1", descuento: "% Desc", regalo: "Regalo", "3x2": "3×2" })[
        e
      ] || e;
  return React.createElement(
    MainLayout,
    {
      title: "Promociones",
      actions: React.createElement(
        React.Fragment,
        null,
        React.createElement(
          "button",
          {
            "data-od-id": "new-promotion-cta",
            className: "btn-primary",
            onClick: () => setPromotionDraft({}),
            style: {
              minHeight: 44,
              display: "flex",
              alignItems: "center",
              gap: 6,
            },
          },
          React.createElement(Icons.Plus, null),
          " Nueva Promoción",
        ),
        React.createElement(PromotionModal, {
          promotion: promotionDraft,
          onClose: () => setPromotionDraft(null),
          onSave: (promotion) => {
            (t((current) =>
              promotion.id
                ? current.map((item) =>
                    item.id === promotion.id ? promotion : item,
                  )
                : [
                    {
                      ...promotion,
                      id: Math.max(0, ...current.map((item) => item.id)) + 1,
                    },
                    ...current,
                  ],
            ),
              setPromotionDraft(null));
          },
        }),
      ),
    },
    React.createElement(
      "div",
      { style: { display: "grid", gridTemplateColumns: "2fr 1fr", gap: 24 } },
      React.createElement(
        "div",
        { className: "card" },
        React.createElement(
          "div",
          {
            style: {
              padding: "16px 20px",
              borderBottom: "1px solid var(--border)",
              fontWeight: 500,
            },
          },
          "Promociones Configuradas",
        ),
        React.createElement(
          "table",
          null,
          React.createElement(
            "thead",
            null,
            React.createElement(
              "tr",
              null,
              React.createElement("th", null, "Promoción"),
              React.createElement("th", null, "Tipo"),
              React.createElement("th", null, "Vigencia"),
              React.createElement("th", null, "Usos"),
              React.createElement("th", null, "Estado"),
            ),
          ),
          React.createElement(
            "tbody",
            null,
            e.map((e) =>
              React.createElement(
                "tr",
                {
                  key: e.id,
                  "data-od-id": `promotion-row-${e.id}`,
                  tabIndex: 0,
                  "aria-label": `Editar promoción ${e.nombre}`,
                  onClick: () => setPromotionDraft(e),
                  onKeyDown: (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      (event.preventDefault(), setPromotionDraft(e));
                    }
                  },
                  style: { cursor: "pointer" },
                },
                React.createElement(
                  "td",
                  null,
                  React.createElement(
                    "div",
                    { style: { fontWeight: 500 } },
                    e.nombre,
                  ),
                  React.createElement(
                    "div",
                    { style: { fontSize: 12, color: "var(--muted)" } },
                    e.valor && `${e.valor}%`,
                    e.minimo && `Mínimo ${formatMoney(e.minimo)}`,
                    e.categoria && ` • Cat: ${e.categoria}`,
                    e.material && ` • Mat: ${e.material}`,
                  ),
                ),
                React.createElement(
                  "td",
                  null,
                  React.createElement(
                    "span",
                    { className: "pill pill-muted" },
                    a(e.tipo),
                  ),
                ),
                React.createElement(
                  "td",
                  { style: { fontSize: 12 } },
                  React.createElement("div", null, e.inicio),
                  React.createElement(
                    "div",
                    { style: { color: "var(--muted)" } },
                    e.fin,
                  ),
                ),
                React.createElement("td", { className: "tabular" }, e.usada),
                React.createElement(
                  "td",
                  null,
                  React.createElement(
                    "span",
                    {
                      className:
                        "pill " + (e.activa ? "pill-success" : "pill-muted"),
                    },
                    e.activa ? "Activa" : "Inactiva",
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
      React.createElement(
        "div",
        null,
        React.createElement(
          "div",
          { className: "card", style: { marginBottom: 16 } },
          React.createElement(
            "div",
            {
              style: {
                padding: "16px 20px",
                borderBottom: "1px solid var(--border)",
                fontWeight: 500,
              },
            },
            "Tipos de Promoción",
          ),
          React.createElement(
            "div",
            { style: { padding: 16 } },
            [
              {
                tipo: "descuento",
                desc: "Porcentaje de descuento aplicado al precio",
              },
              { tipo: "2x1", desc: "Lleva 2, paga 1 (aplica al menor)" },
              { tipo: "3x2", desc: "Lleva 3, paga 2 (aplica al menor)" },
              {
                tipo: "regalo",
                desc: "Producto gratis al superar monto mínimo",
              },
            ].map((e, t) =>
              React.createElement(
                "div",
                { key: t, style: { marginBottom: 12 } },
                React.createElement(
                  "span",
                  { className: "pill pill-gold", style: { marginRight: 8 } },
                  a(e.tipo),
                ),
                React.createElement(
                  "span",
                  { style: { fontSize: 12, color: "var(--muted)" } },
                  e.desc,
                ),
              ),
            ),
          ),
        ),
        React.createElement(
          "div",
          { className: "card" },
          React.createElement(
            "div",
            {
              style: {
                padding: "16px 20px",
                borderBottom: "1px solid var(--border)",
                fontWeight: 500,
              },
            },
            "Resumen del Mes",
          ),
          React.createElement(
            "div",
            { style: { padding: 16 } },
            React.createElement(
              "div",
              {
                style: {
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: 12,
                },
              },
              React.createElement(
                "span",
                { style: { color: "var(--muted)" } },
                "Promociones activas",
              ),
              React.createElement(
                "span",
                { style: { fontWeight: 600 } },
                e.filter((e) => e.activa).length,
              ),
            ),
            React.createElement(
              "div",
              {
                style: {
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: 12,
                },
              },
              React.createElement(
                "span",
                { style: { color: "var(--muted)" } },
                "Total de usos",
              ),
              React.createElement(
                "span",
                { style: { fontWeight: 600 } },
                e.reduce((e, t) => e + t.usada, 0),
              ),
            ),
            React.createElement(
              "div",
              { style: { display: "flex", justifyContent: "space-between" } },
              React.createElement(
                "span",
                { style: { color: "var(--muted)" } },
                "Descuento otorgado",
              ),
              React.createElement(
                "span",
                { style: { fontWeight: 600 } },
                formatMoney(8450),
              ),
            ),
          ),
        ),
      ),
    ),
  );
}
function ReportsView() {
  const [selectedReport, setSelectedReport] = useState(null);
  return React.createElement(
    MainLayout,
    {
      title: "Reportes",
      actions: React.createElement(ReportModal, {
        report: selectedReport,
        onClose: () => setSelectedReport(null),
      }),
    },
    React.createElement(
      "div",
      {
        style: {
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 16,
        },
      },
      [
        {
          title: "Ventas por Periodo",
          desc: "Análisis de ventas diario, semanal y mensual",
        },
        {
          title: "Inventario Valorizado",
          desc: "Valor total del inventario por sucursal",
        },
        {
          title: "Top Productos",
          desc: "Productos más vendidos y margen de ganancia",
        },
        {
          title: "Clientes Activos",
          desc: "Clientes con mayor volumen de compras",
        },
        {
          title: "Cuentas por Cobrar",
          desc: "Estado de créditos y pagos pendientes",
        },
        {
          title: "Reparaciones",
          desc: "Órdenes por estado y tiempo de entrega",
        },
      ].map((e, t) =>
        React.createElement(
          "div",
          {
            key: t,
            className: "card",
            style: { padding: 20, cursor: "pointer" },
          },
          React.createElement(
            "div",
            { style: { fontWeight: 500, marginBottom: 4 } },
            e.title,
          ),
          React.createElement(
            "div",
            {
              style: { fontSize: 13, color: "var(--muted)", marginBottom: 12 },
            },
            e.desc,
          ),
          React.createElement(
            "button",
            {
              "data-od-id": `generate-report-${t}`,
              className: "btn-secondary",
              onClick: () => setSelectedReport(REPORT_DEFINITIONS[t]),
              style: { minHeight: 40, fontSize: 12 },
            },
            "Generar",
          ),
        ),
      ),
    ),
  );
}
function UsersView() {
  const [e, t] = useState(USUARIOS),
    [a, l] = useState(!1),
    [n, r] = useState(null);
  return React.createElement(
    MainLayout,
    {
      title: "Usuarios",
      actions: React.createElement(
        "button",
        {
          className: "btn-primary",
          onClick: () => {
            (r(null), l(!0));
          },
          style: { display: "flex", alignItems: "center", gap: 6 },
        },
        React.createElement(Icons.Plus, null),
        " Nuevo Usuario",
      ),
    },
    React.createElement(
      "div",
      {
        style: {
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 16,
          marginBottom: 24,
        },
      },
      React.createElement(
        "div",
        { className: "card", style: { padding: 20 } },
        React.createElement(
          "div",
          { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } },
          "Total Usuarios",
        ),
        React.createElement(
          "div",
          { style: { fontSize: 24, fontWeight: 600 } },
          e.length,
        ),
      ),
      React.createElement(
        "div",
        { className: "card", style: { padding: 20 } },
        React.createElement(
          "div",
          { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } },
          "Administradores",
        ),
        React.createElement(
          "div",
          { style: { fontSize: 24, fontWeight: 600 } },
          e.filter((e) => "admin" === e.rol).length,
        ),
      ),
      React.createElement(
        "div",
        { className: "card", style: { padding: 20 } },
        React.createElement(
          "div",
          { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } },
          "Encargados",
        ),
        React.createElement(
          "div",
          { style: { fontSize: 24, fontWeight: 600 } },
          e.filter((e) => "encargado" === e.rol).length,
        ),
      ),
      React.createElement(
        "div",
        { className: "card", style: { padding: 20 } },
        React.createElement(
          "div",
          { style: { fontSize: 12, color: "var(--muted)", marginBottom: 8 } },
          "Vendedores",
        ),
        React.createElement(
          "div",
          { style: { fontSize: 24, fontWeight: 600 } },
          e.filter((e) => "vendedor" === e.rol).length,
        ),
      ),
    ),
    React.createElement(
      "div",
      { className: "card" },
      React.createElement(
        "table",
        null,
        React.createElement(
          "thead",
          null,
          React.createElement(
            "tr",
            null,
            React.createElement("th", null, "Usuario"),
            React.createElement("th", null, "Email"),
            React.createElement("th", null, "Rol"),
            React.createElement("th", null, "Sucursales"),
            React.createElement("th", null, "Estado"),
            React.createElement("th", null),
          ),
        ),
        React.createElement(
          "tbody",
          null,
          e.map((a) => {
            return React.createElement(
              "tr",
              { key: a.id },
              React.createElement(
                "td",
                null,
                React.createElement(
                  "div",
                  { style: { display: "flex", alignItems: "center", gap: 10 } },
                  React.createElement(
                    "div",
                    {
                      style: {
                        width: 32,
                        height: 32,
                        borderRadius: "50%",
                        background: "var(--border)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 12,
                        fontWeight: 600,
                      },
                    },
                    a.nombre
                      .split(" ")
                      .map((e) => e[0])
                      .join("")
                      .slice(0, 2),
                  ),
                  React.createElement(
                    "span",
                    { style: { fontWeight: 500 } },
                    a.nombre,
                  ),
                ),
              ),
              React.createElement(
                "td",
                { style: { color: "var(--muted)" } },
                a.email,
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "span",
                  {
                    className: `pill pill-${((n = a.rol), { admin: "danger", encargado: "gold", vendedor: "muted" }[n] || "muted")}`,
                  },
                  a.rol,
                ),
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "div",
                  { style: { display: "flex", gap: 4, flexWrap: "wrap" } },
                  a.sucursales.map((e) =>
                    React.createElement(
                      "span",
                      {
                        key: e,
                        className: "pill pill-muted",
                        style: { fontSize: 10 },
                      },
                      e,
                    ),
                  ),
                ),
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "span",
                  {
                    className: "pill pill-" + (a.activo ? "success" : "muted"),
                  },
                  a.activo ? "Activo" : "Inactivo",
                ),
              ),
              React.createElement(
                "td",
                null,
                React.createElement(
                  "div",
                  { style: { display: "flex", gap: 4 } },
                  React.createElement(
                    "button",
                    {
                      className: "btn-ghost",
                      style: { padding: "4px 8px", fontSize: 11 },
                      onClick: () => {
                        (r(a), l(!0));
                      },
                    },
                    "Editar",
                  ),
                  React.createElement(
                    "button",
                    {
                      className: "btn-ghost",
                      style: {
                        padding: "4px 8px",
                        fontSize: 11,
                        color: a.activo ? "var(--danger)" : "var(--success)",
                      },
                      onClick: () => {
                        return (
                          (l = a.id),
                          void t(
                            e.map((e) =>
                              e.id === l ? { ...e, activo: !e.activo } : e,
                            ),
                          )
                        );
                        var l;
                      },
                    },
                    a.activo ? "Desactivar" : "Activar",
                  ),
                ),
              ),
            );
            var n;
          }),
        ),
      ),
    ),
    a &&
      React.createElement(
        "div",
        {
          style: {
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          },
        },
        React.createElement(
          "div",
          { className: "card", style: { width: 450, padding: 24 } },
          React.createElement(
            "div",
            {
              style: {
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 20,
              },
            },
            React.createElement(
              "h3",
              { style: { fontSize: 16, fontWeight: 600 } },
              n ? "Editar Usuario" : "Nuevo Usuario",
            ),
            React.createElement(
              "button",
              {
                className: "btn-ghost",
                onClick: () => {
                  (l(!1), r(null));
                },
              },
              React.createElement(Icons.Close, null),
            ),
          ),
          React.createElement(
            "form",
            {
              onSubmit: (a) => {
                a.preventDefault();
                const o = a.target,
                  c = {
                    nombre: o.nombre.value,
                    email: o.email.value,
                    rol: o.rol.value,
                    sucursales: Array.from(o.sucursales.selectedOptions).map(
                      (e) => e.value,
                    ),
                    activo: o.activo.checked,
                    pin: o.pin.value,
                  };
                (t(
                  n
                    ? e.map((e) => (e.id === n.id ? { ...e, ...c } : e))
                    : [...e, { id: e.length + 1, ...c }],
                ),
                  l(!1),
                  r(null));
              },
            },
            React.createElement(
              "div",
              {
                style: {
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 12,
                  marginBottom: 12,
                },
              },
              React.createElement(
                "div",
                null,
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "Nombre completo *",
                ),
                React.createElement("input", {
                  name: "nombre",
                  type: "text",
                  defaultValue: n?.nombre || "",
                  style: { width: "100%" },
                  required: !0,
                }),
              ),
              React.createElement(
                "div",
                null,
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "Email *",
                ),
                React.createElement("input", {
                  name: "email",
                  type: "email",
                  defaultValue: n?.email || "",
                  style: { width: "100%" },
                  required: !0,
                }),
              ),
            ),
            React.createElement(
              "div",
              {
                style: {
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 12,
                  marginBottom: 12,
                },
              },
              React.createElement(
                "div",
                null,
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "Rol *",
                ),
                React.createElement(
                  "select",
                  {
                    name: "rol",
                    defaultValue: n?.rol || "vendedor",
                    style: { width: "100%" },
                    required: !0,
                  },
                  React.createElement(
                    "option",
                    { value: "admin" },
                    "Administrador",
                  ),
                  React.createElement(
                    "option",
                    { value: "encargado" },
                    "Encargado",
                  ),
                  React.createElement(
                    "option",
                    { value: "vendedor" },
                    "Vendedor",
                  ),
                ),
              ),
              React.createElement(
                "div",
                null,
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "PIN de autorización *",
                ),
                React.createElement("input", {
                  name: "pin",
                  type: "text",
                  maxLength: "4",
                  defaultValue: n?.pin || "",
                  style: { width: "100%" },
                  placeholder: "4 dígitos",
                  required: !0,
                }),
              ),
            ),
            React.createElement(
              "div",
              { style: { marginBottom: 12 } },
              React.createElement(
                "label",
                {
                  style: {
                    display: "block",
                    fontSize: 12,
                    fontWeight: 500,
                    marginBottom: 6,
                    color: "var(--muted)",
                  },
                },
                "Sucursales asignadas *",
              ),
              React.createElement(
                "select",
                {
                  name: "sucursales",
                  multiple: !0,
                  defaultValue: n?.sucursales || [],
                  style: { width: "100%", height: 80 },
                  required: !0,
                },
                SUCURSALES.map((e) =>
                  React.createElement(
                    "option",
                    { key: e.id, value: e.id },
                    e.nombre,
                    " (",
                    e.id,
                    ")",
                  ),
                ),
              ),
              React.createElement(
                "div",
                {
                  style: { fontSize: 10, color: "var(--muted)", marginTop: 4 },
                },
                "Ctrl/Cmd + clic para seleccionar múltiples",
              ),
            ),
            React.createElement(
              "div",
              { style: { marginBottom: 16 } },
              React.createElement(
                "label",
                {
                  style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    cursor: "pointer",
                  },
                },
                React.createElement("input", {
                  name: "activo",
                  type: "checkbox",
                  defaultChecked: n?.activo ?? !0,
                }),
                React.createElement(
                  "span",
                  { style: { fontSize: 13 } },
                  "Usuario activo",
                ),
              ),
            ),
            React.createElement(
              "div",
              {
                style: { display: "flex", gap: 8, justifyContent: "flex-end" },
              },
              React.createElement(
                "button",
                {
                  type: "button",
                  className: "btn-secondary",
                  onClick: () => {
                    (l(!1), r(null));
                  },
                },
                "Cancelar",
              ),
              React.createElement(
                "button",
                { type: "submit", className: "btn-primary" },
                n ? "Guardar Cambios" : "Crear Usuario",
              ),
            ),
          ),
        ),
      ),
  );
}
function SettingsView() {
  const [e, t] = useState("empresa"),
    [branches, setBranches] = useState(() =>
      SUCURSALES.map((branch) => ({ ...branch, direccion: "", telefono: "" })),
    ),
    [branchDraft, setBranchDraft] = useState(null),
    [savedSection, setSavedSection] = useState(null);
  const saveSettings = (section, event) => {
    const panel = event.currentTarget.closest(".card"),
      controls = Array.from(
        panel?.querySelectorAll("input,select,textarea") || [],
      ),
      values = controls.map((control, index) => ({
        index,
        value: control.value,
        checked: control.checked,
      }));
    (localStorage.setItem(
      `joyeria-settings-${section}`,
      JSON.stringify(values),
    ),
      setSavedSection(section),
      window.setTimeout(
        () =>
          setSavedSection((current) => (current === section ? null : current)),
        2400,
      ));
  };
  return React.createElement(
    MainLayout,
    {
      title: "Configuración",
      actions: React.createElement(
        React.Fragment,
        null,
        savedSection &&
          React.createElement(
            "span",
            {
              "data-od-id": "settings-saved-status",
              className: "pill pill-success",
            },
            "Cambios guardados",
          ),
        React.createElement(BranchModal, {
          branch: branchDraft,
          onClose: () => setBranchDraft(null),
          onSave: (updated) => {
            setBranches((current) => {
              if (updated.id)
                return current.map((branch) =>
                  branch.id === updated.id ? updated : branch,
                );
              const prefix = updated.tipo === "almacen" ? "A" : "T",
                next =
                  Math.max(
                    0,
                    ...current
                      .filter((branch) => branch.id.startsWith(prefix))
                      .map((branch) => Number(branch.id.slice(1)) || 0),
                  ) + 1;
              return [
                ...current,
                { ...updated, id: `${prefix}${String(next).padStart(2, "0")}` },
              ];
            });
            setBranchDraft(null);
          },
        }),
      ),
    },
    React.createElement(
      "div",
      { style: { display: "grid", gridTemplateColumns: "220px 1fr", gap: 24 } },
      React.createElement(
        "div",
        { className: "card", style: { padding: 8, height: "fit-content" } },
        [
          { id: "empresa", label: "Empresa", icon: "🏢" },
          { id: "sucursales", label: "Sucursales", icon: "📍" },
          { id: "ventas", label: "Ventas y Precios", icon: "💰" },
          { id: "impresion", label: "Impresión", icon: "🖨️" },
        ].map((a) =>
          React.createElement(
            "div",
            {
              key: a.id,
              onClick: () => t(a.id),
              style: {
                padding: "10px 12px",
                borderRadius: 6,
                cursor: "pointer",
                background: e === a.id ? "var(--accent-light)" : "transparent",
                color: e === a.id ? "var(--accent)" : "var(--fg)",
                fontWeight: e === a.id ? 500 : 400,
                fontSize: 13,
                display: "flex",
                alignItems: "center",
                gap: 8,
              },
            },
            React.createElement("span", null, a.icon),
            a.label,
          ),
        ),
      ),
      React.createElement(
        "div",
        { className: "card", style: { padding: 24 } },
        "empresa" === e &&
          React.createElement(
            React.Fragment,
            null,
            React.createElement(
              "h2",
              { style: { fontSize: 16, fontWeight: 600, marginBottom: 20 } },
              "Datos de la Empresa",
            ),
            React.createElement(
              "div",
              {
                style: {
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 16,
                },
              },
              React.createElement(
                "div",
                null,
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "Nombre del Negocio",
                ),
                React.createElement("input", {
                  type: "text",
                  defaultValue: "Joyería La Perla",
                  style: { width: "100%" },
                }),
              ),
              React.createElement(
                "div",
                null,
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "RFC",
                ),
                React.createElement("input", {
                  type: "text",
                  defaultValue: "JPE850101ABC",
                  style: { width: "100%" },
                }),
              ),
              React.createElement(
                "div",
                { style: { gridColumn: "1 / -1" } },
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "Dirección Fiscal",
                ),
                React.createElement("input", {
                  type: "text",
                  defaultValue: "Av. Juárez 123, Centro, CDMX",
                  style: { width: "100%" },
                }),
              ),
              React.createElement(
                "div",
                null,
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "Teléfono Principal",
                ),
                React.createElement("input", {
                  type: "text",
                  defaultValue: "55 1234 5678",
                  style: { width: "100%" },
                }),
              ),
              React.createElement(
                "div",
                null,
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "Email",
                ),
                React.createElement("input", {
                  type: "email",
                  defaultValue: "contacto@joyeriaperla.mx",
                  style: { width: "100%" },
                }),
              ),
            ),
            React.createElement(
              "div",
              { style: { marginTop: 24 } },
              React.createElement(
                "button",
                {
                  "data-od-id": `save-settings-${e}`,
                  type: "button",
                  className: "btn-primary",
                  onClick: (event) => saveSettings(e, event),
                },
                "Guardar cambios",
              ),
            ),
          ),
        "sucursales" === e &&
          React.createElement(
            React.Fragment,
            null,
            React.createElement(
              "div",
              {
                style: {
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 20,
                },
              },
              React.createElement(
                "h2",
                { style: { fontSize: 16, fontWeight: 600 } },
                "Sucursales",
              ),
              React.createElement(
                "button",
                {
                  "data-od-id": "new-branch-cta",
                  className: "btn-primary",
                  onClick: () => setBranchDraft({}),
                  style: {
                    minHeight: 44,
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                  },
                },
                React.createElement(Icons.Plus, null),
                " Nueva Sucursal",
              ),
            ),
            React.createElement(
              "table",
              null,
              React.createElement(
                "thead",
                null,
                React.createElement(
                  "tr",
                  null,
                  React.createElement("th", null, "ID"),
                  React.createElement("th", null, "Nombre"),
                  React.createElement("th", null, "Tipo"),
                  React.createElement("th", null, "Dirección"),
                  React.createElement("th", null),
                ),
              ),
              React.createElement(
                "tbody",
                null,
                branches.map((e) =>
                  React.createElement(
                    "tr",
                    { key: e.id },
                    React.createElement("td", { className: "mono" }, e.id),
                    React.createElement(
                      "td",
                      { style: { fontWeight: 500 } },
                      e.nombre,
                    ),
                    React.createElement(
                      "td",
                      null,
                      React.createElement(
                        "span",
                        {
                          className:
                            "pill pill-" +
                            ("tienda" === e.tipo ? "success" : "muted"),
                        },
                        e.tipo,
                      ),
                    ),
                    React.createElement(
                      "td",
                      {
                        style: {
                          color: e.direccion ? "inherit" : "var(--muted)",
                          fontSize: 12,
                        },
                      },
                      e.direccion || "Sin dirección registrada",
                    ),
                    React.createElement(
                      "td",
                      null,
                      React.createElement(
                        "button",
                        {
                          "data-od-id": `edit-branch-${e.id}`,
                          className: "btn-ghost",
                          onClick: () => setBranchDraft(e),
                          style: {
                            minHeight: 40,
                            padding: "4px 8px",
                            fontSize: 11,
                          },
                        },
                        "Editar",
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        "ventas" === e &&
          React.createElement(
            React.Fragment,
            null,
            React.createElement(
              "h2",
              { style: { fontSize: 16, fontWeight: 600, marginBottom: 20 } },
              "Configuración de Ventas",
            ),
            React.createElement(
              "div",
              { style: { marginBottom: 24 } },
              React.createElement(
                "h3",
                {
                  style: {
                    fontSize: 14,
                    fontWeight: 500,
                    marginBottom: 12,
                    color: "var(--muted)",
                  },
                },
                "Precios y Utilidad",
              ),
              React.createElement(
                "div",
                {
                  style: {
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 16,
                  },
                },
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Utilidad Default (%)",
                  ),
                  React.createElement("input", {
                    type: "number",
                    defaultValue: "50",
                    style: { width: "100%" },
                  }),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "IVA (%)",
                  ),
                  React.createElement("input", {
                    type: "number",
                    defaultValue: "16",
                    style: { width: "100%" },
                  }),
                ),
              ),
            ),
            React.createElement(
              "div",
              { style: { marginBottom: 24 } },
              React.createElement(
                "h3",
                {
                  style: {
                    fontSize: 14,
                    fontWeight: 500,
                    marginBottom: 12,
                    color: "var(--muted)",
                  },
                },
                "Mayoreo",
              ),
              React.createElement(
                "div",
                {
                  style: {
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr 1fr",
                    gap: 16,
                  },
                },
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Descuento Global (%)",
                  ),
                  React.createElement("input", {
                    type: "number",
                    defaultValue: "15",
                    style: { width: "100%" },
                  }),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Mínimo Piezas",
                  ),
                  React.createElement("input", {
                    type: "number",
                    defaultValue: "5",
                    style: { width: "100%" },
                  }),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Mínimo Monto",
                  ),
                  React.createElement("input", {
                    type: "number",
                    defaultValue: "5000",
                    style: { width: "100%" },
                  }),
                ),
              ),
            ),
            React.createElement(
              "div",
              { style: { marginBottom: 24 } },
              React.createElement(
                "h3",
                {
                  style: {
                    fontSize: 14,
                    fontWeight: 500,
                    marginBottom: 12,
                    color: "var(--muted)",
                  },
                },
                "Descuentos Manuales (límite sin autorización)",
              ),
              React.createElement(
                "div",
                {
                  style: {
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr 1fr",
                    gap: 16,
                  },
                },
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Vendedor (%)",
                  ),
                  React.createElement("input", {
                    type: "number",
                    defaultValue: "10",
                    style: { width: "100%" },
                  }),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Encargado (%)",
                  ),
                  React.createElement("input", {
                    type: "number",
                    defaultValue: "25",
                    style: { width: "100%" },
                  }),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Admin (%)",
                  ),
                  React.createElement("input", {
                    type: "number",
                    defaultValue: "100",
                    style: { width: "100%" },
                  }),
                ),
              ),
            ),
            React.createElement(
              "button",
              {
                "data-od-id": `save-settings-${e}`,
                type: "button",
                className: "btn-primary",
                onClick: (event) => saveSettings(e, event),
              },
              "Guardar cambios",
            ),
          ),
        "impresion" === e &&
          React.createElement(
            React.Fragment,
            null,
            React.createElement(
              "h2",
              { style: { fontSize: 16, fontWeight: 600, marginBottom: 20 } },
              "Configuración de Impresión",
            ),
            React.createElement(
              "div",
              { style: { marginBottom: 24 } },
              React.createElement(
                "h3",
                {
                  style: {
                    fontSize: 14,
                    fontWeight: 500,
                    marginBottom: 12,
                    color: "var(--muted)",
                  },
                },
                "Tickets de Venta",
              ),
              React.createElement(
                "div",
                {
                  style: {
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 16,
                  },
                },
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Impresora",
                  ),
                  React.createElement(
                    "select",
                    { style: { width: "100%" } },
                    React.createElement(
                      "option",
                      null,
                      "Epson TM-T20III (USB)",
                    ),
                    React.createElement("option", null, "Star TSP143III (Red)"),
                  ),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Ancho de papel",
                  ),
                  React.createElement(
                    "select",
                    { style: { width: "100%" } },
                    React.createElement("option", null, "80mm"),
                    React.createElement("option", null, "58mm"),
                  ),
                ),
                React.createElement(
                  "div",
                  { style: { gridColumn: "1 / -1" } },
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Mensaje en ticket",
                  ),
                  React.createElement("textarea", {
                    defaultValue: "¡Gracias por su compra!",
                    style: { width: "100%", minHeight: 60 },
                  }),
                ),
              ),
            ),
            React.createElement(
              "div",
              { style: { marginBottom: 24 } },
              React.createElement(
                "h3",
                {
                  style: {
                    fontSize: 14,
                    fontWeight: 500,
                    marginBottom: 12,
                    color: "var(--muted)",
                  },
                },
                "Etiquetas de Precio",
              ),
              React.createElement(
                "div",
                {
                  style: {
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 16,
                  },
                },
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Impresora Etiquetas",
                  ),
                  React.createElement(
                    "select",
                    { style: { width: "100%" } },
                    React.createElement("option", null, "Zebra ZD220"),
                    React.createElement("option", null, "Brother QL-800"),
                  ),
                ),
                React.createElement(
                  "div",
                  null,
                  React.createElement(
                    "label",
                    {
                      style: {
                        display: "block",
                        fontSize: 12,
                        fontWeight: 500,
                        marginBottom: 6,
                        color: "var(--muted)",
                      },
                    },
                    "Tamaño etiqueta",
                  ),
                  React.createElement(
                    "select",
                    { style: { width: "100%" } },
                    React.createElement("option", null, "25mm × 15mm"),
                    React.createElement("option", null, "30mm × 20mm"),
                    React.createElement("option", null, "50mm × 25mm"),
                  ),
                ),
              ),
            ),
            React.createElement(
              "button",
              {
                "data-od-id": `save-settings-${e}`,
                type: "button",
                className: "btn-primary",
                onClick: (event) => saveSettings(e, event),
              },
              "Guardar cambios",
            ),
          ),
      ),
    ),
  );
}
function CategoriesView({
  productos: PRODUCTOS = [],
  categorias: CATEGORIAS = [],
  materiales: MATERIALES = [],
  subcategorias: SUBCATEGORIAS_SEED = {},
  colecciones: COLECCIONES_SEED = [],
  currentUser,
  actions = {},
}) {
  const canManageCatalog = currentUser?.rol === "admin";
  const [e, t] = useState(SUBCATEGORIAS_SEED),
    [a, l] = useState(COLECCIONES_SEED),
    [n, r] = useState("categorias"),
    [i, s] = useState(!1),
    [u, p] = useState(""),
    [operationError, setOperationError] = useState(""),
    [editCollection, setEditCollection] = useState(null),
    [catalogModal, setCatalogModal] = useState(null),
    [collectionSubmitting, setCollectionSubmitting] = useState(false),
    g = CATEGORIAS.filter((e) => "joyeria" === e.grupo),
    y = CATEGORIAS.filter((e) => "nojoyeria" === e.grupo),
    R = (e) => PRODUCTOS.filter((t) => t.categoria === e).length,
    E = (e) =>
      PRODUCTOS.filter(
        (t) => t.categoria === e && "Por clasificar" === t.subcategoria,
      ).length,
    b = async () => {
      if (!u.trim()) return;
      if (collectionSubmitting) return;
      setOperationError("");
      setCollectionSubmitting(true);
      try {
        await actions.createCollection(u.trim());
        p("");
        s(!1);
      } catch (error) {
        setOperationError(error.message);
      } finally {
        setCollectionSubmitting(false);
      }
    },
    f = ({ cat: e }) =>
      React.createElement(
        "div",
        {
          className: "card",
          style: { padding: 14, opacity: e.activa === false ? 0.68 : 1 },
        },
        React.createElement(
          "div",
          {
            style: {
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            },
          },
          React.createElement(
            "div",
            { style: { display: "flex", alignItems: "center", gap: 8 } },
            React.createElement(
              "span",
              {
                className:
                  "pill " +
                  ("joyeria" === e.grupo ? "pill-gold" : "pill-accent"),
              },
              e.clave,
            ),
            React.createElement(
              "span",
              { style: { fontWeight: 500 } },
              e.nombre,
            ),
            React.createElement(
              "span",
              {
                className:
                  "pill pill-" + (e.activa === false ? "danger" : "success"),
              },
              e.activa === false ? "Inactiva" : "Activa",
            ),
          ),
          React.createElement(
            "div",
            { style: { display: "flex", alignItems: "center", gap: 12 } },
            React.createElement(
              "span",
              { className: "pill pill-muted" },
              R(e.clave),
            ),
            React.createElement(
              "span",
              {
                className: "mono",
                style: { fontSize: 10, color: "var(--muted)" },
              },
              ((e) => {
                const t = PRODUCTOS.filter((t) => t.categoria === e);
                return t.length > 0 ? t[t.length - 1].sku : "—";
              })(e.clave),
            ),
            canManageCatalog &&
              React.createElement(
                "button",
                {
                  type: "button",
                  className: "btn-ghost",
                  onClick: () =>
                    setCatalogModal({ kind: "category", record: e }),
                  style: { padding: "4px 8px", fontSize: 11 },
                },
                e.activa === false ? "Reactivar" : "Editar",
              ),
          ),
        ),
      );
  useEffect(() => t(SUBCATEGORIAS_SEED), [SUBCATEGORIAS_SEED]);
  useEffect(() => l(COLECCIONES_SEED), [COLECCIONES_SEED]);
  return React.createElement(
    MainLayout,
    { title: "Clasificación" },
    React.createElement(
      "div",
      {
        style: {
          display: "flex",
          gap: 4,
          marginBottom: 24,
          borderBottom: "1px solid var(--border)",
          paddingBottom: 8,
        },
      },
      [
        { key: "categorias", label: `Categorías (${CATEGORIAS.length})` },
        {
          key: "subcategorias",
          label: `Subcategorías (${Object.values(e).flat().length})`,
        },
        { key: "colecciones", label: `Colecciones (${a.length})` },
      ].map((e) =>
        React.createElement(
          "button",
          {
            key: e.key,
            className: n === e.key ? "btn-primary" : "btn-ghost",
            onClick: () => r(e.key),
            style: { padding: "8px 16px", fontSize: 13 },
          },
          e.label,
        ),
      ),
    ),
    operationError &&
      React.createElement(
        "div",
        {
          className: "client-form-error",
          role: "alert",
          style: { marginBottom: 16 },
        },
        operationError,
      ),
    "categorias" === n &&
      canManageCatalog &&
      React.createElement(
        "div",
        {
          style: {
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
            marginBottom: 16,
          },
        },
        React.createElement(
          "button",
          {
            type: "button",
            className: "btn-secondary",
            onClick: () => setCatalogModal({ kind: "material", record: null }),
          },
          React.createElement(Icons.Plus, null),
          " Nuevo material",
        ),
        React.createElement(
          "button",
          {
            type: "button",
            className: "btn-primary",
            onClick: () => setCatalogModal({ kind: "category", record: null }),
          },
          React.createElement(Icons.Plus, null),
          " Nueva categoría",
        ),
      ),
    "categorias" === n &&
      React.createElement(
        "div",
        { style: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 } },
        React.createElement(
          "div",
          null,
          React.createElement(
            "div",
            {
              style: {
                display: "flex",
                alignItems: "center",
                gap: 8,
                marginBottom: 12,
              },
            },
            React.createElement(
              "h2",
              { style: { fontSize: 15, fontWeight: 600 } },
              "Joyería",
            ),
            React.createElement(
              "span",
              { style: { fontSize: 11, color: "var(--muted)" } },
              `${g.length} categorías · ${g.filter((item) => item.activa !== false).length} activas`,
            ),
          ),
          React.createElement(
            "div",
            { style: { display: "flex", flexDirection: "column", gap: 6 } },
            g.map((e) => React.createElement(f, { key: e.clave, cat: e })),
          ),
          React.createElement(
            "div",
            { style: { marginTop: 16 } },
            React.createElement(
              "div",
              {
                style: {
                  fontSize: 11,
                  fontWeight: 500,
                  marginBottom: 10,
                  color: "var(--muted)",
                },
              },
              `Materiales (${MATERIALES.length})`,
            ),
            React.createElement(
              "div",
              {
                style: {
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: 6,
                },
              },
              MATERIALES.map((e) =>
                React.createElement(
                  "div",
                  {
                    key: e.clave,
                    className: "card",
                    style: {
                      padding: "8px 12px",
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      opacity: e.activa === false ? 0.68 : 1,
                    },
                  },
                  React.createElement(
                    "span",
                    {
                      className: "pill pill-gold",
                      style: { fontSize: 10, padding: "2px 6px" },
                    },
                    e.clave,
                  ),
                  React.createElement(
                    "span",
                    { style: { fontSize: 12, flex: 1 } },
                    e.nombre,
                  ),
                  React.createElement(
                    "span",
                    {
                      className:
                        "pill pill-" +
                        (e.activa === false ? "danger" : "success"),
                    },
                    e.activa === false ? "Inactivo" : "Activo",
                  ),
                  canManageCatalog &&
                    React.createElement(
                      "button",
                      {
                        type: "button",
                        className: "btn-ghost",
                        onClick: () =>
                          setCatalogModal({ kind: "material", record: e }),
                        style: { padding: "4px 6px", fontSize: 11 },
                      },
                      e.activa === false ? "Reactivar" : "Editar",
                    ),
                ),
              ),
            ),
          ),
        ),
        React.createElement(
          "div",
          null,
          React.createElement(
            "div",
            {
              style: {
                display: "flex",
                alignItems: "center",
                gap: 8,
                marginBottom: 12,
              },
            },
            React.createElement(
              "h2",
              { style: { fontSize: 15, fontWeight: 600 } },
              "No Joyería",
            ),
            React.createElement(
              "span",
              { style: { fontSize: 11, color: "var(--muted)" } },
              `${y.length} categorías · ${y.filter((item) => item.activa !== false).length} activas`,
            ),
          ),
          React.createElement(
            "div",
            { style: { display: "flex", flexDirection: "column", gap: 6 } },
            y.map((t) =>
              React.createElement(
                "div",
                {
                  key: t.clave,
                  className: "card",
                  style: {
                    padding: 14,
                    opacity: t.activa === false ? 0.68 : 1,
                  },
                },
                React.createElement(
                  "div",
                  {
                    style: {
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 8,
                    },
                  },
                  React.createElement(
                    "div",
                    {
                      style: { display: "flex", alignItems: "center", gap: 8 },
                    },
                    React.createElement(
                      "span",
                      { className: "pill pill-accent" },
                      t.clave,
                    ),
                    React.createElement(
                      "span",
                      { style: { fontWeight: 500 } },
                      t.nombre,
                    ),
                  ),
                  React.createElement(
                    "div",
                    {
                      style: { display: "flex", alignItems: "center", gap: 8 },
                    },
                    React.createElement(
                      "span",
                      { className: "pill pill-muted" },
                      R(t.clave),
                    ),
                    React.createElement(
                      "span",
                      {
                        className:
                          "pill pill-" +
                          (t.activa === false ? "danger" : "success"),
                      },
                      t.activa === false ? "Inactiva" : "Activa",
                    ),
                    E(t.clave) > 0 &&
                      React.createElement(
                        "span",
                        { className: "pill pill-warning" },
                        E(t.clave),
                        " sin clasificar",
                      ),
                    canManageCatalog &&
                      React.createElement(
                        "button",
                        {
                          type: "button",
                          className: "btn-ghost",
                          onClick: () =>
                            setCatalogModal({ kind: "category", record: t }),
                          style: { padding: "4px 6px", fontSize: 11 },
                        },
                        t.activa === false ? "Reactivar" : "Editar",
                      ),
                  ),
                ),
                React.createElement(
                  "div",
                  { style: { fontSize: 11, color: "var(--muted)" } },
                  (e[t.clave] || []).filter((e) => e.activa && !e.sistema)
                    .length,
                  " subcategorías activas",
                ),
              ),
            ),
          ),
        ),
      ),
    "subcategorias" === n &&
      React.createElement(
        "div",
        {
          style: {
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: 20,
          },
        },
        y.map((t) =>
          React.createElement(
            "div",
            { key: t.clave },
            React.createElement(
              "div",
              {
                style: {
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 12,
                },
              },
              React.createElement(
                "div",
                { style: { display: "flex", alignItems: "center", gap: 8 } },
                React.createElement(
                  "span",
                  { className: "pill pill-accent" },
                  t.clave,
                ),
                React.createElement(
                  "span",
                  { style: { fontWeight: 500, fontSize: 14 } },
                  t.nombre,
                ),
              ),
              canManageCatalog &&
                t.activa !== false &&
                React.createElement(
                  "button",
                  {
                    className: "btn-ghost",
                    onClick: () =>
                      setCatalogModal({
                        kind: "subcategory",
                        record: null,
                        category: t,
                      }),
                    style: { padding: "4px 8px", fontSize: 12 },
                  },
                  React.createElement(Icons.Plus, null),
                  " Agregar",
                ),
            ),
            React.createElement(
              "div",
              { style: { display: "flex", flexDirection: "column", gap: 4 } },
              (e[t.clave] || []).map((e) =>
                React.createElement(
                  "div",
                  {
                    key: e.id,
                    className: "card",
                    style: {
                      padding: "10px 12px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      background: e.sistema ? "var(--bg)" : "var(--surface)",
                      borderStyle: e.sistema ? "dashed" : "solid",
                      opacity: e.activa === false ? 0.68 : 1,
                    },
                  },
                  React.createElement(
                    "span",
                    {
                      style: {
                        fontSize: 13,
                        color: e.sistema ? "var(--muted)" : "inherit",
                      },
                    },
                    e.nombre,
                  ),
                  React.createElement(
                    "div",
                    {
                      style: { display: "flex", alignItems: "center", gap: 6 },
                    },
                    React.createElement(
                      "span",
                      {
                        className:
                          "pill pill-" +
                          (e.activa === false ? "danger" : "success"),
                        style: { fontSize: 10 },
                      },
                      e.sistema
                        ? "Sistema · activa"
                        : e.activa === false
                          ? "Inactiva"
                          : "Activa",
                    ),
                    React.createElement(
                      "span",
                      { className: "pill pill-muted", style: { fontSize: 10 } },
                      PRODUCTOS.filter(
                        (a) =>
                          a.categoria === t.clave &&
                          a.subcategoria === e.nombre,
                      ).length,
                    ),
                    canManageCatalog &&
                      React.createElement(
                        "button",
                        {
                          type: "button",
                          className: "btn-ghost",
                          onClick: () =>
                            setCatalogModal({
                              kind: "subcategory",
                              record: e,
                              category: t,
                            }),
                          style: { padding: "4px 6px", fontSize: 11 },
                        },
                        e.activa === false ? "Reactivar" : "Editar",
                      ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    "colecciones" === n &&
      React.createElement(
        "div",
        null,
        React.createElement(
          "div",
          {
            style: {
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 16,
            },
          },
          React.createElement(
            "div",
            null,
            React.createElement(
              "div",
              { style: { fontSize: 13, color: "var(--muted)" } },
              "Las colecciones son etiquetas de merchandising (M:N). Se asignan en lote desde la lista de productos, no durante la captura.",
            ),
          ),
          canManageCatalog &&
            React.createElement(
              "button",
              { className: "btn-primary", onClick: () => s(!0) },
              React.createElement(Icons.Plus, null),
              " Nueva Colección",
            ),
        ),
        i &&
          React.createElement(
            "div",
            {
              className: "card",
              style: { padding: 16, marginBottom: 16, maxWidth: 400 },
            },
            React.createElement("input", {
              type: "text",
              placeholder: "Nombre de colección...",
              value: u,
              onChange: (e) => p(e.target.value),
              onKeyDown: (e) => "Enter" === e.key && b(),
              style: { marginBottom: 12 },
              autoFocus: !0,
            }),
            React.createElement(
              "div",
              { style: { display: "flex", gap: 8 } },
              React.createElement(
                "button",
                {
                  className: "btn-primary",
                  onClick: b,
                  disabled: collectionSubmitting,
                },
                collectionSubmitting ? "Guardando…" : "Guardar",
              ),
              React.createElement(
                "button",
                {
                  className: "btn-ghost",
                  onClick: () => {
                    (s(!1), p(""));
                  },
                },
                "Cancelar",
              ),
            ),
          ),
        React.createElement(CollectionEditModal, {
          collection: canManageCatalog ? editCollection : null,
          onClose: () => setEditCollection(null),
          onSave: async (updated) => {
            await actions.updateCollection(updated);
            setEditCollection(null);
          },
        }),
        React.createElement(
          "div",
          {
            style: {
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: 12,
            },
          },
          a.map((e) => {
            const t = PRODUCTOS.filter((t) =>
              (t.colecciones || []).includes(e.id),
            ).length;
            return React.createElement(
              "div",
              {
                key: e.id,
                className: "card",
                style: { padding: 16, opacity: e.activa === false ? 0.68 : 1 },
              },
              React.createElement(
                "div",
                { style: { fontWeight: 500, marginBottom: 8 } },
                e.nombre,
              ),
              React.createElement(
                "div",
                {
                  style: {
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  },
                },
                React.createElement(
                  "span",
                  { className: "pill pill-muted" },
                  t,
                  " productos",
                ),
                React.createElement(
                  "span",
                  {
                    className:
                      "pill pill-" +
                      (e.activa === false ? "danger" : "success"),
                  },
                  e.activa === false ? "Inactiva" : "Activa",
                ),
                canManageCatalog &&
                  React.createElement(
                    "button",
                    {
                      "data-od-id": `edit-collection-${e.id}`,
                      className: "btn-ghost",
                      onClick: () => setEditCollection(e),
                      style: {
                        minHeight: 40,
                        padding: "4px 8px",
                        fontSize: 11,
                        color: "var(--muted)",
                      },
                    },
                    e.activa === false ? "Reactivar" : "Editar",
                  ),
              ),
            );
          }),
        ),
      ),
    React.createElement(CatalogRecordModal, {
      kind: canManageCatalog ? catalogModal?.kind : null,
      record: catalogModal?.record || null,
      onClose: () => setCatalogModal(null),
      onSave: async (record) => {
        setOperationError("");
        if (catalogModal.kind === "category") {
          if (catalogModal.record) await actions.updateCategory(record);
          else await actions.createCategory(record);
          return;
        }
        if (catalogModal.kind === "material") {
          if (catalogModal.record) await actions.updateMaterial(record);
          else await actions.createMaterial(record);
          return;
        }
        if (catalogModal.record) {
          await actions.updateSubcategory({
            ...record,
            activa: catalogModal.record.sistema ? true : record.activa,
          });
        } else {
          await actions.createSubcategory(
            catalogModal.category.id,
            record.nombre,
          );
        }
      },
    }),
  );
}
function PhysicalCountView() {
  const [e, t] = useState([
      {
        id: 1,
        folio: "CF-001",
        fecha: "2026-08-10",
        sucursal: "T01",
        estado: "completado",
        totalEsperado: 245,
        totalContado: 243,
        diferencia: -2,
        responsable: "Ana Garcia",
      },
      {
        id: 2,
        folio: "CF-002",
        fecha: "2026-08-05",
        sucursal: "T02",
        estado: "completado",
        totalEsperado: 312,
        totalContado: 310,
        diferencia: -2,
        responsable: "Carlos Lopez",
      },
    ]),
    [a, l] = useState(!1),
    [n, r] = useState(null),
    [o, c] = useState(""),
    [i, s] = useState([]),
    [m, d] = useState(""),
    u = (e) => SUCURSALES.find((t) => t.id === e)?.nombre || e,
    p = () => {
      if (!o.trim()) return;
      const e =
        ((t = o.trim()),
        PRODUCTOS.find((e) => e.sku.toLowerCase() === t.toLowerCase()));
      var t;
      if (!e) return (alert("Producto no encontrado: " + o), void c(""));
      const a = i.find((t) => t.sku === e.sku);
      (s(
        a
          ? i.map((t) =>
              t.sku === e.sku ? { ...t, contado: t.contado + 1 } : t,
            )
          : [
              ...i,
              {
                sku: e.sku,
                nombre: e.nombre,
                categoria: e.categoria,
                esperado: e.stock,
                contado: 1,
              },
            ],
      ),
        c(""));
    },
    g = i.filter((e) => e.contado !== e.esperado),
    y = i.reduce((e, t) => e + t.contado, 0),
    R = i.reduce((e, t) => e + t.esperado, 0);
  return React.createElement(
    MainLayout,
    {
      title: "Conteo Fisico de Inventario",
      actions:
        !n &&
        React.createElement(
          "button",
          {
            "data-od-id": "new-physical-count-cta",
            className: "btn-primary",
            onClick: () => l(!0),
            style: {
              minHeight: 44,
              display: "flex",
              alignItems: "center",
              gap: 6,
            },
          },
          React.createElement(Icons.Plus, null),
          " Nuevo Conteo",
        ),
    },
    n
      ? React.createElement(
          "div",
          null,
          React.createElement(
            "div",
            { className: "card", style: { padding: 20, marginBottom: 20 } },
            React.createElement(
              "div",
              {
                style: {
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                },
              },
              React.createElement(
                "div",
                null,
                React.createElement(
                  "div",
                  { style: { display: "flex", alignItems: "center", gap: 12 } },
                  React.createElement(
                    "span",
                    {
                      className: "mono",
                      style: {
                        fontSize: 18,
                        color: "var(--accent)",
                        fontWeight: 600,
                      },
                    },
                    n.folio,
                  ),
                  React.createElement(
                    "span",
                    { className: "pill pill-warning" },
                    "En proceso",
                  ),
                ),
                React.createElement(
                  "div",
                  {
                    style: {
                      fontSize: 13,
                      color: "var(--muted)",
                      marginTop: 4,
                    },
                  },
                  u(n.sucursal),
                  " - ",
                  n.fecha,
                ),
              ),
              React.createElement(
                "div",
                { style: { display: "flex", gap: 8 } },
                React.createElement(
                  "button",
                  {
                    className: "btn-ghost",
                    onClick: () => {
                      (r(null), s([]));
                    },
                    style: { color: "var(--danger)" },
                  },
                  "Cancelar",
                ),
                React.createElement(
                  "button",
                  {
                    className: "btn-primary",
                    onClick: () => {
                      const a = i.reduce((e, t) => e + t.contado, 0),
                        l = i.reduce((e, t) => e + t.esperado, 0),
                        o = {
                          ...n,
                          estado: "completado",
                          totalContado: a,
                          totalEsperado: l,
                          diferencia: a - l,
                        };
                      (t([o, ...e]), r(null), s([]));
                    },
                    disabled: 0 === i.length,
                  },
                  "Finalizar Conteo",
                ),
              ),
            ),
          ),
          React.createElement(
            "div",
            { className: "card", style: { padding: 20, marginBottom: 20 } },
            React.createElement(
              "div",
              { style: { display: "flex", gap: 12, alignItems: "flex-end" } },
              React.createElement(
                "div",
                { style: { flex: 1 } },
                React.createElement(
                  "label",
                  {
                    style: {
                      display: "block",
                      fontSize: 12,
                      fontWeight: 500,
                      marginBottom: 6,
                      color: "var(--muted)",
                    },
                  },
                  "Escanear o escribir SKU",
                ),
                React.createElement(
                  "div",
                  { style: { position: "relative" } },
                  React.createElement("input", {
                    type: "text",
                    value: o,
                    onChange: (e) => c(e.target.value.toUpperCase()),
                    onKeyDown: (e) => "Enter" === e.key && p(),
                    placeholder: "Escanea codigo de barras o escribe SKU...",
                    style: { width: "100%", paddingRight: 40 },
                    autoFocus: !0,
                  }),
                  React.createElement(
                    "span",
                    {
                      style: {
                        position: "absolute",
                        right: 12,
                        top: "50%",
                        transform: "translateY(-50%)",
                        opacity: 0.3,
                      },
                    },
                    React.createElement(Icons.Barcode, null),
                  ),
                ),
              ),
              React.createElement(
                "button",
                { className: "btn-primary", onClick: p },
                "Agregar",
              ),
            ),
          ),
          React.createElement(
            "div",
            {
              style: {
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: 12,
                marginBottom: 20,
              },
            },
            React.createElement(
              "div",
              { className: "card", style: { padding: 16 } },
              React.createElement(
                "div",
                { style: { fontSize: 12, color: "var(--muted)" } },
                "Items escaneados",
              ),
              React.createElement(
                "div",
                { style: { fontSize: 24, fontWeight: 600 } },
                i.length,
              ),
            ),
            React.createElement(
              "div",
              { className: "card", style: { padding: 16 } },
              React.createElement(
                "div",
                { style: { fontSize: 12, color: "var(--muted)" } },
                "Total contado",
              ),
              React.createElement(
                "div",
                { style: { fontSize: 24, fontWeight: 600 } },
                y,
              ),
            ),
            React.createElement(
              "div",
              { className: "card", style: { padding: 16 } },
              React.createElement(
                "div",
                { style: { fontSize: 12, color: "var(--muted)" } },
                "Total esperado",
              ),
              React.createElement(
                "div",
                { style: { fontSize: 24, fontWeight: 600 } },
                R,
              ),
            ),
            React.createElement(
              "div",
              {
                className: "card",
                style: {
                  padding: 16,
                  background:
                    g.length > 0 ? "var(--warning-bg)" : "var(--success-bg)",
                },
              },
              React.createElement(
                "div",
                { style: { fontSize: 12, color: "var(--muted)" } },
                "Con diferencias",
              ),
              React.createElement(
                "div",
                { style: { fontSize: 24, fontWeight: 600 } },
                g.length,
              ),
            ),
          ),
          React.createElement(
            "div",
            { className: "card", style: { padding: 0 } },
            React.createElement(
              "table",
              { className: "data-table" },
              React.createElement(
                "thead",
                null,
                React.createElement(
                  "tr",
                  null,
                  React.createElement("th", null, "SKU"),
                  React.createElement("th", null, "Producto"),
                  React.createElement("th", null, "Categoria"),
                  React.createElement(
                    "th",
                    { style: { textAlign: "center" } },
                    "Esperado",
                  ),
                  React.createElement(
                    "th",
                    { style: { textAlign: "center" } },
                    "Contado",
                  ),
                  React.createElement(
                    "th",
                    { style: { textAlign: "center" } },
                    "Diferencia",
                  ),
                  React.createElement("th", null),
                ),
              ),
              React.createElement(
                "tbody",
                null,
                0 === i.length
                  ? React.createElement(
                      "tr",
                      null,
                      React.createElement(
                        "td",
                        {
                          colSpan: "7",
                          style: {
                            textAlign: "center",
                            padding: 40,
                            color: "var(--muted)",
                          },
                        },
                        React.createElement(
                          "span",
                          {
                            style: {
                              opacity: 0.3,
                              marginBottom: 8,
                              display: "block",
                            },
                          },
                          React.createElement(Icons.Barcode, null),
                        ),
                        React.createElement(
                          "div",
                          null,
                          "Escanea o escribe un SKU para comenzar el conteo",
                        ),
                      ),
                    )
                  : i.map((e) => {
                      const t = e.contado - e.esperado;
                      return React.createElement(
                        "tr",
                        { key: e.sku },
                        React.createElement(
                          "td",
                          {
                            className: "mono",
                            style: { color: "var(--accent)" },
                          },
                          e.sku,
                        ),
                        React.createElement("td", null, e.nombre),
                        React.createElement(
                          "td",
                          null,
                          React.createElement(
                            "span",
                            {
                              className:
                                "pill " +
                                ("joyeria" ===
                                ((a = e.categoria),
                                CATEGORIAS.find((e) => e.clave === a)?.grupo)
                                  ? "pill-gold"
                                  : "pill-accent"),
                            },
                            e.categoria,
                          ),
                          React.createElement(
                            "span",
                            { style: { marginLeft: 6, fontSize: 12 } },
                            ((e) =>
                              CATEGORIAS.find((t) => t.clave === e)?.nombre ||
                              e)(e.categoria),
                          ),
                        ),
                        React.createElement(
                          "td",
                          {
                            style: { textAlign: "center" },
                            className: "tabular",
                          },
                          e.esperado,
                        ),
                        React.createElement(
                          "td",
                          { style: { textAlign: "center" } },
                          React.createElement("input", {
                            type: "number",
                            value: e.contado,
                            onChange: (t) => {
                              return (
                                (a = e.sku),
                                (l = parseInt(t.target.value) || 0),
                                void s(
                                  i.map((e) =>
                                    e.sku === a
                                      ? { ...e, contado: Math.max(0, l) }
                                      : e,
                                  ),
                                )
                              );
                              var a, l;
                            },
                            style: { width: 60, textAlign: "center" },
                            min: "0",
                          }),
                        ),
                        React.createElement(
                          "td",
                          { style: { textAlign: "center" } },
                          React.createElement(
                            "span",
                            {
                              className:
                                "pill " +
                                (0 === t
                                  ? "pill-success"
                                  : t > 0
                                    ? "pill-warning"
                                    : "pill-danger"),
                            },
                            t > 0 ? "+" : "",
                            t,
                          ),
                        ),
                        React.createElement(
                          "td",
                          null,
                          React.createElement(
                            "button",
                            {
                              className: "btn-ghost",
                              onClick: () => {
                                return (
                                  (t = e.sku),
                                  void s(i.filter((e) => e.sku !== t))
                                );
                                var t;
                              },
                              style: { color: "var(--danger)" },
                            },
                            React.createElement(Icons.Trash, null),
                          ),
                        ),
                      );
                      var a;
                    }),
              ),
            ),
          ),
        )
      : React.createElement(
          React.Fragment,
          null,
          React.createElement(
            "div",
            { className: "card", style: { padding: 0 } },
            React.createElement(
              "table",
              { className: "data-table" },
              React.createElement(
                "thead",
                null,
                React.createElement(
                  "tr",
                  null,
                  React.createElement("th", null, "Folio"),
                  React.createElement("th", null, "Fecha"),
                  React.createElement("th", null, "Sucursal"),
                  React.createElement("th", null, "Responsable"),
                  React.createElement(
                    "th",
                    { style: { textAlign: "center" } },
                    "Esperado",
                  ),
                  React.createElement(
                    "th",
                    { style: { textAlign: "center" } },
                    "Contado",
                  ),
                  React.createElement(
                    "th",
                    { style: { textAlign: "center" } },
                    "Diferencia",
                  ),
                  React.createElement("th", null, "Estado"),
                ),
              ),
              React.createElement(
                "tbody",
                null,
                e.map((e) =>
                  React.createElement(
                    "tr",
                    { key: e.id },
                    React.createElement(
                      "td",
                      { className: "mono", style: { color: "var(--accent)" } },
                      e.folio,
                    ),
                    React.createElement("td", null, e.fecha),
                    React.createElement("td", null, u(e.sucursal)),
                    React.createElement("td", null, e.responsable),
                    React.createElement(
                      "td",
                      { style: { textAlign: "center" }, className: "tabular" },
                      e.totalEsperado,
                    ),
                    React.createElement(
                      "td",
                      { style: { textAlign: "center" }, className: "tabular" },
                      e.totalContado,
                    ),
                    React.createElement(
                      "td",
                      { style: { textAlign: "center" } },
                      React.createElement(
                        "span",
                        {
                          className:
                            "pill " +
                            (0 === e.diferencia
                              ? "pill-success"
                              : "pill-danger"),
                        },
                        e.diferencia > 0 ? "+" : "",
                        e.diferencia,
                      ),
                    ),
                    React.createElement(
                      "td",
                      null,
                      React.createElement(
                        "span",
                        {
                          className:
                            "pill pill-" +
                            ("completado" === e.estado ? "success" : "warning"),
                        },
                        e.estado,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
    a &&
      React.createElement(
        "div",
        {
          style: {
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          },
        },
        React.createElement(
          "div",
          { className: "card", style: { width: 400, padding: 0 } },
          React.createElement(
            "div",
            {
              style: {
                padding: "16px 24px",
                borderBottom: "1px solid var(--border)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              },
            },
            React.createElement(
              "h3",
              { style: { fontSize: 16, fontWeight: 600 } },
              "Nuevo Conteo Fisico",
            ),
            React.createElement(
              "button",
              { className: "btn-ghost", onClick: () => l(!1) },
              React.createElement(Icons.Close, null),
            ),
          ),
          React.createElement(
            "div",
            { style: { padding: 24 } },
            React.createElement(
              "label",
              {
                style: {
                  display: "block",
                  fontSize: 12,
                  fontWeight: 500,
                  marginBottom: 6,
                  color: "var(--muted)",
                },
              },
              "Sucursal a contar",
            ),
            React.createElement(
              "select",
              {
                value: m,
                onChange: (e) => d(e.target.value),
                style: { width: "100%" },
              },
              React.createElement(
                "option",
                { value: "" },
                "Selecciona sucursal...",
              ),
              SUCURSALES.map((e) =>
                React.createElement(
                  "option",
                  { key: e.id, value: e.id },
                  e.nombre,
                ),
              ),
            ),
          ),
          React.createElement(
            "div",
            {
              style: {
                padding: "16px 24px",
                borderTop: "1px solid var(--border)",
                display: "flex",
                justifyContent: "flex-end",
                gap: 8,
              },
            },
            React.createElement(
              "button",
              { className: "btn-ghost", onClick: () => l(!1) },
              "Cancelar",
            ),
            React.createElement(
              "button",
              {
                className: "btn-primary",
                onClick: () => {
                  if (!m) return;
                  const t = {
                    id: e.length + 1,
                    folio: "CF-" + String(e.length + 1).padStart(3, "0"),
                    fecha: new Date().toISOString().split("T")[0],
                    sucursal: m,
                    estado: "en_proceso",
                    totalEsperado: 0,
                    totalContado: 0,
                    diferencia: 0,
                    responsable: "Usuario Actual",
                  };
                  (r(t), s([]), l(!1));
                },
                disabled: !m,
              },
              "Iniciar Conteo",
            ),
          ),
        ),
      ),
  );
}
const VENTAS_DEMO = [
  {
    id: 467,
    folio: "V-00467",
    fecha: "2026-08-15",
    hora: "12:42",
    cliente: "Público general",
    vendedor: "Ana García",
    tipoVenta: "menudeo",
    condicion: "contado",
    tipoPago: "tarjeta",
    sucursal: "Centro Histórico",
    items: [
      {
        sku: "AN-OR-0001",
        nombre: "Anillo Ojo Turco Oro 14K",
        cantidad: 1,
        precioUnitario: 6750,
      },
    ],
  },
  {
    id: 466,
    folio: "V-00466",
    fecha: "2026-08-15",
    hora: "11:18",
    cliente: "María González Pérez",
    vendedor: "Carlos Mendoza",
    tipoVenta: "mayoreo",
    condicion: "credito",
    tipoPago: "credito",
    sucursal: "Centro Histórico",
    items: [
      {
        sku: "CO-OR-0001",
        nombre: "Collar Mano de Fátima",
        cantidad: 5,
        precioUnitario: 4080,
      },
      {
        sku: "AN-OR-0001",
        nombre: "Anillo Ojo Turco Oro 14K",
        cantidad: 4,
        precioUnitario: 5738,
      },
      {
        sku: "DI-PL-0001",
        nombre: "Dije Elefante de la Suerte",
        cantidad: 2,
        precioUnitario: 924,
      },
    ],
  },
  {
    id: 465,
    folio: "V-00465",
    fecha: "2026-08-15",
    hora: "10:04",
    cliente: "Roberto Hernández",
    vendedor: "Ana García",
    tipoVenta: "menudeo",
    condicion: "contado",
    tipoPago: "efectivo",
    sucursal: "Centro Histórico",
    items: [
      {
        sku: "DI-PL-0001",
        nombre: "Dije Elefante de la Suerte",
        cantidad: 1,
        precioUnitario: 1200,
      },
    ],
  },
  {
    id: 464,
    folio: "V-00464",
    fecha: "2026-08-14",
    hora: "17:36",
    cliente: "Joyería El Diamante SA",
    vendedor: "Laura Jiménez",
    tipoVenta: "mayoreo",
    condicion: "contado",
    tipoPago: "transferencia",
    sucursal: "Plaza Universidad",
    items: [
      {
        sku: "AN-OR-0001",
        nombre: "Anillo Ojo Turco Oro 14K",
        cantidad: 10,
        precioUnitario: 5738,
      },
    ],
  },
  {
    id: 463,
    folio: "V-00463",
    fecha: "2026-08-14",
    hora: "15:09",
    cliente: "Ana Martínez",
    vendedor: "Laura Jiménez",
    tipoVenta: "menudeo",
    condicion: "contado",
    tipoPago: "tarjeta",
    sucursal: "Plaza Universidad",
    items: [
      {
        sku: "CO-OR-0001",
        nombre: "Collar Mano de Fátima",
        cantidad: 1,
        precioUnitario: 4800,
      },
      {
        sku: "AC-0006",
        nombre: "Figura Buda Meditando",
        cantidad: 1,
        precioUnitario: 450,
      },
      {
        sku: "AC-0004",
        nombre: "Tarot Rider Waite",
        cantidad: 1,
        precioUnitario: 550,
      },
      {
        sku: "PU-OT-0001",
        nombre: "Pulsera 7 Nudos Roja",
        cantidad: 15,
        precioUnitario: 180,
      },
    ],
  },
  {
    id: 462,
    folio: "V-00462",
    fecha: "2026-08-13",
    hora: "13:22",
    cliente: "Distribuidora Oro Fino",
    vendedor: "Carlos Mendoza",
    tipoVenta: "mayoreo",
    condicion: "credito",
    tipoPago: "credito",
    sucursal: "Centro Histórico",
    items: [
      {
        sku: "CO-OR-0001",
        nombre: "Collar Mano de Fátima",
        cantidad: 4,
        precioUnitario: 4080,
      },
      {
        sku: "DI-PL-0001",
        nombre: "Dije Elefante de la Suerte",
        cantidad: 8,
        precioUnitario: 980,
      },
      {
        sku: "PU-OT-0001",
        nombre: "Pulsera 7 Nudos Roja",
        cantidad: 4,
        precioUnitario: 210,
      },
    ],
  },
  {
    id: 461,
    folio: "V-00461",
    fecha: "2026-08-12",
    hora: "18:41",
    cliente: "Público general",
    vendedor: "Laura Jiménez",
    tipoVenta: "menudeo",
    condicion: "contado",
    tipoPago: "efectivo",
    sucursal: "Plaza Universidad",
    items: [
      {
        sku: "AC-0001",
        nombre: "Veladora Roja del Amor",
        cantidad: 10,
        precioUnitario: 95,
      },
    ],
  },
  {
    id: 460,
    folio: "V-00460",
    fecha: "2026-08-10",
    hora: "16:12",
    cliente: "Público general",
    vendedor: "Ana García",
    tipoVenta: "menudeo",
    condicion: "contado",
    tipoPago: "tarjeta",
    sucursal: "Centro Histórico",
    items: [
      {
        sku: "CO-OR-0001",
        nombre: "Collar Mano de Fátima",
        cantidad: 1,
        precioUnitario: 4800,
      },
    ],
  },
  {
    id: 459,
    folio: "V-00459",
    fecha: "2026-08-08",
    hora: "12:05",
    cliente: "María González Pérez",
    vendedor: "Carlos Mendoza",
    tipoVenta: "mayoreo",
    condicion: "contado",
    tipoPago: "transferencia",
    sucursal: "Centro Histórico",
    items: [
      {
        sku: "AN-OR-0002",
        nombre: "Anillo Compromiso Diamante",
        cantidad: 1,
        precioUnitario: 15938,
      },
    ],
  },
  {
    id: 458,
    folio: "V-00458",
    fecha: "2026-08-05",
    hora: "11:47",
    cliente: "Joyería El Diamante SA",
    vendedor: "Laura Jiménez",
    tipoVenta: "mayoreo",
    condicion: "credito",
    tipoPago: "credito",
    sucursal: "Plaza Universidad",
    items: [
      {
        sku: "DI-PL-0002",
        nombre: "Dije Mano de Fátima",
        cantidad: 5,
        precioUnitario: 1240,
      },
    ],
  },
  {
    id: 457,
    folio: "V-00457",
    fecha: "2026-08-03",
    hora: "14:31",
    cliente: "Público general",
    vendedor: "Ana García",
    tipoVenta: "menudeo",
    condicion: "contado",
    tipoPago: "efectivo",
    sucursal: "Centro Histórico",
    items: [
      {
        sku: "AC-0004",
        nombre: "Tarot Rider Waite",
        cantidad: 1,
        precioUnitario: 550,
      },
    ],
  },
  {
    id: 456,
    folio: "V-00456",
    fecha: "2026-08-01",
    hora: "10:16",
    cliente: "Distribuidora Oro Fino",
    vendedor: "Carlos Mendoza",
    tipoVenta: "mayoreo",
    condicion: "contado",
    tipoPago: "transferencia",
    sucursal: "Centro Histórico",
    items: [
      {
        sku: "CO-OR-0001",
        nombre: "Collar Mano de Fátima",
        cantidad: 10,
        precioUnitario: 4080,
      },
      {
        sku: "PU-OT-0001",
        nombre: "Pulsera 7 Nudos Roja",
        cantidad: 28,
        precioUnitario: 150,
      },
    ],
  },
];
const SALES_PAYMENT_LABELS = {
  efectivo: "Efectivo",
  tarjeta: "Tarjeta",
  transferencia: "Transferencia",
  credito: "Crédito",
  mixto: "Mixto",
};
const getSaleTotal = (sale) =>
  sale.total ??
  sale.items.reduce(
    (sum, item) => sum + item.cantidad * item.precioUnitario,
    0,
  );
const formatSalesDate = (value) => {
  if (!value) return "Sin límite";
  return new Intl.DateTimeFormat("es-MX", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  })
    .format(new Date(value + "T12:00:00"))
    .replace(".", "");
};
function getCurrentSalesMonthRange() {
  const today = new Date();
  const year = today.getFullYear();
  const monthIndex = today.getMonth();
  return {
    from: getLocalISODate(new Date(year, monthIndex, 1)),
    to: getLocalISODate(new Date(year, monthIndex + 1, 0)),
  };
}
function getCurrentSalesWeekRange() {
  const today = new Date();
  const dayOfWeek = today.getDay();
  const daysSinceMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
  const monday = new Date(
    today.getFullYear(),
    today.getMonth(),
    today.getDate() - daysSinceMonday,
  );
  const sunday = new Date(
    monday.getFullYear(),
    monday.getMonth(),
    monday.getDate() + 6,
  );
  return { from: getLocalISODate(monday), to: getLocalISODate(sunday) };
}
function SalesDateField({ label, value, onChange, dataId }) {
  const inputId = dataId + "-input";
  return React.createElement(
    "label",
    { className: "sales-date-field", "data-od-id": dataId, htmlFor: inputId },
    React.createElement("span", { className: "sales-date-label" }, label),
    React.createElement("input", {
      id: inputId,
      className: "sales-date-input mono",
      type: "date",
      value,
      onChange: (event) => onChange(event.target.value),
      "aria-label": "Fecha " + label.toLowerCase(),
    }),
  );
}
function SaleDetailModal({ sale, onClose, onCancel }) {
  useEffect(() => {
    if (!sale) return undefined;
    const handleEscape = (event) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [sale?.id]);
  if (!sale) return null;
  const total = getSaleTotal(sale);
  const isPublic = sale.cliente === "Público general";
  return React.createElement(
    "div",
    {
      "data-od-id": "sale-detail-modal",
      role: "dialog",
      "aria-modal": "true",
      "aria-labelledby": "sale-detail-heading",
      style: {
        position: "fixed",
        inset: 0,
        padding: 16,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 110,
      },
    },
    React.createElement(
      "div",
      { className: "card sale-detail-modal" },
      React.createElement(
        "div",
        {
          style: {
            minHeight: 64,
            padding: "12px 16px 12px 24px",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
          },
        },
        React.createElement(
          "div",
          null,
          React.createElement(
            "h2",
            {
              "data-od-id": "sale-detail-heading",
              id: "sale-detail-heading",
              style: { fontSize: 17, fontWeight: 600 },
            },
            "Detalle de venta",
          ),
          React.createElement(
            "p",
            {
              className: "mono",
              style: { marginTop: 3, color: "var(--accent)" },
            },
            sale.folio,
          ),
          sale.estado === "cancelada" &&
            React.createElement(
              "span",
              { className: "pill pill-danger", style: { marginTop: 6, display: "inline-block" } },
              "Cancelada",
            ),
        ),
        React.createElement(
          "button",
          {
            "data-od-id": "close-sale-detail-control",
            type: "button",
            className: "btn-ghost",
            "aria-label": "Cerrar detalle de venta",
            onClick: onClose,
            style: {
              minWidth: 44,
              minHeight: 44,
              padding: 0,
              display: "grid",
              placeItems: "center",
            },
          },
          React.createElement(Icons.Close, null),
        ),
      ),
      React.createElement(
        "div",
        { style: { display: "grid", gap: 16, padding: 24 } },
        React.createElement(
          "div",
          {
            className: "sale-detail-client",
            "data-od-id": "sale-detail-client",
          },
          React.createElement(
            "div",
            { style: { minWidth: 0 } },
            React.createElement(
              "div",
              { className: "sale-detail-meta-label" },
              "Cliente",
            ),
            React.createElement(
              "div",
              { style: { marginTop: 4, fontSize: 16, fontWeight: 600 } },
              sale.cliente,
            ),
            React.createElement(
              "div",
              { style: { marginTop: 3, color: "var(--muted)", fontSize: 12 } },
              "Atendi\xF3: ",
              sale.vendedor,
            ),
          ),
          React.createElement(
            "span",
            {
              className:
                "pill pill-" +
                (isPublic
                  ? "muted"
                  : sale.tipoVenta === "mayoreo"
                    ? "gold"
                    : "accent"),
            },
            isPublic ? "Público general" : "Cliente registrado",
          ),
        ),
        React.createElement(
          "div",
          {
            className: "sale-detail-meta",
            "data-od-id": "sale-detail-metadata",
          },
          React.createElement(
            "div",
            { className: "sale-detail-meta-item" },
            React.createElement(
              "div",
              { className: "sale-detail-meta-label" },
              "Fecha y hora",
            ),
            React.createElement(
              "div",
              { className: "sale-detail-meta-value" },
              formatSalesDate(sale.fecha),
              " \xB7 ",
              sale.hora,
            ),
          ),
          React.createElement(
            "div",
            { className: "sale-detail-meta-item" },
            React.createElement(
              "div",
              { className: "sale-detail-meta-label" },
              "Tipo de venta",
            ),
            React.createElement(
              "div",
              { className: "sale-detail-meta-value" },
              sale.tipoVenta === "mayoreo" ? "Mayoreo" : "Menudeo",
            ),
          ),
          React.createElement(
            "div",
            { className: "sale-detail-meta-item" },
            React.createElement(
              "div",
              { className: "sale-detail-meta-label" },
              "Condici\xF3n",
            ),
            React.createElement(
              "div",
              { className: "sale-detail-meta-value" },
              sale.condicion === "credito" ? "Crédito" : "Contado",
            ),
          ),
          React.createElement(
            "div",
            { className: "sale-detail-meta-item" },
            React.createElement(
              "div",
              { className: "sale-detail-meta-label" },
              "Tipo de pago",
            ),
            React.createElement(
              "div",
              { className: "sale-detail-meta-value" },
              SALES_PAYMENT_LABELS[sale.tipoPago],
            ),
          ),
        ),
        React.createElement(
          "div",
          null,
          React.createElement(
            "div",
            {
              style: {
                display: "flex",
                alignItems: "baseline",
                justifyContent: "space-between",
                gap: 16,
                marginBottom: 8,
              },
            },
            React.createElement(
              "h3",
              { style: { fontSize: 14, fontWeight: 600 } },
              "Piezas vendidas",
            ),
            React.createElement(
              "span",
              { style: { color: "var(--muted)", fontSize: 12 } },
              sale.sucursal,
            ),
          ),
          React.createElement(
            "div",
            {
              className: "sale-detail-items",
              "data-od-id": "sale-detail-items",
            },
            React.createElement(
              "table",
              null,
              React.createElement(
                "thead",
                null,
                React.createElement(
                  "tr",
                  null,
                  React.createElement("th", null, "SKU"),
                  React.createElement("th", null, "Pieza"),
                  React.createElement(
                    "th",
                    { style: { textAlign: "center" } },
                    "Cantidad",
                  ),
                  React.createElement(
                    "th",
                    { style: { textAlign: "right" } },
                    "Precio unitario",
                  ),
                  React.createElement(
                    "th",
                    { style: { textAlign: "right" } },
                    "Subtotal",
                  ),
                ),
              ),
              React.createElement(
                "tbody",
                null,
                sale.items.map((item, index) =>
                  React.createElement(
                    "tr",
                    {
                      key: item.sku + "-" + index,
                      "data-od-id": "sale-item-" + sale.id + "-" + index,
                    },
                    React.createElement(
                      "td",
                      { className: "mono", style: { color: "var(--accent)" } },
                      item.sku,
                    ),
                    React.createElement(
                      "td",
                      { style: { fontWeight: 500 } },
                      item.nombre,
                    ),
                    React.createElement(
                      "td",
                      { className: "tabular", style: { textAlign: "center" } },
                      item.cantidad,
                    ),
                    React.createElement(
                      "td",
                      { className: "tabular", style: { textAlign: "right" } },
                      formatMoney(item.precioUnitario),
                    ),
                    React.createElement(
                      "td",
                      {
                        className: "tabular",
                        style: { textAlign: "right", fontWeight: 600 },
                      },
                       formatMoney(
                         item.total ?? item.cantidad * item.precioUnitario,
                       ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
        sale.payments?.length > 0 &&
          React.createElement(
            "div",
            { style: { display: "grid", gap: 6 } },
            React.createElement(
              "div",
              { className: "sale-detail-meta-label" },
              "Pagos registrados",
            ),
            sale.payments.map((payment) =>
              React.createElement(
                "div",
                {
                  key: payment.id,
                  style: { display: "flex", justifyContent: "space-between" },
                },
                React.createElement(
                  "span",
                  null,
                  SALES_PAYMENT_LABELS[payment.method] || payment.method,
                ),
                React.createElement(
                  "span",
                  { className: "tabular" },
                  formatMoney(payment.amount),
                ),
              ),
            ),
          ),
        React.createElement(
          "div",
          { className: "sale-detail-total" },
          React.createElement(
            "span",
            { style: { color: "var(--muted)", fontSize: 13 } },
            "Total de la venta",
          ),
          React.createElement(
            "span",
            { className: "tabular", style: { fontSize: 24, fontWeight: 700 } },
            formatMoney(total),
          ),
        ),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "16px 24px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
          },
        },
          sale.estado !== "cancelada" && onCancel &&
            React.createElement(
              "button",
              {
                "data-od-id": "cancel-sale-control",
                type: "button",
                className: "btn-secondary",
                onClick: onCancel,
                style: { minHeight: 44, color: "var(--danger)" },
              },
              "Cancelar venta",
            ),
          React.createElement(
            "button",
            {
              "data-od-id": "dismiss-sale-detail-control",
              type: "button",
              className: "btn-secondary",
              onClick: onClose,
              style: { minHeight: 44 },
            },
            "Cerrar",
          ),
      ),
    ),
  );
}
function SalesView({ ventas = [], actions = {}, currentUser }) {
  const [dateRange, setDateRange] = useState(getCurrentSalesWeekRange);
  const [selectedSale, setSelectedSale] = useState(null);
  const currentMonthRange = getCurrentSalesMonthRange();
  const isCurrentMonth =
    dateRange.from === currentMonthRange.from &&
    dateRange.to === currentMonthRange.to;
  const selectFromDate = (value) => {
    setDateRange((current) => ({
      from: value,
      to: value && current.to && value > current.to ? value : current.to,
    }));
  };
  const selectToDate = (value) => {
    setDateRange((current) => ({
      from:
        value && current.from && value < current.from ? value : current.from,
      to: value,
    }));
  };
  const filteredSales = ventas.filter(
    (venta) =>
      (!dateRange.from || venta.fecha >= dateRange.from) &&
      (!dateRange.to || venta.fecha <= dateRange.to),
  );
  const confirmedSales = filteredSales.filter((venta) => venta.estado !== "cancelada");
  const periodTotal = confirmedSales.reduce(
    (sum, venta) => sum + getSaleTotal(venta),
    0,
  );
  const creditSales = confirmedSales.filter(
    (venta) => venta.condicion === "credito",
  ).length;
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");
  const canCancelSales = ["admin", "encargado"].includes(currentUser?.rol);
  const openSaleDetail = async (sale) => {
    setDetailError("");
    if (!sale.summaryOnly || typeof actions.getSaleDetail !== "function") {
      setSelectedSale(sale);
      return;
    }
    setDetailLoading(true);
    try {
      setSelectedSale(await actions.getSaleDetail(sale.id));
    } catch (error) {
      setDetailError(error.message || "No se pudo cargar el detalle de la venta.");
    } finally {
      setDetailLoading(false);
    }
  };
  const cancelSelectedSale = async () => {
    if (!canCancelSales || !selectedSale || typeof actions.cancelSale !== "function") return;
    const reason = window.prompt("Motivo de cancelación de la venta:");
    if (!reason?.trim()) return;
    setDetailError("");
    setDetailLoading(true);
    try {
      setSelectedSale(
        await actions.cancelSale(
          selectedSale.id,
          { reason: reason.trim() },
          crypto.randomUUID(),
        ),
      );
    } catch (error) {
      setDetailError(error.message || "No se pudo cancelar la venta.");
    } finally {
      setDetailLoading(false);
    }
  };
  return React.createElement(
    MainLayout,
    {
      title: "Ventas",
      actions: React.createElement(
        "span",
        { className: "pill pill-success", "data-od-id": "sales-api-label" },
        "API local",
      ),
    },
    React.createElement(
      "div",
      { className: "card", "data-od-id": "sales-screen" },
      React.createElement(
        "div",
        { className: "sales-filter-bar", "data-od-id": "sales-date-filter" },
        React.createElement(
          "div",
          null,
          React.createElement(
            "div",
            { style: { fontWeight: 600 } },
            "Periodo de ventas",
          ),
          React.createElement(
            "div",
            { style: { marginTop: 3, color: "var(--muted)", fontSize: 12 } },
            "La semana en curso se muestra por defecto; puedes elegir cualquier rango.",
          ),
        ),
        React.createElement(
          "div",
          { className: "sales-date-range" },
          React.createElement(SalesDateField, {
            label: "Desde",
            value: dateRange.from,
            onChange: selectFromDate,
            dataId: "sales-date-from-control",
          }),
          React.createElement(SalesDateField, {
            label: "Hasta",
            value: dateRange.to,
            onChange: selectToDate,
            dataId: "sales-date-to-control",
          }),
          React.createElement(
            "button",
            {
              "data-od-id": "reset-sales-current-month",
              type: "button",
              className: "btn-ghost",
              onClick: () => setDateRange(getCurrentSalesMonthRange()),
              disabled: isCurrentMonth,
              style: { minHeight: 44 },
            },
            "Mes actual",
          ),
        ),
      ),
      detailError &&
        React.createElement(
          "div",
          { className: "client-form-error", role: "alert", style: { margin: 16 } },
          detailError,
        ),
      detailLoading &&
        React.createElement(
          "div",
          { className: "api-read-only-notice", role: "status" },
          "Cargando detalle de la venta…",
        ),
      React.createElement(
        "div",
        {
          className: "sales-summary-strip",
          "data-od-id": "sales-period-summary",
        },
        React.createElement(
          "div",
          { className: "sales-summary-item" },
          React.createElement(
            "div",
            { className: "sales-summary-label" },
            "Importe vendido",
          ),
          React.createElement(
            "div",
            { className: "sales-summary-value" },
            formatMoney(periodTotal),
          ),
        ),
        React.createElement(
          "div",
          { className: "sales-summary-item" },
          React.createElement(
            "div",
            { className: "sales-summary-label" },
            "Operaciones",
          ),
          React.createElement(
            "div",
            { className: "sales-summary-value" },
             confirmedSales.length,
          ),
        ),
        React.createElement(
          "div",
          { className: "sales-summary-item" },
          React.createElement(
            "div",
            { className: "sales-summary-label" },
            "Ventas a crédito",
          ),
          React.createElement(
            "div",
            { className: "sales-summary-value" },
            creditSales,
          ),
        ),
      ),
      React.createElement(
        "div",
        {
          style: {
            padding: "12px 16px",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
            gap: 16,
          },
        },
        React.createElement(
          "div",
          { style: { fontWeight: 600 } },
          "Listado de ventas",
        ),
        React.createElement(
          "div",
          { style: { color: "var(--muted)", fontSize: 12 } },
          "Selecciona una venta para consultar sus piezas.",
        ),
      ),
      React.createElement(
        "div",
        { className: "sales-table-wrap", "data-od-id": "sales-table-region" },
        React.createElement(
          "table",
          null,
          React.createElement(
            "thead",
            null,
            React.createElement(
              "tr",
              null,
              React.createElement("th", null, "Folio"),
              React.createElement("th", null, "Estado"),
              React.createElement("th", null, "Fecha"),
              React.createElement("th", null, "Cliente"),
              React.createElement("th", null, "Tipo de venta"),
              React.createElement("th", null, "Condición"),
              React.createElement("th", null, "Tipo de pago"),
              React.createElement("th", null, "Sucursal"),
              React.createElement(
                "th",
                { style: { textAlign: "right" } },
                "Total",
              ),
            ),
          ),
          React.createElement(
            "tbody",
            null,
            filteredSales.map((venta) =>
              React.createElement(
                "tr",
                {
                  key: venta.id,
                  className: "sales-row",
                  "data-od-id": "sale-row-" + venta.id,
                  tabIndex: "0",
                  "aria-label":
                    "Ver detalle de la venta " +
                    venta.folio +
                    " de " +
                    venta.cliente,
                  onClick: () => openSaleDetail(venta),
                  onKeyDown: (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      openSaleDetail(venta);
                    }
                  },
                  style: venta.estado === "cancelada" ? { opacity: 0.65 } : undefined,
                },
                React.createElement(
                  "td",
                  {
                    className: "mono",
                    style: { color: "var(--accent)", fontWeight: 500 },
                  },
                  venta.folio,
                ),
                React.createElement(
                  "td",
                  null,
                  React.createElement(
                    "span",
                    { className: "pill pill-" + (venta.estado === "cancelada" ? "danger" : "success") },
                    venta.estado === "cancelada" ? "Cancelada" : "Confirmada",
                  ),
                ),
                React.createElement(
                  "td",
                  null,
                  React.createElement(
                    "div",
                    null,
                    formatSalesDate(venta.fecha),
                  ),
                  React.createElement(
                    "div",
                    {
                      className: "mono",
                      style: {
                        marginTop: 2,
                        color: "var(--muted)",
                        fontSize: 11,
                      },
                    },
                    venta.hora,
                  ),
                ),
                React.createElement(
                  "td",
                  { style: { fontWeight: 500 } },
                  venta.cliente,
                ),
                React.createElement(
                  "td",
                  null,
                  React.createElement(
                    "span",
                    {
                      className:
                        "pill pill-" +
                        (venta.tipoVenta === "mayoreo" ? "gold" : "muted"),
                    },
                    venta.tipoVenta,
                  ),
                ),
                React.createElement(
                  "td",
                  null,
                  React.createElement(
                    "span",
                    {
                      className:
                        "pill pill-" +
                        (venta.condicion === "credito" ? "accent" : "muted"),
                    },
                    venta.condicion === "credito" ? "Crédito" : "Contado",
                  ),
                ),
                React.createElement(
                  "td",
                  null,
                  SALES_PAYMENT_LABELS[venta.tipoPago],
                ),
                React.createElement(
                  "td",
                  { style: { color: "var(--muted)" } },
                  venta.sucursal,
                ),
                React.createElement(
                  "td",
                  {
                    className: "tabular",
                    style: { textAlign: "right", fontWeight: 600 },
                  },
                  formatMoney(getSaleTotal(venta)),
                ),
              ),
            ),
            filteredSales.length === 0 &&
              React.createElement(
                "tr",
                null,
                React.createElement(
                  "td",
                  {
                    colSpan: "8",
                    style: {
                      padding: 48,
                      textAlign: "center",
                      color: "var(--muted)",
                    },
                  },
                  "No hay ventas dentro del rango seleccionado.",
                ),
              ),
          ),
        ),
      ),
      React.createElement(SaleDetailModal, {
        sale: selectedSale,
        onClose: () => setSelectedSale(null),
        onCancel: canCancelSales ? cancelSelectedSale : undefined,
      }),
    ),
  );
}
export const SCREEN_VIEWS = {
  categories: CategoriesView,
  inventory: InventoryView,
  physicalcount: PhysicalCountView,
  pos: POSView,
  sales: SalesView,
  clients: ClientsView,
  credits: CreditsView,
  promotions: PromotionsView,
  repairs: RepairsView,
  transfers: TransfersView,
  reports: ReportsView,
  users: UsersView,
  settings: SettingsView,
};

export function createLegacyReadModel() {
  return {
    productos: PRODUCTOS,
    categorias: CATEGORIAS,
    materiales: MATERIALES,
    subcategorias: SUBCATEGORIAS_SEED,
    colecciones: COLECCIONES_SEED,
    ventas: VENTAS_DEMO,
    clientes: CLIENTES.map((client) => ({
      ...client,
      creditoActivo: client.tipo === "mayoreo" && Boolean(client.limiteCredito),
    })),
    reparaciones: REPARACIONES.map(normalizeRepairSeed),
  };
}

export { Sidebar };
