# -*- coding: utf-8 -*-


from odoo import http
from odoo.http import request
from datetime import datetime, time, timedelta, time
from functools import reduce

import json


class ManzanaElearning(http.Controller):
    @http.route('/manzana_beneficiary/attendees', type='json', auth='user', methods=['POST'])
    def manzana_beneficiary_attendees(self, slideChanel):
        attendees = request.env['slide.channel.partner'].sudo().search([('channel_id', '=', int(slideChanel))])
        course_attendees = []
        for attendee in attendees:
            course_attendees.append({
            'id': attendee.id,
            'name': attendee.partner_id.name,
            'attendance': False,
        })


        return json.dumps({
            'course_attendees': course_attendees
        })
