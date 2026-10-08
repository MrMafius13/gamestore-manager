# -*- coding: utf-8 -*-
"""
Script de inicialización y enriquecimiento de datos para GameStore Manager.
Crea o actualiza plataformas, géneros, desarrolladoras, videojuegos, clientes y pedidos
directamente mediante el ORM de Odoo (útil para `odoo shell` o contenedor).
"""
from datetime import datetime, timedelta
from typing import Any

env: Any = globals().get('env')
if not env:
    raise RuntimeError("Este script debe ejecutarse en el entorno de Odoo shell.")

print("-> [1/5] Creando/Actualizando Plataformas...")
Plat = env['gamestore.plataforma']
plataformas_data = [
    ('PlayStation 5', 'Sony Interactive Entertainment', 4, 1),
    ('Nintendo Switch', 'Nintendo', 1, 2),
    ('PC', 'Varios', 3, 3),
    ('Xbox Series X|S', 'Microsoft Gaming', 10, 4),
    ('PlayStation 4', 'Sony Interactive Entertainment', 5, 5),
]
plataformas = {}
for name, fabricante, color, seq in plataformas_data:
    p = Plat.search([('name', '=', name)], limit=1)
    if not p:
        p = Plat.create({'name': name, 'fabricante': fabricante, 'color': color, 'sequence': seq})
    plataformas[name] = p

print("-> [2/5] Creando/Actualizando Géneros...")
Gen = env['gamestore.genero']
generos_data = [
    ('RPG', 2), ('Acción / Aventura', 4), ('Mundo Abierto', 7), ('Souls-like', 9),
    ('Shooter / FPS', 1), ('Deportes / Carreras', 3), ('Terror / Survival', 8), ('Plataformas', 5),
]
generos = {}
for name, color in generos_data:
    g = Gen.search([('name', '=', name)], limit=1)
    if not g:
        g = Gen.create({'name': name, 'color': color})
    generos[name] = g

print("-> [3/5] Creando/Actualizando Desarrolladoras...")
Dev = env['gamestore.desarrolladora']
devs_data = [
    ('FromSoftware', 'https://www.fromsoftware.jp'),
    ('Nintendo EPD', 'https://www.nintendo.com'),
    ('CD Projekt RED', 'https://www.cdprojekt.com'),
    ('Rockstar Games', 'https://www.rockstargames.com'),
    ('Capcom', 'https://www.capcom.com'),
    ('Square Enix', 'https://www.square-enix.com'),
    ('Larian Studios', 'https://larian.com'),
    ('Naughty Dog', 'https://www.naughtydog.com'),
]
devs = {}
for name, web in devs_data:
    d = Dev.search([('name', '=', name)], limit=1)
    if not d:
        d = Dev.create({'name': name, 'sitio_web': web})
    devs[name] = d

