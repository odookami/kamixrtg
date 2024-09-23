# -*- coding: utf-8 -*-
{
    'name': "Inventory Quality Check",

    'summary': """
        Quality Check for Kalbe Milko""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'bmo_inventory', 'stock'],

    # always loaded
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'reports/report_internal_transfer.xml',
        'reports/qc_sample_request.xml',
        'views/quality_check_template.xml',
        'views/stock_move_line.xml',
        'views/picking.xml',
        'views/res_config_settings.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
