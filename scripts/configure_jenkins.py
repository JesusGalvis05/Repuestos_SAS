"""Genera la configuracion local de Jenkins sin imprimir secretos."""

import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = ROOT / "jenkins/.env"
    lines = target.read_text(encoding="utf-8").splitlines() if target.exists() else []
    values = dict(
        line.split("=", 1) for line in lines if "=" in line and not line.startswith("#")
    )
    defaults = {
        "JENKINS_ADMIN_ID": "admin",
        "JENKINS_ADMIN_PASSWORD": secrets.token_urlsafe(32),
        "JENKINS_HTTP_PORT": "8081",
        "DOCKER_SOCKET_GID": "0",
        "JG_REPOSITORY_URL": "https://github.com/JesusGalvis05/Repuestos_SAS.git",
        "JG_GITHUB_USER": "",
        "JG_GITHUB_TOKEN": "",
    }
    for key, value in defaults.items():
        if key not in values or (
            key == "JENKINS_ADMIN_PASSWORD" and not values[key].strip()
        ):
            position = next(
                (i for i, line in enumerate(lines) if line.startswith(key + "=")), None
            )
            if position is None:
                lines.append(f"{key}={value}")
            else:
                lines[position] = f"{key}={value}"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "Jenkins configurado. Credenciales en jenkins/.env; no se imprimieron secretos."
    )


if __name__ == "__main__":
    main()
