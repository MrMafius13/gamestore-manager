# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GamestorePlataforma(models.Model):
    _name = 'gamestore.plataforma'
    _description = 'Plataforma'
    _order = 'sequence, name'

    name = fields.Char(string='Nombre', required=True)
    fabricante = fields.Char(string='Fabricante')
    sequence = fields.Integer(string='Secuencia', default=10)
    color = fields.Integer(string='Color')
    active = fields.Boolean(string='Activa', default=True)
    videojuego_ids = fields.One2many('gamestore.videojuego', 'plataforma_id', string='Videojuegos')
    videojuego_count = fields.Integer(string='Nº de videojuegos', compute='_compute_videojuego_count')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Ya existe una plataforma con ese nombre.'),
    ]

    @api.depends('videojuego_ids')
    def _compute_videojuego_count(self):
        for plataforma in self:
            plataforma.videojuego_count = len(plataforma.videojuego_ids)


class GamestoreGenero(models.Model):
    _name = 'gamestore.genero'
    _description = 'Género'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    color = fields.Integer(string='Color')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Ya existe un género con ese nombre.'),
    ]


class GamestoreDesarrolladora(models.Model):
    _name = 'gamestore.desarrolladora'
    _description = 'Desarrolladora'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    logo = fields.Image(string='Logo', max_width=256, max_height=256)
    pais_id = fields.Many2one('res.country', string='País')
    sitio_web = fields.Char(string='Sitio web')
    active = fields.Boolean(string='Activa', default=True)
    videojuego_ids = fields.One2many('gamestore.videojuego', 'desarrolladora_id', string='Videojuegos')
    videojuego_count = fields.Integer(string='Nº de videojuegos', compute='_compute_videojuego_count')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Ya existe una desarrolladora con ese nombre.'),
    ]

    @api.depends('videojuego_ids')
    def _compute_videojuego_count(self):
        for desarrolladora in self:
            desarrolladora.videojuego_count = len(desarrolladora.videojuego_ids)

    def action_ver_videojuegos(self):
        """Smart button: abre los videojuegos de esta desarrolladora."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Videojuegos de {self.name}',
            'res_model': 'gamestore.videojuego',
            'view_mode': 'kanban,list,form',
            'domain': [('desarrolladora_id', '=', self.id)],
            'context': {'default_desarrolladora_id': self.id},
        }
