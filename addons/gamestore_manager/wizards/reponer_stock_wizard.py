# -*- coding: utf-8 -*-
from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class GamestoreReponerStockWizard(models.TransientModel):
    """Asistente (wizard) para reponer el stock de varios videojuegos a la vez.

    Los TransientModel guardan datos temporales que Odoo limpia automáticamente;
    son la base de los asistentes en ventana emergente.
    """
    _name = 'gamestore.reponer.stock.wizard'
    _description = 'Asistente para reponer stock'

    linea_ids = fields.One2many('gamestore.reponer.stock.wizard.linea', 'wizard_id', string='Videojuegos')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        contexto = self.env.context
        Videojuego = self.env['gamestore.videojuego']
        if contexto.get('active_model') == 'gamestore.videojuego' and contexto.get('active_ids'):
            juegos = Videojuego.browse(contexto['active_ids'])
        else:
            # Abierto desde el menú: proponer los juegos con stock bajo o agotados
            juegos = Videojuego.search([('estado_stock', 'in', ('agotado', 'bajo'))])
        res['linea_ids'] = [
            Command.create({
                'videojuego_id': juego.id,
                # Sugerencia: llegar al doble del stock mínimo
                'cantidad': max(juego.stock_minimo * 2 - juego.stock, 1),
            })
            for juego in juegos
        ]
        return res

    def action_reponer(self):
        self.ensure_one()
        lineas = self.linea_ids.filtered(lambda l: l.cantidad > 0)
        if not lineas:
            raise UserError(_('Indica al menos una cantidad mayor que cero.'))
        for linea in lineas:
            juego = linea.videojuego_id
            juego.stock += linea.cantidad
            juego.message_post(body=_('Stock repuesto: +%(cantidad)s unidades (total: %(total)s).',
                                      cantidad=linea.cantidad, total=juego.stock))
            # Cerrar alertas de reposición pendientes
            juego.activity_ids.filtered(lambda a: a.summary == _('Reponer stock')).action_done()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Stock actualizado'),
                'message': _('Se ha repuesto el stock de %s videojuego(s).', len(lineas)),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }


class GamestoreReponerStockWizardLinea(models.TransientModel):
    _name = 'gamestore.reponer.stock.wizard.linea'
    _description = 'Línea del asistente de reposición'

    wizard_id = fields.Many2one('gamestore.reponer.stock.wizard', required=True, ondelete='cascade')
    videojuego_id = fields.Many2one('gamestore.videojuego', string='Videojuego', required=True)
    stock_actual = fields.Integer(related='videojuego_id.stock', string='Stock actual')
    stock_minimo = fields.Integer(related='videojuego_id.stock_minimo', string='Stock mínimo')
    cantidad = fields.Integer(string='Unidades a añadir', default=1)
