# -*- coding: utf-8 -*-
"""
Migración previa para Odoo 18:
Enlaza registros existentes que pudieron haber sido creados manualmente o por script
con sus correspondientes external IDs (XML IDs) en ir_model_data para evitar errores
de clave duplicada (UniqueViolation) al importar demo_data.xml enriquecido.
"""

def migrate(cr, version):
    if not version:
        return

    cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'gamestore_plataforma'")
    if not cr.fetchone():
        return

    cr.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_model_data') THEN
                -- Plataformas
                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_plataforma_ps5', 'gamestore_manager', 'gamestore.plataforma', id, false
                FROM gamestore_plataforma WHERE name = 'PlayStation 5'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_plataforma_switch', 'gamestore_manager', 'gamestore.plataforma', id, false
                FROM gamestore_plataforma WHERE name = 'Nintendo Switch'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_plataforma_pc', 'gamestore_manager', 'gamestore.plataforma', id, false
                FROM gamestore_plataforma WHERE name = 'PC'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_plataforma_xbox', 'gamestore_manager', 'gamestore.plataforma', id, false
                FROM gamestore_plataforma WHERE name = 'Xbox Series X|S'
                ON CONFLICT (module, name) DO NOTHING;

                -- Géneros
                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_genero_rpg', 'gamestore_manager', 'gamestore.genero', id, false
                FROM gamestore_genero WHERE name = 'RPG'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_genero_accion', 'gamestore_manager', 'gamestore.genero', id, false
                FROM gamestore_genero WHERE name = 'Acción / Aventura'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_genero_mundo_abierto', 'gamestore_manager', 'gamestore.genero', id, false
                FROM gamestore_genero WHERE name = 'Mundo Abierto'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_genero_soulslike', 'gamestore_manager', 'gamestore.genero', id, false
                FROM gamestore_genero WHERE name = 'Souls-like'
                ON CONFLICT (module, name) DO NOTHING;

                -- Desarrolladoras
                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_dev_fromsoftware', 'gamestore_manager', 'gamestore.desarrolladora', id, false
                FROM gamestore_desarrolladora WHERE name = 'FromSoftware'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_dev_nintendo', 'gamestore_manager', 'gamestore.desarrolladora', id, false
                FROM gamestore_desarrolladora WHERE name = 'Nintendo EPD'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_dev_cdprojekt', 'gamestore_manager', 'gamestore.desarrolladora', id, false
                FROM gamestore_desarrolladora WHERE name = 'CD Projekt RED'
                ON CONFLICT (module, name) DO NOTHING;

                -- Videojuegos
                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_juego_zelda', 'gamestore_manager', 'gamestore.videojuego', id, false
                FROM gamestore_videojuego WHERE name = 'The Legend of Zelda: Tears of the Kingdom'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_juego_elden_ring_ps5', 'gamestore_manager', 'gamestore.videojuego', id, false
                FROM gamestore_videojuego WHERE name = 'Elden Ring'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_juego_cyberpunk_pc', 'gamestore_manager', 'gamestore.videojuego', id, false
                FROM gamestore_videojuego WHERE name = 'Cyberpunk 2077: Phantom Liberty'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_juego_mario_switch', 'gamestore_manager', 'gamestore.videojuego', id, false
                FROM gamestore_videojuego WHERE name = 'Super Mario Wonder'
                ON CONFLICT (module, name) DO NOTHING;

                -- Clientes
                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_cliente_carlos', 'gamestore_manager', 'res.partner', id, false
                FROM res_partner WHERE email = 'carlos.gomez@example.com'
                ON CONFLICT (module, name) DO NOTHING;

                INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                SELECT 'demo_cliente_lucia', 'gamestore_manager', 'res.partner', id, false
                FROM res_partner WHERE email = 'lucia.gamer@example.com'
                ON CONFLICT (module, name) DO NOTHING;
            END IF;
        END $$;
    """)
