from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = 'stock.location'

    programa_id = fields.Many2one('pf.programas', string='Programa Asociado')

    def get_programa(self):
        self.ensure_one()
        if self.programa_id:
            return self.programa_id
        elif self.location_id:
            return self.location_id.get_programa()
        return False

    @api.model
    def create(self, vals):
        if 'programa_id' not in vals and vals.get('location_id'):
            parent_location = self.browse(vals['location_id'])
            parent_programa = parent_location.get_programa()
            if parent_programa:
                vals['programa_id'] = parent_programa.id
        return super(StockLocation, self).create(vals)

    def write(self, vals):
        if 'programa_id' not in vals and vals.get('location_id'):
            parent_location = self.env['stock.location'].browse(vals['location_id'])
            parent_programa = parent_location.get_programa()
            if parent_programa:
                vals['programa_id'] = parent_programa.id
        return super(StockLocation, self).write(vals)