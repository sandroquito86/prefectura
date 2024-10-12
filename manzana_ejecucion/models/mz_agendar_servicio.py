# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AgendarServicio(models.Model):
    _name = 'mz.agendar_servicio'
    _description = 'Agendar Servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    
    modulo_id = fields.Many2one(string='Módulo', comodel_name='pf.modulo', ondelete='restrict',
                                default=lambda self: self.env.ref('prefectura_base.modulo_2').id,tracking=True)
    beneficiario_id_domain = fields.Char(compute="_compute_beneficiario_id_domain", readonly=True, store=False, )
    beneficiario_id = fields.Many2one(string='Beneficiario', comodel_name='mz.beneficiario', ondelete='restrict', tracking=True, required=True)
    programa_id = fields.Many2one('pf.programas', string='Programa', required=True, default=lambda self: self.env.programa_id)
    servicio_id = fields.Many2one(string='Servicio', comodel_name='mz.asignacion.servicio', ondelete='restrict',domain="[('programa_id', '=?', programa_id)]")  
    # generar_horario_id
    personal_id_domain = fields.Char(compute="_compute_personal_id_domain", readonly=True, store=False, )
    personal_id = fields.Many2one(string='Personal', comodel_name='hr.employee', ondelete='restrict',)
    horario_id_domain = fields.Char(compute="_compute_horario_id_domain", readonly=True, store=False, )
    horario_id = fields.Many2one(string='Horarios', comodel_name='mz.planificacion.servicio', ondelete='restrict')  

             
    @api.depends('modulo_id')
    def _compute_beneficiario_id_domain(self):
      for record in self:         
        beneficiario_ids = record.beneficiario_id.search([]).ids
        record.beneficiario_id_domain = [('id', 'in', beneficiario_ids)]    

    @api.depends('servicio_id')
    def _compute_personal_id_domain(self):
      for record in self:    
        personal = self.env['mz.horarios.servicio'].search([('servicio_id','=',record.servicio_id.id)]).personal_id.ids        
        record.personal_id_domain = [('id', 'in', personal)]     

    
    @api.depends('servicio_id', 'personal_id')
    def _compute_horario_id_domain(self):
        for record in self:
            # Buscar todos los horarios planificados para este servicio y personal
            horarios_planificados = self.env['mz.planificacion.servicio'].search([
                ('generar_horario_id.servicio_id', '=', record.servicio_id.id),
                ('generar_horario_id.personal_id', '=', record.personal_id.id),
            ])
            # Filtrar los horarios que aún tienen capacidad disponible
            horarios_disponibles = horarios_planificados.filtered(
                lambda h: len(h.beneficiario_ids) < h.maximo_beneficiarios
            )
            
            # Crear el dominio con los IDs de los horarios disponibles
            record.horario_id_domain = [('id', 'in', horarios_disponibles.ids)]
       
       
