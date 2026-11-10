# Matriz de verificación

Las pruebas operacionales usan PostgreSQL real y migraciones Alembic en esquemas
aislados. No se sustituyen los bloqueos por SQLite. Puede usar una conexión
`TEST_DATABASE_URL` o PostgreSQL efímero con Testcontainers.

| Escenario Fase 1 | Comprobación automatizada |
| --- | --- |
| Hash seguro, verificación y clave incorrecta | Pytest unitario Argon2id |
| Contrato JWT, emisor/audiencia y firma | Pytest unitario |
| Configuración insegura y validación de entradas | Pytest unitario |
| Migración upgrade/downgrade/upgrade y correspondencia ORM | PostgreSQL + `alembic check` |
| Administrador inicial único y último administrador protegido | PostgreSQL + HTTP |
| Login y logout; cookie HttpOnly, SameSite | Endpoints reales contra PostgreSQL |
| Roles y prohibición de administración para vendedor | HTTP 403; vendedor sin permiso de costos |
| Renovación y reutilización de refresh | Rotación y revocación persistidas |
| Intentos fallidos y bloqueo | Cinco fallos 401 y contador persistente |
| Cambio de contraseña | Contraseña nueva válida y sesiones antiguas revocadas |
| Desactivación de cuenta | Token previo inmediatamente rechazado |
| Origin no autorizado y errores sin secretos | HTTP 403/422 |
| Operación inválida | Sin usuario ni auditoría parcial tras rollback |
| Búsqueda/paginación y correo duplicado | Contratos HTTP y 409 |
| Renovación simultánea | Dos transacciones: un éxito y replay detectado |
| Aprovisionamiento simultáneo | Dos transacciones: un único administrador |
| Cambios simultáneos de administradores | Siempre queda uno activo |
| Revocación propia y de terceros | Idempotencia y autorización de propiedad |
| Formulario de acceso | Validación antes de enviar y control mostrar/ocultar contraseña |
| Construcción frontend | TypeScript estricto y bundle Vite |

## Escenarios comerciales conservados

Los doce escenarios obligatorios del documento maestro siguen pendientes de
implementación en las fases correspondientes: producto multiproveedor, comparador,
orden de compra, recepción parcial, entrada de stock, venta, salida, costo/utilidad,
rechazo por falta de stock, devolución, confidencialidad de costos e idempotencia
de recepción. La Fase 1 verifica que el vendedor carece del permiso de costos;
la protección de respuestas comerciales se probará cuando existan esos endpoints.

También quedan pendientes las pruebas monetarias Decimal/NUMERIC, ventas simultáneas,
valoración promedio móvil, traslados, reservas, devoluciones y conciliación del kardex.
No se presentan esos casos futuros como pruebas aprobadas.

## Registro de ejecución

Entorno de implementación: Windows, Python 3.12, Node 24 y PostgreSQL 18.4 local
aislado en `127.0.0.1:55432`; servidor habitual sin cambios. Resultados finales:
véase `verificacion.md`. El 9 de noviembre se ejecutó Docker: construcción,
migraciones, salud, escritura/lectura y persistencia aprobadas. Pytest dentro
de api con PostgreSQL db obtuvo **32 pruebas aprobadas, sin omisiones**.
Las evidencias están en `entrega-1/evidencias/ejecuciones/20261109-193746/`.

Se capturaron y revisaron ready y Swagger en navegador real. La evaluación de
accesibilidad del frontend con lector de pantalla sigue pendiente.
