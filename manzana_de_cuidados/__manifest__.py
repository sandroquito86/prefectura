# -*- coding: utf-8 -*-
{
    'name': "manzana_de_cuidados",

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
    'depends': ['hr','base','mail','prefectura_base','website_slides'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/mz_security.xml',
        'security/ir.model.access.csv',
        'data/data_base.xml',
        'menu/mz_menu.xml',
        'views/mz_beneficiario_views.xml',
        'views/mz_catalogo_views.xml',
        'views/mz_servicio_views.xml',
        'views/mz_curso_views.xml',
        'views/mz_catalogo_items_views.xml',
        'views/mz_programas_view.xml',
        'views/views_gestion_academica/mz_slide_channel_inherit_views.xml',
        'views/views_empleado/mz_empleado_view.xml',
        'views/views_servicio/mz_asignacion_servicio_view.xml',
        'views/views_servicio/mz_horarios_servicio_view.xml',
        'views/views_servicio/mz_planificacion_servicio_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
     'installable': True,
    'application': True,
    'auto_install': False,
}

