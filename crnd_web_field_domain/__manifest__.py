{
    'name': 'CRnD Web Field Domain',
    'category': 'Technical Settings',
    'summary': """
        Web Field Domain by CRnD allows create computed field domains.
    """,
    'author': 'Center of Research and Development',
    'support': 'info@crnd.pro',
    'website': 'https://crnd.pro',
    'license': 'LGPL-3',
    'version': '17.0.0.5.1',
    'depends': [
        'web',
    ],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'crnd_web_field_domain/static/src/js/field_domain_owl.js',
        ],
    },
    'qweb': [
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
