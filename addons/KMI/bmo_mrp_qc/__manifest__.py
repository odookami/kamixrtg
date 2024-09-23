# -*- coding: utf-8 -*-
{
    'name'                  : "MRP QC KAMI",
    'summary'               : """
                                Short (1 phrase/line) summary of the module's purpose, used as
                                subtitle on modules listing or apps.openerp.com""",
    'description'           : """
                                Long description of module's purpose
                            """,
    'author'                : "bemosoft - tian",
    'website'               : "http://www.bemosoft.com",
    'category'              : 'Manufacturing/Manufacturing',
    'version'               : '14.0.1',
    'depends'               : ['base','bmo_mrp','mrp'],
    'data'                  : [ 
                                'security/group_security.xml',
                                'security/ir.model.access.csv',
                                'data/data.xml',
                                'data/data_record.xml',
                                'wizard/report_mrp_qc_summary.xml',
                                'wizard/report_mrp_qc.xml',
                                'views/config.xml',
                                'views/views.xml',
                                'views/menu_view.xml',
                            ],
}
