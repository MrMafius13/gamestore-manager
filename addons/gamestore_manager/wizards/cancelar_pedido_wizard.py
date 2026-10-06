# -*- coding: utf-8 -*-
from odoo import fields, models


class GamestoreCancelarPedidoWizard(models.TransientModel):
    """Asistente que obliga a indicar un motivo antes de cancelar pedidos."""
    _name = 'gamestore.cancelar.pedido.wizard'
    _description = 'Asistente para cancelar pedidos'

    pedido_ids = fields.Many2many('gamestore.pedido', string='Pedidos', required=True)
    motivo = fields.Text(string='Motivo', required=True)

    def action_confirmar(self):
        self.ensure_one()
        self.pedido_ids.cancelar_con_motivo(self.motivo)
        return {'type': 'ir.actions.act_window_close'}
