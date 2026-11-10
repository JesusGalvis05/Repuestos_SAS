# Registro de avance

## Fase 1 — implementación disponible

- [x] Repositorio, backend FastAPI y frontend React reales.
- [x] Separación por rutas, esquemas, modelos, servicios y repositorios.
- [x] Una única aplicación ASGI, sesiones SQLAlchemy y transacciones delimitadas.
- [x] PostgreSQL y primera migración Alembic con seeds de roles/permisos.
- [x] Login, logout, perfil, cambio de contraseña y control de sesiones.
- [x] Rotación de refresh, revocación, detección de replay y bloqueo de acceso.
- [x] RBAC backend; alta de usuarios, asignación de roles y desactivación.
- [x] Aprovisionamiento inicial por consola y protección del último administrador.
- [x] Pantalla de acceso, inicio protegido, perfil y administración responsive.
- [x] Variables de entorno, scripts, depuración VS Code y Docker Compose.
- [x] Pruebas Pytest con PostgreSQL real y pruebas frontend.
- [x] Verificar construcción, salud, migraciones, comunicación y persistencia en Docker (9 de noviembre de 2026).

La Fase 1 tiene implementación funcional y validación de contenedores aprobada.
Esta entrega sigue limitada a DevOps; no se inicia la Fase 2.
Los resultados concretos de ejecución se registran en `pruebas.md`.

Adaptación académica Docker: Compose de dos servicios, diagnóstico de comunicación,
CI y documento PDF preparados. Resultado actual: 32 pruebas backend aprobadas
dentro de Docker, sin omisiones. Publicación y Actions remoto aprobados y verificados;
el detalle y la rúbrica de 150 puntos están en `entrega-1/`.

## Fases conservadas, aún pendientes

| Fase | Alcance pendiente |
| --- | --- |
| 2 — Catálogos | Categorías, marcas, productos únicos, referencias equivalentes, imágenes, vehículos y compatibilidad verificada, búsqueda y filtros |
| 3 — Proveedores | CRUD, catálogo individual, ofertas, comparador con costos/entrega/vigencia, historial, importación Excel/CSV con vista previa y propuestas |
| 4 — Inventario y compras | Bodegas, ubicaciones, saldos, reservas, kardex inmutable, ajustes, traslados, compras, recepciones parciales, pagos, devoluciones y valoración |
| 5 — Ventas | Clientes, descuentos autorizados, pago/venta/entrega separados, devoluciones, recibos internos PDF y stock a la entrega |
| 6 — Finanzas | Costo promedio móvil, utilidad, gastos, aportes y retiros, socios 50/50 configurables, distribuciones, indicadores reales y reportes |
| 7 — Calidad y preparación | Pruebas completas comerciales y concurrencia, seguridad operacional, documentación final, datos demostrativos separados, respaldo/restauración y despliegue |

Se conservan alertas deterministas de mínimos, agotados, compras pendientes,
inactividad, ofertas vencidas y precios bajo costo; recomendación de reposición
según ventas y entrega. La disponibilidad del proveedor nunca será stock propio.
Los comprobantes internos no representan facturación electrónica DIAN.

No se crean tablas comerciales ni pantallas simuladas antes de su fase. La
especificación integral queda en `requisitos-maestros.md`.
