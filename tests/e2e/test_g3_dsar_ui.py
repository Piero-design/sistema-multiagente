"""Group 3 (DSAR) web page, end to end in a real browser (Playwright), against the RUNNING platform.

Run (platform up, `pip install playwright pytest httpx`; uses the installed Chrome, no browser download):
    pytest tests/e2e/test_g3_dsar_ui.py -q
Env: PLATFORM_URL (default http://localhost:8080), PLAYWRIGHT_CHANNEL (default chrome; empty = bundled Chromium),
HEADED=1 to watch it. Synthetic data only (example.test); it only touches G3's own pages and cases."""
import os
import re
import time

import httpx
import pytest

sync_api = pytest.importorskip("playwright.sync_api")
expect = sync_api.expect

BASE = os.getenv("PLATFORM_URL", "http://localhost:8080")
DPO, LEGAL = ("dpo", "demo-dpo"), ("legal", "demo-legal")


def _platform_up() -> bool:
    try:
        return httpx.get(f"{BASE}/api/agents", timeout=30).status_code == 200
    except httpx.HTTPError:
        return False


pytestmark = pytest.mark.skipif(not _platform_up(), reason=f"la plataforma no responde en {BASE}")


def create_case(rights=("erasure",)) -> str:
    """A pending-identity case through the agent's own MCP tool (the same path as the «Crear caso» button)."""
    eid = httpx.post(f"{BASE}/api/agents/dsar/execute", timeout=30, json={"action": "dsar_crear_caso", "input": {
        "principal_id": "person-001", "request_types": list(rights), "policy_id": "PE-LEY29733",
        "received_at": time.strftime("%Y-%m-%d"), "identity_status": "pending"}}).json()["execution_id"]
    for _ in range(60):
        e = httpx.get(f"{BASE}/api/executions/{eid}", timeout=30).json()
        if e["status"] == "succeeded":
            return e["result"]["output"]["case_id"]
        assert e["status"] != "failed", e.get("error")
        time.sleep(1)
    raise AssertionError("el caso no se creó a tiempo")


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        channel = os.getenv("PLAYWRIGHT_CHANNEL", "chrome") or None
        b = p.chromium.launch(channel=channel, headless=os.getenv("HEADED") != "1")
        yield b
        b.close()


@pytest.fixture
def page(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, locale="es-PE")
    pg = ctx.new_page()
    pg.set_default_timeout(30_000)
    yield pg
    ctx.close()


def login(page, user):
    page.goto(f"{BASE}/agentes/dsar/gestion")
    page.locator("input[name=u]").fill(user[0])
    page.locator("input[name=p]").fill(user[1])
    page.get_by_role("button", name="Entrar").click()


def test_one_dsar_entry_with_two_tabs(page):
    page.goto(f"{BASE}/agentes/dsar")
    expect(page.get_by_role("heading", name=re.compile("G3 · Derechos de titulares"))).to_be_visible()
    nav = page.locator("nav")
    expect(nav.get_by_role("link", name="G3 · DSAR")).to_have_count(1)
    expect(nav.get_by_text("Gestión DSAR")).to_have_count(0)            # no separate menu entry any more
    expect(page.get_by_role("button", name="Herramientas del agente")).to_be_visible()
    expect(page.get_by_role("button", name="Gestión (DPO)")).to_be_visible()
    for action in ("Calcular plazos", "Crear caso", "Controles y cláusulas ISO de un caso", "Preguntar al asistente"):
        expect(page.get_by_role("button", name=action, exact=True)).to_be_visible()


def test_controls_tool_shows_clauses_of_a_case(page):
    case_id = create_case()
    page.goto(f"{BASE}/agentes/dsar")
    page.get_by_role("button", name="Controles y cláusulas ISO de un caso").click()
    page.locator("input[name=case_id]").fill(case_id)
    page.get_by_role("button", name="Ejecutar").click()
    result = page.locator("pre").first
    expect(result).to_contain_text("Cláusula 8.3", timeout=60_000)
    expect(result).to_contain_text("A.1.3.7")


def test_management_needs_a_dpo(page):
    page.goto(f"{BASE}/agentes/dsar/gestion")
    expect(page.get_by_role("heading", name="Iniciar sesión")).to_be_visible()
    login(page, LEGAL)
    expect(page.get_by_text("se requiere DPO")).to_be_visible()
    expect(page.get_by_role("button", name="Indicadores")).to_have_count(0)


def test_dpo_verifies_identity_and_approves_from_the_case(page):
    case_id = create_case()
    login(page, DPO)
    expect(page.get_by_text("dpo · DPO")).to_be_visible()
    page.locator("select[name=case]").select_option(case_id)
    expect(page.get_by_role("heading", name=f"{case_id} · IDENTITY_PENDING")).to_be_visible()
    expect(page.get_by_text("Sin registros: la identidad no está verificada")).to_be_visible()
    expect(page.get_by_role("cell", name="Cláusula 8.3")).to_be_visible()

    page.get_by_role("button", name="Verificar identidad").click()
    expect(page.get_by_role("heading", name=f"{case_id} · APPROVAL_REQUIRED")).to_be_visible()
    expect(page.get_by_role("cell", name="Cláusula 8.3")).to_have_count(0)    # risk treated: identity verified
    expect(page.get_by_role("cell", name="crm-001")).to_be_visible()          # now the agent searched the records

    page.locator("input[name=note]").first.fill("Aprobado en prueba de interfaz")
    page.get_by_role("button", name="Aprobar").click()
    expect(page.get_by_text("Decisión humana: APPROVED")).to_be_visible()
    expect(page.get_by_text("dpo · Aprobado en prueba de interfaz")).to_be_visible()


def test_indicators_tab_draws_charts(page):
    login(page, DPO)
    page.get_by_role("button", name="Indicadores").click()
    for title in ("Plazos de los expedientes abiertos", "Casos por estado", "Casos por derecho", "Casos por semana"):
        expect(page.get_by_role("heading", name=title)).to_be_visible()
    expect(page.get_by_text("cláusula 9.1")).to_be_visible()
    expect(page.locator("[role=listitem]").first).to_be_visible()             # at least one bar is drawn


def test_mail_demo_goes_to_human_triage(page):
    login(page, DPO)
    page.get_by_role("button", name="Correos entrantes").click()
    page.get_by_role("button", name="Cargar 5 correos de demostración").click()
    page.get_by_role("button", name="Revisar buzón y analizar").click()
    # Without a local model every mail waits for a person: a triage card appears.
    expect(page.get_by_role("heading", name=re.compile(r"^Triaje · correo #")).first).to_be_visible(timeout=90_000)
