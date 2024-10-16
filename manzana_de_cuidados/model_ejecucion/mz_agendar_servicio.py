# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class AgendarServicio(models.Model):
    _name = 'mz.agendar_servicio'
    _description = 'Agendar Servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    
    STATE_SELECTION = [('borrador', 'Borrador'), ('solicitud', 'Solicitado'),('aprobado', 'Aprobado'),
                       ('atendido', 'Atendido'), ('anulado', 'Anulado')]

    state = fields.Selection(STATE_SELECTION, 'Estado', readonly=True, tracking=True, default='borrador', )
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
    fecha_solicitud = fields.Date(string='Fecha', required=True, tracking=True)
    horario_id = fields.Many2one(string='Horarios', comodel_name='mz.planificacion.servicio', ondelete='restrict')  
    codigo = fields.Char(string='Código', readonly=True, store=True)
    mensaje = fields.Text(string='Mensaje', compute='_compute_mensaje')
    active = fields.Boolean(default=True, string='Activo', tracking=True)

    @api.depends('servicio_id', 'personal_id')
    def _compute_mensaje(self):
        dia_dict = dict(self.env['mz.detalle.horarios'].fields_get(allfields=['dias'])['dias']['selection'])
        for record in self:
            if record.servicio_id and record.personal_id:
                domain = [
                    ('servicio_id', '=', record.servicio_id.id),
                    ('personal_id', '=', record.personal_id.id),
                    ('active', '=', True),
                ]
                horarios_planificados = self.env['mz.horarios.servicio'].search(domain)
                if horarios_planificados:
                    dias_nombres = [dia_dict.get(horario.dias, '') for horario in horarios_planificados.detalle_horario_ids]
                    record.mensaje = 'La disponibilidad de horarios es: ' + ' - '.join(dias_nombres)
                else:
                    record.mensaje = 'No hay horarios disponibles'
            else:
                record.mensaje = ''


    @api.constrains('beneficiario_id', 'horario_id')
    def _check_unique_beneficiario_horario(self):
        for record in self:
            existing = self.search([
                ('beneficiario_id', '=', record.beneficiario_id.id),
                ('horario_id', '=', record.horario_id.id),
                ('id', '!=', record.id)
            ])            
            if existing:
                raise ValidationError("El beneficiario ya ha solicitado este horario.")       
            
    @api.constrains('horario_id', 'beneficiario_id')
    def _check_horario_capacity(self):
        for record in self:
            if record.horario_id and record.beneficiario_id:
                # Contar las asistencias actuales para este horario
                asistencias_count = self.env['mz.asistencia_servicio'].search_count([
                    ('planificacion_id', '=', record.horario_id.id)
                ])
                
                # Verificar si se excede la capacidad máxima
                if asistencias_count >= record.horario_id.maximo_beneficiarios:
                    raise ValidationError(f"El horario seleccionado ya ha alcanzado su capacidad máxima de {record.horario_id.maximo_beneficiarios} beneficiarios.")

            
                
    @api.depends('modulo_id','programa_id')
    def _compute_beneficiario_id_domain(self):
      for record in self:         
        beneficiario_ids = record.beneficiario_id.search([('programa_id','=',record.programa_id.id)]).ids
        record.beneficiario_id_domain = [('id', 'in', beneficiario_ids)]    

    @api.depends('servicio_id')
    def _compute_personal_id_domain(self):
      for record in self:    
        personal = self.env['mz.horarios.servicio'].search([('servicio_id','=',record.servicio_id.id)]).personal_id.ids        
        record.personal_id_domain = [('id', 'in', personal)]     

    
    @api.depends('servicio_id', 'personal_id','fecha_solicitud')
    def _compute_horario_id_domain(self):
        for record in self:
            if record.servicio_id and record.personal_id and record.fecha_solicitud:
                domain = [
                    ('generar_horario_id.servicio_id', '=', record.servicio_id.id),
                    ('generar_horario_id.personal_id', '=', record.personal_id.id),
                    ('fecha', '=', record.fecha_solicitud),
                ]
                horarios_planificados = self.env['mz.planificacion.servicio'].search(domain)
                
                horarios_disponibles = horarios_planificados.filtered(
                    lambda h: h.beneficiarios_count < h.maximo_beneficiarios
                )
                
                record.horario_id_domain = [('id', 'in', horarios_disponibles.ids)]
            else:
                record.horario_id_domain = [('id', 'in', [])]


    
    @api.onchange('beneficiario_id')
    def _onchange_beneficiario_id(self):
        for record in self:
            record.servicio_id = False
            record.personal_id = False
            record.fecha_solicitud = False
            record.horario_id = False

    @api.onchange('servicio_id')
    def _onchange_servicio_id(self):
        for record in self:
            record.personal_id = False
            record.fecha_solicitud = False
            record.horario_id = False

    @api.onchange('personal_id')
    def _onchange_personal_id(self):
        for record in self:
            record.fecha_solicitud = False
            record.horario_id = False

    @api.onchange('fecha_solicitud')
    def _onchange_fecha_solicitud(self):
        for record in self:
            record.horario_id = False

    def solicitar_horario(self):
        for record in self:
            if not record.horario_id:
                raise ValidationError("Debe seleccionar un horario.")
            codigo = self._generate_codigo()
            record.codigo = codigo
            record.state = 'solicitud'

    def _generate_codigo(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        prefix = 'PRE-GUAYAS'
        
        # Buscar el último código generado este año, excluyendo los registros en estado borrador
        last_record = self.search([
            ('create_date', '>=', f'{current_year}-01-01 00:00:00'),
            ('state', '!=', 'borrador')
        ], order='create_date desc', limit=1)
        if last_record and last_record.codigo:
            last_number = int(last_record.codigo.split('-')[2])
        else:
            last_number = 0

        new_number = last_number + 1
        new_number_str = str(new_number).zfill(7)
        
        return f'{prefix}-{new_number_str}-{current_month:02d}-{current_year}'

    def aprobar_horario(self):
        for record in self:
            # Verificar nuevamente la capacidad antes de aprobar
            asistencias_count = self.env['mz.asistencia_servicio'].search_count([
                ('planificacion_id', '=', record.horario_id.id)
            ])
            if asistencias_count >= record.horario_id.maximo_beneficiarios:
                raise ValidationError(f"No se puede aprobar. El horario ya ha alcanzado su capacidad máxima de {record.horario_id.maximo_beneficiarios} beneficiarios.")
            
            record.state = 'aprobado'
            if record.horario_id and record.beneficiario_id:
                self.env['mz.asistencia_servicio'].create({
                    'planificacion_id': record.horario_id.id,
                    'beneficiario_id': record.beneficiario_id.id,
                })


       
       
