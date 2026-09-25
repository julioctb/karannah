# Sistema de interfaz — Joyería SaaS

## Dirección y sensación

Herramienta operativa para vendedores y administradores de una joyería. Debe sentirse precisa como un corte de inventario, calmada como un mostrador ordenado y suficientemente compacta para completar ventas y tareas administrativas sin perder contexto.

- Dominio: mostrador, ticket, pieza, inventario, sucursal, cliente, mayoreo, crédito y reparación.
- Mundo cromático: papel blanco de recibo, grafito de libro contable, plata pulida, índigo operativo, oro reservado para mayoreo y colores semánticos discretos.
- Firma de interacción: los flujos secundarios se resuelven en contexto. Un cliente creado desde el POS regresa seleccionado a la venta; sus condiciones comerciales se administran desde Clientes.
- Evitar: navegación innecesaria entre módulos, CTAs primarios duplicados, paneles decorativos y formularios alternativos para la misma regla.

## Tokens visuales

Usar los tokens del HTML como fuente de verdad. No introducir colores crudos nuevos.

```css
:root {
  --bg: oklch(98% 0.005 250);
  --surface: oklch(100% 0 0);
  --fg: oklch(22% 0.02 240);
  --muted: oklch(50% 0.018 240);
  --border: oklch(90% 0.008 240);
  --accent: oklch(48% 0.12 270);
  --accent-light: oklch(95% 0.03 270);
  --success: oklch(55% 0.16 145);
  --success-bg: oklch(95% 0.04 145);
  --warning: oklch(70% 0.15 85);
  --warning-bg: oklch(95% 0.04 85);
  --danger: oklch(55% 0.2 25);
  --danger-bg: oklch(95% 0.04 25);
  --gold: oklch(75% 0.12 85);
  --gold-bg: oklch(96% 0.03 85);
}
```

- Índigo: acciones y selección.
- Oro: clasificación mayoreo; no usar como acento decorativo.
- Verde, ámbar y rojo: éxito, advertencia y error únicamente.
- Fondo y superficies: misma familia fría; la jerarquía depende de cambios leves de luminosidad.

## Tipografía

- Display y cuerpo: `Inter`, pesos 400–700.
- Datos, SKU, teléfono y cifras operativas: `JetBrains Mono`, pesos 400–500.
- Cifras: números tabulares.
- Encabezados: peso 600, sin sobredimensionar.
- Etiquetas de formulario: 12 px, peso 500, color `--muted`.

## Profundidad y geometría

- Estrategia: bordes y cambios sutiles de superficie; no mezclar con sombras dramáticas.
- Controles: radio de 6 px.
- Tarjetas, paneles y modales: radio de 8 px.
- Separadores: `1px solid var(--border)`.
- Overlay de modal: negro al 50%; tarjeta blanca centrada y contenida dentro del viewport.
- Enfoque: anillo de 2 px en `--accent`, desplazado 2 px.

## Espaciado

- Unidad base: 8 px.
- Microespacio: 4–6 px para icono/texto y metadatos.
- Componentes: 8–16 px.
- Secciones: 20–24 px.
- Altura mínima de controles táctiles: 44 px.
- Modales de formulario: `min(620px, calc(100vw - 32px))`, máximo 90 vh.

## Patrones de acción

- Una sola acción primaria por contexto. Acciones auxiliares usan `btn-secondary` o `btn-ghost`.
- Botón primario: fondo `--accent` y texto blanco; hover mantiene o aumenta el contraste.
- Controles segmentados: siempre secundarios; la selección usa `--accent-light`, texto `--accent` y borde `--accent`.
- Acciones destructivas usan `--danger`; nunca usar color solo como decoración.
- Todos los controles deben tener hover, active, focus-visible y disabled.

## Patrón de modal

- Encabezado con título, explicación breve y cierre de 44×44 px.
- Cuerpo en cuadrícula de dos columnas; cambia a una columna por debajo de 760 px.
- Errores inline bajo el campo, sin cambiar el layout abruptamente.
- Pie con Cancelar secundario y una única acción primaria.
- Escape cierra el modal.
- Añadir `role="dialog"`, `aria-modal`, título enlazado y `data-od-id` en región, controles y CTA.

## Clientes y permisos

Estas reglas son invariantes y deben permanecer centralizadas:

1. Todo cliente nuevo se registra como `menudeo`, sin crédito y con saldo inicial cero.
2. Clientes y POS reutilizan el mismo modal `NewClientModal`; no crear formularios alternativos.
3. Si el alta ocurre en POS, el cliente nuevo queda seleccionado en la venta.
4. Solo un usuario con rol `admin` puede administrar condiciones comerciales.
5. La autorización se deriva de un único helper: `canManageClientCommercialProfile`.
6. El cambio comercial pasa por `updateClientCommercialProfile`; no modificar tipo o crédito directamente desde una vista.
7. Un cliente mayoreo puede existir sin crédito.
8. El crédito solo puede estar activo cuando el cliente es mayoreo y tiene un límite mayor que cero.
9. Cambiar a menudeo desactiva crédito y elimina el límite.
10. El método Crédito del POS permanece deshabilitado si `creditoActivo` es falso.

Patrones asociados:

- Alta: `NewClientModal` con nombre, teléfono y correo; muestra la política de menudeo sin exponer tipo ni límite.
- Administración: `ClientCommercialModal`, accesible desde el botón Administrar en la tabla de Clientes.
- Tabla: muestra tipo, crédito, disponible y gestión administrativa; “Sin crédito” es un estado explícito.
- Mayoreo: pill dorado; menudeo y ausencia de crédito: tratamiento neutro.

## Integridad técnica

- La fuente de verdad del frontend es el proyecto Vite/React: `src/App.jsx` es
  el shell, `src/screens/` contiene las vistas heredadas, `src/components/`
  contiene estados y límites compartidos, `src/domain/` concentra reglas del
  modelo visual, `src/lib/api.js` concentra el contrato HTTP y sus adaptadores,
  `src/context/AuthContext.jsx` es dueño de la sesión, `src/pages/` contiene
  pantallas independientes y `src/styles.css` contiene los tokens y estilos.
- `joyeria-saas-prototipo.html` es referencia heredada (artefacto de OpenDesign, `renderer: "html"`). Solo se sincroniza con correcciones críticas; no se editan features en él.
- React y ReactDOM se instalan por npm (`react@18.3.1`, `react-dom@18.3.1`); no reintroducir dependencias remotas ni copias en `assets/runtime` para la app React.
- Fuentes locales en `src/assets/` (`inter-latin.woff2`, `jetbrains-mono-latin.woff2`); los `@font-face` de `src/styles.css` usan `url('./assets/...')`.
- No reintroducir el patrón `return` + salto de línea antes de `React.createElement` (ASI rompe la vista: `ReportsView` y `SettingsView` ya fueron corregidos en ambas fuentes).
- Conservar la forma segura de FileReader: `["readAsData"+"URL"](`; el visualizador corrompe `.readAsDataURL(`.
- Mantener `data-od-id` en regiones, CTAs y controles relevantes.
