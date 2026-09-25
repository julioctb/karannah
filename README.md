# Joyería SaaS

Plataforma de gestión para una joyería con múltiples sucursales.

## Arquitectura

```
React/Vite (frontend)
├── Auth local     → desarrollo sin servicios externos
├── Supabase Auth  → producción (Fase 9)
└── FastAPI /api/v1 (backend)
    ├── Autorización por rol y sucursal
    ├── Reglas de negocio (POS, crédito, inventario)
    ├── PostgreSQL local
    └── Imágenes locales mediante adaptador de almacenamiento
```

- **Auth local** permite desarrollar con JWT HMAC y usuarios semilla sin depender de Supabase.
- **Supabase Auth** gestionará identidad y sesiones en producción. El frontend lo usará solo para autenticarse.
- **FastAPI** es la única API para datos operativos. Valida el proveedor de
  autenticación configurado y accede a PostgreSQL.
- **Almacenamiento local** persiste imágenes durante el desarrollo. Supabase
  Storage reemplazará ese adaptador únicamente en la Fase 9.
- La `service_role` **nunca** se expone al frontend.

## Estructura

```
Joyeria/
├── frontend/        App React/Vite
├── backend/         API FastAPI
├── docs/
│   ├── API_CONTRACT.md Contrato frontend/backend
│   ├── system.md    Especificación de diseño y reglas de dominio
│   └── prototype/   HTML del prototipo original (referencia)
├── .env.example     Índice de configuración
└── README.md
```

## Setup

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev        # http://localhost:5173
npm run build
```

### Backend

```bash
docker compose up -d postgres   # desde la raiz del proyecto
cd backend
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000   # http://localhost:8000/docs
pytest
```

PostgreSQL queda disponible en `localhost:54329`. Para detenerlo usa
`docker compose stop postgres`; el volumen conserva los datos entre reinicios.

`DATABASE_URL` debe usar `postgresql+asyncpg://`. El seed crea datos de negocio,
pero no identidades. Para invitar al primer administrador:

```bash
python -m app.provision_user \
  --email admin@example.com \
  --name "Administrador" \
  --role admin
```

Para encargados y vendedores agrega una o más opciones `--branch T01`.

Las imágenes se guardan por defecto en `backend/media/products/` y FastAPI las
sirve desde `/media/products`. `PRODUCT_MEDIA_ROOT`, límites de bytes y píxeles
se configuran en `backend/.env`.

## Estado del proyecto

Estado actual: **Fase 4 completada funcionalmente: POS, ventas y crédito conectados**.

React y FastAPI operan CRUD de catálogo, productos con variantes, clientes,
imágenes, inventario, cotización, caja, checkout, pagos, crédito, aprobaciones de
descuento, historial de ledger y cancelación compensatoria de ventas sobre el
contrato local, incluyendo el reporte server-side de recuperación de crédito. La
concurrencia sobre PostgreSQL real y la consolidación final de migraciones quedan
para el cierre del desarrollo. Supabase queda reservado para la Fase 9.

Ver el plan por fases completo en `docs/PLAN.md`.
