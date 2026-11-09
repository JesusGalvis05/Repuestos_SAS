# Documentación académica — Fase 1

## Problema y justificación

JG Repuestos requiere trazabilidad de productos, proveedores, compras, ventas e
inventario para evaluar su operación y rentabilidad. Los catálogos de proveedores
pueden referirse al mismo repuesto con códigos diferentes; disponibilidad externa
y existencia propia son conceptos distintos. La ausencia de información integrada
dificulta comparar adquisiciones y reconstruir movimientos. El sistema busca
reducir esa fragmentación mediante datos coherentes y operaciones auditables.

Esta descripción expresa la necesidad presentada, no resultados de entrevistas
ni mediciones de campo que no se hayan realizado. La primera entrega construye
la identidad y autorización necesarias antes de operar datos comerciales.

## Objetivo general

Desarrollar incrementalmente un sistema web de gestión comercial e inventario
para JG Repuestos con seguridad, trazabilidad y valoración consistente.

## Objetivos específicos

1. Centralizar identidad, usuarios, sesiones y permisos por operación.
2. Normalizar el catálogo interno y vincular ofertas y aplicaciones verificadas.
3. Asegurar consistencia de compras, ventas y existencias mediante movimientos.
4. Calcular costo y rentabilidad con precisión decimal y reglas documentadas.
5. Validar requisitos con pruebas reproducibles y documentación del software real.

## Alcance y requisitos

La especificación completa se conserva en `requisitos-maestros.md`, adaptada a
Python. El estado de cada fase está en `avance.md`.

| ID | Requisito Fase 1 | Criterio verificable |
| --- | --- | --- |
| RF01 | Crear primer administrador sin credenciales iniciales | CLI interactiva, migración sin usuarios, alta concurrente única |
| RF02 | Iniciar sesión de usuario activo | JWT válido, cookie HttpOnly y registro de último acceso |
| RF03 | Renovar sesión con rotación | Nuevo refresh, rechazo y revocación ante replay |
| RF04 | Finalizar y revocar sesiones | Access previo rechazado inmediatamente |
| RF05 | Administrar cuentas y roles | Sólo `users.manage`; proteger último administrador |
| RF06 | Cambiar contraseña | Verificar actual y revocar todas las sesiones |
| RF07 | Auditar operaciones sensibles | Registros persistentes sin contraseñas ni tokens |
| RF08 | Consultar perfil y sesiones propias | Sin acceso a sesiones de otra persona |
| RF09 | Bloquear intentos repetidos | Cinco fallos, bloqueo de quince minutos persistente |
| RNF01 | API versionada y documentada | `/api/v1`, OpenAPI y errores identificables |
| RNF02 | Integridad y concurrencia | Transacciones SQLAlchemy, restricciones y bloqueos PostgreSQL |
| RNF03 | Configuración reproducible | Locks de dependencias, Alembic, scripts y Compose |
| RNF04 | Usabilidad y accesibilidad | Español, etiquetas, foco, teclado, estados de carga y errores |
| RNF05 | Protección de información | Hash Argon2id, secretos fuera de Git, CORS restringido |
| RNF06 | Monolito modular | Una app ASGI con capas separadas por módulo |

No se afirma cumplimiento de metas de rendimiento o disponibilidad sin pruebas
de carga y medición de infraestructura. Los requisitos comerciales se validarán
en fases 2–7, con prioridad alta para proveedores.

## Historias de usuario

| ID | Historia | Aceptación |
| --- | --- | --- |
| HU01 | Como administrador inicial quiero crear mi cuenta de forma segura | Sin contraseña por defecto, mínimo 12 caracteres, un solo aprovisionamiento |
| HU02 | Como integrante quiero iniciar sesión para acceder a mi espacio | Error comprensible, sin revelar si existe el correo, inicio protegido |
| HU03 | Como administrador quiero asignar responsabilidades | Roles iniciales disponibles; vendedor sin `costs.read`; API rechaza accesos prohibidos |
| HU04 | Como integrante quiero revisar y cerrar mis accesos | Lista de sesiones propias y confirmación antes de revocar |
| HU05 | Como administrador quiero desactivar una cuenta | Sesiones invalidadas sin borrar historial ni dejar el sistema sin administrador |
| HU06 | Como integrante quiero cambiar mi contraseña | Actual verificada, nueva distinta, cierre de sesiones |

## Casos de uso implementados

**CU01 — Acceder.** Actor: usuario activo. Entrada: correo y contraseña. Flujo:
validar contrato, bloquear fila de usuario, verificar hash y bloqueo temporal,
crear sesión y credenciales, auditar, confirmar transacción. Alternativas: datos
inválidos (422), credenciales rechazadas o bloqueo (401 con auditoría persistida).

**CU02 — Administrar cuenta.** Actor: administrador con `users.manage`. Flujo:
consultar usuarios, seleccionar cuenta, confirmar cambio, serializar operación,
validar roles y último administrador, revocar sesiones, auditar y confirmar.
Alternativas: sin permiso (403), rol inexistente (422), conflicto de último
administrador (409). No se elimina físicamente al usuario.

**CU03 — Renovar sesión.** Actor: navegador con cookie válida y Origin permitido.
Flujo: buscar hash, bloquear usuario/sesión/token, consumir credencial, generar
nueva y confirmar. Alternativas: vencimiento/revocación (401), replay (revocar y
401), origen no permitido (403). La vigencia absoluta no se extiende.

**CU04 — Cambiar contraseña.** Actor: usuario autenticado. Verificar contraseña
actual y contrato de la nueva, guardar hash, revocar sesiones y auditar. Una
operación inválida revierte por completo; el éxito requiere nuevo acceso.

## Trazabilidad de diseño

Arquitectura y componentes: `arquitectura.md` y `diagramas.md`. Decisiones:
`decisiones/`. Verificación: `pruebas.md`. Manuales: `manual-tecnico.md` y
`manual-usuario.md`. Las secuencias de compras y ventas se presentan únicamente
como diseño futuro hasta implementar sus fases.
