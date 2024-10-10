from odoo import models, fields, api
from random import randint
from datetime import date
from dateutil.relativedelta import relativedelta


class Beneficiarios(models.Model):
    _name = 'pf.beneficiario'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Beneficiarios'

    
    name = fields.Char(string="Nombre del Beneficiario", compute="_compute_name", store=True, default="Nombre del Beneficiario")
    image = fields.Image(string="Imagen del Beneficio")  # Campo para la imagen
    category_ids = fields.Many2many('pf.categoria_beneficario', 'gi_beneficiario_categoria_rel', 'beneficiario_id', 'categoria_id', 
                                    string='Categorías')  
    apellido_paterno = fields.Char(string='Apellido Paterno')
    apellido_materno = fields.Char(string='Apellido Materno')
    primer_nombre = fields.Char(string='Primer Nombre')
    segundo_nombre = fields.Char(string='Segundo Nombre')   
    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento") 
    edad = fields.Char(string="Edad", compute="_compute_edad", store=True)
    cedula = fields.Char(string='Cédula de Identidad') 
    pais_id = fields.Many2one('res.country', string='Pais', ondelete='restrict')
    provincia_id = fields.Many2one("res.country.state", string='Provincia', ondelete='restrict', 
                                   domain="[('country_id', '=?', pais_id)]")
    user_id = fields.Many2one('res.users', string="Usuario", help="Usuario asociado para acceder al sistema")
    modulo_ids = fields.Many2many(
        'pf.modulo', 
        string="Módulos",
        help="Selecciona los módulos a los que pertenece este beneficiario"
    )
    programa_ids = fields.Many2many('pf.programas', string='Programas',)
    
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
    

class CategoriaBeneficiario(models.Model):

    _name = "pf.categoria_beneficario"
    _description = "Categoría de Beneficiario"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Nombre Categoría", required=True)
    color = fields.Integer(string='Color', default=_get_default_color)
   
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


