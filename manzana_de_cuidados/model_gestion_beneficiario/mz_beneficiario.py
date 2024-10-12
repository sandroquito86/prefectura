# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api
import re
from .. import utils

class Beneficiario(models.Model):
    _name = 'mz.beneficiario'
    _description = 'beneficiario que solicitan servicios'
    _inherits = {'pf.beneficiario': 'beneficiario_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']

    beneficiario_id = fields.Many2one('pf.beneficiario', string="Beneficiario", required=True, ondelete="cascade")
    dependientes_ids = fields.One2many('mz.dependiente', 'beneficiario_id', string='Dependientes')
    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    programa_id = fields.Many2one('pf.programas', string='Programa', required=True)
    

    

    @api.onchange('email')
    def _onchange_email(self):
        """
        Validate the email format.
        """
        if self.email and not self._validar_email(self.email):
            return {
                'warning': {
                    'title': "Correo Electrónico Inválido",
                    'message': "El correo electrónico ingresado no es válido."
                }
            }
        
    @api.onchange('tipo_documento', 'numero_documento')
    def _onchange_documento(self):
        if self.tipo_documento == 'dni' and self.numero_documento:
            if not utils.validar_cedula(self.numero_documento):
                return {'warning': {
                    'title': "Cédula Inválida",
                    'message': "El número de cédula ingresado no es válido."
                }}

    
    

    def _validar_email(self, email):
        """
        Validate the email format using a regular expression.
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    @api.constrains('numero_documento', 'tipo_documento')
    def _check_documento(self):
        for record in self:
            if record.tipo_documento == 'dni':
                if not utils.validar_cedula(record.numero_documento):
                    raise ValidationError("El número de cédula ingresado no es válido.")
                
    @api.model
    def create(self, vals):
        # Buscar si ya existe un beneficiario con el mismo número de documento
        numero_documento = vals.get('numero_documento')
        tipo_documento = vals.get('tipo_documento')
        
        if numero_documento and tipo_documento:
            existing_beneficiario = self.env['pf.beneficiario'].search([
                ('numero_documento', '=', numero_documento),
                ('tipo_documento', '=', tipo_documento)
            ], limit=1)
            
            if existing_beneficiario:
                # Si existe, usamos ese beneficiario en lugar de crear uno nuevo
                vals['beneficiario_id'] = existing_beneficiario.id
                # Actualizamos los campos del beneficiario existente
                existing_beneficiario.write({'programa_ids': [(4, vals['programa_id'])]})
            else:
                # Si no existe, creamos un nuevo beneficiario
                new_beneficiario = self.env['pf.beneficiario'].create({
                    k: v for k, v in vals.items() if k in self.env['pf.beneficiario']._fields
                })
                new_beneficiario.write({'programa_ids': [(4, vals['programa_id'])]})
                vals['beneficiario_id'] = new_beneficiario.id

        return super(Beneficiario, self).create(vals)

    @api.constrains('numero_documento', 'tipo_documento')
    def _check_unique_documento(self):
        for record in self:
            existing = self.search([
                ('numero_documento', '=', record.numero_documento),
                ('tipo_documento', '=', record.tipo_documento),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError("Ya existe un beneficiario con este número y tipo de documento.")
    

    def crear_user(self):
        user_vals = {
            'name': self.name,
            'login': self.email,
            'email': self.email,
            'company_id': self.company_id.id,
            'company_ids': [(4, self.company_id.id)],
            'password': self.numero_documento,
            # 'groups_id': [(6, 0, [self.env.ref('prefectura_base.group_portal').id])]
        }
        user = self.env['res.users'].create(user_vals)
        self.user_id = user.id
    

    

    