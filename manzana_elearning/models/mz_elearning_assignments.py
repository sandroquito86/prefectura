# -*- coding: utf-8 -*-
import json
import logging
import time
from datetime import date, datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_date




class MzElearningAssignments(models.Model):
    _name = 'mz.elearning.assignments'
    _description = 'Tareas de estudiantes'

    name = fields.Char('Nombre')
    description_task = fields.Char('Description')
    course_id = fields.Many2one('slide.channel')
    teacher_id = fields.Many2one('res.users', string='Docente')
    deadline = fields.Datetime('Fecha de Entrega', store=True, required=True, tracking=True)
    max_score = fields.Float('Calificación Máxima')
    student_assignments_ids = fields.One2many('mz.student.assignments', 'assignment_id')


class MzStudentAssignments(models.Model):
    _name = 'mz.student.assignments'
    _description = 'Entrega de tareas de estudiantes'
    _rec_name = 'student_id'

    name = fields.Char('Nombre')
    assignment_id = fields.Many2one('mz.elearning.assignments', required=True)
    student_id = fields.Many2one('mz.beneficiario')
    submitted_file = fields.Binary('Submitted File', required=True)
    status = fields.Selection([
        ('pending', 'Pendiente'),
        ('submitted', 'Entregado'),
        ('late', 'Atrasado'),
        ('not_submitted', 'No Entregado'),
    ], string='Estado de la Entrega', default='pending', required=True)
    grade = fields.Float('Calificación', digits=(4, 2))
    feedback = fields.Text('Comentarios del Profesor')

    

    
