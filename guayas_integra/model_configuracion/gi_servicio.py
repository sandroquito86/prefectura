# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from string import ascii_letters, digits
import string


class Servicios(models.Model):
    _name = 'gi.servicio'
    _description = 'Servicios'
    _order = 'name ASC'
    
    name = fields.Char(string='Servicio', required=True)    
    area_id = fields.Many2one(string='Área', comodel_name='gi.area', ondelete='restrict')
    

