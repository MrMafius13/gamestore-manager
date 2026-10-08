#!/usr/bin/env python3
"""
Entrypoint inteligente para Odoo 18 en GameStore Manager.
Detecta el estado de PostgreSQL y de la base de datos 'gamestore':
1. Espera a que PostgreSQL esté listo y acepta conexiones en db:5432.
2. Si la base de datos 'gamestore' no existe, la crea con SQL nativo.
3. Si la base de datos no tiene las tablas de Odoo, ejecuta la inicialización completa:
   instala 'gamestore_manager' con todo el catálogo y pedidos de prueba.
4. Arranca el servidor web Odoo 18 en http://0.0.0.0:8069.
"""
import os
import sys
import time
import subprocess
import psycopg2


def wait_and_prepare_db(max_retries=60):
    print("⏳ [1/3] Conectando a PostgreSQL (db:5432)...", flush=True)
    conn_gs = None
    
    # 1. Intentar conectar directamente a la base de datos 'gamestore' (creada por POSTGRES_DB)
    for attempt in range(max_retries):
        try:
            conn_gs = psycopg2.connect(
                host="db",
                port=5432,
                user="odoo",
                password="odoo",
                dbname="gamestore",
            )
            conn_gs.autocommit = True
            break
        except Exception:
            # Si no existe 'gamestore', intentar conectar a 'postgres' para crearla
            try:
                conn_pg = psycopg2.connect(
                    host="db",
                    port=5432,
                    user="odoo",
                    password="odoo",
                    dbname="postgres",
                )
                conn_pg.autocommit = True
                cur_pg = conn_pg.cursor()
                cur_pg.execute("SELECT 1 FROM pg_database WHERE datname = 'gamestore'")
                if not cur_pg.fetchone():
                    print("📦 Creando base de datos 'gamestore' en PostgreSQL...", flush=True)
                    cur_pg.execute("CREATE DATABASE gamestore ENCODING 'utf8' OWNER odoo")
                conn_pg.close()
            except Exception:
                pass
            time.sleep(1)

    if not conn_gs:
        print("❌ Error: No se pudo conectar a PostgreSQL.", flush=True)
        return False

    # 2. Comprobar si ya tiene tablas inicializadas de Odoo (ir_module_module)
    print("🔍 [2/3] Comprobando tablas de Odoo en 'gamestore'...", flush=True)
    try:
        cur_gs = conn_gs.cursor()
        cur_gs.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_module_module'"
        )
        tables_exist = cur_gs.fetchone() is not None
        conn_gs.close()
        return tables_exist
    except Exception as e:
        print(f"⚠️ Error comprobando tablas: {e}", flush=True)
        if conn_gs:
            conn_gs.close()
        return False


def main():
    already_initialized = wait_and_prepare_db()

    if not already_initialized:
        print(
            "🚀 [3/3] Inicializando Odoo 18 e instalando 'gamestore_manager' con catálogo y datos demo...",
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
            print("✅ 'gamestore_manager' instalado y base de datos inicializada correctamente.", flush=True)
        else:
            print(f"⚠️ Odoo init finalizó con código {res.returncode}", flush=True)
    else:
        print("✅ Base de datos 'gamestore' ya inicializada. Omitiendo instalación inicial.", flush=True)

    print("🌐 Arrancando servidor web Odoo 18 en http://0.0.0.0:8069...", flush=True)
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--dev=reload,xml"]
    cmd = ["odoo", "-c", "/etc/odoo/odoo.conf", "-d", "gamestore"] + args
    os.execvp("odoo", cmd)


if __name__ == "__main__":
    main()
