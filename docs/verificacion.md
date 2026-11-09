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

## Entrega Docker — Escenario 3

La entrega académica adapta el Compose a exactamente api y db, sin publicar
PostgreSQL al host. La configuración fue validada con Compose standalone oficial
2.39.4, checksum contrastado y `config --quiet` con salida 0. El motor Docker no
está instalado: imágenes, red activa, persistencia al recrear y CI remoto siguen
pendientes de ejecución real.

La suite actual obtuvo 31 pruebas backend aprobadas y una omitida exclusiva de
Docker. Las dos pruebas frontend y la compilación aprobaron. El PDF académico de
7 páginas y las evidencias reales, incluyendo las limitaciones, están en `entrega-1/`.
