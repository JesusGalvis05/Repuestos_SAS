# Guion de demostración reproducible

## Preparación

Instalar Docker Desktop con motor de contenedores Linux y Compose v2. Ejecutar
desde la raíz del repositorio. No usar la cuenta operacional de la aplicación
local en estas demostraciones.

```powershell
python scripts/configure.py
docker version
docker compose version
docker compose config --quiet
docker build --target runtime -t jg-repuestos-api:academic backend
docker compose build
docker compose up -d --wait --wait-timeout 180
```

El configurador conserva las claves existentes y completa usuario/nombre de base.
No imprime secretos. Si una base ya tiene volumen, cambiar `.env` no cambia su
contraseña; alinear credenciales con la base sin eliminar datos.

## Estado y red

```powershell
docker compose ps
docker ps
docker network inspect jg-network
docker compose exec -T api id -u
docker compose exec -T api alembic current
docker compose exec -T api alembic check
```

Verificar dos servicios saludables, UID 10001, red con ambos contenedores,
únicamente 8000 publicado y revisión Alembic `0001_identity`. No copiar IPs de
`inspect` a la configuración: la API siempre utiliza el nombre DNS `db`.

Abrir http://localhost:8000/api/v1/docs y probar GET `/api/v1/health` y `/ready`.
Los endpoints `/users` rechazan solicitudes sin JWT; no se abre una ruta pública
para simplificar la demostración.

## Escritura y lectura reales

```powershell
docker compose exec -T api python -m app.diagnostics roundtrip
```

Esta operación crea un usuario UUID temporal inactivo, sin roles y con contraseña
aleatoria cuyo valor se descarta. Confirma el INSERT, inicia otra sesión, consulta
los campos, consulta puerto real con PostgreSQL y elimina únicamente ese registro.
Capturar la salida JSON real con `status=passed`, `host=db`, `server_port=5432` y
`cleanup=passed`. Estos valores son **criterios esperados**, no evidencia obtenida
en este equipo sin Docker.

## Persistencia al recrear

```powershell
$demo = docker compose exec -T api python -m app.diagnostics create | ConvertFrom-Json
$demoId = $demo.id
docker compose down
docker compose up -d --wait --wait-timeout 180
docker compose exec -T api python -m app.diagnostics read --id $demoId
docker compose exec -T api python -m app.diagnostics delete --id $demoId
```

Guardar el UUID para limpieza si una ejecución se interrumpe. Nunca usar `down -v`
en esta prueba. `read` debe encontrar el mismo UUID después de recrear ambos
contenedores. `delete` valida UUID, correo derivado, marca de demostración, estado
inactivo y ausencia de roles; no acepta borrar usuarios normales.

## Automatización de evidencias

```powershell
.\.venv\Scripts\python.exe scripts/docker_evidence.py
```

El recolector ejecuta las etapas anteriores, guarda comandos/códigos de salida,
sanea secretos, comprueba salud, UID, migraciones, comunicación y persistencia y
deja los dos contenedores activos al finalizar. Si falla, guarda diagnóstico y
reintenta limpiar sólo su registro temporal. Revisar `resultado.json`; si incluye
`pending_demo_id`, limpiar únicamente ese ID con el comando anterior.

`docker compose config` produce credenciales interpoladas; para una captura de
configuración usar exclusivamente `03-compose-config.txt` saneado. El script
no guarda `.env` ni credenciales del administrador en las evidencias.

También se incluye la validación real de Compose portátil en
`evidencias/compose-validacion-real.json` y su JSON normalizado saneado en
`evidencias/compose-config-real.json`. No requiere motor y no sustituye las
pruebas de construcción, comunicación interna ni persistencia.

## Logs y finalización

```powershell
docker compose logs api
docker compose logs db
docker compose down
```

Los logs del recolector ya están saneados. Antes de compartir una captura manual,
comprobar que no revele secretos ni información personal. `down` conserva el volumen.

## GitHub Actions

Publicar el repositorio sin secretos, abrir Actions → Docker - Entrega 1 y esperar
la ejecución completa. Descargar el artefacto `evidencias-docker-<número>` y guardar
la URL y captura del pipeline aprobado. El job principal ejecuta Docker real;
el job frontend compila y prueba React. Ninguna imagen se publica a un registro.
