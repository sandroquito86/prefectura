# -*- coding: utf-8 -*-

##############################################################################
#

#
##############################################################################
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import ascii_letters, digits, whitespace

class Catalogo(models.Model):
    _name = 'pf.tipo_discapacidad'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Tipo de Dispacidad'

    name = fields.Char(string="Nombre del Catalogo", required=True, tracking=True)
    descripcion = fields.Char(string="descripcion", required=True)
   
    _sql_constraints = [('name_unique', 'UNIQUE(name)', "Catálogo debe ser único"),]    

  
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            model_ids = record.search([('id', '!=',record.id)])        
            list_names = [x.name.upper() for x in model_ids if x.name]        
            if record.name.upper() in list_names:
                raise ValidationError("Tipo de discapacidad: %s , ya existe, no se permite valores duplicados" % (record.name.upper()))    
 