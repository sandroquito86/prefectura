# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Curso(models.Model):
    _name = 'mz.curso'
    _description = 'Curso'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nombre del Curso', required=True, tracking=True)
    descripcion = fields.Text(string='Descripción', tracking=True)
    instructor_id = fields.Many2one('res.users', string='Instructor', tracking=True)
    capacidad = fields.Integer(string='Capacidad Operativa', required=True, tracking=True)
    horario_ids = fields.One2many('mz.horario_curso', 'curso_id', string='Horarios')
    inscripciones_ids = fields.One2many('mz.inscripcion', 'curso_id', string='Inscripciones')
    # tarea_ids = fields.One2many('mz.tarea', 'curso_id', string='Tareas')

    @api.constrains('capacidad')
    def _check_capacidad(self):
        for record in self:
            if record.capacidad < 1:
                raise ValidationError("La capacidad operativa debe ser al menos 1.")
            
        
class HorarioCurso(models.Model):
    _name = 'mz.horario_curso'
    _description = 'Horario del Curso'

    curso_id = fields.Many2one('mz.curso', string='Curso', ondelete='cascade', required=True)
    dia_semana = fields.Selection([
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miércoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sábado', 'Sábado'),
        ('domingo', 'Domingo'),
    ], string='Día de la Semana', required=True)
    hora_inicio = fields.Float(string='Hora de Inicio', required=True)
    hora_fin = fields.Float(string='Hora de Fin', required=True)

    @api.constrains('hora_inicio', 'hora_fin')
    def _check_horas(self):
        for record in self:
            if record.hora_fin <= record.hora_inicio:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            
class Inscripcion(models.Model):
    _name = 'mz.inscripcion'
    _description = 'Inscripción al Curso'

    curso_id = fields.Many2one('mz.curso', string='Curso', ondelete='cascade', required=True)
    beneficiario_id = fields.Many2one('mz.beneficiario', string='Beneficiario', ondelete='cascade', required=True)
    fecha_inscripcion = fields.Date(string='Fecha de Inscripción', default=fields.Date.today, tracking=True)
    state = fields.Selection([
        ('inscrito', 'Inscrito'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ], string='Estado', default='inscrito', tracking=True)
    # calificacion_ids = fields.One2many('mz.calificacion', 'inscripcion_id', string='Calificaciones')

    @api.constrains('curso_id', 'beneficiario_id')
    def _check_capacidad_curso(self):
        for record in self:
            if record.state == 'inscrito':
                inscriptos = self.search_count([
                    ('curso_id', '=', record.curso_id.id),
                    ('state', '=', 'inscrito')
                ])
                if inscriptos > record.curso_id.capacidad:
                    raise ValidationError("La capacidad del curso ha sido alcanzada.")