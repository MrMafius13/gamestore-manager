#!/usr/bin/env python3
"""
Entrypoint inteligente para Odoo 18 en GameStore Manager.
Detecta el estado de PostgreSQL y de la base de datos 'gamestore':
1. Espera a que PostgreSQL esté listo y acepte conexiones en db:5432.
2. Si la base de datos 'gamestore' no existe, la crea con SQL nativo.
3. Si 'gamestore_manager' no está instalado, arranca Odoo con '-i gamestore_manager'
   para instalar el módulo con su catálogo y pedidos demo en un solo paso.
4. Arranca directamente el servidor web Odoo 18 en http://0.0.0.0:8069.
"""
import os
import sys
import time
import psycopg2

DB_HOST = os.environ.get("DB_HOST", "db")


def wait_and_prepare_db(max_retries=60):
    print(f"⏳ [1/2] Conectando a PostgreSQL ({DB_HOST}:5432)...", flush=True)
    conn_gs = None

    # 1. Conectar directamente a 'gamestore' (creada automáticamente por POSTGRES_DB)
    for attempt in range(max_retries):
        try:
            conn_gs = psycopg2.connect(
                host=DB_HOST,
                port=5432,
                user="odoo",
                password="odoo",
                dbname="gamestore",
                connect_timeout=5,
            )
            conn_gs.autocommit = True
            break
        except Exception:
            # Fallback: intentar conectar a 'postgres' para crear 'gamestore' si no existe
            try:
                conn_pg = psycopg2.connect(
                    host=DB_HOST,
                    port=5432,
                    user="odoo",
                    password="odoo",
                    dbname="postgres",
                    connect_timeout=5,
                )
                conn_pg.autocommit = True
                cur_pg = conn_pg.cursor()
                cur_pg.execute("SELECT 1 FROM pg_database WHERE datname = 'gamestore'")
                if not cur_pg.fetchone():
                    print("📦 Creando base de datos 'gamestore' en PostgreSQL...", flush=True)
                    cur_pg.execute("CREATE DATABASE gamestore ENCODING 'utf8' OWNER odoo")
                conn_pg.close()
            except Exception as e:
                print(f"   intento {attempt+1}: {e}", flush=True)
            time.sleep(1)

    if not conn_gs:
        print("❌ Error: No se pudo conectar a PostgreSQL tras varios intentos.", flush=True)
        return False

    # 2. Comprobar si 'gamestore_manager' ya está completamente instalado
    print("🔍 [2/2] Comprobando estado de 'gamestore_manager'...", flush=True)
    try:
        cur_gs = conn_gs.cursor()
        cur_gs.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_module_module'"
        )
        if cur_gs.fetchone():
            cur_gs.execute(
                "SELECT 1 FROM ir_module_module WHERE name = 'gamestore_manager' AND state = 'installed'"
            )
            module_installed = cur_gs.fetchone() is not None
            conn_gs.close()
            return module_installed
        conn_gs.close()
        return False
    except Exception as e:
        print(f"⚠️ Nota al comprobar tablas: {e}", flush=True)
        if conn_gs:
            conn_gs.close()
        return False


def main():
    already_initialized = wait_and_prepare_db()

    args = sys.argv[1:] if len(sys.argv) > 1 else ["--dev=reload,xml"]
    if os.environ.get("DB_HOST"):
        args.append(f"--db_host={os.environ['DB_HOST']}")

    if not already_initialized:
        print(
            "🚀 Inicializando Odoo 18 e instalando 'gamestore_manager' con catálogo y datos demo...",
            flush=True,
        )
        cmd = ["odoo", "-c", "/etc/odoo/odoo.conf", "-d", "gamestore", "-i", "gamestore_manager"] + args
    else:
        print("✅ Base de datos 'gamestore' ya inicializada. Arrancando servidor web...", flush=True)
        cmd = ["odoo", "-c", "/etc/odoo/odoo.conf", "-d", "gamestore"] + args

    print("🌐 Arrancando servidor web Odoo 18 en http://0.0.0.0:8069...", flush=True)
    os.execvp("odoo", cmd)


if __name__ == "__main__":
    main()
