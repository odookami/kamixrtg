# -*- coding: utf-8 -*-
{
    'name'              : "Custom Sale Order",
    'summary'           : """
                            Short (1 phrase/line) summary of the module's purpose, used as
                            subtitle on modules listing or apps.openerp.com""",
    'description'       : """
                            Long description of module's purpose
                        """,
    'author'            : "bemosoft",
    'website'           : "http://www.yourcompany.com",
    'category'          : 'Uncategorized',
    'version'           : '0.1',
    'depends'           : ['base', 'sale', 'sale_management', 'stock'],
    'data'              : [
                            'security/ir.model.access.csv',
                            'security/security.xml',
                            'wizard/wizard_report_cogs_view.xml',
                            'views/sale_order.xml',
                            'views/stock_move.xml',
                        ],
}
