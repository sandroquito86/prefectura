# -*- coding: utf-8 -*-

##############################################################################
#

#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ElearningSchedule(models.Model):
    _name = 'elearning.schedule'
    _description = 'eLearning Schedule'

    name = fields.Char(string='Nombre', required=True)
    course_id = fields.Many2one('slide.channel', string='Curso', required=True)
    start_datetime = fields.Datetime(string='Fecha y Hora de Inicio', required=True)
    end_datetime = fields.Datetime(string='Fecha y Hora de Fin', required=True)
    instructor_id = fields.Many2one('res.users', string='Instructor')
    description = fields.Text(string='Description')

    @api.constrains('start_datetime', 'end_datetime')
    def _check_dates(self):
        for record in self:
            if record.start_datetime > record.end_datetime:
                raise ValidationError("La fecha de finalización debe ser posterior a la fecha de inicio")