# Capturas y evidencias reales

Actualización: 9 de noviembre de 2026. Docker ya fue ejecutado: construcción,
migraciones, salud, red, comunicación, persistencia y 32 pruebas aprobadas.
Las salidas originales saneadas están en
`../evidencias/ejecuciones/20261109-193746/` y sus extractos se incorporaron al PDF.

Capturas HTTP ya obtenidas con Microsoft Edge headless sobre la API Docker:

| Archivo disponible | Contenido real |
| --- | --- |
| [11-api-ready.png](11-api-ready.png) | Respuesta HTTP 200 de `/api/v1/ready` |
| [12-swagger.png](12-swagger.png) | Swagger de JG Repuestos servido en el puerto 8000 |

`capturas-http.json` registra URL, fecha y método de captura. No son imágenes
generadas a partir de texto ni capturas de un pipeline remoto.

## Capturas de consola y GitHub pendientes

Las salidas de consola ya existen en TXT; si la evaluación exige PNG, capturar
su visualización o repetir los comandos reales. Guardar imágenes legibles con
comando y resultado visibles. No generar imágenes que
imiten una consola ni marcar como aprobada una ejecución inexistente.

| Archivo | Contenido exacto a capturar |
| --- | --- |
| 01-docker-build.png | `docker build --target runtime -t jg-repuestos-api:academic backend` terminado sin errores |
| 02-compose-up.png | `docker compose up -d --wait --wait-timeout 180` y ambos servicios saludables |
| 03-docker-ps.png | `docker compose ps` y `docker ps`, dos contenedores y sólo API publicada |
| 04-network.png | `docker network inspect jg-network`, nombre y pertenencia de api/db |
| 05-configuracion.png | `evidencias/compose-config-real.json` saneado o `03-compose-config.txt`, dos servicios y `db:5432` |
| 06-escritura-lectura.png | JSON real de `python -m app.diagnostics roundtrip`, puerto 5432 y limpieza aprobada |
| 07-persistencia.png | UUID creado, down sin -v, nuevo up, lectura del mismo UUID y limpieza |
| 08-migraciones-logs.png | `alembic current`, `alembic check` y logs de arranque sin secretos |
| 09-github-actions.png | URL visible, commit y workflow aprobado con todos los pasos |
| 10-repositorio.png | Repositorio GitHub real, carpetas frontend/backend, README y commits |

Pendiente también: nombre del estudiante, institución, asignatura, docente y URL
real del repositorio. Al capturar, ocultar contraseñas, cookies, tokens y `.env`.
Regenerar el PDF después de incorporar resultados y actualizar el informe.
