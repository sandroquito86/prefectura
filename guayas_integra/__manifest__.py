# -*- coding: utf-8 -*-
{
    'name': "guayas_integra",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/gi_beneficiarios_menu_view.xml',
        # CATALOGO
        'views/catalogo/gi_catalogo_view.xml',          
        'views/catalogo/gi_catalogo_items_view.xml', 
        'views/catalogo/gi_catalogo_area_view.xml',
         'views/catalogo/gi_catalogo_servicio_view.xml',
         

        #CONFIGURACION
        'views/configuracion/gi_pais_view.xml',
        'views/configuracion/gi_provincia_view.xml',  
        'views/configuracion/gi_categoria_beneficiario_view.xml', 
       
        #REGISTRO  
        'views/registro/gi_beneficiarios_view.xml',
        'views/registro/gi_personal_view.xml',       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

