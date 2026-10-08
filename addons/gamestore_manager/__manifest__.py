# -*- coding: utf-8 -*-
{
    'name': 'GameStore Manager',
    'version': '18.0.1.0.1',
    'summary': 'Gestión de una tienda de videojuegos: catálogo, clientes, pedidos e informes',
    'description': """
GameStore Manager
=================
Módulo de gestión para una tienda de videojuegos:

* Catálogo de videojuegos con plataformas, géneros y desarrolladoras.
* Clientes (extensión de los contactos de Odoo) con historial de compras.
* Pedidos con flujo de estados y control automático de stock.
* Asistentes para reponer stock y cancelar pedidos.
* Informes PDF y análisis de ventas (pivot / gráficos).
* API REST en JSON.
    """,
    'author': 'Tu Nombre',
    'website': 'https://github.com/tu-usuario/gamestore-manager',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        # Seguridad (siempre primero)
        'security/security.xml',
        'security/ir.model.access.csv',
        # Datos
        'data/sequence.xml',
        'data/cron.xml',
        # Informes PDF
        'reports/report_pedido.xml',
        'reports/report_inventario.xml',
        # Asistentes
        'wizards/reponer_stock_wizard_views.xml',
        'wizards/cancelar_pedido_wizard_views.xml',
        # Vistas
        'views/catalogo_views.xml',
        'views/videojuego_views.xml',
        'views/res_partner_views.xml',
        'views/pedido_views.xml',
        'views/informe_ventas_views.xml',
        # Datos de prueba / iniciales
        'demo/demo_data.xml',
        # Menús (al final: referencian acciones definidas arriba)
        'views/menus.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
}
