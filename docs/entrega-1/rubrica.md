# Matriz de evaluación — 150 puntos

Fecha de revisión: 9 de noviembre de 2026, America/Bogota.
Los estados no representan una calificación otorgada por el docente.

| Criterio | Puntos | Estado de implementación | Evidencia / validación pendiente |
| --- | ---: | --- | --- |
| 1. Repositorio GitHub | 15 | Estructura, README, ignores y cuatro commits publicados verificados | https://github.com/JesusGalvis05/Repuestos_SAS; master 18aea1e confirmado por consulta autenticada |
| 2. Contenedor aplicación | 20 | Construcción real aprobada; Python específico, locks, Uvicorn y Alembic | Ejecución Docker: `05-docker-build.txt`, `12-alembic-current.txt`, `13-alembic-check.txt` |
| 3. Segundo contenedor | 15 | PostgreSQL saludable; volumen conserva datos al recrear; sin puerto host | `07-compose-up.txt`, `18-persistencia-leer.txt`, `28-final-compose-ps.txt` |
| 4. Docker Compose | 20 | Config/build/up aprobados; sólo `api`/`db` saludables en `jg-network` | `03-compose-config.txt`, `06-compose-build.txt`, `10-network-inspect.txt` |
| 5. Comunicación | 35 | Escritura/lectura/limpieza y persistencia aprobadas en `db:5432`; 32 pruebas dentro de api | `14-escritura-lectura-limpieza.txt`, `18-persistencia-leer.txt`, `22-pytest.txt` |
| 6. Buenas prácticas | 15 | UID 10001 comprobado en ejecución, db sin puerto publicado, revisión estática y secretos saneados | `11-api-user.txt`, `28-final-compose-ps.txt`, `evidencias/seguridad-local.json` |
| 7. GitHub Actions | 15 | Ejecución remota aprobada por push; docker y frontend en success, con artefactos descargados | https://github.com/JesusGalvis05/Repuestos_SAS/actions/runs/42731671529; `evidencias/github-actions/42731671529/` |
| 8. Documento evidencias | 15 | Informe/PDF con diagrama, logs locales/remotos, URL del repo y dos capturas HTTP | Faltan PNG de consola/interfaz Actions y datos académicos del estudiante |

Las pruebas Docker del 9 de noviembre están en
`evidencias/ejecuciones/20261109-193746/`. Su `resultado.json` indica comunicación
y persistencia aprobadas; `22-pytest-result.json` registra 32 pruebas aprobadas
sin omisiones y `runtime-restoration.json` confirma restauración de la imagen normal.

Los registros `blocked` del 8 de noviembre se conservan como historial. La prueba
`pytest-local.txt` anterior corresponde a PostgreSQL nativo; las evidencias del 9
ya utilizan dos contenedores reales. Ninguna de ellas representa una ejecución
remota de GitHub Actions.

La evidencia remota adicional está en `evidencias/github-actions/42731671529/`:
`github-run.json` identifica el push, commit, trabajos y resultado success;
`22-pytest.txt` registra 32 pruebas aprobadas en el runner de GitHub y
`resultado.json` confirma comunicación y persistencia remotas aprobadas.

`compose-config-real.json` contiene la configuración normalizada y saneada por
Compose portátil oficial; `config --quiet` terminó con código 0. Se comprobó el
SHA-256 del binario contra el archivo oficial de la misma versión. Esto valida
Compose, pero no prueba construcción de imágenes ni arranque del motor.
