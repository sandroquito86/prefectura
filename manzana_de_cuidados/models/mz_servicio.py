# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api

class Servicio(models.Model):
    _name = 'mz.servicio'
    _description = 'Solicitudesde Beneficiarios'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nombre del Servicio/Curso', required=True, tracking=True)
    descripcion = fields.Text(string='Descripción', tracking=True)
    capacidad = fields.Integer(string='Capacidad Operativa', required=True, tracking=True)
    horario_ids = fields.One2many('mz.horario', 'servicio_id', string='Horarios')
    asistencias_ids = fields.One2many('mz.asistencia', 'servicio_id', string='Asistencias')

    