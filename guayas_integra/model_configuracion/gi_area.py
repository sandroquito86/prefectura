# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from string import ascii_letters, digits
import string


class Area(models.Model):
    _name = 'gi.area'
    _description = 'Areas' 

    
    name = fields.Char(string='Nombre', required=True)
    

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', "El área debe ser único.")
    ]    

    @api.constrains('name')
    def _check_name_marca_insensitive(self):
        for record in self:
            model_ids = record.search([('id', '!=',record.id)])        
            list_names = [x.name.upper() for x in model_ids if x.name]        
            if record.name.upper() in list_names:
                raise ValidationError("Ya existe el Área: %s , no se permiten valores duplicados" % (record.name.upper())) 
    