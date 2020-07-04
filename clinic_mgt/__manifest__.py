# -*- coding: utf-8 -*-
{
    'name': "Clinic Management",

    'summary': """
        Clinic Management Systems""",

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
    'depends': ['base_setup','mail','contacts', 'portal','sale','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'data/data.xml',
        'reports/templates/paper_sizes.xml',
        #'reports/templates/entry_forms_template.xml',
        #'reports/templates/refferal_forms_template.xml',
        #'reports/templates/item_stock_card_template.xml',
        #'reports/templates/medicines_inventory_template.xml',
        #'reports/templates/medical_record_template.xml',
        #'reports/templates/daily_billout_template.xml',
        #'reports/templates/lab_results_template.xml',
        #'reports/templates/prescription_template.xml',
        #'reports/templates/medical_certificate_template.xml',
    ],
    
    # 'qweb': ['static/src/xml/many2many_checkboxes.xml', ],
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}