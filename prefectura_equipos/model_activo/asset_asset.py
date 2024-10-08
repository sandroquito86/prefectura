# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo import models, fields, api
import json
class AssetAsset(models.Model): 
    _name = 'asset.asset'
    _description = 'Activo'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
        
    # @api.model
    # def _get_estado_domain(self):         
    #   return [('categoria_id', 'in',self.categoria_id.estados_ids.ids)]    
        
    #NUEVOS CAMPOS 
             
    sigla = fields.Char(string='Sigla')  
    reparto_id = fields.Many2one(string='Reparto', comodel_name='res.company', ondelete='restrict', required=True,
                                 default=lambda s: s.env.company.id) 
    grupo_id = fields.Many2one(string='Grupo', comodel_name='pg_equipos.grupo', required=True, ondelete='restrict', tracking=True, )    
    categoria_id = fields.Many2one(string='Categoria', comodel_name='pg_equipos.categoria', ondelete='restrict', required=True,tracking=True )   
    tipo_id = fields.Many2one(string='Tipo de Activo', comodel_name='pg_equipos.nombre_equipo', ondelete='restrict', required=True,tracking=True )  
    serial = fields.Char('Serial no.', size=64,tracking=True)
    asset_id_domain = fields.Char ( compute = "_compute_asset_id_domain" , readonly = True, store = False, )
    image_medium = fields.Binary("Medium-sized image")
    componente_id_domain = fields.Char ( compute = "_compute_componente_id_domain" , readonly = True, store = False, )  
    color = fields.Many2one(string='Color', comodel_name='asset.color', ondelete='restrict',tracking=True)
    marca_id = fields.Many2one(string='Marca', comodel_name='pg_equipos.marca', ondelete='restrict',required=True, tracking=True)    
    modelo_id = fields.Many2one(string='Modelo', comodel_name='pg_equipos.modelo', ondelete='restrict',required=True, tracking=True)      
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id, index=True,)  
    departamento_id = fields.Many2one(string='Departamento', comodel_name='hr.department', ondelete='restrict', 
                                      domain="[('company_id','=',reparto_id)]",)
    empleado_id = fields.Many2one('hr.employee', domain="[('company_id','!=',False),('company_id','=',reparto_id)]", string='Responsable del Activo', required=True, tracking=True)                                                                                                
    user_id = fields.Many2one('res.users', 'Usuario', related='empleado_id.user_id', readonly=True, store=True,)       
    estado_id = fields.Selection(string='Estado', selection=[('op', 'Operativo'), ('mant', 'Mantenimiento'),('op_lim_men', 'Operativo con limitaciones menores'),
                                                             ('op_lim_may', 'Operativo con limitaciones mayores'), ('no_op', 'No operativo')],tracking=True)
    detalle_caracteristicas_ids = fields.One2many('asset.det_caracteristica', 'asset_id', 'Características de activos',) 
    detalle_caracteristica_especifica_ids = fields.One2many('asset.det_caracteristica_especifica', 'asset_id', 'Características de activos',)
    #MODIFICACION DE CAMPOS EXISTENTES       
    CRITICALITY_SELECTION = [('0', 'General'), ('1', 'Importante'), ('2', 'Muy Importante'), ('3', 'Critico'), ]
    name = fields.Char(string="Descripcion", required=False, compute='_concatenar_nombre_activo', store=True) 
    criticality = fields.Selection(CRITICALITY_SELECTION, 'Criticidad',default="0", tracking=True)           
    active = fields.Boolean('Activo/Inactivo', default=True, )
    asset_number = fields.Char('Código ICRON', size=16, required=False)#10.5    
    esbye = fields.Char('Código ESBYE')#10.5    
    manufacturer_id = fields.Many2one('res.partner', 'Fabricante', )
    start_date = fields.Date('Fecha de inicio', tracking=True)
    warranty_start_date = fields.Date('Inicio de Garantía', tracking=True)
    purchase_date = fields.Date('Fecha de Adquisiciòn', required=True, tracking=True )
    warranty_end_date = fields.Date('Fin de Garantía', tracking=True)  
    maintenance_date = fields.Datetime(string='Fecha de Mantenimiento', tracking=True)
    tipo_activo = fields.Selection(string='Tipo de activo', selection=[('ordinario', 'Ordinario'), ('estrategico', 'Estratégico')],default='ordinario') 
    
    descripcion = fields.Char(string='Descripcion',)
    
    motor = fields.Char(string='Motor', required=True, tracking=True)
    chasis = fields.Char(string='Chasis', required=True, tracking=True) 
    file_biblioteca_ids = fields.Many2many('ir.attachment', 'asset_biblioteca_rel', 'activo_id', 'archivo_id', string="Archivos",
                                    help='Adjuntar los documentos del activo', copy=False)
              
    _sql_constraints = [('name_unique', 'UNIQUE(name)',"Nombre  del activo debe ser único!!"),
                        ('asset_number_serie', 'UNIQUE(serial)',"Serial ingresado ya existe!!"),
                        ('asset_number_icron', 'UNIQUE(asset_number)',"Código ICRON ingresado ya existe!!")] 
    
    
    @api.constrains('name','asset_number','serial')
    def _check_asset_number(self):       
        for record in self:         
          if not(record.serial or record.asset_number):
            raise ValidationError("Debe ingresar el codigo Icron o el serial del Activo")
          validacion=0
          if(record.asset_number):
            validacion += 1
            if(len(record.asset_number)!=16 or record.asset_number.find(".")!=10):          
              raise ValidationError("Código Icron no cumple con sus caracteristicas")
            
     
    @api.constrains('detalle_caracteristicas_ids')
    def _check_caracteristica_obligatorio(self):
      for record in self:          
        caracteristicas = self.env['asset.config_caracteristica'].search([('tipo_id','=',record.tipo_id.id)],limit=1).caracteristica_ids  
        caracteristica_obligatorio = caracteristicas.filtered(lambda valor: valor.es_obligatorio == True ).caracteristica_id                   
        caracteristicas_ingresadas = record.detalle_caracteristicas_ids.caracteristica_id        
        diferencia =  caracteristica_obligatorio - caracteristicas_ingresadas                
        if(diferencia):
          raise ValidationError("Las siguientes caracteristicas  son obligatorias:\n{}".format(diferencia.mapped('name')))
        else:
          for lineas in record.detalle_caracteristicas_ids:
            if not (lineas.valor_id):
              raise ValidationError("Existen caracteristicas definidas que no tienen un valor..")
            
    @api.onchange('grupo_id')
    def _onchange_grupo_id(self):
      self.categoria_id = False
      
    @api.depends('tipo_id')
    def _compute_componente_id_domain(self):
      for record in self:
        if(record.tipo_id): 
          record.componente_id_domain = json.dumps([('id' , 'in' , record.tipo_id.componente_ids.ids)])
        else:
          record.componente_id_domain = json.dumps([('id' , 'in' , [])])     
        
    @api.depends('categoria_id.marca_ids')
    def _compute_asset_id_domain(self):
      for record in self:
        if(record.categoria_id):          
          record.asset_id_domain = json.dumps([('id' , 'in' , record.categoria_id.marca_ids.ids)])
        else:
          record.asset_id_domain = json.dumps([('id' , 'not in' , [])])          
          
    @api.onchange('categoria_id')
    def _onchange_categoria_id(self):
      for record in self:
        self.tipo_id = False    
    
    @api.onchange('tipo_id')
    def _onchange_tipo_id(self):
      for record in self:
        if(record.tipo_id):
          caracteristicas = self.env['asset.config_caracteristica'].search([('tipo_id','=',record.tipo_id.id)],limit=1).caracteristica_ids   
          caracteristica_obligatorio = caracteristicas.filtered(lambda valor: valor.es_obligatorio == True)  
          record.detalle_caracteristicas_ids = False        
          for linea in caracteristica_obligatorio:          
            self.detalle_caracteristicas_ids = [(0, 0,  { 'caracteristica_id':linea.caracteristica_id})]
            
      
    @api.depends('asset_number','tipo_id.abreviatura','marca_id.name','modelo_id.name','serial')
    def _concatenar_nombre_activo(self):
      for line in self: 
        _nombre = ""        
        if line.tipo_id:
          _nombre=str(line.tipo_id.abreviatura.upper())                  
        if line.marca_id:          
          _nombre += "-" + str(line.marca_id.name.upper())
        if line.modelo_id:          
          _nombre += "-" + str(line.modelo_id.name.upper())
        if line.asset_number:          
          _nombre += "-" +str(line.asset_number)[-5:].upper()
        if line.serial:          
          _nombre += "-" +str(line.serial.upper())
        line.name = _nombre
            
              
    @api.onchange('marca_id')    
    def _onchange_field(self):        
      self.modelo_id = False       
      
     
    @api.onchange('reparto_id')
    def _onchange_reparto_id(self):
        self.empleado_id = False
              
    @api.model
    def create(self, vals):                
      result = super(AssetAsset, self).create(vals)       
      return result     
    
    def write(self, values):      
      result = super(AssetAsset, self).write(values)    
      return result
   
    
    def ver_activos(self):
        _condicion = [(id,'=',False)]
        if self.user_has_groups('prefectura_equipos.grupo_equipos_administrador_general') or self.user_has_groups('prefectura_equipos.grupo_equipos_registrador_general'):
          _condicion = [(1,'=',1)]
        elif self.user_has_groups('prefectura_equipos.grupo_equipos_registrador_sucursal'):
          _condicion = [('reparto_id','=',self.env.user.company_id.id)]  
        
        diccionario= {
                        'name': ('Ingreso de Activos'),        
                        'domain': _condicion,
                        'res_model': 'asset.asset',
                        'views': [(self.env.ref('prefectura_equipos.assets_tree_view').id, 'tree'),(self.env.ref('prefectura_equipos.assets_form_view').id, 'form')],
                        'search_view_id':[self.env.ref('prefectura_equipos.assets_search').id, 'search'],                           
                        'view_mode': 'tree,form',
                        'type': 'ir.actions.act_window',
                        'context': {'search_default_reparto':1},
                    } 
        return diccionario 

    def ver_activos_caracteristicas_especificas(self):        
        _condicion = [(id,'=',False)]
        if self.user_has_groups('prefectura_equipos.grupo_equipos_administrador_general') or self.user_has_groups('prefectura_equipos.group_tecnico_general'):
          _condicion = [(1,'=',1)]
        elif self.user_has_groups('prefectura_equipos.group_tecnico_reparto'):
          grupos = self.env['asset.permiso_acceso'].search([('reparto_id','=',self.env.user.company_id.id)]).grupo_id
          categoria = self.env['asset.permiso_acceso'].search([('grupo_id','in',grupos.ids)]).categoria_ids
          _condicion = [('reparto_id','=',self.env.user.company_id.id),('grupo_id','=',grupos.ids),('categoria_id','=',categoria.ids)]          
        diccionario= {
                        'name': ('Características Específicas y Componentes'),        
                        'domain': _condicion,
                        'res_model': 'asset.asset',
                        'views': [(self.env.ref('prefectura_equipos.assets_caracteristicas_especificas_tree_view').id, 'tree'),(self.env.ref('prefectura_equipos.assets__assets_caracteristicas_especificas_form_view').id, 'form')],
                        'search_view_id':[self.env.ref('prefectura_equipos.assets_caracteristicas_especificas_search').id, 'search'],                           
                        'view_mode': 'tree,form',
                        'type': 'ir.actions.act_window',
                        'context': {'search_default_reparto':1},
                    } 
        return diccionario 
      
      
