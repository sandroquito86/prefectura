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
    tipo_documento = fields.Selection([
        ('dni', 'DNI'),
        ('pasaporte', 'Pasaporte'),
        ('carnet_extranjeria', 'Carnet de Extranjería')
    ], string='Tipo de Documento', required=True, tracking=True)
    numero_documento = fields.Char(string='Número de Documento', required=True, tracking=True)
    direccion = fields.Char(string='Dirección', tracking=True)
    telefono = fields.Char(string='Teléfono', tracking=True)
    email = fields.Char(string='Correo Electrónico', tracking=True)
    dependientes_ids = fields.One2many('mz.dependiente', 'beneficiario_id', string='Dependientes')
    aprobado = fields.Boolean(string='Aprobado', default=False, tracking=True)
    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    programa_id = fields.Many2one('mz.programa', string='Programa', required=True)
    
    
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('por_aprobar', 'Por Aprobar'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada')
    ], string='Estado', default='borrador', required=True)

    @api.onchange('cedula', 'tipo_documento', 'fecha_nacimiento')
    def _onchange_cedula(self):
        if self.numero_documento:
            self.cedula = self.numero_documento

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
                
    # @api.model
    # def create(self, vals):
    #     # Crear el beneficiario normalmente
    #     beneficiario = super(Beneficiario, self).create(vals)

    #     # Verificar si el usuario ya está creado, si no lo está, crear uno nuevo
    #     if not beneficiario.user_id:
    #         # Crear el usuario en el sistema
    #         user_vals = {
    #             'name': beneficiario.name,
    #             'login': beneficiario.email,
    #             'email': beneficiario.email,
    #             'company_id': beneficiario.company_id.id,
    #             'company_ids': [(4, beneficiario.company_id.id)],
    #             # al crear el usuario debes asignarle los grupos bases  que por defecto debe tener el beneficiario 
    #             # 'groups_id': [(6, 0, [self.env.ref('module_name.group_portal').id])]  # Asignar el grupo adecuado, como eLearning portal
    #         }
    #         user = self.env['res.users'].create(user_vals)
    #         beneficiario.user_id = user.id

        # return beneficiario
    
    def action_por_aprobar(self):
        self.state = 'por_aprobar'

    def action_aprobada(self):
        user_vals = {
            'name': self.name,
            'login': self.email,
            'email': self.email,
            'company_id': self.company_id.id,
            'company_ids': [(4, self.company_id.id)],
            'password': self.cedula,
            # 'groups_id': [(6, 0, [self.env.ref('prefectura_base.group_portal').id])]
        }
        user = self.env['res.users'].create(user_vals)
        self.user_id = user.id
        self.state = 'aprobada'
    
    def action_rechazada(self):
        self.state = 'rechazada'
    

    