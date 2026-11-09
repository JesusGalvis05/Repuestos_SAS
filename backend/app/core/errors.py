from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException


class DomainError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code, self.message, self.status = code, message, status


def error_response(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse(
        {"error": {"code": code, "message": message}},
        status_code=status,
        headers={"WWW-Authenticate": "Bearer"} if status == 401 else None,
    )


def register_errors(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        messages = {404: "Recurso no encontrado.", 405: "Método no permitido."}
        return error_response(
            f"HTTP_{exc.status_code}",
            messages.get(exc.status_code, "Solicitud rechazada."),
            exc.status_code,
        )

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        return error_response(exc.code, exc.message, exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # No incluir inputs: podrían contener contraseñas o tokens.
        fields = [{"field": ".".join(map(str, e["loc"])), "type": e["type"]} for e in exc.errors()]
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Revise los datos ingresados.",
                    "fields": fields,
                }
            },
            status_code=422,
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, exc: IntegrityError):
        return error_response(
            "CONFLICT", "La operación entra en conflicto con un registro existente.", 409
        )
