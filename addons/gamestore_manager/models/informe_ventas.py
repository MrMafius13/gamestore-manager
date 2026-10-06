# -*- coding: utf-8 -*-
from odoo import fields, models, tools


class GamestoreInformeVentas(models.Model):
    """Modelo de solo lectura respaldado por una VISTA de PostgreSQL.

    _auto = False indica a Odoo que no cree una tabla: en su lugar, init()
    crea una vista SQL que une pedidos, líneas y videojuegos. Esto permite
    analizar las ventas con vistas pivot y gráficos de forma muy eficiente.
    """
    _name = 'gamestore.informe.ventas'
    _description = 'Análisis de ventas'
    _auto = False
    _order = 'fecha desc'
    _rec_name = 'pedido_id'

    fecha = fields.Datetime(string='Fecha', readonly=True)
    pedido_id = fields.Many2one('gamestore.pedido', string='Pedido', readonly=True)
    cliente_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    vendedor_id = fields.Many2one('res.users', string='Vendedor', readonly=True)
    videojuego_id = fields.Many2one('gamestore.videojuego', string='Videojuego', readonly=True)
    plataforma_id = fields.Many2one('gamestore.plataforma', string='Plataforma', readonly=True)
    desarrolladora_id = fields.Many2one('gamestore.desarrolladora', string='Desarrolladora', readonly=True)
    cantidad = fields.Integer(string='Unidades vendidas', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', readonly=True)
    importe = fields.Monetary(string='Importe', readonly=True)
    estado = fields.Selection(
        [('confirmado', 'Confirmado'), ('pagado', 'Pagado'), ('entregado', 'Entregado')],
        string='Estado', readonly=True,
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    l.id                    AS id,
                    p.fecha                 AS fecha,
                    p.id                    AS pedido_id,
                    p.cliente_id            AS cliente_id,
                    p.vendedor_id           AS vendedor_id,
                    l.videojuego_id         AS videojuego_id,
                    v.plataforma_id         AS plataforma_id,
                    v.desarrolladora_id     AS desarrolladora_id,
                    l.cantidad              AS cantidad,
                    p.currency_id           AS currency_id,
                    l.subtotal              AS importe,
                    p.estado                AS estado
                FROM gamestore_pedido_linea l
                JOIN gamestore_pedido p     ON p.id = l.pedido_id
                JOIN gamestore_videojuego v ON v.id = l.videojuego_id
                WHERE p.estado IN ('confirmado', 'pagado', 'entregado')
            )
        """)
