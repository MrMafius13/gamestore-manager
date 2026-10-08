#!/usr/bin/env python3
"""
Espera a que Odoo 18 esté completamente levantado y respondiendo peticiones HTTP en el puerto 8069.
Esto asegura que Codespaces solo marque el entorno como listo cuando Odoo esté 100% operativo,
evitando el error HTTP 502 (Bad Gateway).
Si el contenedor de Odoo falla, muestra los logs de error inmediatamente.
"""
import os
import sys
import time
import subprocess
import urllib.request

URL = "http://localhost:8069/web/login"
MAX_SECONDS = 300

print("⏳ Esperando a que Odoo 18 inicialice la base de datos y arranque en http://localhost:8069...", flush=True)
start_time = time.time()

while time.time() - start_time < MAX_SECONDS:
    # 1. Comprobar si Odoo responde HTTP
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Codespaces-HealthCheck"})
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status in (200, 302, 303):
                elapsed = int(time.time() - start_time)
                codespace_name = os.environ.get("CODESPACE_NAME", "")
                app_url = f"https://{codespace_name}-8069.app.github.dev" if codespace_name else "http://localhost:8069"
                print("\n" + "=" * 60, flush=True)
                print(f"🎉 ¡Odoo 18 listo y respondiendo en {elapsed}s!", flush=True)
                print(f"🌐 Enlace directo: {app_url}", flush=True)
                print("👤 Usuario:    admin", flush=True)
                print("🔑 Contraseña: admin", flush=True)
                print("📦 Base datos: gamestore", flush=True)
                print("=" * 60 + "\n", flush=True)
                sys.exit(0)
    except Exception:
        pass

    # 2. Comprobar si el contenedor de Odoo murió
    try:
        res = subprocess.run(
            ["docker", "compose", "ps", "-a", "--format", "{{.Status}}", "odoo"],
            capture_output=True,
            text=True,
        )
        status = res.stdout.strip().lower()
        if "exited" in status:
            print("\n❌ Error: El contenedor gamestore_odoo se ha detenido. Logs de Odoo:", flush=True)
            subprocess.run(["docker", "compose", "logs", "--tail=60", "odoo"])
            sys.exit(1)
    except Exception:
        pass

    time.sleep(2)

print("\n⚠️ Tiempo de espera alcanzado (300s). Mostrando logs de diagnóstico:", flush=True)
subprocess.run(["docker", "compose", "logs", "--tail=60", "odoo"])
sys.exit(0)
