"""Valida con Compose oficial; no necesita ni verifica un motor Docker."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from docker_evidence import ROOT, sanitize, secret_values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--binary", type=Path, help="Ruta de Compose standalone oficial"
    )
    args = parser.parse_args()
    if args.binary:
        executable = args.binary.resolve()
        command = [str(executable)]
        digest = hashlib.sha256(executable.read_bytes()).hexdigest()
        checksum_file = executable.with_suffix(".sha256")
        checksum_matches = (
            checksum_file.exists()
            and checksum_file.read_text().split()[0].lower() == digest
        )
        if checksum_file.exists():
            assert checksum_matches, "El binario no coincide con el checksum descargado"
    elif shutil.which("docker"):
        command, digest, checksum_matches = ["docker", "compose"], None, None
    else:
        parser.exit(2, "No hay Compose disponible. No se simuló la validación.\n")
    commands = []
    for arguments in [
        ["version"],
        ["-f", "docker-compose.yml", "config", "--quiet"],
        ["-f", "docker-compose.yml", "config", "--format", "json"],
    ]:
        result = subprocess.run(
            command + arguments,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        commands.append({"arguments": arguments, "exit_code": result.returncode})
        if result.returncode:
            parser.exit(1, sanitize(result.stderr, secret_values()))
        if arguments == ["version"]:
            version = result.stdout.strip()
    normalized = json.loads(result.stdout)
    assert set(normalized["services"]) == {"api", "db"}
    assert not normalized["services"]["db"].get("ports")
    env = normalized["services"]["api"]["environment"]
    assert env["POSTGRES_HOST"] == "db" and env["POSTGRES_PORT"] == "5432"
    directory = ROOT / "docs/entrega-1/evidencias"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "compose-config-real.json").write_text(
        sanitize(json.dumps(normalized, ensure_ascii=False, indent=2), secret_values()),
        encoding="utf-8",
    )
    report = {
        "scope": "compose-cli-only; sin motor ni contenedores",
        "status": "passed",
        "version": version,
        "binary_sha256": digest,
        "checksum_file_matches": checksum_matches,
        "commands": commands,
        "services": sorted(normalized["services"]),
        "database_host": "db",
        "database_port": 5432,
        "database_published_ports": [],
        "engine_build_run": "pending",
    }
    (directory / "compose-validacion-real.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
