# -*- coding: utf-8 -*-

##############################################################################
#

#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    instructor_id = fields.Many2one('hr.employee', string='Docente', help='Docente responsable del curso')
    schedule_ids = fields.One2many('elearning.schedule', 'course_id', string='Horarios')