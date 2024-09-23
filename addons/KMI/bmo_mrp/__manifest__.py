# -*- coding: utf-8 -*-
{
    'name'              : "MRP - KAMI",
    'summary'           : """
                            Short (1 phrase/line) summary of the module's purpose, used as
                            subtitle on modules listing or apps.openerp.com""",
    'description'       : """
                                Long description of module's purpose
                            """,
    'author'            : "bemosoft - tian",
    'website'           : "http://www.bemosoft.com",
    'category'          : 'Manufacturing/Manufacturing',
    'version'           : '14.0.1',
    'depends'           : ['base', 'mrp','product','bmo_inventory'],
    'data'              : [
                            'security/security.xml',
                            'security/ir.model.access.csv',
                            'wizard/revisi_reason_wizard_view.xml',
                            'views/type_category_view.xml',
                            'data/data.xml',
                            'data/seq.xml',
                            'views/res_config_settings_views.xml',
                            'views/product_view.xml',
                            'views/stock_production_lot_view.xml',
                            'views/mrp_okp_view.xml',
                            'views/number_batch_proses_view.xml',
                            'views/bom_view.xml',
                            'views/scrap_view.xml',
                            'views/mrp_production_batch_view.xml',
                            'views/mrp_production_view.xml',
                            'wizard/import_mrp_wizard_view.xml',
                            'reports/report_mrp_mixing.xml',
                            'data/cron.xml',
                          ],
}
