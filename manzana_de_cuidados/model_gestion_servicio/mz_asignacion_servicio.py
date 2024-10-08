# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from string import ascii_letters, digits
import string


class AsignarServicio(models.Model):
    _name = 'mz.asignacion.servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Asignación de Servicios' 
    _rec_name = 'servicio_id'

    @api.model
    def _get_tipo_servicios_domain(self):
        catalogo_id = self.env.ref('manzana_de_cuidados.tipo_servicio').id
        return [('catalogo_id', '=', catalogo_id)]
    
    servicio_id = fields.Many2one(string='Servicio', comodel_name='mz.items', ondelete='restrict',domain=_get_tipo_servicios_domain)     
    personal_ids = fields.Many2many(string='Empleados Responsables', comodel_name='mz.empleado', relation='mz_asignacion_servicio_items_empleado_rel', 
                                      column1='asignacion_servicio_id', column2='empleado_id')
    
    # servicio_domain_id = fields.Char(string='Domain Servicios',compute='_compute_author_domain_field')
    

    _sql_constraints = [('name_unique', 'UNIQUE(servicio_id)', "El servicio no puede estar duplicado.")]  

    programa_id = fields.Many2one('pf.programas', string='Programa', required=True, tracking=True)

    domain_programa_id = fields.Char(string='Domain Programa',compute='_compute_domain_programas')

    @api.depends('servicio_id')
    def _compute_domain_programas(self):
        for record in self:
            programas = self.env['pf.programas'].search([('modulo_id', '=', self.env.ref('prefectura_base.modulo_2').id)]).mapped('modulo_id')
            if programas:
                record.domain_programa_id = [('id', 'in', programas.ids)]
            else:
                record.domain_programa_id = [('id', 'in', [])]

class Pf_programas(models.Model):
    _inherit = 'pf.programas'
    _description = 'Programas'

    servicio_ids = fields.One2many('mz.asignacion.servicio', 'programa_id', string='Servicios')
    model_count_mz = fields.Integer(compute="_compute_model_count_mz", string="", store=True)

    @api.depends('servicio_ids')
    def _compute_model_count_mz(self):
        model_data = self.env['mz.asignacion.servicio']._read_group([
            ('programa_id', 'in', self.ids),
        ], ['programa_id'], ['__count'])
        models_brand = {brand.id: count for brand, count in model_data}
        for record in self:
            record.model_count_mz = models_brand.get(record.id, 0)

    def action_brand_model(self):
        self.ensure_one()
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'mz.asignacion.servicio',
            'name': 'Servicios',
            'context': {'search_default_programa_id': self.id, 'default_programa_id': self.id}
        }

        return view



   