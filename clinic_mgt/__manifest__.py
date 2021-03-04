# -*- coding: utf-8 -*-
{
    'name': "Clinic Management",

    'summary': """
        Clinic Management Systems for Odoo 12""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Daryll Gay Bangoy",
    'website': "http://www.linkedin.com/lyradb",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_setup','mail','contacts', 'portal', 'sale_management', 'board', #'jasper_reports',
                'account', 'field_image_preview', 'auth_session_timeout', 'smile_web_auto_refresh'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/billing_views.xml',
        'data/data.xml',
        'data/ribbon_data.xml',
        'views/base_view.xml',
        'views/cashier_recon_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}