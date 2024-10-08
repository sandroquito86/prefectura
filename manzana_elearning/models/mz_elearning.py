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




class MzElearning(models.Model):
    _inherit = 'slide.channel'
    _description = 'E-learning de Manzana de Cuidados'




    

    
