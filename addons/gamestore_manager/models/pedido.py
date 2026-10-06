# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError

ESTADOS = [
    ('borrador', 'Borrador'),
    ('confirmado', 'Confirmado'),
    ('pagado', 'Pagado'),
    ('entregado', 'Entregado'),
    ('cancelado', 'Cancelado'),
]


class GamestorePedido(models.Model):
    _name = 'gamestore.pedido'
    _description = 'Pedido'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, id desc'

    # Campos
    name = fields.Char(
        string='Referencia', required=True, copy=False, readonly=True, index=True, default='Nuevo',
    )
    cliente_id = fields.Many2one(
        'res.partner', string='Cliente', required=True, index=True, tracking=True,
    )
    vendedor_id = fields.Many2one(
        'res.users', string='Vendedor', index=True, tracking=True,
        default=lambda self: self.env.user,
    )
    fecha = fields.Datetime(string='Fecha', required=True, default=fields.Datetime.now, tracking=True)
    fecha_confirmacion = fields.Datetime(string='Fecha de confirmación', readonly=True, copy=False)
    linea_ids = fields.One2many('gamestore.pedido.linea', 'pedido_id', string='Líneas', copy=True)

    currency_id = fields.Many2one(
        'res.currency', string='Moneda', required=True,
        default=lambda self: self.env.company.currency_id,
    )
    total = fields.Monetary(string='Total', compute='_compute_totales', store=True, tracking=True)
    cantidad_total = fields.Integer(string='Unidades', compute='_compute_totales', store=True)

    estado = fields.Selection(
        ESTADOS, string='Estado', required=True, default='borrador',
        copy=False, tracking=True, index=True, group_expand='_group_expand_estado',
    )
    motivo_cancelacion = fields.Text(string='Motivo de cancelación', readonly=True, copy=False)
    notas = fields.Html(string='Notas')

    # Calculados
    @api.depends('linea_ids.subtotal', 'linea_ids.cantidad')
    def _compute_totales(self):
        for pedido in self:
            pedido.total = sum(pedido.linea_ids.mapped('subtotal'))
            pedido.cantidad_total = sum(pedido.linea_ids.mapped('cantidad'))

    @api.model
    def _group_expand_estado(self, estados, domain):
        """Muestra todas las columnas de estado en la vista kanban, aunque estén vacías."""
        return [clave for clave, _etiqueta in ESTADOS]

    # ORM
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('gamestore.pedido') or 'Nuevo'
        pedidos = super().create(vals_list)
        # Todo contacto que hace un pedido pasa a ser cliente de la tienda
        pedidos.cliente_id.filtered(lambda c: not c.es_cliente_gamestore).sudo().write(
            {'es_cliente_gamestore': True}
        )
        return pedidos

    @api.ondelete(at_uninstall=False)
    def _unlink_solo_borrador_o_cancelado(self):
        if any(pedido.estado not in ('borrador', 'cancelado') for pedido in self):
            raise UserError(_('Solo se pueden eliminar pedidos en borrador o cancelados.'))

    # Lógica de stock
    def _cantidades_por_videojuego(self):
        self.ensure_one()
        cantidades = defaultdict(int)
        for linea in self.linea_ids:
            cantidades[linea.videojuego_id] += linea.cantidad
        return cantidades

    def _comprobar_stock(self):
        self.ensure_one()
        faltantes = [
            _('• %(juego)s: solicitado %(pedido)s, disponible %(stock)s',
              juego=juego.display_name, pedido=cantidad, stock=juego.stock)
            for juego, cantidad in self._cantidades_por_videojuego().items()
            if cantidad > juego.stock
        ]
        if faltantes:
            raise UserError(
                _('No hay stock suficiente para confirmar %s:\n', self.name) + '\n'.join(faltantes)
            )

    def _mover_stock(self, signo):
        """signo = -1 descuenta stock (confirmar), +1 lo devuelve (cancelar).
        Se usa sudo() porque los dependientes no tienen permiso de escritura
        sobre el catálogo, pero sus pedidos sí deben actualizar el stock."""
        self.ensure_one()
        for juego, cantidad in self._cantidades_por_videojuego().items():
            juego.sudo().stock += signo * cantidad

    # Botones / flujo de estados
    def action_confirmar(self):
        for pedido in self:
            if pedido.estado != 'borrador':
                raise UserError(_('Solo se pueden confirmar pedidos en borrador.'))
            if not pedido.linea_ids:
                raise UserError(_('No puedes confirmar un pedido sin videojuegos.'))
            pedido._comprobar_stock()
            pedido._mover_stock(-1)
            pedido.write({'estado': 'confirmado', 'fecha_confirmacion': fields.Datetime.now()})
        return True

    def action_pagar(self):
        if any(pedido.estado != 'confirmado' for pedido in self):
            raise UserError(_('Solo se pueden marcar como pagados los pedidos confirmados.'))
        self.write({'estado': 'pagado'})
        return True

    def action_entregar(self):
        if any(pedido.estado != 'pagado' for pedido in self):
            raise UserError(_('Solo se pueden entregar pedidos pagados.'))
        self.write({'estado': 'entregado'})
        return True

    def action_cancelar(self):
        """Abre el asistente que solicita el motivo de cancelación."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cancelar pedido'),
            'res_model': 'gamestore.cancelar.pedido.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_pedido_ids': self.ids},
        }

    def cancelar_con_motivo(self, motivo):
        """Cancela los pedidos, devuelve el stock si ya se había descontado
        y deja constancia del motivo en el chatter."""
        for pedido in self:
            if pedido.estado == 'entregado':
                raise UserError(_('El pedido %s ya fue entregado y no se puede cancelar.', pedido.name))
            if pedido.estado == 'cancelado':
                continue
            if pedido.estado in ('confirmado', 'pagado'):
                pedido._mover_stock(+1)
            pedido.write({'estado': 'cancelado', 'motivo_cancelacion': motivo})
            pedido.message_post(body=_('Pedido cancelado. Motivo: %s', motivo))
        return True

    def action_borrador(self):
        if any(pedido.estado != 'cancelado' for pedido in self):
            raise UserError(_('Solo los pedidos cancelados pueden volver a borrador.'))
        self.write({'estado': 'borrador', 'motivo_cancelacion': False, 'fecha_confirmacion': False})
        return True

    def action_imprimir(self):
        return self.env.ref('gamestore_manager.action_report_pedido').report_action(self)
