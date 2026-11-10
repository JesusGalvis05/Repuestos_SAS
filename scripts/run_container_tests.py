"""Guarda Pytest dentro de api sin secretos del entorno ni JWT."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from docker_evidence import ROOT, sanitize, secret_values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="Directorio de evidencias de esta ejecución"
    )
    args = parser.parse_args()
    command = [
        "docker",
        "compose",
        "exec",
        "-T",
        "-e",
        "RUN_DOCKER_COMMUNICATION=1",
        "api",
        "python",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    output = sanitize(result.stdout + result.stderr, secret_values())
    directory = args.output or ROOT / "docs/entrega-1/evidencias/ci"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "22-pytest.txt").write_text(
        "$ "
        + " ".join(command)
        + "\n"
        + output
        + f"\nExit code: {result.returncode}\n",
        encoding="utf-8",
    )
    print(output)
    count = re.search(r"(\d+) passed", output)
    (directory / "22-pytest-result.json").write_text(
        json.dumps(
            {
                "status": "passed" if result.returncode == 0 else "failed",
                "scope": "pytest dentro de api contra PostgreSQL db:5432",
                "exit_code": result.returncode,
                "passed": int(count.group(1)) if count else None,
                "github_actions_run": os.environ.get("GITHUB_ACTIONS") == "true",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
