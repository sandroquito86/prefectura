# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta
from random import randint

class Consulta(models.Model):
    _name = 'mz.consulta'
    _description = 'Consulta Médica'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'codigo'

    codigo = fields.Char(string='Código', readonly=True, store=True)
    fecha = fields.Date(string='Fecha', required=True, tracking=True)
    hora = fields.Float(string='Hora', required=True, tracking=True, compute='_compute_hora')
    beneficiario_id = fields.Many2one(string='Beneficiario', comodel_name='mz.beneficiario', ondelete='restrict', tracking=True, required=True)
    programa_id = fields.Many2one('pf.programas', string='Programa', required=True, default=lambda self: self.env.programa_id)
    servicio_id = fields.Many2one(string='Servicio', comodel_name='mz.asignacion.servicio', ondelete='restrict', domain="[('programa_id', '=?', programa_id)]")
    personal_id = fields.Many2one(string='Personal Médico', comodel_name='hr.employee', ondelete='restrict', tracking=True)
    
    # Información del paciente
    genero = fields.Selection([
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro')
    ], string='Género')
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento', tracking=True)
    edad = fields.Char(string="Edad", compute="_compute_edad")
    
    # Motivo de consulta y síntomas
    motivo_consulta = fields.Text(string='Motivo de Consulta', required=True, tracking=True)
    sintomas = fields.Text(string='Síntomas', tracking=True)
    
    # Signos vitales
    presion_arterial = fields.Char(string='Presión Arterial', tracking=True)
    frecuencia_cardiaca = fields.Integer(string='Frecuencia Cardíaca', tracking=True)
    frecuencia_respiratoria = fields.Integer(string='Frecuencia Respiratoria', tracking=True)
    temperatura = fields.Float(string='Temperatura (°C)', tracking=True)
    peso = fields.Float(string='Peso (kg)', tracking=True)
    altura = fields.Float(string='Altura (cm)', tracking=True)
    imc = fields.Float(string='IMC', compute='_compute_imc', store=True)
    
    # Examen físico
    examen_fisico = fields.Text(string='Examen Físico', tracking=True)
    
    # Diagnóstico y tratamiento
    diagnostico = fields.Text(string='Diagnóstico', tracking=True)
    tratamiento = fields.Text(string='Tratamiento', tracking=True)
    
    # Historial médico
    antecedentes_personales = fields.Text(string='Antecedentes Personales', tracking=True)
    antecedentes_familiares = fields.Text(string='Antecedentes Familiares', tracking=True)
    alergias = fields.Text(string='Alergias', tracking=True)
    medicamentos_actuales = fields.Text(string='Medicamentos Actuales', tracking=True)
    
    # Seguimiento
    observaciones = fields.Text(string='Observaciones', tracking=True)
    proxima_cita = fields.Date(string='Próxima Cita', tracking=True)

    historia_clinica_id = fields.Many2one('mz.historia.clinica', string='Historia Clínica', readonly=True)
    
    @api.model
    def default_get(self, fields_list):
        defaults = super(Consulta, self).default_get(fields_list)
        
        context = self.env.context
        defaults['personal_id'] = context.get('default_personal_id')
        defaults['beneficiario_id'] = context.get('default_beneficiario_id')
        defaults['servicio_id'] = context.get('default_servicio_id')
        defaults['programa_id'] = context.get('default_programa_id')
        defaults['fecha'] = context.get('default_fecha')
        
        if defaults.get('beneficiario_id'):
            beneficiario = self.env['mz.beneficiario'].browse(defaults['beneficiario_id'])
            defaults['genero'] = beneficiario.genero
            defaults['fecha_nacimiento'] = beneficiario.fecha_nacimiento
        
        return defaults

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        for record in self:
            if record.fecha_nacimiento:
                hoy = date.today()
                diferencia = relativedelta(hoy, record.fecha_nacimiento)
                record.edad = f"{diferencia.years} años, {diferencia.months} meses, {diferencia.days} días"
            else:
                record.edad = "Sin fecha de nacimiento"

    @api.depends('fecha')
    def _compute_hora(self):
        for record in self:
            record.hora = randint(0, 23) + randint(0, 59) / 100

    @api.depends('peso', 'altura')
    def _compute_imc(self):
        for record in self:
            if record.peso and record.altura:
                altura_m = record.altura / 100  # convertir cm a m
                record.imc = record.peso / (altura_m * altura_m)
            else:
                record.imc = 0

    @api.model
    def create(self, vals):
        if not vals.get('codigo'):
            vals['codigo'] = self.env['ir.sequence'].next_by_code('mz.consulta.sequence') or 'Nuevo'
        return super(Consulta, self).create(vals)
    
    

    def create(self, vals):
        consulta = super(Consulta, self).create(vals)
        consulta.crear_historia_clinica()
        return consulta

    def write(self, vals):
        res = super(Consulta, self).write(vals)
        self.actualizar_historia_clinica()
        return res

    def crear_historia_clinica(self):
        for consulta in self:
            historia_clinica = self.env['mz.historia.clinica'].create({
                'beneficiario_id': consulta.beneficiario_id.id,
                'consulta_id': consulta.id,
                'fecha': consulta.fecha,
                'motivo_consulta': consulta.motivo_consulta,
                'diagnostico': consulta.diagnostico,
                'tratamiento': consulta.tratamiento,
                'observaciones': consulta.observaciones,
                'signos_vitales': f"PA: {consulta.presion_arterial}, FC: {consulta.frecuencia_cardiaca}, FR: {consulta.frecuencia_respiratoria}, Temp: {consulta.temperatura}"
            })
            consulta.historia_clinica_id = historia_clinica.id

    def actualizar_historia_clinica(self):
        for consulta in self:
            if consulta.historia_clinica_id:
                consulta.historia_clinica_id.write({
                    'motivo_consulta': consulta.motivo_consulta,
                    'diagnostico': consulta.diagnostico,
                    'tratamiento': consulta.tratamiento,
                    'observaciones': consulta.observaciones,
                    'signos_vitales': f"PA: {consulta.presion_arterial}, FC: {consulta.frecuencia_cardiaca}, FR: {consulta.frecuencia_respiratoria}, Temp: {consulta.temperatura}"
                })