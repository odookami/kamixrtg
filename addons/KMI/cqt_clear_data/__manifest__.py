# -*- coding: utf-8 -*-
{
    'name': "Mass Clear Data | Mass Remove Data",
    'version': '14.0.0.0.0',
    'description': "User can easily clear the data",
    'author': 'CRON QUOTECH',
    'support': 'cronquotech@gmail.com',
    'website': "https://cronquotech.odoo.com",
    'summary': '''
    Clean, Clear, Delete, Clean Data, data clean,
    Clear data, data clear, Delete Data,
    Bulk, Bulk delete, bulk clear, clear bulk,
    multi clear, multi remove, multi clean,
    SQl, SQl delete, Delete records,
    Delete all, all delete, data cleaner, DB cleaner, cleaner,
    Database, Database cleaner, bulk cleaner, tool, DB tool, DB delete tool, invoice, invoices, customer,
    payments, vendor, data delete, delete data''',
    'category': 'Tools',
    'depends': ['base'],
    'license': 'OPL-1',
    'price': 2.00,
    'currency': "USD",
    'data': [
        # 'security/ir.model.access.csv',
        'security/clear_data_security.xml',
        'wizard/cqt_clear_data_view.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False
}
