# Despliegue

El Compose académico vigente está en `docker-compose.yml`, con sólo api y db.
La API se publica en 8000 y PostgreSQL no publica puertos. Las alternativas que
siguen conservan el despliegue local previo y el contenedor único raíz; no se
agregan al Compose de la actividad. Véase `entrega-1/demostracion.md`.

## En este equipo Windows

Después de preparar el entorno y compilar el frontend:

```powershell
.\.venv\Scripts\python.exe scripts/deploy_local.py
```

El script inicia un PostgreSQL **dedicado** en `127.0.0.1:55433` y sirve React y
FastAPI en un único proceso en `http://localhost:8080`. No modifica la instalación
habitual de PostgreSQL. La base persiste en `.local/pg-app`; su configuración
secreta está en `.local/application.env`, excluida de Git y de Docker.

En el primer arranque genera un administrador y muestra una contraseña aleatoria
una sola vez, tras comprobar su acceso HTTP. Nunca sustituye la contraseña de una
cuenta existente. Cambie la contraseña desde Mi cuenta. El identificador mostrado
es un usuario de la aplicación; no se envía ningún correo.

Los procesos permanecen activos después de cerrar esta consola. Este arranque
manual no instala servicios automáticos: tras reiniciar Windows ejecute el script
otra vez. Si el puerto 8080 ya está ocupado, se detiene sin modificar usuarios.
Para verificar disponibilidad abra `/api/v1/ready`. Los logs están en
`.local/application.log` y `.local/pg-app.log`.

La URL local funciona únicamente en este equipo. No representa una publicación
en internet.

## Publicación con contenedor único y PostgreSQL administrado

El `Dockerfile` de la raíz construye React y lo sirve desde la misma aplicación
FastAPI. No crea otra aplicación backend. El comando `python -m app.deploy`
ejecuta Alembic antes de iniciar Uvicorn y respeta el puerto de entorno `PORT`.
La base PostgreSQL se suministra como infraestructura externa.

Variables necesarias del proveedor:

- `DATABASE_URL`: URL PostgreSQL con prefijo `postgresql+psycopg://`, credenciales
  del proveedor y los parámetros SSL que éste indique.
- `JWT_SECRET`: secreto nuevo, aleatorio y almacenado en el gestor del proveedor.
- `APP_ENV=production` y `COOKIE_SECURE=true`.
- `ALLOWED_ORIGINS`: lista JSON con el origen HTTPS definitivo, sin barra final.
- `FRONTEND_DIST=/app/web`: ya configurado en la imagen.

Tras publicar, crear el primer administrador mediante la consola privada del
proveedor: `python -m app.cli create-admin`. No se incorpora un endpoint de
aprovisionamiento público ni una contraseña a la imagen.

Para crear recursos y obtener una URL pública es necesario conectar una cuenta
de alojamiento compatible. No hay una cuenta de ese tipo autorizada/conectada
en el entorno de esta entrega. Railway se ha propuesto como opción compatible;
no se ha creado ningún proyecto ni recurso facturable allí.
