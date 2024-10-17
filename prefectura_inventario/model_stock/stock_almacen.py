from odoo import models, fields

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    code = fields.Char('Name', required=True, size=10)