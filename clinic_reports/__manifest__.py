# -*- coding: utf-8 -*-
{
    'name': "clinic_reports",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['clinic_mgt'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/paper_sizes.xml',
        # 'reports/daily_billout_info_template.xml',
        # 'reports/entry_forms_template.xml',
        'reports/item_stock_card_template.xml',
        # 'reports/lab_request_template.xml',
        'reports/lab_results_template.xml',
        'reports/medical_certificate_template.xml',
        'reports/medical_record_template.xml',
        'reports/medicines_inventory_template.xml',
        'reports/prescription_template.xml',
        # 'reports/referral_letter_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
