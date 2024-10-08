# -*- coding: utf-8 -*-
{
    'name': "KAMI API Oracle",

    'summary': """
        API Oracle""",

    'description': """
        Modul untuk integrasi dengan aplikasi oracle pada PT Kalbe Milko Indonesia
    """,

    'author': "Agus Priyanto ~ PT. Berkah Metro Optima",
    'website': "http://www.bemosoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account', 'sale_stock', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/invoice.xml',
        'views/company.xml',
        'views/res_partner.xml',
        'views/views.xml',
        'views/sale.xml',
        'wizards/get_partner.xml',
    ]
}
