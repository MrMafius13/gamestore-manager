# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

ESTADOS_VENTA = ('confirmado', 'pagado', 'entregado')


class GamestoreVideojuego(models.Model):
    _name = 'gamestore.videojuego'
    _description = 'Videojuego'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'


    # Campos
    name = fields.Char(string='Nombre', required=True, tracking=True)
    portada = fields.Image(string='Portada', max_width=512, max_height=512)
    plataforma_id = fields.Many2one(
        'gamestore.plataforma', string='Plataforma',
        required=True, ondelete='restrict', index=True, tracking=True,
    )
    genero_ids = fields.Many2many('gamestore.genero', string='Géneros')
    desarrolladora_id = fields.Many2one(
        'gamestore.desarrolladora', string='Desarrolladora',
        ondelete='restrict', index=True, tracking=True,
    )
    fecha_lanzamiento = fields.Date(string='Fecha de lanzamiento')
    pegi = fields.Selection(
        [('3', 'PEGI 3'), ('7', 'PEGI 7'), ('12', 'PEGI 12'), ('16', 'PEGI 16'), ('18', 'PEGI 18')],
        string='Clasificación PEGI',
    )
    descripcion = fields.Html(string='Descripción')
    active = fields.Boolean(string='Activo', default=True)

    currency_id = fields.Many2one(
        'res.currency', string='Moneda', required=True,
        default=lambda self: self.env.company.currency_id,
    )
    precio = fields.Monetary(string='Precio', currency_field='currency_id', tracking=True)
    stock = fields.Integer(string='Stock', default=0, tracking=True)
    stock_minimo = fields.Integer(
        string='Stock mínimo', default=5,
        help='Por debajo de este valor se genera una alerta de reposición.',
    )
    estado_stock = fields.Selection(
        [('agotado', 'Agotado'), ('bajo', 'Stock bajo'), ('disponible', 'Disponible')],
        string='Estado del stock', compute='_compute_estado_stock', store=True,
    )

    linea_pedido_ids = fields.One2many('gamestore.pedido.linea', 'videojuego_id', string='Líneas de pedido')
    unidades_vendidas = fields.Integer(
        string='Unidades vendidas', compute='_compute_ventas', store=True,
    )
    importe_vendido = fields.Monetary(
        string='Importe vendido', compute='_compute_ventas', store=True, currency_field='currency_id',
    )

    _sql_constraints = [
        ('precio_positivo', 'CHECK(precio >= 0)', 'El precio no puede ser negativo.'),
        ('stock_positivo', 'CHECK(stock >= 0)', 'El stock no puede ser negativo.'),
        ('stock_minimo_positivo', 'CHECK(stock_minimo >= 0)', 'El stock mínimo no puede ser negativo.'),
        ('nombre_plataforma_uniq', 'unique(name, plataforma_id)',
         'Este videojuego ya existe para esa plataforma.'),
    ]

    # Campos calculados
    @api.depends('stock', 'stock_minimo')
    def _compute_estado_stock(self):
        for juego in self:
            if juego.stock <= 0:
                juego.estado_stock = 'agotado'
            elif juego.stock <= juego.stock_minimo:
                juego.estado_stock = 'bajo'
            else:
                juego.estado_stock = 'disponible'

    @api.depends('linea_pedido_ids.cantidad', 'linea_pedido_ids.subtotal', 'linea_pedido_ids.pedido_id.estado')
    def _compute_ventas(self):
        for juego in self:
            lineas = juego.linea_pedido_ids.filtered(lambda l: l.pedido_id.estado in ESTADOS_VENTA)
            juego.unidades_vendidas = sum(lineas.mapped('cantidad'))
            juego.importe_vendido = sum(lineas.mapped('subtotal'))

    def _compute_display_name(self):
        """Muestra 'Nombre (Plataforma)' en los desplegables."""
        for juego in self:
            if juego.plataforma_id:
                juego.display_name = f'{juego.name} ({juego.plataforma_id.name})'
            else:
                juego.display_name = juego.name

    # Acciones
    def action_ver_pedidos(self):
        """Smart button: pedidos que incluyen este videojuego."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pedidos de %s', self.display_name),
            'res_model': 'gamestore.pedido',
            'view_mode': 'list,form',
            'domain': [('linea_ids.videojuego_id', '=', self.id)],
        }

    def action_reponer_stock(self):
        """Abre el asistente de reposición con los videojuegos seleccionados."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reponer stock'),
            'res_model': 'gamestore.reponer.stock.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_model': self._name, 'active_ids': self.ids},
        }

    # Automatizaciones (cron)
    @api.model
    def _cron_alerta_stock_bajo(self):
        """Tarea programada: crea una actividad para los encargados por cada
        videojuego con stock bajo o agotado que aún no tenga una alerta abierta."""
        grupo = self.env.ref('gamestore_manager.group_gamestore_encargado', raise_if_not_found=False)
        responsable = (grupo and grupo.users.filtered(lambda u: not u.share)[:1]) or self.env.ref('base.user_admin')
        tipo_actividad = self.env.ref('mail.mail_activity_data_todo')

        juegos = self.search([('estado_stock', 'in', ('agotado', 'bajo'))])
        for juego in juegos:
            ya_avisado = juego.activity_ids.filtered(
                lambda a: a.activity_type_id == tipo_actividad and a.summary == _('Reponer stock')
            )
            if ya_avisado:
                continue
            juego.activity_schedule(
                activity_type_id=tipo_actividad.id,
                summary=_('Reponer stock'),
                note=_('Quedan %(stock)s unidades (mínimo: %(minimo)s).',
                       stock=juego.stock, minimo=juego.stock_minimo),
                user_id=responsable.id,
            )
        return len(juegos)
