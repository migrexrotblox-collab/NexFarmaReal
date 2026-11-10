from pathlib import Path
import py_compile
import re
import sys

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("ERROR: falta Jinja2. Ejecuta: pip install -r requirements.txt")
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
APP = ROOT / "app.py"
errors = []

try:
    py_compile.compile(str(APP), doraise=True)
except Exception as exc:
    errors.append(f"Python: {exc}")

env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
for path in sorted(TEMPLATES.glob("*.html")):
    try:
        env.parse(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Jinja {path.name}: {exc}")

base = (TEMPLATES / "base.html").read_text(encoding="utf-8")
if base.count("<title>") != 1 or base.count("</title>") != 1:
    errors.append("base.html: etiqueta <title> incompleta")

for path in sorted(TEMPLATES.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"<form\b[^>]*>", text, re.I):
        opening = match.group(0)
        if not re.search(r"method\s*=\s*['\"]post['\"]", opening, re.I):
            continue
        end = text.find("</form>", match.end())
        body = text[match.end():end if end >= 0 else len(text)]
        if "csrf_token" not in body:
            errors.append(f"{path.name}: formulario POST sin csrf_token")

app_text = APP.read_text(encoding="utf-8")
css_text = (ROOT / "static" / "css" / "style.css").read_text(encoding="utf-8")
js_text = (ROOT / "static" / "js" / "main.js").read_text(encoding="utf-8")
if '@app.get("/logout")' in app_text or "@app.get('/logout')" in app_text:
    errors.append("app.py: cerrar sesión debe ser POST protegido por CSRF")
if "safe_local_target" not in app_text:
    errors.append("app.py: falta validación de redirecciones locales")
for path in sorted(TEMPLATES.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    if re.search(r"href\s*=\s*['\"]\{\{\s*url_for\(['\"]logout['\"]", text, re.I):
        errors.append(f"{path.name}: logout no debe ser un enlace GET; usar formulario POST")
if "notes,created_at,updated_at" not in app_text.replace(" ", ""):
    errors.append("app.py: comprobar que las notas del checkout se guarden en orders")
if 'html[data-theme="dark"]' not in css_text:
    errors.append("style.css: faltan estilos completos del modo oscuro")
if ".checkout-step{display:none}" in css_text:
    errors.append("style.css: los bloques de checkout están ocultos sin clase active")
if 'font-family:"Plus Jakarta Sans"' in css_text:
    errors.append("style.css: hay una tipografía remota no cargada tras quitar Google Fonts")
if "localStorage" not in js_text or "nexafarma-theme" not in js_text:
    errors.append("main.js: falta persistencia del modo visual")
agent_js = ROOT / "static" / "js" / "agent.js"
agent_template = TEMPLATES / "agent.html"
agent_html = agent_template.read_text(encoding="utf-8") if agent_template.is_file() else ""
if not agent_js.is_file() or 'id="agentWindow"' not in agent_html or 'id="agentWidgetToggle"' not in base or '@app.get("/agente-ia")' not in app_text or '@app.post("/api/agent")' not in app_text:
    errors.append("Agente IA: falta su página dedicada, JavaScript o alguna ruta del agente")
if '_agent_cart_add_is_denied' not in app_text or 'AGENT_MODEL' not in app_text:
    errors.append("Agente IA: falta validación de negaciones o configuración específica del modelo")
home_text = (TEMPLATES / "home.html").read_text(encoding="utf-8")
if 'nf-hero' not in home_text or 'tu bienestar' not in home_text.lower() or 'nexafarma-promo.mp4' in home_text:
    errors.append("Portada: falta la experiencia visual de farmacia NexaFarma")
if 'requires_prescription' not in app_text or '_agent_is_medical_advice_request' not in app_text:
    errors.append("Seguridad sanitaria: falta el bloqueo de artículos con fórmula o de consultas clínicas")
for key in ("GMAIL_API_CLIENT_ID", "GMAIL_API_CLIENT_SECRET", "GMAIL_API_REFRESH_TOKEN", "GMAIL_API_FROM", "GMAIL_API_REPLY_TO"):
    if not re.search(rf"^{key}=", (ROOT / ".env.example").read_text(encoding="utf-8"), re.M):
        errors.append(f".env.example: falta la variable {key}")
if "fonts.googleapis.com" in css_text:
    errors.append("style.css: queda una dependencia externa de Google Fonts; usar fuentes locales")
env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
for key in ("WOMPI_PUBLIC_KEY", "WOMPI_INTEGRITY_SECRET", "WOMPI_EVENTS_SECRET"):
    if re.search(rf"^{key}=[ \t]*\S+", env_example, re.M):
        errors.append(f".env.example: {key} debe quedar vacío para no simular que Wompi está configurado")
for key in ("SECRET_KEY", "ADMIN_PASSWORD", "GROQ_API_KEY", "GMAIL_API_CLIENT_SECRET", "GMAIL_API_REFRESH_TOKEN", "RESEND_API_KEY", "SMTP_PASSWORD"):
    if re.search(rf"^{key}=[ \t]*\S+", env_example, re.M):
        errors.append(f".env.example: {key} debe quedar vacío; no publicar credenciales de ejemplo ni reales")
functions = set(re.findall(r"^def\s+(\w+)\s*\(", app_text, re.M))
for path in sorted(TEMPLATES.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    for endpoint in set(re.findall(r"url_for\(['\"]([A-Za-z_]\w*)['\"]", text)):
        if endpoint not in functions and endpoint != "static":
            errors.append(f"{path.name}: url_for('{endpoint}') no existe en app.py")

if errors:
    print("VERIFICACIÓN FALLIDA")
    print("- " + "\n- ".join(errors))
    raise SystemExit(1)

print("VERIFICACIÓN OK")
print(f"Plantillas Jinja: {len(list(TEMPLATES.glob('*.html')))}")
print("Python app.py: OK")
print("CSRF en formularios POST: OK")
print("Rutas url_for: OK")
print("base.html / <title>: OK")