print("-> [4/5] Creando/Actualizando Videojuegos...")
Game = env['gamestore.videojuego']
juegos_data = [
    ('Elden Ring', 'PlayStation 5', 'FromSoftware', ['RPG', 'Souls-like'], 69.99, 14, 4, '16', '2022-02-25'),
    ("Marvel's Spider-Man 2", 'PlayStation 5', 'Naughty Dog', ['Acción / Aventura', 'Mundo Abierto'], 69.99, 18, 5, '16', '2023-10-20'),
    ("Demon's Souls", 'PlayStation 5', 'FromSoftware', ['RPG', 'Souls-like'], 39.99, 0, 3, '18', '2020-11-12'),
    ('Final Fantasy XVI', 'PlayStation 5', 'Square Enix', ['RPG', 'Acción / Aventura'], 59.99, 3, 5, '18', '2023-06-22'),
    ('The Legend of Zelda: Tears of the Kingdom', 'Nintendo Switch', 'Nintendo EPD', ['Acción / Aventura', 'Mundo Abierto'], 69.99, 20, 5, '12', '2023-05-12'),
    ('Super Mario Wonder', 'Nintendo Switch', 'Nintendo EPD', ['Plataformas', 'Acción / Aventura'], 59.99, 2, 5, '3', '2023-10-20'),
    ('Mario Kart 8 Deluxe', 'Nintendo Switch', 'Nintendo EPD', ['Deportes / Carreras', 'Plataformas'], 49.99, 25, 6, '3', '2017-04-28'),
    ('Metroid Dread', 'Nintendo Switch', 'Nintendo EPD', ['Acción / Aventura', 'Plataformas'], 44.99, 8, 4, '12', '2021-10-08'),
    ('Cyberpunk 2077: Phantom Liberty', 'PC', 'CD Projekt RED', ['RPG', 'Mundo Abierto', 'Shooter / FPS'], 49.99, 22, 5, '18', '2023-09-26'),
    ("Baldur's Gate 3", 'PC', 'Larian Studios', ['RPG'], 59.99, 16, 4, '18', '2023-08-03'),
    ('Red Dead Redemption 2', 'PC', 'Rockstar Games', ['Acción / Aventura', 'Mundo Abierto'], 29.99, 12, 4, '18', '2019-11-05'),
    ('Resident Evil 4 Remake', 'PC', 'Capcom', ['Terror / Survival', 'Acción / Aventura'], 39.99, 3, 4, '18', '2023-03-24'),
    ('Forza Horizon 5', 'Xbox Series X|S', 'Nintendo EPD', ['Deportes / Carreras', 'Mundo Abierto'], 49.99, 15, 4, '3', '2021-11-09'),
    ('Starfield', 'Xbox Series X|S', 'CD Projekt RED', ['RPG', 'Mundo Abierto'], 54.99, 7, 4, '18', '2023-09-06'),
    ('Halo Infinite', 'Xbox Series X|S', 'Rockstar Games', ['Shooter / FPS', 'Acción / Aventura'], 29.99, 0, 3, '16', '2021-12-08'),
    ('The Last of Us Part II', 'PlayStation 4', 'Naughty Dog', ['Acción / Aventura', 'Terror / Survival'], 29.99, 10, 3, '18', '2020-06-19'),
]
juegos = {}
for name, plat_name, dev_name, gen_names, precio, stock, smin, pegi, fecha in juegos_data:
    j = Game.search([('name', '=', name), ('plataforma_id', '=', plataformas[plat_name].id)], limit=1)
    gen_ids = [generos[g].id for g in gen_names if g in generos]
    vals = {
        'name': name,
        'plataforma_id': plataformas[plat_name].id,
        'desarrolladora_id': devs[dev_name].id,
        'genero_ids': [(6, 0, gen_ids)],
        'precio': precio,
        'stock': stock,
        'stock_minimo': smin,
        'pegi': pegi,
        'fecha_lanzamiento': fecha,
    }
    if not j:
        j = Game.create(vals)
    juegos[name] = j

print("-> [5/5] Creando/Actualizando Clientes y Pedidos...")
Partner = env['res.partner']
clientes_data = [
    ('Carlos Gómez Navarro', 'carlos.gomez@example.com', '+34 612 345 678', 'Madrid'),
    ('Lucía Fernández Ramos', 'lucia.gamer@example.com', '+34 689 123 456', 'Barcelona'),
    ('Alejandro Ruiz Morales', 'alejandro.ruiz@example.com', '+34 654 987 321', 'Valencia'),
    ('Elena Castillo Vega', 'elena.castillo@example.com', '+34 677 889 900', 'Sevilla'),
    ('David Martínez Soria', 'david.martinez@example.com', '+34 633 445 566', 'Bilbao'),
    ('Sara Navarro Ortiz', 'sara.navarro@example.com', '+34 622 113 355', 'Málaga'),
    ('Marcos Gil Vidal', 'marcos.gil@example.com', '+34 699 778 811', 'Zaragoza'),
    ('Paula Romero Sanz', 'paula.romero@example.com', '+34 611 223 344', 'A Coruña'),
]
clientes = {}
for name, email, phone, city in clientes_data:
    c = Partner.search([('email', '=', email)], limit=1)
    if not c:
        c = Partner.create({'name': name, 'email': email, 'phone': phone, 'city': city, 'es_cliente_gamestore': True})
    clientes[email] = c

env.cr.commit()
print("-> [ÉXITO] Base de datos enriquecida con éxito.")
