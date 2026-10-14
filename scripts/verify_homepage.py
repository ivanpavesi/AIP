"""Verifica il sito locale con Chromium e axe-core, senza cambiare la CSP.

Prima: npm ci; pip install -e '.[dev]'; avviare uvicorn su 127.0.0.1:8000.
Uso: python scripts/verify_homepage.py --chromium /usr/bin/chromium
Senza --chromium usa il browser installato con: playwright install chromium.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument("--chromium", default=None)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
output = root / "artifacts"
output.mkdir(exist_ok=True)
axe_script = (root / "node_modules/axe-core/axe.min.js").read_text()
base_url = "http://127.0.0.1:8000"
report = {"viewports": [], "checks": []}

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=args.chromium, headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 1100})
    page = context.new_page()
    errors, requests = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda request: requests.append(request))

    for label, width, height in [("desktop", 1440, 1100), ("mobile", 390, 844), ("reflow", 320, 800)]:
        page.set_viewport_size({"width": width, "height": height})
        page.goto(base_url, wait_until="networkidle")
        # DevTools valuta axe nel contesto di test; nessuna eccezione alla CSP dell'app.
        page.evaluate(axe_script)
        result = page.evaluate("async () => await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})")
        assert not result["violations"], [(v["id"], v["description"]) for v in result["violations"]]
        assert not page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        if label != "reflow":
            page.screenshot(path=str(output / f"homepage-{label}.png"), full_page=True)
        report["viewports"].append({"label": label, "width": width, "axe_violations": 0, "horizontal_overflow": False})

    # Ogni elemento interattivo è raggiungibile, nel corretto ordine, con Tab.
    page.goto(base_url, wait_until="networkidle")
    expected = ["Vai al contenuto principale", "Scuole di Psicoterapia Cognitiva", "codice-personale", "Accedi ai questionari", "Accedi all’area terapeuta", "Accesso Ricercatore", "Accesso Amministratore"]
    for item in expected:
        page.keyboard.press("Tab")
        active = page.evaluate("({id:document.activeElement.id,text:document.activeElement.textContent, label:document.activeElement.getAttribute('aria-label')})")
        assert item in (active["id"] + active["text"] + (active["label"] or "")), active
    report["checks"].append("Ordine Tab verificato su tutti i collegamenti e sul campo codice")

    requests.clear()
    page.locator("#codice-personale").fill("SYNTHETIC-NOT-A-CREDENTIAL")
    page.get_by_role("link", name="Accedi ai questionari").click()
    page.locator("#patient-status").get_by_text("L’accesso non è ancora attivo.").wait_for()
    assert page.url.rstrip("/") == base_url
    assert any(request.headers.get("hx-request") == "true" for request in requests)
    assert all("SYNTHETIC-NOT-A-CREDENTIAL" not in request.url + (request.post_data or "") for request in requests)
    assert all(urlparse(request.url).hostname == "127.0.0.1" for request in requests)
    assert not errors, errors
    assert not context.cookies()
    report["checks"].extend(["HTMX mostra avviso senza inviare il codice", "Nessun cookie o errore JavaScript"])

    for name, path in [("Accedi all’area terapeuta", "/terapeuta"), ("Accesso Ricercatore", "/ricercatore"), ("Accesso Amministratore", "/amministratore")]:
        page.goto(base_url)
        page.get_by_role("link", name=name).click()
        assert page.url == base_url + path
        page.get_by_text("L’accesso non è ancora attivo.").wait_for()
    report["checks"].append("Collegamenti terapeuta, ricercatore e amministratore verificati")

    no_js = browser.new_context(java_script_enabled=False)
    fallback = no_js.new_page()
    fallback.goto(base_url)
    fallback.get_by_role("link", name="Accedi ai questionari").click()
    assert fallback.url == base_url + "/paziente"
    fallback.get_by_text("L’accesso non è ancora attivo.").wait_for()
    report["checks"].append("Accesso paziente mostra la pagina informativa anche senza JavaScript")
    browser.close()

(output / "browser-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
