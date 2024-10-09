from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class PfEmployee(models.Model):
    _inherit = 'hr.employee'

    if_autoridad = fields.Boolean(string='Es Autoridad', default=False)
    
    # Name fields
    nombre = fields.Char(string="Nombre", compute="_compute_name", store=True, readonly=True)
    apellido_paterno = fields.Char(string='Apellido Paterno')
    apellido_materno = fields.Char(string='Apellido Materno')
    primer_nombre = fields.Char(string='Primer Nombre')
    segundo_nombre = fields.Char(string='Segundo Nombre')
    
    # Other fields
    service_ids = fields.Many2many('gi.servicio', string="Servicios Asignados")
    edad = fields.Char(string="Edad", compute="_compute_edad", store=True)
    provincia_id = fields.Many2one("res.country.state", string="Provincia", domain="[('country_id', '=?', country_id)]")
    sucursal_id = fields.Many2one('pf.sucursal', string='Sucursal', required=True)
    modulo_ids = fields.Many2many(
        'pf.modulo', 
        string="Módulos",
        help="Selecciona los módulos a los que pertenece este beneficiario"
    )

    @api.depends('birthday')
    def _compute_edad(self):
        for record in self:
            if record.birthday:
                hoy = date.today()
                diferencia = relativedelta(hoy, record.birthday)
                record.edad = f"{diferencia.years} años, {diferencia.months} meses, {diferencia.days} días"
            else:
                record.edad = "Sin fecha de nacimiento"

    @api.model
    def create(self, vals):
        # Compute the full name before creating the record
        full_name = self._get_full_name(vals)
        vals['nombre'] = full_name
        
        # Also set the name for the resource
        if 'name' not in vals:
            vals['name'] = full_name
        
        return super(PfEmployee, self).create(vals)

    def write(self, vals):
        name_fields = ['apellido_paterno', 'apellido_materno', 'primer_nombre', 'segundo_nombre']
        
        if any(field in vals for field in name_fields):
            # Create a temporary dictionary with updated values
            temp_vals = dict(self.read(['apellido_paterno', 'apellido_materno', 'primer_nombre', 'segundo_nombre'])[0])
            temp_vals.update({k: vals[k] for k in name_fields if k in vals})
            
            # Compute the new full name
            full_name = self._get_full_name(temp_vals)
            vals['nombre'] = full_name
            vals['name'] = full_name  # This will update the related resource name
        
        return super(PfEmployee, self).write(vals)

    def _get_full_name(self, record):
        """
        Construye el nombre completo basado en los campos individuales.
        Retorna una cadena vacía si no hay datos.
        """
        if isinstance(record, dict):
            nombres = filter(None, [
                record.get('apellido_paterno', ''),
                record.get('apellido_materno', ''),
                record.get('primer_nombre', ''),
                record.get('segundo_nombre', '')
            ])
        else:
            nombres = filter(None, [
                record.apellido_paterno,
                record.apellido_materno,
                record.primer_nombre,
                record.segundo_nombre
            ])
        return " ".join(nombres) or "Sin nombre"

    @api.depends('apellido_paterno', 'apellido_materno', 'primer_nombre', 'segundo_nombre')
    def _compute_name(self):
        for record in self:
            full_name = self._get_full_name(record)
            record.nombre = full_name
            record.name = full_name  # This updates the name in hr.employee
            if record.resource_id:
                record.resource_id.name = full_name  # This updates the name in resource.resource

    @api.constrains('nombre', 'apellido_paterno', 'apellido_materno', 'primer_nombre', 'segundo_nombre')
    def _check_name_not_empty(self):
        for record in self:
            if not record.nombre:
                raise ValidationError("El nombre no puede estar vacío. Por favor, proporcione al menos un nombre o apellido.")