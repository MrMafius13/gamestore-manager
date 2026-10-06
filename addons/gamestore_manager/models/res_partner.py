# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

ESTADOS_VENTA = ('confirmado', 'pagado', 'entregado')


class ResPartner(models.Model):
    """Los clientes de la tienda son contactos de Odoo (res.partner) ampliados
    mediante herencia, en lugar de un modelo nuevo. Así se aprovechan la
    libreta de direcciones, el chatter y la integración con el resto de Odoo."""
    _inherit = 'res.partner'

    es_cliente_gamestore = fields.Boolean(string='Cliente GameStore', default=False)
    gamestore_pedido_ids = fields.One2many('gamestore.pedido', 'cliente_id', string='Pedidos GameStore')
    gamestore_pedido_count = fields.Integer(string='Nº de pedidos', compute='_compute_gamestore_estadisticas')
    gamestore_currency_id = fields.Many2one(
        'res.currency', compute='_compute_gamestore_currency_id', string='Moneda GameStore',
    )
    gamestore_total_gastado = fields.Monetary(
        string='Total gastado', compute='_compute_gamestore_estadisticas',
        currency_field='gamestore_currency_id',
    )
    gamestore_ultima_compra = fields.Datetime(string='Última compra', compute='_compute_gamestore_estadisticas')
    gamestore_plataforma_favorita_id = fields.Many2one(
        'gamestore.plataforma', string='Plataforma favorita', compute='_compute_gamestore_estadisticas',
    )

    def _compute_gamestore_currency_id(self):
        for partner in self:
            partner.gamestore_currency_id = self.env.company.currency_id

    @api.depends('gamestore_pedido_ids.estado', 'gamestore_pedido_ids.total')
    def _compute_gamestore_estadisticas(self):
        for partner in self:
            pedidos = partner.gamestore_pedido_ids
            validos = pedidos.filtered(lambda p: p.estado in ESTADOS_VENTA)
            partner.gamestore_pedido_count = len(pedidos)
            partner.gamestore_total_gastado = sum(validos.mapped('total'))
            partner.gamestore_ultima_compra = max(validos.mapped('fecha')) if validos else False

            # Plataforma con más unidades compradas
            unidades = {}
            for linea in validos.linea_ids:
                plataforma = linea.videojuego_id.plataforma_id
                unidades[plataforma] = unidades.get(plataforma, 0) + linea.cantidad
            partner.gamestore_plataforma_favorita_id = (
                max(unidades, key=unidades.get) if unidades else False
            )

    def action_ver_pedidos_gamestore(self):
        """Smart button: historial de pedidos del cliente."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pedidos de %s', self.name),
            'res_model': 'gamestore.pedido',
            'view_mode': 'list,form',
            'domain': [('cliente_id', '=', self.id)],
            'context': {'default_cliente_id': self.id},
        }
