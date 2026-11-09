from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles


class SPAStaticFiles(StaticFiles):
    """Sirve el build React y permite navegación directa sin ocultar errores de API."""

    async def get_response(self, path: str, scope):
        route_path = path.replace("\\", "/").lstrip("/")
        if route_path == "api" or route_path.startswith("api/"):
            raise HTTPException(status_code=404)
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            # Los assets inexistentes deben dar 404, no recibir HTML como JavaScript.
            if (
                exc.status_code != 404
                or route_path.startswith("assets/")
                or "." in route_path.rsplit("/", 1)[-1]
            ):
                raise
            return await super().get_response("index.html", scope)
