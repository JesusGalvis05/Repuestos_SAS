"""Fija el grafo instalado tras actualizar pyproject e instalar .[dev]."""
from importlib.metadata import distribution
from pathlib import Path
import tomllib

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

root = Path(__file__).resolve().parents[1]
project = tomllib.loads((root / "backend/pyproject.toml").read_text(encoding="utf-8"))["project"]


def resolve(requirements):
    resolved, seen = {}, set()
    queue = [Requirement(r) for r in requirements]
    while queue:
        req = queue.pop()
        name = canonicalize_name(req.name)
        key = (name, tuple(sorted(req.extras)))
        if key in seen:
            continue
        seen.add(key)
        package = distribution(name)
        resolved[name] = package.version
        for raw in package.requires or []:
            child = Requirement(raw)
            if not child.marker or any(child.marker.evaluate({"extra": extra}) for extra in {"", *req.extras}):
                queue.append(child)
    return resolved


runtime = resolve(project["dependencies"])
all_packages = resolve(project["dependencies"] + project["optional-dependencies"]["dev"])


def lines(packages):
    return "".join(f"{name}=={version}" + ('; sys_platform == "win32"' if name == "pywin32" else "") + "\n"
                   for name, version in sorted(packages.items()))


(root / "backend/requirements.lock").write_text("# Generado por scripts/lock_dependencies.py\n" + lines(runtime), encoding="utf-8")
(root / "backend/requirements-dev.lock").write_text("-r requirements.lock\n" + lines({n: v for n, v in all_packages.items() if n not in runtime}), encoding="utf-8")
print("Dependencias de ejecución y pruebas fijadas.")
