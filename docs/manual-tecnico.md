# Manual técnico

Instalación y ejecución: `../README.md`. Requisitos: Python 3.12+, Node 24,
PostgreSQL 17+; Docker Desktop/Compose v2 para contenedores. Abrir la raíz del
repositorio en VS Code, preparar entorno, migrar, crear administrador e iniciar
backend y frontend. No es necesario activar el entorno virtual para los scripts.

## Configuración

| Variable backend | Uso |
| --- | --- |
| DATABASE_URL | URL `postgresql+psycopg://...`; nunca SQLite como sustituto operacional |
| JWT_SECRET | Secreto aleatorio de al menos 32 caracteres |
| APP_ENV | development, test o production |
| COOKIE_SECURE | false sólo HTTP local; true para HTTPS |
| ALLOWED_ORIGINS | Lista JSON explícita de orígenes del navegador |
| ACCESS_TOKEN_MINUTES | 10 por defecto; máximo 30 |
| REFRESH_TOKEN_DAYS | Caducidad absoluta de sesión; 7 por defecto |
| LOGIN_MAX_ATTEMPTS | 5 por defecto |
| LOGIN_LOCK_MINUTES | 15 por defecto |
| FRONTEND_DIST | Ruta opcional al build React para servir SPA y API en el mismo proceso |

`scripts/configure.py` genera secretos distintos por instalación sin imprimirlos.
No sobrescribe archivos existentes. Si cambia la contraseña local de PostgreSQL,
actualice coherentemente la base, `.env` raíz y `backend/.env`.

## Contratos implementados

| Método y ruta `/api/v1` | Acceso y efecto |
| --- | --- |
| GET /health | Público; vida del proceso |
| GET /ready | Público; conexión y tabla de usuarios disponibles |
| POST /auth/login | Correo/contraseña; JWT y cookie refresh |
| POST /auth/refresh | Cookie + Origin permitido; rotación |
| POST /auth/logout | Cookie + Origin permitido; revocación idempotente |
| GET /auth/me | JWT y sesión vigente; perfil y permisos |
| POST /auth/change-password | JWT; actual/nueva; revoca todas las sesiones |
| GET /auth/sessions | JWT; sólo sesiones propias activas |
| DELETE /auth/sessions/{id} | JWT; sólo sesión propia; revocación idempotente |
| GET /users | `users.manage`; búsqueda y paginación |
| POST /users | `users.manage`; crea cuenta y asigna roles |
| PATCH /users/{id} | `users.manage`; nombre, roles y estado |
| GET /roles | `users.manage`; roles y permisos sembrados por migración |

Ejemplo de error: `{"error":{"code":"FORBIDDEN","message":"..."}}`.
422 contiene campos y tipos de validación sin copiar inputs secretos. La API no
expone hashes, cookies ni entidades ORM. Las solicitudes reciben `X-Request-ID`;
el log registra método, estado y duración sin cuerpos ni cabeceras de acceso.

## Evolución y pruebas

Desde backend: `python -m alembic revision --autogenerate -m "descripcion"`;
revisar manualmente restricciones y datos; ejecutar `upgrade head` y `check`.
Las revisiones importan únicamente sus propias definiciones estables. `downgrade`
puede destruir datos y sólo se valida automáticamente en esquemas de prueba.

Dependencias Python fijadas en `requirements.lock` y `requirements-dev.lock`;
instalar con pip, luego `pip install --no-deps -e ./backend`. Para actualizar,
modificar pyproject, resolver en entorno limpio con `pip install -e ./backend[dev]`,
ejecutar `python scripts/lock_dependencies.py` y repetir pruebas. Frontend usa
`npm ci` y `package-lock.json`; no se incluyen dependencias instaladas en Git.

El backend usa SQLAlchemy síncrono en rutas síncronas. Los servicios no hacen
commit: comparten la transacción de solicitud. En procesos administrativos se usa
`with session, session.begin()`. No compartir sesiones entre hilos ni solicitudes.

## Operación y límites

Una contraseña cambiada o un rol modificado fuerza nuevo acceso. No hay correo
de recuperación, MFA ni autenticación externa en Fase 1. Se debe mantener un
procedimiento operacional controlado para recuperar cuentas administrativas.
No hay tablas, datos ni reportes comerciales todavía.

Antes de producción: proxy HTTPS, orígenes y cookies seguras, usuario de base con
privilegios mínimos para la API, credencial de migración separada, respaldos
probados, política de retención de auditoría, limpieza de sesiones expiradas,
rate limiting por origen y revisión de dependencias. El Compose entregado es local.

## Respaldo y restauración

Ejemplo de respaldo desde el contenedor, sin exponer credenciales en argumentos:

```powershell
docker compose exec db pg_dump -U jg -d jg_repuestos -Fc -f /tmp/jg.dump
docker compose cp db:/tmp/jg.dump .local/jg.dump
```

Proteja el archivo con controles de acceso y almacenamiento cifrado. Para
restaurar, cree una base vacía separada y pruebe allí; no restaure sobre datos
operacionales sin un procedimiento de recuperación aprobado. En esa base:

```powershell
docker compose cp .local/jg.dump db:/tmp/jg.dump
docker compose exec db createdb -U jg jg_restore
docker compose exec db pg_restore -U jg -d jg_restore /tmp/jg.dump
```

Verificar revisión Alembic, integridad y acceso antes de promover una restauración.
La Fase 7 ampliará y probará este procedimiento con todos los módulos.
