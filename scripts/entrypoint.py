#!/usr/bin/env python3
"""
Entrypoint inteligente para Odoo 18 en GameStore Manager.
Detecta el estado de la base de datos 'gamestore' en PostgreSQL:
1. Espera a que PostgreSQL esté listo.
2. Si la base de datos 'gamestore' no existe en PostgreSQL, la crea con SQL nativo.
3. Si la base de datos no tiene las tablas de Odoo, ejecuta la inicialización completa:
   instala 'gamestore_manager' y carga los datos de demostración.
4. Arranca el servidor web Odoo 18 en el puerto 8069.
"""
import sys
import time
import subprocess
import psycopg2


def wait_and_prepare_db(max_retries=60):
    print("⏳ [1/3] Conectando a PostgreSQL (db:5432)...", flush=True)
    conn = None
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
            break
        except Exception as e:
            time.sleep(1)

    if not conn:
        print("❌ Error: No se pudo conectar a PostgreSQL.", flush=True)
        return False

    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'gamestore'")
    db_exists = cur.fetchone() is not None

    if not db_exists:
        print("📦 [2/3] Creando base de datos 'gamestore' en PostgreSQL...", flush=True)
        cur.execute("CREATE DATABASE gamestore ENCODING 'utf8' OWNER odoo")
        print("✅ Base de datos 'gamestore' creada en PostgreSQL.", flush=True)
    conn.close()

    # Comprobar si ya tiene tablas inicializadas de Odoo
    print("🔍 Comprobando tablas de Odoo en 'gamestore'...", flush=True)
    conn_gs = psycopg2.connect(
        host="db",
        port=5432,
        user="odoo",
        password="odoo",
        dbname="gamestore",
    )
    cur_gs = conn_gs.cursor()
    cur_gs.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_module_module'"
    )
    tables_exist = cur_gs.fetchone() is not None
    if tables_exist:
        cur_gs.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_model_data') THEN
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_plataforma_ps5', 'gamestore_manager', 'gamestore.plataforma', id, false FROM gamestore_plataforma WHERE name = 'PlayStation 5' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_plataforma_switch', 'gamestore_manager', 'gamestore.plataforma', id, false FROM gamestore_plataforma WHERE name = 'Nintendo Switch' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_plataforma_pc', 'gamestore_manager', 'gamestore.plataforma', id, false FROM gamestore_plataforma WHERE name = 'PC' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_plataforma_xbox', 'gamestore_manager', 'gamestore.plataforma', id, false FROM gamestore_plataforma WHERE name = 'Xbox Series X|S' ON CONFLICT (module, name) DO NOTHING;

                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_genero_rpg', 'gamestore_manager', 'gamestore.genero', id, false FROM gamestore_genero WHERE name = 'RPG' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_genero_accion', 'gamestore_manager', 'gamestore.genero', id, false FROM gamestore_genero WHERE name = 'Acción / Aventura' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_genero_mundo_abierto', 'gamestore_manager', 'gamestore.genero', id, false FROM gamestore_genero WHERE name = 'Mundo Abierto' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_genero_soulslike', 'gamestore_manager', 'gamestore.genero', id, false FROM gamestore_genero WHERE name = 'Souls-like' ON CONFLICT (module, name) DO NOTHING;

                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_dev_fromsoftware', 'gamestore_manager', 'gamestore.desarrolladora', id, false FROM gamestore_desarrolladora WHERE name = 'FromSoftware' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_dev_nintendo', 'gamestore_manager', 'gamestore.desarrolladora', id, false FROM gamestore_desarrolladora WHERE name = 'Nintendo EPD' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_dev_cdprojekt', 'gamestore_manager', 'gamestore.desarrolladora', id, false FROM gamestore_desarrolladora WHERE name = 'CD Projekt RED' ON CONFLICT (module, name) DO NOTHING;

                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_juego_zelda', 'gamestore_manager', 'gamestore.videojuego', id, false FROM gamestore_videojuego WHERE name = 'The Legend of Zelda: Tears of the Kingdom' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_juego_elden_ring_ps5', 'gamestore_manager', 'gamestore.videojuego', id, false FROM gamestore_videojuego WHERE name = 'Elden Ring' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_juego_cyberpunk_pc', 'gamestore_manager', 'gamestore.videojuego', id, false FROM gamestore_videojuego WHERE name = 'Cyberpunk 2077: Phantom Liberty' ON CONFLICT (module, name) DO NOTHING;
                    INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                    SELECT 'demo_juego_mario_switch', 'gamestore_manager', 'gamestore.videojuego', id, false FROM gamestore_videojuego WHERE name = 'Super Mario Wonder' ON CONFLICT (module, name) DO NOTHING;
                END IF;
            END $$;
        """)
        conn_gs.commit()
    conn_gs.close()

    return tables_exist


def main():
    already_initialized = wait_and_prepare_db()

    if not already_initialized:
        print(
            "🚀 [3/3] Inicializando Odoo 18 e instalando 'gamestore_manager' con datos demo...",
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
            print("✅ 'gamestore_manager' instalado correctamente.", flush=True)
        else:
            print(f"⚠️ Odoo init finalizó con código {res.returncode}", flush=True)
    else:
        print("✅ Base de datos 'gamestore' ya inicializada. Omitiendo instalación inicial.", flush=True)

    print("🌐 Arrancando servidor web Odoo 18 en http://0.0.0.0:8069...", flush=True)
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--dev=reload,xml"]
    cmd = ["odoo", "-c", "/etc/odoo/odoo.conf", "-d", "gamestore"] + args
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
