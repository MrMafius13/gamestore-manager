# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GamestorePedidoLinea(models.Model):
    _name = 'gamestore.pedido.linea'
    _description = 'Línea de pedido'
    _order = 'pedido_id, sequence, id'

    pedido_id = fields.Many2one(
        'gamestore.pedido', string='Pedido', required=True, ondelete='cascade', index=True,
    )
    sequence = fields.Integer(string='Secuencia', default=10)
    videojuego_id = fields.Many2one(
        'gamestore.videojuego', string='Videojuego', required=True, ondelete='restrict', index=True,
    )
    plataforma_id = fields.Many2one(related='videojuego_id.plataforma_id', string='Plataforma')
    stock_disponible = fields.Integer(related='videojuego_id.stock', string='Stock disponible')
    cantidad = fields.Integer(string='Cantidad', default=1, required=True)
    currency_id = fields.Many2one(related='pedido_id.currency_id', string='Moneda')
    precio_unitario = fields.Monetary(
        string='Precio unitario', compute='_compute_precio_unitario',
        store=True, readonly=False, precompute=True,
    )
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)
    cliente_id = fields.Many2one(related='pedido_id.cliente_id', string='Cliente')
    estado = fields.Selection(related='pedido_id.estado', string='Estado')

    _sql_constraints = [
        ('cantidad_positiva', 'CHECK(cantidad > 0)', 'La cantidad debe ser mayor que cero.'),
        ('precio_positivo', 'CHECK(precio_unitario >= 0)', 'El precio no puede ser negativo.'),
    ]

    @api.depends('videojuego_id')
    def _compute_precio_unitario(self):
        for linea in self:
            linea.precio_unitario = linea.videojuego_id.precio

    @api.depends('cantidad', 'precio_unitario')
    def _compute_subtotal(self):
        for linea in self:
            linea.subtotal = linea.cantidad * linea.precio_unitario
