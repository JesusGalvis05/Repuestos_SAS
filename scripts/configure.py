"""Genera configuración local; no imprime secretos ni sobrescribe archivos existentes."""
from pathlib import Path
import secrets
import shutil

root = Path(__file__).resolve().parents[1]
root_env = root / ".env"
if not root_env.exists():
    root_env.write_text(f"POSTGRES_PASSWORD={secrets.token_hex(24)}\nJWT_SECRET={secrets.token_hex(48)}\n", encoding="utf-8")
values = dict(line.split("=", 1) for line in root_env.read_text(encoding="utf-8").splitlines()
              if "=" in line and not line.startswith("#"))
backend_env = root / "backend/.env"
if not backend_env.exists():
    backend_env.write_text("APP_ENV=development\n"
        f"DATABASE_URL=postgresql+psycopg://jg:{values['POSTGRES_PASSWORD']}@localhost:5432/jg_repuestos\n"
        f"JWT_SECRET={values['JWT_SECRET']}\nCOOKIE_SECURE=false\n"
        'ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:8080","http://127.0.0.1:5173","http://127.0.0.1:8080"]\n', encoding="utf-8")
frontend_env = root / "frontend/.env"
if not frontend_env.exists():
    shutil.copyfile(root / "frontend/.env.example", frontend_env)
print("Configuración local preparada. Los archivos existentes se conservaron.")
