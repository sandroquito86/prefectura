from odoo import models, fields, api

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    programa_id = fields.Many2one('pf.programas', string='Programa Asociado', related='warehouse_id.programa_id', store=True)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self.env.user.has_group('prefectura_inventario.group_stock_program_manager'):
            user_programa = self.env.user.employee_id.programa_id
            if user_programa:
                domain = (domain or []) + [('programa_id', '=', user_programa.id)]
        return super(StockPickingType, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def create(self, vals):
        if 'warehouse_id' in vals and 'programa_id' not in vals:
            warehouse = self.env['stock.warehouse'].browse(vals['warehouse_id'])
            vals['programa_id'] = warehouse.programa_id.id
        return super(StockPickingType, self).create(vals)

    def write(self, vals):
        if 'warehouse_id' in vals:
            warehouse = self.env['stock.warehouse'].browse(vals['warehouse_id'])
            vals['programa_id'] = warehouse.programa_id.id
        return super(StockPickingType, self).write(vals)