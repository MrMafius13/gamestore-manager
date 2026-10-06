# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Any

# 'env' es la variable global provista en tiempo de ejecución por `odoo shell`
env: Any = globals().get('env')

print("-> Iniciando carga de datos en Odoo...")

# Plataformas
Plat = env['gamestore.plataforma']
ps5 = Plat.search([('name', '=', 'PlayStation 5')], limit=1) or Plat.create({
    'name': 'PlayStation 5',
    'fabricante': 'Sony Interactive Entertainment',
    'color': 4,
    'sequence': 1,
})
switch = Plat.search([('name', '=', 'Nintendo Switch')], limit=1) or Plat.create({
    'name': 'Nintendo Switch',
    'fabricante': 'Nintendo',
    'color': 1,
    'sequence': 2,
})
pc = Plat.search([('name', '=', 'PC')], limit=1) or Plat.create({
    'name': 'PC',
    'fabricante': 'Varios',
    'color': 3,
    'sequence': 3,
})
xbox = Plat.search([('name', '=', 'Xbox Series X|S')], limit=1) or Plat.create({
    'name': 'Xbox Series X|S',
    'fabricante': 'Microsoft Gaming',
    'color': 10,
    'sequence': 4,
})

# Géneros
Gen = env['gamestore.genero']
rpg = Gen.search([('name', '=', 'RPG')], limit=1) or Gen.create({'name': 'RPG', 'color': 2})
accion = Gen.search([('name', '=', 'Acción / Aventura')], limit=1) or Gen.create({'name': 'Acción / Aventura', 'color': 4})
mundo = Gen.search([('name', '=', 'Mundo Abierto')], limit=1) or Gen.create({'name': 'Mundo Abierto', 'color': 7})
souls = Gen.search([('name', '=', 'Souls-like')], limit=1) or Gen.create({'name': 'Souls-like', 'color': 9})

# Desarrolladoras
Dev = env['gamestore.desarrolladora']
fromsoft = Dev.search([('name', '=', 'FromSoftware')], limit=1) or Dev.create({
    'name': 'FromSoftware',
    'sitio_web': 'https://www.fromsoftware.jp'
})
nintendo = Dev.search([('name', '=', 'Nintendo EPD')], limit=1) or Dev.create({
    'name': 'Nintendo EPD',
    'sitio_web': 'https://www.nintendo.com'
})
cdprojekt = Dev.search([('name', '=', 'CD Projekt RED')], limit=1) or Dev.create({
    'name': 'CD Projekt RED',
    'sitio_web': 'https://www.cdprojekt.com'
})

# Videojuegos
Game = env['gamestore.videojuego']
zelda = Game.search([('name', '=', 'The Legend of Zelda: Tears of the Kingdom')], limit=1) or Game.create({
    'name': 'The Legend of Zelda: Tears of the Kingdom',
    'plataforma_id': switch.id,
    'desarrolladora_id': nintendo.id,
    'genero_ids': [(6, 0, [accion.id, mundo.id])],
    'precio': 69.99,
    'stock': 18,
    'stock_minimo': 5,
    'pegi': '12',
    'fecha_lanzamiento': '2023-05-12',
    'descripcion': '<p>Una aventura épica por las tierras y los cielos de Hyrule.</p>',
})

elden = Game.search([('name', '=', 'Elden Ring')], limit=1) or Game.create({
    'name': 'Elden Ring',
    'plataforma_id': ps5.id,
    'desarrolladora_id': fromsoft.id,
    'genero_ids': [(6, 0, [rpg.id, souls.id])],
    'precio': 59.99,
    'stock': 12,
    'stock_minimo': 4,
    'pegi': '16',
    'fecha_lanzamiento': '2022-02-25',
    'descripcion': '<p>Alzate, Sinluz, y déjate guiar por la gracia en las Tierras Intermedias.</p>',
})

cyberpunk = Game.search([('name', '=', 'Cyberpunk 2077: Phantom Liberty')], limit=1) or Game.create({
    'name': 'Cyberpunk 2077: Phantom Liberty',
    'plataforma_id': pc.id,
    'desarrolladora_id': cdprojekt.id,
    'genero_ids': [(6, 0, [rpg.id, mundo.id])],
    'precio': 49.99,
    'stock': 25,
    'stock_minimo': 5,
    'pegi': '18',
    'fecha_lanzamiento': '2023-09-26',
    'descripcion': '<p>Un thriller de espionaje en el futurista distrito de Dogtown.</p>',
})

mario = Game.search([('name', '=', 'Super Mario Wonder')], limit=1) or Game.create({
    'name': 'Super Mario Wonder',
    'plataforma_id': switch.id,
    'desarrolladora_id': nintendo.id,
    'genero_ids': [(6, 0, [accion.id])],
    'precio': 59.99,
    'stock': 3,
    'stock_minimo': 5,
    'pegi': '3',
    'fecha_lanzamiento': '2023-10-20',
    'descripcion': '<p>La evolución del juego clásico de desplazamiento lateral de Mario.</p>',
})

# Clientes
Partner = env['res.partner']
carlos = Partner.search([('email', '=', 'carlos.gomez@example.com')], limit=1) or Partner.create({
    'name': 'Carlos Gómez Navarro',
    'email': 'carlos.gomez@example.com',
    'phone': '+34 612 345 678',
    'city': 'Madrid',
    'es_cliente_gamestore': True,
})

lucia = Partner.search([('email', '=', 'lucia.gamer@example.com')], limit=1) or Partner.create({
    'name': 'Lucía Fernández Ramos',
    'email': 'lucia.gamer@example.com',
    'phone': '+34 689 123 456',
    'city': 'Barcelona',
    'es_cliente_gamestore': True,
})

# Pedidos
Order = env['gamestore.pedido']
if not Order.search_count([]):
    # Entregado
    p1 = Order.create({
        'cliente_id': carlos.id,
        'fecha': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'),
        'linea_ids': [
            (0, 0, {'videojuego_id': zelda.id, 'cantidad': 1, 'precio_unitario': 69.99}),
            (0, 0, {'videojuego_id': mario.id, 'cantidad': 1, 'precio_unitario': 59.99}),
        ],
    })
    p1.action_confirmar()
    p1.action_pagar()
    p1.action_entregar()

    # Pagado
    p2 = Order.create({
        'cliente_id': lucia.id,
        'fecha': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
        'linea_ids': [
            (0, 0, {'videojuego_id': elden.id, 'cantidad': 1, 'precio_unitario': 59.99}),
        ],
    })
    p2.action_confirmar()
    p2.action_pagar()

    # Confirmado
    p3 = Order.create({
        'cliente_id': carlos.id,
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'linea_ids': [
            (0, 0, {'videojuego_id': cyberpunk.id, 'cantidad': 1, 'precio_unitario': 49.99}),
        ],
    })
    p3.action_confirmar()

env.cr.commit()
print("-> [EXITO] Datos creados y confirmados en la base de datos.")
