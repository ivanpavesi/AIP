from bs4 import BeautifulSoup
import pytest


def test_homepage_and_local_assets(client):
    response = client.get("/")
    assert response.status_code == 200
    page = BeautifulSoup(response.text, "html.parser")
    assert page.html["lang"] == "it"
    assert "Scuole di Psicoterapia Cognitiva" in page.h1.get_text(" ", strip=True)
    assert len(page.select("h1")) == 1
    assert page.select_one("label[for='codice-personale']")
    field = page.select_one("#codice-personale")
    assert "name" not in field.attrs
    assert not page.select("form")
    action = page.select_one("[hx-get]")
    assert action["hx-params"] == "none"
    assert "Gli accessi non sono ancora attivi" in response.text
    for asset in ["/static/css/app.css", "/static/js/htmx.min.js"]:
        assert client.get(asset).status_code == 200
    assert not response.cookies


@pytest.mark.parametrize("path,title", [
    ("/paziente", "Accesso Paziente"), ("/terapeuta", "Area Terapeuta"),
    ("/ricercatore", "Accesso Ricercatore"), ("/amministratore", "Accesso Amministratore"),
])
def test_future_areas_are_explicitly_unavailable(client, path, title):
    response = client.get(path)
    assert response.status_code == 200
    assert title in response.text
    assert "L’accesso non è ancora attivo." in response.text
    assert not response.cookies
    assert client.post(path, data={"code": "synthetic-example"}).status_code == 405


def test_htmx_returns_only_unavailable_message(client):
    response = client.get("/paziente", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert "L’accesso non è ancora attivo." in response.text
    assert "<html" not in response.text
    assert response.headers["vary"] == "HX-Request"


def test_security_headers_and_host_validation(client):
    response = client.get("/")
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert "'unsafe-inline'" not in response.headers["content-security-policy"]
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert client.get("/", headers={"host": "untrusted.example"}).status_code == 400


def test_health_without_database_and_no_auth_api(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
