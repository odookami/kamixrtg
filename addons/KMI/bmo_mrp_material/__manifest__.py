# -*- coding: utf-8 -*-
{
    'name': "Material Usage",

    'summary': """Material Usage""",

    'description': """Material Usage""",

    'author': "Dani R. / Tian",
    'website': "https://www.bemosoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Report',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'bmo_mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/material_usage.xml',
        'views/res_config.xml',
        'views/mrp_pm_daily_conf_view.xml',
        'wizard/pm_daily.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
