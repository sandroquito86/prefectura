# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api

class Asistencia(models.Model):
    _name = 'mz.asistencia'
    _description = 'Asistencia al Servicio/Curso'

    servicio_id = fields.Many2one('mz.servicio', string='Servicio/Curso', ondelete='cascade', required=True)
    beneficiario_id = fields.Many2one('mz.beneficiario', string='Beneficiario', ondelete='cascade', required=True)
    fecha = fields.Date(string='Fecha', required=True, default=fields.Date.today)
    asistio = fields.Boolean(string='Asistió', default=False)