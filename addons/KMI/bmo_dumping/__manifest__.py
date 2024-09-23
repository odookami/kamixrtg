# -*- coding: utf-8 -*-
{
    'name'              : "Dumping",
    'summary'           : """
                            Short (1 phrase/line) summary of the module's purpose, used as
                            subtitle on modules listing or apps.openerp.com""",
    'description'       : """
                                Long description of module's purpose
                            """,
    'author'            : "Tian",
    'website'           : "https://bemosoft.odoo.com/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category'          : 'Tools',
    'version'           : '0.1',
    # any module necessary for this one to work correctly
    'depends'           : ['base','mail','bmo_batch_record', 'bmo_mrp', 'bmo_material_request'],
    # always loaded
    'data'              : [
                            'security/ir.model.access.csv',
                            'reports/report_dumping.xml',
                            'views/views.xml',
                            'views/master_dumping_view.xml',
                            'views/stock_picking.xml',
                            # 'views/templates.xml',
                            ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
