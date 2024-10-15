# -*- coding: utf-8 -*-
{
    'name': "manzana_cuidados_elearning",

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
    'depends': ['base','hr',  'website_slides', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/mz_elearning_views.xml',
        
        'views/mz_elearning_menu_views.xml',
        'views/website_slides_templates_course.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'assets': {
        'web.assets_frontend': [
            'manzana_elearning/static/src/js/button_file.js',
        ],
        'web.assets_backend': [
            'manzana_elearning/static/src/components/attendance_beneficiary/attendance_beneficiary.js',
            'manzana_elearning/static/src/components/attendance_beneficiary/attendance_beneficiary.xml',
        ],
},
}

