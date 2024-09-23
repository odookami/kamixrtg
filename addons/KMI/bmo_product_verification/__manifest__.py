# -*- coding: utf-8 -*-
{
    'name': "Inline Product Verification",

    'summary': """
        Inline Product Verification""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PT. Berkah Metro Optima ~ Agus Priyanto - 085921110004",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail', 'bmo_batch_record', 'bmo_product_st', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/inline_product_verification.xml',
        'views/master.xml',
        'reports/menu_report.xml',
        'views/templates.xml',
    ],
}
