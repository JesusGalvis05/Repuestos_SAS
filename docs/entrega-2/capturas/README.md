# Capturas de la Entrega 2

Las imágenes obtenidas son capturas reales de Docker Desktop o del navegador
Edge. Cada PNG tiene un JSON con fecha, origen y método de captura.

| Archivo | Evidencia | Estado |
| --- | --- | --- |
| `01-jenkins-docker.png` | Jenkins ejecutándose en Docker Desktop | Obtenida |
| `02-panel-jenkins.png` | Panel con sesión iniciada | Obtenida |
| `03-repositorio.png` | Trabajo con URL GitHub y selección de rama | Obtenida |
| `04-pipeline-inicial.png` | Tres etapas aprobadas antes del error | Obtenida, build 1 |
| `05-prueba-fallida.png` | Aserción 600 frente a 601 y resultado fallido | Obtenida, build 2 |
| `06-etapas-omitidas.png` | Construcción y humo omitidos tras el fallo | Obtenida, consola build 2 |
| `07-pipeline-corregido.png` | Nueva ejecución con tres etapas aprobadas | Obtenida, build 3 |
| `08-actions-fallido.png` | API oficial de Actions: fallo y commit visibles | Obtenida |
| `09-actions-corregido.png` | API oficial de Actions: aprobado tras corregir | Obtenida |
| `10-reporte-pytest.png` | Reporte de pruebas publicado en Jenkins | Obtenida, build 3: 32 aprobadas |

Conservo el número de build o commit, el nombre del trabajo y su resultado.
Evito mostrar `.env`, tokens, cookies y credenciales. Los registros y XML completos
se descargan de los artefactos; solo incorporo fragmentos necesarios y revisados.

El PDF final debe incluir portada con datos reales, enlace al repositorio,
arquitectura, tres etapas, fallo y corrección, tabla comparativa, conclusiones
basadas en resultados y referencias APA.

La imagen de Actions captura la respuesta real de `api.github.com`, no su panel
web. Para agregar además una captura del panel, abro la ejecución enlazada en el
informe con mi sesión de GitHub y capturo el nombre, commit y resultado.
