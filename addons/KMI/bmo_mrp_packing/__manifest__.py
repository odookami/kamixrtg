# -*- coding: utf-8 -*-
{
    'name': "MRP Packing",

    'summary': """MRP Packing""",

    'description': """MRP Packing""",

    'author': "Dani R.",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Production',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'bmo_batch_record', 'bmo_mrp', 'bmo_inventory', 'stock', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/pack.xml',
        'views/banded.xml',
        'views/line.xml',
        'views/whs_line.xml',
        'views/mrp_sortir.xml',
        'views/res_config.xml',
        'views/menu.xml',
        'data/ir_sequence.xml',
        'wizard/wizard_lhp.xml',
        # 'views/mrp_packing_report.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
