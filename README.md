# NexaFarma — tienda virtual de farmacia y bienestar

NexaFarma es una marca ficticia para un proyecto académico. La aplicación transforma la base técnica de una tienda virtual en una experiencia de catálogo de cuidado personal, higiene, botiquín y dispositivos de bienestar. No representa una farmacia real ni ofrece diagnóstico, prescripción o validación de fórmulas médicas.

## Incluye

- Catálogo con búsqueda, filtros por categoría, precios ilustrativos en COP y control de inventario.
- Fichas de productos, carrito, favoritos, registro e inicio de sesión, historial de pedidos y comprobantes PDF.
- Panel administrativo para productos, categorías, pedidos, clientes, descuentos, reseñas, mensajes y ajustes.
- Protección para productos marcados como sujetos a fórmula: se pueden mostrar en el catálogo, pero se bloquean en carrito y asistentes; esta demo no implementa verificación de prescripciones.
- Opciones de correo transaccional (Gmail API por HTTPS, SMTP o Resend), Google OAuth, Groq, Wompi y Mercado Pago, pendientes de credenciales y pruebas reales.
- Plantillas HTML/Jinja, Bootstrap 5, CSS local y JavaScript. La lógica de negocio, seguridad, base de datos y pagos está implementada en Python con Flask.
- Base SQLite limpia: al iniciar se crea `nexafarma.db` con 22 productos de demostración (12 genéricos y 10 referencias de marcas reales). No se empaquetan cuentas, pedidos, sesiones, bases de datos ni claves privadas.

## Requisitos

Python 3.11 o 3.12 recomendado. Se requiere conexión a Internet para instalar las dependencias la primera vez y para los proveedores externos que elijas activar. Las páginas usan CSS propio; Bootstrap se carga desde CDN, así que las clases y componentes propios siguen dando estructura si no hay acceso a esa CDN, aunque Bootstrap no estará disponible.

## Instalación en Windows

1. Descomprime el ZIP en una carpeta normal, por ejemplo `C:\Proyectos\NexaFarma`.
2. Abre PowerShell en esa carpeta y crea el entorno:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Crea el archivo de configuración local:

```powershell
Copy-Item .env.example .env
```

4. Edita `.env`. Para una primera prueba local, define una `SECRET_KEY` larga y aleatoria. Para habilitar el panel de administración, rellena también `ADMIN_EMAIL` y `ADMIN_PASSWORD` con datos propios (mínimo recomendado para administrador: 16 caracteres). No compartas `.env` ni lo subas a GitHub.
5. Inicia la aplicación:

```powershell
python app.py
```

6. Abre `http://127.0.0.1:5000`. La base SQLite se crea automáticamente en el directorio del proyecto. En la primera carga habrá 22 productos de demostración y referencias de consumo, no medicamentos sujetos a fórmula.

También puedes ejecutar `iniciar_nexafarma.bat` en Windows: crea el entorno virtual, instala los paquetes si faltan, crea `.env` desde la plantilla y abre el sitio. Antes de usarlo, edita `.env` y cambia los valores secretos.

## Configuración inicial del administrador

El usuario administrador se crea o actualiza al arrancar solamente cuando `ADMIN_EMAIL` y `ADMIN_PASSWORD` tienen valores. Configúralos en `.env` antes de ejecutar `python app.py`. No hay una contraseña predeterminada publicada en el proyecto. Entra desde **Entrar** y luego usa **Administración**.

## Persistencia en Render (muy importante)

Render usa un sistema de archivos efímero por defecto. Esta versión admite guardar la base SQLite y las imágenes subidas en un disco persistente: en el Web Service agrega un disco con **Mount Path** `/var/data` y define la variable `NEXAFARMA_DATA_DIR=/var/data`. La aplicación utilizará `/var/data/nexafarma.db` y `/var/data/uploads`. El ZIP incluye un `Procfile` con Gunicorn para iniciar el servicio web. Consulta `CONFIGURACION_PRODUCCION.md` para ver los pasos completos.

Los discos persistentes requieren un servicio Render de pago. Render Free no admite discos persistentes; en ese plan se requiere migrar la aplicación a PostgreSQL. Esta versión aún no usa `DATABASE_URL` de PostgreSQL.

