from odoo.exceptions import ValidationError
from odoo import models, fields, api
import re
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.addons.prefectura_base import utils

class MzSolicitudBeneficiario(models.Model):
    _name = 'mz.solicitud.beneficiario'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Solicitud de Beneficiario'

    name = fields.Char(string='Nombre',  tracking=True, compute='_compute_name', store=True)
    apellido_paterno = fields.Char(string='Apellido Paterno', required=True, tracking=True)
    apellido_materno = fields.Char(string='Apellido Materno', required=True, tracking=True)
    primer_nombre = fields.Char(string='Primer Nombre', required=True, tracking=True)
    segundo_nombre = fields.Char(string='Segundo Nombre', tracking=True)
    edad = fields.Char(string="Edad", compute="_compute_edad")
    tipo_documento = fields.Selection([
        ('dni', 'DNI'),
        ('pasaporte', 'Pasaporte'),
        ('carnet_extranjeria', 'Carnet de Extranjería')
    ], string='Tipo de Documento', required=True, tracking=True)
    numero_documento = fields.Char(string='Número de Documento', required=True, tracking=True)
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento', required=True, tracking=True)
    direccion = fields.Char(string='Dirección')
    pais_id = fields.Many2one('res.country', string='Pais', ondelete='restrict')
    provincia_id = fields.Many2one("res.country.state", string='Provincia', ondelete='restrict', 
                                   domain="[('country_id', '=?', pais_id)]")
    ciudad_id = fields.Many2one('res.country.ciudad', string='Ciudad' , ondelete='restrict', 
                                   domain="[('state_id', '=?', provincia_id)]")
    telefono = fields.Char(string='Teléfono', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'Enviado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado')
    ], string='Estado', default='draft', required=True)

    programa_id = fields.Many2one('pf.programas', string='Programa', required=True)

    @api.depends('apellido_paterno', 'apellido_materno', 'primer_nombre', 'segundo_nombre')
    def _compute_name(self):
        for record in self:
            # Filtrar campos que no están vacíos y unirlos con un espacio
            nombres = filter(None, [
                record.apellido_paterno,
                record.apellido_materno,
                record.primer_nombre,
                record.segundo_nombre
            ])
            # Unir los nombres filtrados en una sola cadena
            record.name = " ".join(nombres) if nombres else "Nombre del Beneficiario"

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        for record in self:
            if record.fecha_nacimiento:
                hoy = date.today()
                diferencia = relativedelta(hoy, record.fecha_nacimiento)
                record.edad = f"{diferencia.years} años, {diferencia.months} meses, {diferencia.days} días"
            else:
                record.edad = "Sin fecha de nacimiento"

    @api.onchange('tipo_documento', 'numero_documento')
    def _onchange_documento(self):
        if self.tipo_documento == 'dni' and self.numero_documento:
            if not utils.validar_cedula(self.numero_documento):
                return {'warning': {
                    'title': "Cédula Inválida",
                    'message': "El número de cédula ingresado no es válido."
                }}
            
    def action_submit(self):
        self.state = 'submitted'


    def action_approve(self):
        self.state = 'approved'
        beneficiario = self.env['mz.beneficiario'].create({
            'name': self.name,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'primer_nombre': self.primer_nombre,
            'segundo_nombre': self.segundo_nombre,
            'tipo_documento': self.tipo_documento,
            'numero_documento': self.numero_documento,
            'fecha_nacimiento': self.fecha_nacimiento,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'programa_id' : self.programa_id.id,
            'pais_id': self.pais_id.id,
            'provincia_id': self.provincia_id.id,
            'ciudad_id': self.ciudad_id.id
        })
        beneficiario.crear_user()


    def action_reject(self):
        self.state = 'rejected'

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
    def _validar_email(self, email):
        """
        Validate the email format using a regular expression.
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None