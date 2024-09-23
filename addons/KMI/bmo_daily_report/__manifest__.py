# -*- coding: utf-8 -*-
{
    'name': "Form Laporan Harian",
    'summary': """
        Form Laporan Harian UnLoader (OBOL),  
        Labeling (OBOL) 1, Labeling (OBOL) 2, Packing (OBOL).
    """,
    'author': "Dani R.",
    'website': "https://www.bemosoft.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Production',
    'version': '0.1',
    # any module necessary for this one to work correctly
    # 'depends': ['base', 'web', 'bmo_batch_record'],
    'depends': ['base', 'mail', 'bmo_batch_record', 'bmo_mrp', 'web_domain_field', 'bmo_product_st'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/menu_report.xml',
        'views/daily_report.xml',
        'views/loader.xml',
        'views/unscramble.xml',
        'views/filling.xml',
        'views/retort.xml',
        'views/unloader.xml',
        'views/packing.xml',
        'views/labeling.xml',
        'views/banded_usage.xml',

        # 'views/labeling2.xml',
        # 'views/product_st.xml',
        # 'data/packing_params.xml',
        # 'views/params.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
