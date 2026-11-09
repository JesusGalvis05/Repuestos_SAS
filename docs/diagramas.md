# Diagramas mantenibles

## C4 — contexto

```mermaid
flowchart LR
  A[Administrador] --> J[JG Repuestos]
  S[Socio] --> J
  V[Vendedor] --> J
  I[Inventario] --> J
  J -. Futuro .-> P[Proveedores: catálogos y órdenes]
  J -. Futuro .-> C[Clientes: comprobantes internos]
```

## C4 — contenedores

```mermaid
flowchart TB
  U[Persona usuaria] --> B[SPA React / TypeScript / Tailwind]
  B -->|REST JSON /api/v1, JWT + cookie HttpOnly| F[Monolito FastAPI / Python]
  F -->|SQLAlchemy 2.0 / psycopg| D[(PostgreSQL)]
  M[Alembic, ejecución previa al arranque] --> D
  CLI[CLI de aprovisionamiento] --> F
```

La CLI reutiliza servicios del monolito, no es otra aplicación backend desplegable.
En el Compose académico sólo existen api y db; React se ejecuta con Vite en el
host y dirige `/api` a FastAPI. El despliegue local alternativo sirve el build
React desde el mismo proceso FastAPI. No se incluye nginx como tercer servicio.

## Componentes implementados

```mermaid
flowchart LR
  HTTP[Rutas FastAPI] --> SC[Esquemas Pydantic]
  HTTP --> AU[Dependencias JWT + RBAC]
  HTTP --> SV[Servicios de identidad]
  SV --> RP[Repositorio de identidad]
  SV --> AR[Repositorio de auditoría]
  RP --> MO[Modelos SQLAlchemy]
  AR --> AM[Modelo AuditLog]
  MO --> PG[(PostgreSQL)]
  AM --> PG
  TX[Dependencia sesión/transacción] --> HTTP
```

## Entidad-relación — esquema existente

```mermaid
erDiagram
  users ||--o{ user_roles : tiene
  roles ||--o{ user_roles : asignado
  roles ||--o{ role_permissions : concede
  permissions ||--o{ role_permissions : autoriza
  users ||--o{ auth_sessions : inicia
  auth_sessions ||--o{ refresh_tokens : rota
  users |o--o{ audit_logs : actor
  users {
    uuid id PK
    varchar email UK
    varchar full_name
    varchar password_hash
    boolean active
    integer failed_attempts
    timestamptz locked_until
    timestamptz last_login_at
  }
  auth_sessions {
    uuid id PK
    uuid user_id FK
    timestamptz expires_at
    timestamptz revoked_at
  }
  refresh_tokens {
    uuid id PK
    uuid session_id FK
    varchar token_hash UK
    timestamptz consumed_at
  }
  audit_logs {
    uuid id PK
    uuid actor_id FK
    varchar action
    varchar target_id
    json details
    timestamptz created_at
  }
```

Las entidades comerciales del documento maestro se agregarán con migraciones
de las fases correspondientes; este diagrama no afirma que existan todavía.

## Secuencia implementada — autenticación

```mermaid
sequenceDiagram
  actor U as Usuario
  participant R as React
  participant F as FastAPI
  participant S as IdentityService
  participant P as PostgreSQL
  U->>R: Correo y contraseña
  R->>F: POST /api/v1/auth/login
  F->>S: Validación Pydantic y caso de uso
  S->>P: BEGIN / usuario FOR UPDATE
  S->>S: Verificar Argon2id / actividad / bloqueo
  alt Acceso válido
    S->>P: Sesión + hash refresh + auditoría
    F->>P: COMMIT antes de enviar respuesta
    F-->>R: Access JWT + cookie HttpOnly
  else Rechazado
    S->>P: Contador + auditoría
    F->>P: COMMIT antes de enviar respuesta
    F-->>R: 401 genérico
  end
```

## Diseño futuro — compra y recepción (Fase 4)

```mermaid
sequenceDiagram
  actor U as Compras
  participant A as API monolito
  participant S as Servicio compras
  participant P as PostgreSQL
  U->>A: Confirmar recepción parcial + clave idempotencia
  A->>S: Permisos y contrato validados
  S->>P: BEGIN / idempotencia única / bloquear orden y saldos
  S->>S: Validar pendiente y distribuir costos con Decimal
  S->>P: Recibo + movimientos + saldo + costo promedio + auditoría
  S->>P: Guardar respuesta idempotente
  A->>P: COMMIT
  A-->>U: Recepción confirmada
```

## Diseño futuro — venta entregada (Fase 5)

```mermaid
sequenceDiagram
  actor U as Vendedor
  participant A as API monolito
  participant S as Servicio ventas
  participant P as PostgreSQL
  U->>A: Entregar venta + clave idempotencia
  A->>S: Permisos y contrato validados
  S->>P: BEGIN / idempotencia única / bloquear venta y saldos
  S->>S: Validar disponibilidad y descuentos autorizados
  alt Existencias suficientes
    S->>P: Movimiento salida + costo histórico + estado entrega + auditoría
    S->>P: Guardar respuesta idempotente
    A->>P: COMMIT
    A-->>U: Venta entregada
  else Existencias insuficientes
    A->>P: ROLLBACK
    A-->>U: Conflicto de existencias
  end
```
