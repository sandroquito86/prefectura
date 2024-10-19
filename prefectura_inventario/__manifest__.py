# -*- coding: utf-8 -*-
{
    'name': "prefectura/prefectura_inventario",

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
    'depends': ['base','stock','prefectura_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
         'data/stock_grupos.xml',        
        'data/regla_almacen.xml',
        'views/stock_menu_view.xml',
        'views/stock/stock_almacen_view.xml',



        'views/stock/stock_programa_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

