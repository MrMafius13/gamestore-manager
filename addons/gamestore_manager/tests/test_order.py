# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestGamestorePedido(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cliente = cls.env['res.partner'].create({
            'name': 'Juan Pérez Gamer',
            'email': 'juan.gamer@test.com',
        })
        cls.plataforma = cls.env['gamestore.plataforma'].create({
            'name': 'Nintendo Switch Test',
        })
        cls.juego_a = cls.env['gamestore.videojuego'].create({
            'name': 'Super Adventure Test',
            'plataforma_id': cls.plataforma.id,
            'precio': 50.0,
            'stock': 5,
        })
        cls.juego_b = cls.env['gamestore.videojuego'].create({
            'name': 'Kart Racing Test',
            'plataforma_id': cls.plataforma.id,
            'precio': 40.0,
            'stock': 2,
        })

    def test_01_calculo_totales_pedido(self):
        """Comprueba que el total del pedido sea la suma exacta de sus líneas."""
        pedido = self.env['gamestore.pedido'].create({
            'cliente_id': self.cliente.id,
            'linea_ids': [
                (0, 0, {'videojuego_id': self.juego_a.id, 'cantidad': 2}),  # 2 * 50 = 100
                (0, 0, {'videojuego_id': self.juego_b.id, 'cantidad': 1}),  # 1 * 40 = 40
            ]
        })
        self.assertEqual(pedido.cantidad_total, 3)
        self.assertEqual(pedido.total, 140.0)
        self.assertEqual(pedido.estado, 'borrador')

    def test_02_flujo_confirmacion_y_descuento_stock(self):
        """Al confirmar, se debe descontar el stock de los juegos correspondientes."""
        stock_inicial_a = self.juego_a.stock
        pedido = self.env['gamestore.pedido'].create({
            'cliente_id': self.cliente.id,
            'linea_ids': [
                (0, 0, {'videojuego_id': self.juego_a.id, 'cantidad': 3}),
            ]
        })

        pedido.action_confirmar()
        self.assertEqual(pedido.estado, 'confirmado')
        self.assertEqual(self.juego_a.stock, stock_inicial_a - 3)

        # Flujo de pago y entrega
        pedido.action_pagar()
        self.assertEqual(pedido.estado, 'pagado')
        pedido.action_entregar()
        self.assertEqual(pedido.estado, 'entregado')

    def test_03_bloqueo_por_falta_de_stock(self):
        """Si se solicita más de lo disponible, debe abortar con UserError."""
        pedido = self.env['gamestore.pedido'].create({
            'cliente_id': self.cliente.id,
            'linea_ids': [
                (0, 0, {'videojuego_id': self.juego_b.id, 'cantidad': 99}),  # solo hay 2
            ]
        })
        with self.assertRaises(UserError):
            pedido.action_confirmar()

    def test_04_cancelacion_repone_stock(self):
        """Cancelar un pedido confirmado debe devolver las unidades al inventario."""
        stock_antes = self.juego_a.stock
        pedido = self.env['gamestore.pedido'].create({
            'cliente_id': self.cliente.id,
            'linea_ids': [
                (0, 0, {'videojuego_id': self.juego_a.id, 'cantidad': 2}),
            ]
        })
        pedido.action_confirmar()
        self.assertEqual(self.juego_a.stock, stock_antes - 2)

        # Cancelar con motivo
        pedido.cancelar_con_motivo("El cliente solicitó cambio de título")
        self.assertEqual(pedido.estado, 'cancelado')
        self.assertEqual(self.juego_a.stock, stock_antes)
