# -*- coding: utf-8 -*-

# Base on Charlie.Huang, rt_one2many_multi_selection
# Created on 2018-08-15
# author: 广州尚鹏，http://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Odoo在线中文用户手册（长期更新）
# http://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# http://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# http://www.sunpop.cn/odoo10_developer_document_offline/
# description:

{
    'name': "App One2Many multi add widget, batch add product in Sale,Purchase,Inventory,MRP,Account Invoice Order Line, 批量增加产品",
    'version': '11.0.8.15',
    'author': 'Sunpop.cn',
    'category': 'Base',
    'website': 'http://www.sunpop.cn',
    'license': 'LGPL-3',
    'sequence': 2,
    'summary': """
    multi add, multi add products, batch add, batch add products, mass add, mass add product. multi add partner, multi add order line. multi add any object in one2many tree view.enable in Sale Order, Purchase Order, BOM, Stock Picking or Account.
    """,
    'description': """
        This module very useful and time saver if you want to add multiple products on single click.
        And you can also make any one2many field to get this feature by config the xml.

    1. 一键快速将多个产品加到销售订单中。
    2. 一键快速将多个产品加到采购订单中。
    3. 一键快速将多个产品加到制造Bom中。
    4. 一键快速将多个产品加到库存调拨单中。
    5. 一键快速将多个产品加到客户收款单、供应商帐单中。
    6. 通过xml配置，可以批量加入指定对象至各种one2many单据明细。
    7. 在多选的弹出页可以进行过滤、分组，然后批量加入。
    """,
    'price': 68.00,
    'currency': 'EUR',
    'depends': [
        'base',
        # uncomment follow 5 line to active relate function
        # 'sale_management',
        # 'purchase',
        'stock',
        # 'mrp',
        # 'account',
        # 'purchase_requisition'
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'views/templates.xml',
        # uncomment follow line to active relate function
        'views/views.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'css': [
    ],
    'qweb': [
    ],
    'js': [
    ],
    'images': [
    ],
    'post_load': None,
    'post_init_hook': None,
    'installable': True,
    'application': True,
    'auto_install': False,
}
