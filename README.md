# JG Repuestos

**Entrega proyecto 1 · Escenario 3 · Docker (150 puntos).**
Fecha límite: **martes 10 de noviembre de 2026, 23:55, America/Bogota**.
Esta entrega no desarrolla funcionalidades de Fase 2.

[Informe académico PDF](docs/entrega-1/JG_Repuestos_Entrega_1_Escenario_3.pdf) ·
[Matriz de los ocho criterios](docs/entrega-1/rubrica.md) ·
[Guion de demostración y evidencias](docs/entrega-1/demostracion.md)

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
al arrancar `api`, dentro del mismo contenedor y antes de Uvicorn. Si Alembic
falla, el servidor no se inicia. No hay tercer servicio de migraciones.

- API: http://localhost:8000/api/v1/health
- OpenAPI/Swagger: http://localhost:8000/api/v1/docs
- Disponibilidad API/BD: http://localhost:8000/api/v1/ready

`docker compose down` detiene servicios y conserva la base. El volumen contiene
datos persistentes. No borre el volumen para actualizar la aplicación.

`docker-compose.yml` contiene **exactamente dos servicios**, `api` y `db`,
unidos a la red bridge `jg-network`. Sólo la API publica `127.0.0.1:8000`.
PostgreSQL usa `db:5432`, sin puerto publicado al host, y el volumen
`postgres_data`. El backend arma su URL con `SQLAlchemy.URL.create` a partir de
`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST=db` y
`POSTGRES_PORT=5432`, por lo que admite caracteres especiales sin concatenarlos.
Con `DOCKER_RUNTIME=true` se rechaza cualquier otro host o puerto de PostgreSQL.

La imagen usa Python `3.12.16-slim-bookworm`, dependencias fijadas y UID/GID 10001.
PostgreSQL usa `17.11-bookworm`. Son versiones de imágenes oficiales verificadas
en los catálogos de [Python](https://github.com/docker-library/official-images/blob/master/library/python)
y [PostgreSQL](https://github.com/docker-library/official-images/blob/master/library/postgres).
La espera por salud sigue la [documentación oficial de Compose](https://docs.docker.com/compose/how-tos/startup-order/).

El frontend permanece separado y se ejecuta con Vite en el host; no se agrega
un tercer contenedor. `frontend/Dockerfile` y el Dockerfile raíz son alternativas
de despliegue anteriores, no forman parte del Compose académico.

## Demostrar comunicación real y persistencia

```powershell
docker compose config --quiet
docker compose build
docker compose up -d --wait --wait-timeout 180
docker compose ps
docker ps
docker network inspect jg-network
docker compose exec -T api python -m app.diagnostics roundtrip
docker compose logs api
docker compose logs db
```

El diagnóstico inserta un usuario temporal **inactivo y sin roles**, confirma la
transacción, lo lee en una sesión nueva y elimina exclusivamente ese UUID y sus
marcas de demostración. No crea endpoints de escritura ni muestra contraseñas.
El JSON resultante identifica host, puerto real del servidor y limpieza.

Para ejecutar todos los comandos, recrear ambos contenedores conservando el
volumen y comprobar que el registro sigue existiendo:

```powershell
.\.venv\Scripts\python.exe scripts/docker_evidence.py
```

El recolector deja salidas reales saneadas en `docs/entrega-1/evidencias/ejecuciones/`.
Devuelve error y registra el bloqueo cuando Docker no existe. No inventa resultados.
`docker compose config` imprime secretos interpolados: para capturas use la salida
saneada del recolector; para validar sin imprimirlos use `config --quiet`.

## Ejecutar desde Visual Studio Code en Windows

Abra esta carpeta en VS Code e instale las extensiones recomendadas. Necesita
Python 3.12+, Node 24 y PostgreSQL 17+ (local o con Docker).

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m app.cli create-admin
cd ..
```

Para depurar el backend en el host, configure PostgreSQL local y ajuste
`DATABASE_URL` en `backend/.env` antes de migrar. El PostgreSQL del Compose no
publica 5432 y no es accesible desde un backend ejecutado en el host.
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

El workflow `.github/workflows/docker-ci.yml` está configurado para comprobar
build, salud, migraciones, comunicación real, persistencia, Pytest y frontend.
Utiliza Buildx y apaga los dos servicios mediante `if: always()`. No publica imágenes.
La ejecución remota por push ya está verificada: **docker y frontend aprobados**,
32 pruebas backend y comunicación/persistencia correctas.
[Actions aprobado](https://github.com/JesusGalvis05/Repuestos_SAS/actions/runs/42731671529).
[Matriz de pruebas](docs/pruebas.md).

También puede ejecutar Pytest dentro de `api`, manteniendo los mismos dos servicios:

```powershell
docker build --target test -t jg-repuestos-api:academic backend
docker compose up -d --no-build --force-recreate --wait api
docker compose exec -T -e RUN_DOCKER_COMMUNICATION=1 api python -m pytest -q -p no:cacheprovider
```

Las pruebas crean esquemas aislados y la demostración se limpia por UUID. Al
terminar, `docker compose build` y `docker compose up -d --wait` recuperan la
imagen de ejecución sin herramientas de pruebas.

## Estado de validación y GitHub

El 9 de noviembre de 2026 se ejecutó la validación con Docker instalado:
construcción, salud, migraciones, red, escritura/lectura y persistencia aprobadas.
La suite dentro de api contra db obtuvo **32 pruebas aprobadas, sin omisiones**.
Quedaron activos sólo api y db saludables, con la imagen runtime restaurada.
Los resultados están en `docs/entrega-1/evidencias/ejecuciones/20261109-193746/`.
La API responde en http://localhost:8000/api/v1/docs.

El remoto `origin` apunta a https://github.com/JesusGalvis05/Repuestos_SAS.
Se confirmó el push de `master` y la ejecución remota de GitHub Actions
`42731671529` con resultado `success` para el commit `18aea1e`.
Los artefactos originales saneados están en
`docs/entrega-1/evidencias/github-actions/42731671529/`.

Se validó además el archivo con Compose oficial portátil 2.39.4, sin instalar un
motor: SHA-256 comprobado y `config --quiet` con salida 0. La configuración
normalizada saneada y el resultado están en `docs/entrega-1/evidencias/`.
Para repetir con un Compose standalone ya descargado:

```powershell
.\.venv\Scripts\python.exe scripts/validate_compose.py --binary .local/tools/docker-compose.exe
```

Los commits locales conservan el historial. Una vez autenticado en GitHub,
verifique las ramas remotas y publique los commits de trabajo mediante un push
normal, sin forzar ni reemplazar el historial remoto. Use el gestor de credenciales;
nunca introduzca un token en la URL. Adjunte la ejecución real de Actions aprobada.

La rúbrica solicita commits frecuentes y descriptivos; no exige múltiples ramas.
Las ramas y pull requests son una práctica opcional para cambios futuros.

## Generar el PDF académico

```powershell
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements-evidence.lock
.\.venv\Scripts\python.exe scripts/build_evidence_pdf.py
```

El PDF incluye las limitaciones pendientes; sólo incorpore capturas obtenidas de
ejecuciones reales. La lista exacta está en `docs/entrega-1/capturas/README.md`.

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
