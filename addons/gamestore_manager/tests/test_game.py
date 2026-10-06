# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
import psycopg2


@tagged('post_install', '-at_install')
class TestGamestoreVideojuego(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plataforma_ps5 = cls.env['gamestore.plataforma'].create({
            'name': 'PlayStation 5 Test',
            'fabricante': 'Sony',
        })
        cls.genero_rpg = cls.env['gamestore.genero'].create({
            'name': 'RPG Test',
        })
        cls.juego = cls.env['gamestore.videojuego'].create({
            'name': 'Test RPG Adventure',
            'plataforma_id': cls.plataforma_ps5.id,
            'genero_ids': [(4, cls.genero_rpg.id)],
            'precio': 69.99,
            'stock': 10,
            'stock_minimo': 3,
        })

    def test_01_calculo_estado_stock(self):
        """Verifica que el estado de stock cambie dinámicamente según la cantidad."""
        self.assertEqual(self.juego.estado_stock, 'disponible')

        # Stock bajo (menor o igual al mínimo)
        self.juego.stock = 3
        self.assertEqual(self.juego.estado_stock, 'bajo')

        # Stock agotado
        self.juego.stock = 0
        self.assertEqual(self.juego.estado_stock, 'agotado')

    def test_02_display_name_personalizado(self):
        """El nombre visible debe incluir la plataforma entre paréntesis."""
        self.assertEqual(self.juego.display_name, 'Test RPG Adventure (PlayStation 5 Test)')

    def test_03_precio_negativo_constraint(self):
        """No se debe permitir guardar un precio negativo."""
        with self.assertRaises(Exception):
            with self.cr.savepoint():
                self.env['gamestore.videojuego'].create({
                    'name': 'Juego Inválido',
                    'plataforma_id': self.plataforma_ps5.id,
                    'precio': -10.0,
                    'stock': 5,
                })
