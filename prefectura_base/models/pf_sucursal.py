from odoo import models, fields, api

class Sucursal(models.Model):
    _name = 'pf.sucursal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sucursal'

    name = fields.Char(string='Nombre', required=True)
    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle 2')
    zip = fields.Char(string='Código Postal')
    city = fields.Char(string='Ciudad')
    pais_id = fields.Many2one('res.country', string='Pais', ondelete='restrict')
    provincia_id = fields.Many2one("res.country.state", string='Provincia', ondelete='restrict', 
                                   domain="[('country_id', '=?', pais_id)]")
    email = fields.Char(string='Email')
    phone = fields.Char(string='Teléfono')
    mobile = fields.Char(string='Móvil')
    website = fields.Char(string='Sitio Web')
    
    image = fields.Binary(string='Imagen', attachment=True)
    
    active = fields.Boolean(default=True, string='Activo')
    modulo_ids = fields.Many2many(
        'pf.modulo', 
        string="Módulos",
        help="Selecciona los módulos a los que pertenece este beneficiario"
    )
    programas_ids = fields.One2many(
        'pf.programas',
        'sucursal_id',
        string='Programas'
    )
    @api.model
    def create(self, vals):
        # Aquí puedes agregar lógica adicional antes de crear la sucursal
        return super(Sucursal, self).create(vals)
    
    def write(self, vals):
        # Aquí puedes agregar lógica adicional antes de actualizar la sucursal
        return super(Sucursal, self).write(vals)
    
class PfProgramas(models.Model):
    _name = 'pf.programas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Programas'

    name = fields.Char(string='Nombre', required=True)
    sucursal_id = fields.Many2one('pf.sucursal', string='Sucursal', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Teléfono')
    mobile = fields.Char(string='Móvil')
    
    image = fields.Binary(string='Imagen', attachment=True)
    
    active = fields.Boolean(default=True, string='Activo')
    modulo_id = fields.Many2one(
        'pf.modulo', 
        string="Proceso",
        help="Selecciona el Programa al que pertenece"
    )
    
    image_128 = fields.Image(string='Imagen', max_width=128, max_height=128)
    @api.onchange('sucursal_id')
    def _onchange_sucursal_id(self):
        if self.env.context.get('default_modulo_id'):
            self.modulo_id = self.env.context['default_modulo_id']

    
    
    
    
    
    @api.model
    def create(self, vals):
        # Aquí puedes agregar lógica adicional antes de crear la sucursal
        return super(PfProgramas, self).create(vals)
    
    def write(self, vals):
        # Aquí puedes agregar lógica adicional antes de actualizar la sucursal
        return super(PfProgramas, self).write(vals)