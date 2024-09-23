# -*- coding: utf-8 -*-
{
	'name'          : "Inventory",
	'summary'       : """
						Short (1 phrase/line) summary of the module's purpose, used as
						subtitle on modules listing or apps.openerp.com""",
	'description'   : """
							Long description of module's purpose
						""",

	'author'        : "bemosoft",
	'website'       : "https://bemosoft.odoo.com/",
	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category'      : 'Inventory',
	'version'       : '14.0.1',

	# any module necessary for this one to work correctly
	'depends'       : ['base','sale','stock','product','hr', 'product_expiry','mrp','stock_account'],

	# always loaded
	'data'          : [
						'security/group_security.xml',
						'security/ir.model.access.csv',
						'security/ir_rule.xml',
						'views/product_group.xml',
						'views/master_type_view.xml',
						'data/data.xml',
						'views/base_users_views.xml',
						'views/stock_location_view.xml',
						'views/stock_quant_view.xml',
						'views/stock_move.xml',
						'views/stock_production_lot_view.xml',
						'views/product_view.xml',
						'views/revisi_onhand.xml',
						# 'wizard/update_lot_number.xml',
						'wizard/import_picking_wizard_view.xml',
						'wizard/import_detail_operation_wizard.xml',
						'wizard/wizard_tags_location_view.xml',
						'wizard/show_status.xml',
						'views/picking.xml',
						'views/stock_move_line.xml',
						'views/stock_scrap_view.xml',
						'views/stock_inventory_view.xml',
						'wizard/sales_daybook_report_product_category_wizard.xml',
						'wizard/stock_card_in.xml',
						'wizard/stock_card_out.xml',
						'wizard/import_sml_do.xml',
						'wizard/wizard_material_transaction.xml',
						'wizard/report_valuation_wizard_view.xml',
						'report/report_pdf.xml',
						'report/inventory_valuation_detail_template.xml',
					],
}
