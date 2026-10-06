#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Demostración para GameStore Manager
--------------------------------------------
Muestra cómo interactuar con el módulo tanto mediante:
1. API REST HTTP (JSON)
2. API XML-RPC nativa de Odoo

Uso:
    python scripts/api_demo.py
"""

import json
import urllib.request
import urllib.error
import xmlrpc.client

BASE_URL = "http://localhost:8069"
DB = "gamestore"
USER = "admin"
PASSWORD = "admin"


def demo_rest_api():
    print("=" * 60)
    print(" 1. DEMOSTRACIÓN DE API REST (HTTP / JSON)")
    print("=" * 60)

    # 1. Obtener catálogo
    url = f"{BASE_URL}/api/gamestore/games"
    print(f"\n[GET] Consultando catálogo en: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GameStore-Demo/1.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"-> Respuesta (Código {resp.status}):")
            print(f"   Total videojuegos encontrados: {data.get('count', 0)}")
            for g in data.get('data', [])[:3]:
                print(f"   * [{g['plataforma']}] {g['name']} - {g['precio']} {g['moneda']} (Stock: {g['stock']})")
    except urllib.error.URLError as e:
        print(f"   [AVISO] No se pudo conectar al servidor Odoo: {e}")
        print("   Asegúrate de tener arrancado Odoo ('docker compose up -d').")
        return

    # 2. Obtener plataformas
    url_plat = f"{BASE_URL}/api/gamestore/platforms"
    print(f"\n[GET] Consultando plataformas: {url_plat}")
    try:
        with urllib.request.urlopen(url_plat) as resp:
            plat_data = json.loads(resp.read().decode('utf-8'))
            for p in plat_data.get('data', []):
                print(f"   * {p['name']} ({p.get('fabricante') or 'General'}) - {p.get('videojuego_count', 0)} títulos")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. Crear pedido vía POST
    url_order = f"{BASE_URL}/api/gamestore/orders"
    payload = {
        "cliente_id": 1,
        "confirmar": False,  # Se crea en borrador
        "lineas": [
            {"videojuego_id": 1, "cantidad": 1}
        ],
        "notas": "Pedido creado automáticamente desde script demo REST"
    }
    print(f"\n[POST] Creando pedido de prueba: {url_order}")
    try:
        post_data = json.dumps(payload).encode('utf-8')
        post_req = urllib.request.Request(
            url_order,
            data=post_data,
            headers={"Content-Type": "application/json", "User-Agent": "GameStore-Demo/1.0"}
        )
        with urllib.request.urlopen(post_req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print(f"-> Respuesta (Código {resp.status}):")
            print(f"   Referencia: {res['data']['reference']} | Estado: {res['data']['estado']} | Total: {res['data']['total']}")
    except Exception as e:
        print(f"   Error al crear pedido vía REST: {e}")


def demo_xmlrpc():
    print("\n" + "=" * 60)
    print(" 2. DEMOSTRACIÓN DE XML-RPC NATIVO DE ODOO")
    print("=" * 60)
    common_url = f"{BASE_URL}/xmlrpc/2/common"
    object_url = f"{BASE_URL}/xmlrpc/2/object"

    try:
        common = xmlrpc.client.ServerProxy(common_url)
        uid = common.authenticate(DB, USER, PASSWORD, {})
        print(f"-> Autenticación con Odoo exitosa. UID de usuario: {uid}")

        models = xmlrpc.client.ServerProxy(object_url)
        # Búsqueda y lectura de videojuegos con stock > 0
        juegos = models.execute_kw(
            DB, uid, PASSWORD,
            'gamestore.videojuego', 'search_read',
            [[['stock', '>', 0]]],
            {'fields': ['name', 'precio', 'stock', 'plataforma_id'], 'limit': 3}
        )
        print("-> Videojuegos disponibles leídos vía XML-RPC:")
        for j in juegos:
            print(f"   * ID {j['id']}: {j['name']} ({j['plataforma_id'][1]}) - {j['precio']} € - Stock: {j['stock']}")
    except Exception as e:
        print(f"   [AVISO] No se pudo completar llamada XML-RPC: {e}")


if __name__ == '__main__':
    demo_rest_api()
    demo_xmlrpc()
