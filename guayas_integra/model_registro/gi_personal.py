from odoo import models, fields, api
from random import randint
from datetime import date
from dateutil.relativedelta import relativedelta


class ServiceStaff(models.Model):
    _name = 'gi.personal'
    _description = 'Personal encargado de brindar servicios'
    _inherits = {'hr.employee': 'employee_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string="Empleado", required=True, ondelete="cascade")    
    nombre = fields.Char(string="Nombre del Beneficiario", compute="_compute_name", store=True)
    apellido_paterno = fields.Char(string='Apellido Paterno')
    apellido_materno = fields.Char(string='Apellido Materno')
    primer_nombre = fields.Char(string='Primer Nombre')
    segundo_nombre = fields.Char(string='Segundo Nombre')  
    service_ids = fields.Many2many('gi.servicio', string="Servicios Asignados")
    edad = fields.Char(string="Edad", compute="_compute_edad", store=True)
    provincia_id = fields.Many2one("res.country.state", string="Provincia", domain="[('country_id', '=?', country_id)]")


    @api.depends('birthday')
    def _compute_edad(self):
        for record in self:
            if record.birthday:
                hoy = date.today()
                diferencia = relativedelta(hoy, record.birthday)
                record.edad = f"{diferencia.years} años, {diferencia.months} meses, {diferencia.days} días"
            else:
                record.edad = "Sin fecha de nacimiento"

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
            record.nombre = " ".join(nombres) if nombres else "Nombre del Beneficiario"
            record.name = record.nombre


    @api.model
    def create(self, vals):
        # Crear el empleado solo si no se proporciona
        if 'employee_id' not in vals:
            employee_vals = {
                'name': vals.get('nombre'),  # Asegúrate de que este campo esté disponible en vals
                # Aquí no es necesario incluir job_id ni department_id ya que se heredan
                # Agrega aquí otros campos necesarios para crear el empleado si es necesario
            }
            employee = self.env['hr.employee'].create(employee_vals)
            vals['employee_id'] = employee.id  # Asocia el nuevo empleado al registro de gi.personal

        return super(ServiceStaff, self).create(vals)