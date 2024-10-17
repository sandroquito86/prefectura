from odoo import models, fields, api

class PfProgramas(models.Model):
    _inherit = 'pf.programas'

    warehouse_id = fields.Many2one('stock.warehouse', string='Almacén Asociado', readonly=True)

    @api.model
    def create(self, vals):
        programa = super(PfProgramas, self).create(vals)
        programa._create_inventory_structure()
        return programa

    def _create_inventory_structure(self):
        self.ensure_one()
        WarehouseObj = self.env['stock.warehouse']
        LocationObj = self.env['stock.location']
        
        # Crear almacén con nombre descriptivo
        warehouse_name = f"{self.name}(ALMACEN)"
        warehouse_vals = {
            'name': warehouse_name,
            'code': self.sigla[:15],
            'company_id': self.sucursal_id.company_id.id,
        }
        warehouse = WarehouseObj.create(warehouse_vals)
        
        # Asociar el almacén al programa
        self.warehouse_id = warehouse.id

        # Actualizar el nombre de la ubicación de existencias
        stock_location = warehouse.lot_stock_id
        stock_location.write({
            'name': 'Existencias'
        })

        # Actualizar el nombre completo de la ubicación de existencias
        stock_location._compute_complete_name()

        return True
    
    def write(self, vals):
        res = super(PfProgramas, self).write(vals)
        
        # Verificar si se cambió el nombre o la sigla
        if 'name' in vals or 'sigla' in vals:
            for programa in self:
                if programa.warehouse_id:
                    warehouse_vals = {}
                    
                    # Actualizar el nombre del almacén si cambió el nombre del programa
                    if 'name' in vals:
                        warehouse_vals['name'] = f"{programa.name}(ALMACEN)"
                    
                    # Actualizar el código del almacén si cambió la sigla
                    if 'sigla' in vals:
                        warehouse_vals['code'] = programa.sigla[:15]
                    
                    # Actualizar el almacén
                    if warehouse_vals:
                        programa.warehouse_id.write(warehouse_vals)
                        
                        # Actualizar el nombre de la ubicación de stock si cambió el nombre del almacén
                        if 'name' in vals:
                            stock_location = programa.warehouse_id.lot_stock_id
                            stock_location.write({'name': 'Existencias'})
                            stock_location._compute_complete_name()
        
        return res