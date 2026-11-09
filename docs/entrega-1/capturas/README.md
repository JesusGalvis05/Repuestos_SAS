# Capturas pendientes (sólo ejecuciones reales)

Guardar PNG legibles, con comando y resultado visibles. No generar imágenes que
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
