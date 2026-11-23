# Entrega 2 - Jenkins e integración continua

Para esta entrega reutilizo FastAPI, PostgreSQL, las migraciones, las pruebas y
las etapas `test` y `runtime` de `backend/Dockerfile`. Agregué Jenkins y un
pipeline de tres etapas. El workflow de la primera entrega se conserva.

Repositorio: https://github.com/JesusGalvis05/Repuestos_SAS

## Resultados comprobados

El 22 de noviembre de 2026 inicié Jenkins desde Docker y ejecuté el trabajo
`JG-Repuestos` desde GitHub. El [build 1](http://localhost:8081/job/JG-Repuestos/1/)
aprobó las tres etapas: 32 pruebas sin fallos ni omisiones, imagen runtime y prueba
de humo. Los contenedores temporales se limpiaron al finalizar.

También aprobaron [CI - Entrega 2](https://github.com/JesusGalvis05/Repuestos_SAS/actions/runs/45105227996)
y [Docker - Entrega 1](https://github.com/JesusGalvis05/Repuestos_SAS/actions/runs/45105228059)
para el commit `fd6806e`. La API de desarrollo conserva sus dos contenedores
saludables; `health`, `ready` y escritura/lectura en PostgreSQL respondieron bien.

En el primer arranque corregí una propiedad antigua de CSRF en JCasC. Jenkins
2.580.2 utiliza `crumbIssuer: { standard: {} }`; CSRF sigue activo. La corrección
está en el commit local `112342b` y aún no se ha publicado.

Después de autorizar la rama, [Jenkins 2](http://localhost:8081/job/JG-Repuestos/2/)
y [Actions 45106218087](https://github.com/JesusGalvis05/Repuestos_SAS/actions/runs/45106218087)
detectaron el error: 31 pruebas aprobadas y una fallida. Construcción y humo no
se ejecutaron. Solo falta autorizar la publicación de la corrección para cerrar
la secuencia en ambos sistemas.

## Archivos

| Archivo | Función |
| --- | --- |
| `jenkins/Dockerfile` | Jenkins LTS 2.580.2 con Java 21, Docker CLI y Python |
| `jenkins/plugins.txt` | Versiones de los plugins |
| `jenkins/casc.yaml` | Usuario, permisos y configuración JCasC |
| `jenkins/jobs.groovy` | Trabajo `JG-Repuestos` conectado al repositorio Git |
| `jenkins/compose.yaml` | Servidor local y volumen persistente |
| `Jenkinsfile` | Pipeline declarativo de tres etapas |
| `ci/compose.yaml` | Dependencias temporales y aisladas de cada ejecución |
| `scripts/ci_pipeline.py` | Comandos compartidos entre Jenkins y Actions |
| `.github/workflows/jenkins-parity.yml` | Workflow comparable con Jenkins |

## Iniciar Jenkins

Necesito Docker Desktop con motor Linux activo, Python 3.12 o superior para el
configurador, Internet para la primera construcción y el puerto 8081 disponible.
Desde la raíz del proyecto ejecuto:

```powershell
python scripts/configure_jenkins.py
docker compose --env-file jenkins/.env -f jenkins/compose.yaml config --quiet
docker compose --env-file jenkins/.env -f jenkins/compose.yaml up --build -d --wait --wait-timeout 600
docker compose --env-file jenkins/.env -f jenkins/compose.yaml ps
```

Abro http://localhost:8081. El usuario está en `JENKINS_ADMIN_ID` y la contraseña
en `JENKINS_ADMIN_PASSWORD`, dentro de `jenkins/.env`. El configurador genera la
contraseña y conserva la existente. JCasC crea el usuario automáticamente;
no se usa el asistente ni `initialAdminPassword`.

La plantilla `jenkins/.env.example` se publica; `jenkins/.env` está ignorado.
Para cambiar el puerto edito `JENKINS_HTTP_PORT` y vuelvo a ejecutar `up`.

Para revisar los registros o detener Jenkins conservando sus datos:

```powershell
docker compose --env-file jenkins/.env -f jenkins/compose.yaml logs --tail 100 jenkins
docker compose --env-file jenkins/.env -f jenkins/compose.yaml down
```

No uso `down -v` para detener Jenkins: eliminaría el volumen con sus resultados.
Los cambios de plugins o JCasC se aplican reconstruyendo con el comando de inicio.

## Repositorio privado

Completo `JG_GITHUB_USER` y `JG_GITHUB_TOKEN` en `jenkins/.env` si el repositorio
es privado. El token debe permitir leer el contenido de `JesusGalvis05/Repuestos_SAS`;
no necesita escritura. La URL no contiene contraseñas. Después recreo Jenkins:

```powershell
docker compose --env-file jenkins/.env -f jenkins/compose.yaml up -d --force-recreate --wait --wait-timeout 600
```

JCasC registra la credencial como `jg-github`. No incluyo el token en capturas,
documentos ni comandos. Para que funcione el checkout, el Jenkinsfile y sus scripts
deben estar publicados en la rama elegida. El checkout de `master` ya se verificó;
la publicación de la rama de demostración requiere una autorización separada.

## Ejecutar el pipeline

1. Inicio sesión y abro el trabajo `JG-Repuestos`.
2. Selecciono **Build with Parameters / Construir con parámetros**.
3. Uso `BRANCH=master` para la versión estable o `demo/entrega-2` para la demostración.
4. Abro el build y reviso las etapas, **Console Output**, **Test Result** y artefactos.

El inicio en Jenkins es manual. GitHub Actions se activa con push o pull request.
No configuré un webhook público hacia el computador local.

Las etapas son:

1. **Pruebas automatizadas:** descarga con `checkout scm`, construye el entorno
   `test` y ejecuta Pytest con PostgreSQL dentro de Docker. El reporte XML se
   publica con el paso Jenkins `junit`; las pruebas siguen siendo Python.
   Un fallo, un reporte vacío o pruebas omitidas impiden continuar.
2. **Construcción de imagen:** solo después de aprobar las pruebas, construye
   `runtime` y etiqueta `jg-repuestos-ci:jenkins-N-runtime`, usando el número de build.
3. **Prueba de humo:** inicia esa imagen sin reconstruir y verifica
   `/api/v1/health`, `/api/v1/ready` y `app.diagnostics roundtrip`.

La construcción del entorno de pruebas de la primera etapa es necesaria para
ejecutar Pytest. La imagen final de aplicación se construye en la segunda etapa.

## Aislamiento y limpieza

Cada ejecución crea un proyecto `jg-ci-*`, su propia red y PostgreSQL temporal en
`tmpfs`. No publica puertos de API o base de datos ni utiliza el volumen de
desarrollo `jg-repuestos_postgres_data`. La conexión interna sigue siendo `db:5432`.

`post { always { ... } }` limpia aunque fallen las pruebas. Solo elimina recursos
del proyecto temporal y sus etiquetas de imagen; no usa `docker system prune`.
El identificador de la imagen construida queda registrado en `build.json`.
Los reportes se guardan en `ci-results/` y se publican como artefactos.

Si el equipo se apaga abruptamente, la limpieza podría no ejecutarse. Desde el
workspace de ese build puedo recuperarla, usando su identificador real:

```powershell
python3 scripts/ci_pipeline.py cleanup --run-id jenkins-1
```

## Socket de Docker y seguridad

Esta configuración es para el laboratorio local. Montar `/var/run/docker.sock`
permite a Jenkins controlar el motor Docker; un pipeline malicioso podría acceder
a otros contenedores o datos del host. El usuario sin privilegios y la eliminación
de capacidades no neutralizan el poder del socket.

Por eso solo publico `127.0.0.1:8081`, exijo autenticación, desactivo el registro
y el acceso anónimo y ejecuto únicamente código propio revisado. No uso
`privileged`. Para un servidor compartido usaría agentes y motores aislados.
En Linux, `DOCKER_SOCKET_GID` debe coincidir con el grupo propietario del socket;
el valor inicial 0 corresponde al laboratorio con Docker Desktop.

## Comparación

| Aspecto | Jenkins | GitHub Actions |
| --- | --- | --- |
| Configuración | `Jenkinsfile`, JCasC y Compose | `.github/workflows/jenkins-parity.yml` |
| Administración | Mantengo contenedor, plugins y volumen | GitHub administra el runner hospedado |
| Pruebas | Docker Desktop, contenedores temporales | Runner Ubuntu, contenedores temporales |
| Inicio | Botón del trabajo y selección de rama | Push o pull request |
| Resultados | Etapas, consola, reporte XML y artefactos | Pasos, registros y artefactos descargables |

El workflow `CI - Entrega 2` usa los mismos comandos y orden. Si las pruebas fallan,
construcción y humo quedan omitidos; limpieza y artefactos se ejecutan igualmente.
El workflow anterior sigue activo, así que un push puede mostrar ambos.

## Evidencias y estado

- [Validación local](evidencias/validacion-local.json).
- [Borrador del informe universitario](informe.md).
- [Demostración de error y corrección](demostracion.md).
- [Lista de capturas](capturas/README.md).

Una prueba nativa o validar YAML no demuestra una ejecución desde Jenkins.
Los resultados pendientes solo se completan después de ejecutarlos.
La guía `CI-U2E4-Guia-Ejercicio.pdf` y el ZIP mencionados no estuvieron disponibles
para esta revisión; la implementación sigue los requisitos del texto adjunto.

## Referencias

Jenkins. (s. f.). *Docker*. https://www.jenkins.io/doc/book/installing/docker/

Jenkins. (s. f.). *Pipeline syntax*. https://www.jenkins.io/doc/book/pipeline/syntax/

Jenkins. (s. f.). *Configuration as Code*. https://plugins.jenkins.io/configuration-as-code/

GitHub. (s. f.). *Events that trigger workflows*. https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

Docker. (s. f.). *Docker daemon attack surface*. https://docs.docker.com/engine/security/#docker-daemon-attack-surface
