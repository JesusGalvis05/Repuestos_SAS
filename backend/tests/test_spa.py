import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def web_client(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text('<html lang="es">JG Repuestos</html>', encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/app.js").write_text("console.log('JG')", encoding="utf-8")
    monkeypatch.setenv("JWT_SECRET", "static-test-secret-at-least-32-characters")
    monkeypatch.setenv("FRONTEND_DIST", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    try:
        with TestClient(create_app()) as client:
            yield client
    finally:
        get_settings.cache_clear()


def test_spa_supports_direct_navigation(web_client):
    for path in ["/", "/ingresar", "/perfil", "/usuarios"]:
        response = web_client.get(path)
        assert response.status_code == 200
        assert "JG Repuestos" in response.text
    assert web_client.get("/assets/app.js").headers["content-type"].startswith("text/javascript")


def test_spa_does_not_hide_api_or_asset_errors(web_client):
    assert web_client.get("/api/v1/not-found").status_code == 404
    assert web_client.get("/api/v1/health").json()["status"] == "ok"
    assert web_client.get("/assets/missing.js").status_code == 404
    assert web_client.get("/missing.css").status_code == 404
