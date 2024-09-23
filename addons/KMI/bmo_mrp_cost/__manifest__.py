# -*- coding: utf-8 -*-
{
    'name'              : "MRP COST - KAMI",
    'summary'           : """
                            Short (1 phrase/line) summary of the module's purpose, used as
                            subtitle on modules listing or apps.openerp.com""",
    'description'       : """
                                Long description of module's purpose
                            """,
    'author'            : "bemosoft - tian",
    'website'           : "http://www.bemosoft.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category'          : 'Manufacturing/Manufacturing',
    'version'           : '14.0.1',
    # any module necessary for this one to work correctly
    'depends'           : ['base','product','mrp','bmo_mrp','percent_field','bmo_closing_period','bmo_inventory','stock_account'],
    # always loaded
    'data'              : [
                            'security/group_security.xml',
                            'security/ir.model.access.csv',
                            'data/data.xml',
                            'views/res_config_view.xml',
                            'views/product_view.xml',
                            'views/views.xml',
                            'views/config_view.xml',
                            'wizard/wizard_report_cogs_view.xml',
                            'views/menu_view.xml',
                        ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