Si `nexafarma.db` ya está rastreada por tu repositorio, quítala del índice de Git con `git rm --cached --ignore-unmatch nexafarma.db` y sube el cambio. El ZIP de esta entrega no incluye la base local ni `.env`.

## Integraciones externas

Todas las credenciales sensibles se dejan vacías en `.env.example` intencionalmente.

- **Gmail API:** configura un cliente OAuth y el refresh token de una cuenta que controles; usa `EMAIL_PROVIDER=gmail_api` y define `GMAIL_API_CLIENT_ID`, `GMAIL_API_CLIENT_SECRET`, `GMAIL_API_REFRESH_TOKEN`, `GMAIL_API_FROM` y, opcionalmente, `GMAIL_API_REPLY_TO`.
- **SMTP:** configura `EMAIL_PROVIDER=smtp`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` y TLS/SSL de acuerdo con tu proveedor.
- **Resend:** configura `EMAIL_PROVIDER=resend`, `RESEND_API_KEY` y `RESEND_FROM` con un dominio verificado.
- **Mercado Pago:** define `MERCADOPAGO_ACCESS_TOKEN` y `MERCADOPAGO_WEBHOOK_SECRET`, y usa una `BASE_URL` pública HTTPS en el despliegue. En local puede ejecutarse el catálogo, pero un webhook público requiere una URL accesible.
- **Wompi:** define `WOMPI_PUBLIC_KEY`, `WOMPI_INTEGRITY_SECRET` y `WOMPI_EVENTS_SECRET`. Deja `WOMPI_TEMPORARILY_UNAVAILABLE=1` hasta finalizar las pruebas con las credenciales de prueba y el webhook; solo después de comprobar el flujo de punta a punta se puede cambiar a `0`.
- **WhatsApp y redes:** rellena `WHATSAPP_NUMBER` con el número de atención en formato internacional sin `+` ni espacios. Si queda vacío, los accesos a WhatsApp se ocultan. Cambia también los enlaces sociales de ejemplo antes de publicar.
- **Google OAuth:** define client ID/secret y una URI de callback registrada exactamente igual en Google Cloud y en `GOOGLE_OAUTH_REDIRECT_URI`.
- **Groq:** define `GROQ_API_KEY` y un `AGENT_MODEL` compatible si quieres activar el asistente generativo. Sin clave el sistema usa respuestas locales limitadas.

No hay integración externa confirmada en este paquete, porque requiere credenciales del titular de cada cuenta. No habilites cobros reales hasta validar el ambiente, firma de webhooks, URLs de retorno, estados de pedido y reembolsos con el proveedor.

## Pruebas y diagnóstico

```powershell
python -m py_compile app.py
python verificar_nexafarma.py
python -m unittest discover -s tests -v
```

`/salud` comprueba que el proceso y la base responden, y muestra indicadores de configuración de pagos. Es un endpoint de diagnóstico básico, no una certificación de seguridad. Para probar rutas HTTP, corre la aplicación en tu entorno y visita el catálogo, las fichas, el carrito, el login, el checkout y el panel administrativo. Las pruebas automáticas no deben apuntarse a datos reales.

## Base de datos y archivos

- SQLite: `nexafarma.db` (se crea al arrancar; no se incluye en el ZIP).
- Imágenes base de cinco referencias: `static/uploads/`. Las fotos agregadas desde el administrador se guardan en `static/uploads/` en local y en el directorio de datos configurado en producción. Cinco referencias adicionales usan imágenes remotas de sus distribuidores.
- Plantillas: `templates/`.
- CSS, JS e iconos: `static/`.
- Configuración sensible: `.env` (excluido de Git por `.gitignore`).

Haz una copia de seguridad privada de la base y de `static/uploads` cuando comiences a guardar datos útiles. En caso de querer reiniciar la demo desde cero, detén la aplicación y elimina únicamente `nexafarma.db`; al arrancar se reconstruye el catálogo de muestra. Esa operación borra usuarios, pedidos y demás registros locales.

## Antes de publicar

Configura HTTPS, `SECRET_KEY`, credenciales de proveedor, dirección real, teléfono, correo, condiciones de entrega, privacidad, política de devoluciones y datos legales. Revisa las normas sanitarias y de protección al consumidor que correspondan a tu operación real. NexaFarma en este paquete es solo una demostración académica y no está preparada para vender medicamentos regulados sin los flujos legales, técnicos y profesionales aplicables.
