from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    programa_id = fields.Many2one('pf.programas', string='Programa Asociado', ondelete='restrict')
    code = fields.Char('Código', size=10)

    @api.model
    def action_open_warehouses(self):
        # Lógica para determinar el dominio
        domain = self.get_domain_based_on_user()
        return {
            'name': 'Warehouses',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.warehouse',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'default_domain': domain  # Puedes agregar el dominio al contexto
            },
        }

    @api.model
    def get_domain_based_on_user(self):
        if self.env.user.has_group('stock.group_stock_manager'):
            return []  # Todos los almacenes
        elif self.env.user.has_group('prefectura_inventario.group_stock_program_manager'):
            user_programa = self.env.user.employee_id.programa_id
            if user_programa:
                return [('programa_id', '=', user_programa.id)]
            else:
                return [('id', '=', False)]  # No mostrar nada
        else:
            return [('id', '=', False)]  # No mostrar nada


    @api.model
    def create(self, vals):
        # Si el usuario pertenece al grupo Administrador de Inventario, no se asigna programa_id
        if self.env.user.has_group('stock.group_stock_manager'):
            vals['programa_id'] = False
        else:
            # Si no se proporciona programa_id, asignar el del usuario actual (Administrador de Programa u otros)
            if 'programa_id' not in vals:
                user_programa = self.env.user.employee_id.programa_id
                if user_programa:
                    vals['programa_id'] = user_programa.id

        warehouse = super(StockWarehouse, self).create(vals)
        
        # Añadir resupply warehouse si el programa está asignado
        if warehouse.programa_id:
            company_warehouse = self.env['stock.warehouse'].search([
                ('company_id', '=', warehouse.company_id.id),
                ('id', '!=', warehouse.id)
            ], limit=1)
            if company_warehouse:
                warehouse.write({'resupply_wh_ids': [(4, company_warehouse.id)]})
        
        return warehouse


    def write(self, vals):
        if 'programa_id' in vals:
            programa = self.env['pf.programas'].browse(vals['programa_id'])
            vals['company_id'] = programa.sucursal_id.company_id.id
        return super(StockWarehouse, self).write(vals)

    @api.onchange('programa_id')
    def onchange_programa_id(self):
        if self.programa_id:
            company_warehouse = self.env['stock.warehouse'].search([
                ('company_id', '=', self.company_id.id),
                ('id', '!=', self.id)
            ], limit=1)
            if company_warehouse:
                self.resupply_wh_ids = [(4, company_warehouse.id)]

   