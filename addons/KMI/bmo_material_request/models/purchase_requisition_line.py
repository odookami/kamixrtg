# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class MaterialPurchaseRequisitionLine(models.Model):
    _name = "material.purchase.requisition.line"
    _description = 'Material Purchase Requisition Lines'

    
    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions', 
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    lot_producing_id = fields.Many2one(
        'stock.production.lot', string='Lot/Serial Number', copy=False,
        domain="[('product_id', '=', product_id)]"
    )
    qty = fields.Float(
        string='Quantity',
        default=1,
        required=True,
        digits=(30,4),
    )
    uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    partner_id = fields.Many2many(
        'res.partner',
        string='Vendors',
    )
    requisition_type = fields.Selection(
        selection=[
                    ('internal','Internal Picking'),
        ],
        string='Requisition Action',
        # ! set to internal
        default='internal',
        required=True,
    )
    is_available = fields.Boolean(
        string='Available') 
    move_id = fields.Many2one(
        'stock.move', string='Components')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
