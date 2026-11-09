# ADR 0002 — Sesiones, RBAC y consistencia

Estado: implementado para identidad; contrato de diseño para comercio.

Access JWT de diez minutos, firmado HS256 con secreto aleatorio, emisor y audiencia
verificados. Incluye usuario y sesión; cada solicitud verifica usuario activo,
sesión vigente y permisos actuales. No existen comodines que evadan RBAC.
El frontend almacena el access token sólo en memoria.

Refresh aleatorio de 48 bytes, persistido sólo como SHA-256, en cookie HttpOnly
SameSite Strict y Secure en producción. Caducidad absoluta de siete días; rotar
no extiende la sesión. Se conservan los hashes consumidos para detectar replay y
revocar toda la sesión. Origin se exige en refresh y logout. La aplicación usa
proxy del mismo origen; una topología con dominios distintos exige revisar cookies.

Una renovación simultánea con la misma credencial permite como máximo un éxito;
la segunda es reutilización y revoca la sesión. El frontend serializa renovaciones
en una pestaña y, cuando está disponible, mediante Web Locks entre pestañas.

Los fallos de login son resultados del servicio y respuestas HTTP explícitas:
la transacción confirma contadores y auditoría aunque responda 401. Los errores
de dominio ordinarios revierten. Cada petición confirma su transacción antes de
enviar la respuesta mediante `Depends(..., scope="function")`.

Los bloqueos siguen usuario → sesión → token. La administración usa además un
advisory lock transaccional fijo, incluyendo el alta inicial, para impedir que
dos cambios concurrentes eliminen al último administrador activo. No se expone
registro público. El aprovisionamiento requiere acceso local al proceso.

Logout y revocar sesión conservan el mismo efecto al repetirse; no duplican su
auditoría. La repetición de create-admin se rechaza sin crear cuentas adicionales.
La idempotencia documental de compras y ventas se implementará junto con esas
operaciones (véase arquitectura); no se declara implementada en la Fase 1.

La limitación actual de acceso es por cuenta conocida; antes de producción se
debe agregar limitación por origen/IP en el proxy, TLS, retención de auditorías,
limpieza de sesiones expiradas y política de recuperación de administradores.
Una recuperación de contraseña por correo no pertenece al alcance inicial.
