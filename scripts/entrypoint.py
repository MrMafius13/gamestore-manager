#!/usr/bin/env python3
"""
Entrypoint inteligente para Odoo 18 en GameStore Manager.
Detecta si la base de datos 'gamestore' existe en PostgreSQL:
- Si no existe (primer arranque / GitHub Codespaces / clonación limpia):
  la crea automáticamente, instala 'gamestore_manager' y carga los datos de prueba.
- Si ya existe (desarrollo diario): arranca Odoo inmediatamente sin demoras.
"""
import sys
import time
import subprocess
import psycopg2


def wait_for_db(max_retries=40):
    print("⏳ Esperando conexión con PostgreSQL (db:5432)...", flush=True)
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="db",
                port=5432,
                user="odoo",
                password="odoo",
                dbname="postgres",
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'gamestore'")
            exists = cur.fetchone() is not None
            conn.close()
            return exists
        except Exception:
            time.sleep(1)
    print("⚠️ Tiempo de espera agotado al conectar con PostgreSQL.", flush=True)
    return True


def main():
    exists = wait_for_db()
    if not exists:
        print(
            "📦 Primera ejecución detectada: Creando base de datos 'gamestore' "
            "e instalando 'gamestore_manager' con datos demo...",
            flush=True,
        )
        res = subprocess.run(
            [
                "odoo",
                "-c",
                "/etc/odoo/odoo.conf",
                "-d",
                "gamestore",
                "-i",
                "gamestore_manager",
                "--without-demo=False",
                "--stop-after-init",
            ]
        )
        if res.returncode == 0:
            print(
                "✅ Base de datos 'gamestore' y módulo 'gamestore_manager' creados correctamente.",
                flush=True,
            )
        else:
            print(
                f"⚠️ Advertencia: odoo terminó con código de salida {res.returncode}",
                flush=True,
            )
    else:
        print("✅ Base de datos 'gamestore' ya existente.", flush=True)

    print("🚀 Arrancando servidor Odoo 18 en http://localhost:8069...", flush=True)
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--dev=reload,xml"]
    cmd = ["odoo", "-c", "/etc/odoo/odoo.conf"] + args
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
