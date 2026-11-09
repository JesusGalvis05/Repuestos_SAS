"""Completa configuración sin imprimir secretos ni sustituir valores existentes."""

from pathlib import Path
import secrets
import shutil
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def configure(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    values = dict(
        line.split("=", 1) for line in lines if "=" in line and not line.startswith("#")
    )
    defaults = {
        "POSTGRES_USER": "jg",
        "POSTGRES_DB": "jg_repuestos",
        "POSTGRES_PASSWORD": secrets.token_hex(24),
        "JWT_SECRET": secrets.token_hex(48),
        "APP_ENV": "development",
        "COOKIE_SECURE": "false",
        "ALLOWED_ORIGINS": '["http://localhost:5173","http://localhost:8000","http://127.0.0.1:5173","http://127.0.0.1:8000"]',
    }
    for key, default in defaults.items():
        if not values.get(key, "").strip("\"'"):
            values[key] = default
            index = next(
                (i for i, line in enumerate(lines) if line.startswith(key + "=")), None
            )
            if index is None:
                lines.append(f"{key}={default}")
            else:
                lines[index] = f"{key}={default}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return values


def main():
    values = configure(ROOT / ".env")
    backend_env = ROOT / "backend/.env"
    if not backend_env.exists():
        user, password, name = (
            quote(values[k], safe="")
            for k in ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
        )
        backend_env.write_text(
            f"DATABASE_URL=postgresql+psycopg://{user}:{password}@localhost:5432/{name}\n"
            f"JWT_SECRET={values['JWT_SECRET']}\nAPP_ENV=development\nCOOKIE_SECURE=false\n"
            f"ALLOWED_ORIGINS={values['ALLOWED_ORIGINS']}\n",
            encoding="utf-8",
        )
    frontend_env = ROOT / "frontend/.env"
    if not frontend_env.exists():
        shutil.copyfile(ROOT / "frontend/.env.example", frontend_env)
    print(
        "Configuración preparada; secretos no impresos y valores existentes conservados."
    )


if __name__ == "__main__":
    main()
