# Verificación de la entrega — 8 de noviembre de 2026

Alcance: Fase 1 y cambio obligatorio de arquitectura/stack.

| Verificación ejecutada | Resultado |
| --- | --- |
| Pytest con PostgreSQL 18.4 real, esquemas aislados y migraciones Alembic | **22 aprobadas** |
| Upgrade → downgrade → upgrade; `alembic check` | Aprobado en pruebas PostgreSQL |
| Concurrencia: rotación refresh, primer administrador y último administrador | Aprobado con transacciones independientes |
| Pruebas React/Vitest | **2 aprobadas** |
| Compilación TypeScript + Vite | Aprobada; rutas cargadas por demanda |
| `npm audit` tras actualizar Vitest | **0 vulnerabilidades reportadas** |
| Comunicación HTTP Vite → proxy → FastAPI → PostgreSQL | Aprobada: login, perfil, usuarios, refresh, logout y rechazo de token revocado |
| Compilación de módulos Python | Aprobada |

El ensayo HTTP inició servidores temporalmente en puertos 15173 y 18000, creó un
esquema y administrador exclusivamente de prueba y los eliminó al terminar. El
PostgreSQL temporal se ubicó en `.local/pg-test`, puerto 55432, sin modificar bases
ni usuarios de la instalación habitual. No se creó un administrador operacional.

Límites observados:

- Docker no está disponible en este equipo: construcción y ejecución de Compose
  pendientes de verificación. El workflow de CI está preparado; no se afirma que
  haya sido ejecutado en GitHub.
- Las pruebas de Starlette emitieron un aviso de deprecación sobre su adaptador
  httpx; las 22 pruebas aprobaron. La migración a httpx2 se evaluará al actualizar
  las dependencias de pruebas.
- Vite emitió avisos sobre comentarios de anotación de la dependencia Zod, sin
  afectar el resultado de compilación.
- No se realizó inspección visual de navegador ni evaluación con lector de pantalla.

No se declara cerrada la aceptación de contenedores ni se avanza a Fase 2.

## Despliegue local posterior

Por solicitud de despliegue se inició una instancia persistente de la aplicación
en `http://localhost:8080/ingresar`, con PostgreSQL dedicado en 55433 y administrador
generado aleatoriamente. Se comprobaron disponibilidad, HTML, login, perfil y
logout por HTTP. Las credenciales no se incorporan a este documento ni al repositorio.

Se agregaron dos pruebas para navegación directa de la SPA y conservación de
errores 404 de API/assets; ambas aprobaron junto con siete pruebas unitarias.
Se corrigió la normalización de separadores de rutas en Windows. El contenedor
único de la raíz sigue pendiente de construcción en un entorno con Docker.

No se ha realizado publicación pública: no hay cuenta de alojamiento conectada.
Se propuso habilitar Railway para continuar ese despliegue.

## Entrega Docker — Escenario 3 (actualizado el 9 de noviembre)

La entrega académica adapta el Compose a exactamente api y db, sin publicar
PostgreSQL al host. La configuración fue validada con Compose standalone oficial
2.39.4, checksum contrastado y `config --quiet` con salida 0. Tras instalar Docker,
el 9 de noviembre se ejecutó la validación completa con Engine 29.9.2 y Compose
5.6.1: construcción, salud, migraciones, red y puerto interno db:5432 aprobados.

La suite dentro de api obtuvo **32 pruebas aprobadas, sin omisiones**. La prueba
de persistencia recuperó el mismo UUID después de recrear ambos contenedores,
conservando el volumen, y limpió sólo su registro. Se restauró la imagen runtime
sin Pytest y quedaron activos exactamente api y db saludables. UID 10001, CapDrop
ALL y ausencia de puertos publicados en db se comprobaron por inspección real.

El PDF actualizado incluye extractos de los logs y capturas HTTP reales de ready
y Swagger. Evidencias: `entrega-1/evidencias/ejecuciones/20261109-193746/`.
GitHub Actions remoto quedó aprobado en la ejecución 42731671529 para el commit
18aea1e, con docker/frontend en success y 32 pruebas backend aprobadas. Se
descargaron los artefactos reales en `entrega-1/evidencias/github-actions/42731671529/`.
Las capturas de consola/interfaz de Actions y datos de portada aún
deben completarse para la entrega académica.
