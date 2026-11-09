"""Guarda Pytest dentro de api sin secretos del entorno ni JWT."""

import subprocess

from docker_evidence import ROOT, sanitize, secret_values


def main():
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
    directory = ROOT / "docs/entrega-1/evidencias/ci"
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
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
