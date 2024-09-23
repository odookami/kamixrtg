# -*- coding: utf-8 -*-
{
    'name'          : "Closing Period",
    'summary'       : """ Closing Period""",
    'description'   :   """ Closing Period 
                        - Sales
                        - Inventory
                        - Accounting
                     """,

    'author'        : "My Company",
    'website'       : "https://bemosoft.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category'      : 'Tools',
    'version'       : '14.0.1',
    # any module necessary for this one to work correctly
    'depends'       : ['base','account','sale','sale_management'],
    # always loaded
    'data'          : [
                        'security/account_security.xml',
                        'security/ir.model.access.csv',
                        'views/account_menuitem.xml',
                        'views/account_views.xml',
                        'views/account_end_fy.xml',
                        'views/sale_order_view.xml',
                        'views/mrp_view.xml',
                        'views/inventory_view.xml',
                     ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
