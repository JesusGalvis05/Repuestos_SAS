# ADR 0001 — Monolito modular Python

Estado: aceptado por instrucción obligatoria del usuario.

Contexto: el documento inicial proponía un backend Java. El cambio solicitado
exige Python conservando reglas comerciales, documentación y desarrollo por fases.

Decisión: FastAPI, SQLAlchemy 2.0 síncrono con psycopg, Pydantic v2, Alembic y
PostgreSQL; React + TypeScript + Vite + Tailwind. Una sola aplicación backend,
módulos de negocio y API REST `/api/v1`. Pytest sustituye JUnit. `Decimal`
sustituye BigDecimal; `NUMERIC` sigue siendo obligatorio para importes futuros.

Las rutas delegan reglas a servicios y datos a repositorios; los esquemas nunca
exponen directamente los modelos persistentes. Las funciones HTTP síncronas
corren en el thread pool de FastAPI, evitando bloquear el bucle ASGI con psycopg.

Consecuencias: despliegue y transacciones locales simples. Los contratos quedan
listos para clientes móviles futuros. No se incorporan colas, microservicios ni
procesos backend independientes. Los endpoints comerciales se agregan al mismo
monolito cuando su fase sea aceptada.
