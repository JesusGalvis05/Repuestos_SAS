# Demostración del fallo y la corrección

Uso la prueba existente `test_access_contract_and_wrong_key`, que valida la
duración configurada de 600 segundos del token. En una rama de demostración
cambio temporalmente la expectativa a 601. La implementación sigue emitiendo
600, por lo que la aserción debe fallar. Después restauro la expectativa original.
No desactivo validaciones ni cambio la funcionalidad.

## Secuencia de Jenkins y GitHub

1. Publico la configuración funcional, después de autorizar el push.
2. Ejecuto Jenkins con esa rama y guardo el build aprobado.
3. Publico en `demo/entrega-2` el commit `prueba de error`.
4. Ejecuto Jenkins con `BRANCH=demo/entrega-2` antes de publicar la corrección.
5. Guardo el fallo de Pytest y las etapas de construcción y humo omitidas.
6. Espero también la ejecución fallida de `CI - Entrega 2` en Actions.
7. Publico `correccion de prueba` y ejecuto nuevamente Jenkins.
8. Guardo los resultados aprobados de ambos sistemas.

Cada push requiere autorización previa. No publico ambos commits juntos antes
de capturar el fallo: Jenkins descargaría la punta ya corregida de la rama.
No es necesario fusionar el historial de demostración a `master`.

`evidencias/simulacion-local.json`, cuando exista, contiene los hashes y resultados
de la comprobación nativa en un worktree separado. Esa prueba no sustituye la
secuencia real en Jenkins y Actions.

## Diagnóstico de etapas sin Jenkins

Desde PowerShell, con Docker iniciado:

```powershell
$env:CI_RUN_ID = 'manual-' + [guid]::NewGuid().ToString('N').Substring(0,12)
try {
    python scripts/ci_pipeline.py test
    if ($LASTEXITCODE -ne 0) { throw 'Fallaron las pruebas' }
    python scripts/ci_pipeline.py build
    if ($LASTEXITCODE -ne 0) { throw 'Fallo la construccion' }
    python scripts/ci_pipeline.py smoke
    if ($LASTEXITCODE -ne 0) { throw 'Fallo la prueba de humo' }
} finally {
    python scripts/ci_pipeline.py cleanup
}
```

Los reportes quedan en `ci-results/<identificador>/`, que no se versiona.
Esta ejecución tampoco equivale a ejecutar desde el servidor Jenkins.

## Comprobar la primera entrega

```powershell
docker compose up -d --wait --wait-timeout 180
docker compose ps
docker compose exec -T api python -m app.diagnostics roundtrip
```

No cambio credenciales ni elimino el volumen de la base de desarrollo.
