# Matriz de evaluación — 150 puntos

Fecha de revisión: 8 de noviembre de 2026, America/Bogota.
Los estados no representan una calificación otorgada por el docente.

| Criterio | Puntos | Estado de implementación | Evidencia / validación pendiente |
| --- | ---: | --- | --- |
| 1. Repositorio GitHub | 15 | Estructura, README, ignores y commits locales preparados | Historial `git log`; falta publicar URL real y confirmar acceso GitHub |
| 2. Contenedor aplicación | 20 | Dockerfile con Python específico, locks, UID 10001, Uvicorn y Alembic | `backend/Dockerfile`; build real pendiente de Docker |
| 3. Segundo contenedor | 15 | PostgreSQL específico, variables, healthcheck y volumen; sin puerto host | `docker-compose.yml`; arranque y persistencia en Docker pendientes |
| 4. Docker Compose | 20 | Exactamente `api`/`db`, red `jg-network`, salud y reinicio; configuración validada con Compose oficial 2.39.4 | `evidencias/compose-validacion-real.json`; build/up requieren motor Docker |
| 5. Comunicación | 35 | URL segura `db:5432`, diagnóstico privado y prueba Pytest con limpieza | Pruebas PostgreSQL nativo reales; falta ejecución dentro de Docker y recreación con volumen |
| 6. Buenas prácticas | 15 | Ignores, variables sin secretos, versiones y usuario no privilegiado | Revisión estática e inspección Git; UID y aislamiento efectivos pendientes de Docker |
| 7. GitHub Actions | 15 | Workflow Push/PR con Buildx, integración, persistencia, logs saneados y cierre | `.github/workflows/docker-ci.yml`; pipeline aprobado pendiente de GitHub |
| 8. Documento evidencias | 15 | Informe Markdown, PDF, diagrama y carpeta de capturas | PDF generado; faltan capturas Docker/Actions, URL y datos académicos del estudiante |

Las evidencias locales están en `evidencias/`. `validacion-estatica.json` sólo
certifica revisión de archivos. `pytest-local.txt` corresponde a PostgreSQL nativo,
no a la red Docker. Los registros con estado `blocked` demuestran una limitación
real del entorno, no el cumplimiento de los criterios de ejecución.

`compose-config-real.json` contiene la configuración normalizada y saneada por
Compose portátil oficial; `config --quiet` terminó con código 0. Se comprobó el
SHA-256 del binario contra el archivo oficial de la misma versión. Esto valida
Compose, pero no prueba construcción de imágenes ni arranque del motor.
