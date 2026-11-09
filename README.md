# JG Repuestos

Sistema comercial e inventario para JG Repuestos, Colombia. Monolito modular con
**Python, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic y PostgreSQL**. Frontend
React, TypeScript, Vite y Tailwind CSS. API versionada: `/api/v1`.

Esta entrega implementa **Fase 1: fundamentos, autenticación, usuarios y roles**.
El inicio muestra el estado real de conexión; las métricas comerciales se
incorporarán con sus módulos. Consulte [avance y pendientes](docs/avance.md).

Para ejecutar el build completo sin Docker en este equipo Windows, consulte
[despliegue local](docs/despliegue.md). El script `scripts/deploy_local.py` sirve
frontend y API en `http://localhost:8080` y genera el administrador inicial sin
guardar su contraseña. El `Dockerfile` de la raíz prepara también un contenedor
único para alojar FastAPI y React con PostgreSQL externo.

## Ejecutar con Docker Compose

Requisitos: Python 3.12+ para el configurador y Docker Desktop con Compose v2.
Desde la raíz:

```powershell
python scripts/configure.py
docker compose up --build -d
docker compose exec api python -m app.cli create-admin
```

El último comando solicita nombre, correo y contraseña de forma interactiva;
no hay usuarios ni contraseñas predeterminadas. El alta inicial se bloquea
atómicamente cuando existe un administrador activo. Las migraciones se ejecutan
en el servicio `migrate` antes del inicio de la API.

- Aplicación: http://localhost:8080
- OpenAPI/Swagger: http://localhost:8000/api/v1/docs
- Disponibilidad API/BD: http://localhost:8000/api/v1/ready

`docker compose down` detiene servicios y conserva la base. El volumen contiene
datos persistentes. No borre el volumen para actualizar la aplicación.

## Ejecutar desde Visual Studio Code en Windows

Abra esta carpeta en VS Code e instale las extensiones recomendadas. Necesita
Python 3.12+, Node 24 y PostgreSQL 17+ (local o con Docker).

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1
docker compose up db -d
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m app.cli create-admin
cd ..
```

Si utiliza PostgreSQL local, configure una base y usuario dedicados y ajuste
`DATABASE_URL` en `backend/.env` antes de migrar; omita `docker compose up db`.
No copie contraseñas de bases reales al repositorio.

En una terminal ejecute:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/backend.ps1
```

En otra:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/frontend.ps1
```

Abra http://localhost:5173. Vite redirige `/api` a FastAPI. Use F5 con
**FastAPI: JG Repuestos** para depurar; no inicie simultáneamente el script
backend en el mismo puerto. Las tareas de VS Code incluyen migraciones,
frontend, preparación y Pytest. `npm.cmd` evita conflictos con `npm.ps1` en
equipos con ejecución de scripts restringida.

## Pruebas y verificación

```powershell
cd backend
# PostgreSQL real: las pruebas crean y eliminan solamente esquemas test_<UUID>.
$env:TEST_DATABASE_URL='postgresql+psycopg://usuario:clave@localhost:5432/base_de_pruebas'
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe -m alembic check
cd ../frontend
npm.cmd ci
npm.cmd test
npm.cmd run build
```

Alternativa: defina `USE_TESTCONTAINERS=1` y Pytest levantará PostgreSQL 17
mediante Docker. Sin ambas opciones, se ejecutan las pruebas unitarias y las de
PostgreSQL se omiten explícitamente. Use una base exclusiva de pruebas y un
usuario con permiso para crear esquemas. Las pruebas usan Alembic, no
`metadata.create_all()`.

La integración continua verifica backend, frontend y el arranque completo con
Docker Compose. [Matriz de pruebas](docs/pruebas.md).

## Seguridad y operación

- Argon2id; JWT de 10 minutos y sesión revocable comprobada en cada solicitud.
- Refresh opaco en cookie HttpOnly, SameSite Strict; sólo su hash se almacena.
- Rotación de refresh con detección de reutilización; revocación de la sesión.
- Tokens de acceso únicamente en memoria del navegador.
- Roles `admin`, `partner`, `seller`, `inventory`; permisos comprobados en API.
- Contadores de intentos fallidos y bloqueo temporal persistentes en PostgreSQL.
- Cambio de contraseña o de acceso revoca las sesiones afectadas.
- Auditoría de accesos, fallos, creación de usuarios y cambios de privilegios.
- CORS con lista explícita y validación de Origin para operaciones con cookies.

Compose es un entorno **local** ligado a `127.0.0.1`. Para producción configure
HTTPS, `APP_ENV=production`, `COOKIE_SECURE=true`, orígenes HTTPS y un gestor de
secretos; adapte el proxy. Cambiar `.env` después de crear el volumen no cambia
automáticamente la contraseña de PostgreSQL.

[Arquitectura](docs/arquitectura.md) · [Requisitos completos adaptados](docs/requisitos-maestros.md)
· [Manual técnico](docs/manual-tecnico.md) · [Manual de usuario](docs/manual-usuario.md)
· [Documentación académica](docs/academico.md) · [Diagramas](docs/diagramas.md)
