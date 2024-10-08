# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from string import ascii_letters, digits
import string
import datetime


class AsignacionHorarios(models.Model):
    _name = 'mz.horarios.servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Asignación de Horarios' 
    _rec_name = 'servicio_id'

    @api.model
    def _get_tipo_servicios_domain(self):
        catalogo_id = self.env.ref('manzana_de_cuidados.tipo_servicio').id
        return [('catalogo_id', '=', catalogo_id)]
    
    servicio_id = fields.Many2one(string='Servicio', comodel_name='mz.items', ondelete='restrict',domain=_get_tipo_servicios_domain)   
    personal_id = fields.Many2one(string='Personal', comodel_name='mz.empleado', ondelete='restrict',)   
    domain_personal_id = fields.Char(string='Domain Personal',compute='_compute_author_domain_field')    
    detalle_horario_ids = fields.One2many(string='Detalle Horarios', comodel_name='mz.detalle.horarios', inverse_name='asignacion_horario_id',)
    
    
    

    _sql_constraints = [('name_unique', 'UNIQUE(servicio_id,personal_id)', "Ya existe una persona con este servicio.")]    

    @api.depends('servicio_id')
    def _compute_author_domain_field(self):
        for record in self:
            empleados = self.env['mz.asignacion.servicio'].search([('servicio_id', '=', record.servicio_id.id)]).mapped('personal_ids')
            if empleados:
                record.domain_personal_id = [('id', 'in', empleados.ids)]
            else:
                record.domain_personal_id = [('id', 'in', [])]


class DetalleHorarios(models.Model):
    _name = 'mz.detalle.horarios'
    _description = 'Detalle de Horarios'
    _order = 'fecha, horainicio ASC'    
                

    asignacion_horario_id = fields.Many2one(string='Cabecera', comodel_name='mz.horarios.servicio', ondelete='restrict',)
    fecha = fields.Date(string='Fecha', required=True, default=fields.Datetime.now, )
    horainicio = fields.Float(string='Hora Inicio')
    horafin = fields.Float(string='Hora Fin',)       
    hora = fields.Char(string='Hora')
    estado = fields.Boolean(default='True')    
    observacion = fields.Char(string='Observación')
    fecha_actualizacion = fields.Date(string='Fecha Actualiza', readonly=True, default=fields.Datetime.now, )
    dias = fields.Selection([('0', 'LUNES'), ('1', 'MARTES'), ('2', 'MIERCOLES'), ('3', 'JUEVES'), ('4', 'VIERNES'), 
                                                            ('5', 'SABADO'), ('6', 'DOMINGO')],string='Dia')
    property_valuation = fields.Selection([
        ('manual_periodic', 'Manual'),
        ('real_time', 'Automated')], string='Inventory Valuation',
        company_dependent=True, copy=True, required=True,
        help="""Manual: The accounting entries to value the inventory are not posted automatically.
        Automated: An accounting entry is automatically created to value the inventory when a product enters or leaves the company.
        """)
    duracionconsulta = fields.Float(string='Duración del Servicio')

    _sql_constraints = [('name_unique', 'UNIQUE(asignacion_horario_id,dias)', "No se permiten días repetidos.")]    
    
   