class DetalleCaracteristicaActivo(models.Model):
    _name = "asset.det_caracteristica"
    _description = 'Detalle Caracteristica' 
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'caracteristica_id'
    
    asset_id = fields.Many2one('asset.asset', string="Activos", ondelete='restrict', required=True, index=True, )  
    caracteristica_id_domain = fields.Char ( compute = "_compute_caracteristica_id_domain" , readonly = True, store = False, )
    caracteristica_id = fields.Many2one('asset.catalogo_caracteristica', string="Característica", required=True, ondelete='restrict', tracking=True)       
    valor_id = fields.Many2one('asset.caracteristica_valor', string="Valor Característica",  ondelete='restrict', tracking=True,
                               domain="[('caracteristica_id', '=', caracteristica_id)]")  
    
    @api.depends('caracteristica_id')
    def _compute_caracteristica_id_domain(self):
      for record in self:        
        all_caracteristicas= self.env['asset.config_caracteristica'].search([('tipo_id','=',record.asset_id.tipo_id.id)],limit=1).caracteristica_ids.caracteristica_id     
        listado_caracteristicas = record.asset_id.detalle_caracteristicas_ids.caracteristica_id  
        restantes = all_caracteristicas - listado_caracteristicas        
        record.caracteristica_id_domain = json.dumps([('id' , 'in' , restantes.ids)])
        
  

    


    