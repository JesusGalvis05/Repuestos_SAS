# Manual de usuario — Fase 1

## Primer acceso

El responsable técnico prepara el entorno y crea el primer administrador con la
consola indicada en README. No existe registro público. El administrador crea las
demás cuentas y comunica la contraseña inicial mediante un canal seguro.

Abra la dirección local de la aplicación e ingrese correo y contraseña. Cinco
fallos consecutivos bloquean temporalmente la cuenta durante quince minutos.
El mensaje no revela si un correo está registrado. Una sesión vencida o revocada
requiere un nuevo acceso.

## Inicio

La vista principal identifica al usuario y consulta el estado real de conexión
de la API con PostgreSQL. Presenta accesos al perfil y al equipo cuando el permiso
lo permite. Los módulos comerciales y sus indicadores se incorporan por fases;
no aparecen métricas de ventas inventadas.

## Equipo y usuarios

Disponible para administradores. Buscar por nombre o correo, navegar páginas y
crear una cuenta con nombre, correo, contraseña de al menos doce caracteres y uno
o más roles. Los roles iniciales son Administrador, Socio, Vendedor e Inventario.
Los permisos se aplican también en el servidor. Vendedor no tiene acceso a costos
internos ni finanzas; disponer de varios roles acumula sus permisos.

En Administrar puede cambiar roles o desactivar una cuenta. Revise la confirmación:
estas acciones cierran las sesiones de la cuenta afectada. Debe conservar al menos
un administrador activo. La desactivación mantiene historial y auditoría.

## Mi cuenta y seguridad

El perfil muestra datos personales, roles, último acceso y sesiones activas.
Las fechas se presentan en hora de Colombia. Revise dispositivo, inicio y vigencia
y revoque una sesión que no reconozca. Si revoca la sesión que está usando, deberá
ingresar de nuevo. La lista puede contener varias sesiones del mismo navegador.

Cambiar contraseña requiere la actual, una nueva distinta de al menos doce
caracteres y su confirmación. El cambio cierra todas las sesiones. El botón
Cerrar sesión también solicita confirmación. Si hay un fallo de conexión durante
el cierre, el sistema informa el problema para poder reintentar.

## Problemas frecuentes

- Sin conexión: confirmar que backend y PostgreSQL estén en ejecución; reintentar.
- Sin permiso: solicitar al administrador que revise el rol de la cuenta.
- Credenciales rechazadas: revisar datos o esperar el bloqueo temporal.
- Sin acceso al sistema: contactar al administrador; no existe recuperación por correo en esta fase.
