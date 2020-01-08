# -*- coding: utf-8 -*-

import openerp.addons.decimal_precision as dp
from openerp import _, api, fields, models


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    product_uop_qty = fields.Float(
        string='Quantity (UOP)',
        digits=dp.get_precision('Product Unit of Measure'))
    product_uop = fields.Many2one(
        comodel_name="product.uom", string='Product UOP', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(StockTransferDetails, self).default_get(fields)
        for item in res.get('item_ids'):
            pack_op = self.env['stock.pack.operation'].browse(
                item.get('packop_id'))
            if pack_op.exists() and len(pack_op.linked_move_operation_ids) == 1:
                linked_move_operation = pack_op.linked_move_operation_ids[:1]
                p_uop = linked_move_operation.move_id.product_uop
                p_uop_qty = linked_move_operation.move_id.product_uop_qty
                item.update({
                    'product_uop': p_uop.id,
                    'product_uop_qty': p_uop_qty
                })
        return res


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    product_uop_qty = fields.Float(
        string='Quantity (UOP)',
        digits=dp.get_precision('Product Unit of Measure'))
    product_uop = fields.Many2one(
        comodel_name="product.uom", string='Product UOP', readonly=True)

    @api.onchange('product_uop_qty')
    def _onchange_product_uop_qty(self):
        warning = {}
        pack_operation = self.packop_id
        if len(pack_operation.linked_move_operation_ids) > 1:
            warning.update({
                'title': _('Warning'),
                'message': _("The product_uop_qty changing do have any effect "
                             "in case the linked moves are more than one")})
        linked_move_operation = pack_operation.linked_move_operation_ids[:1]
        if linked_move_operation:
            p_qty = linked_move_operation.move_id.product_qty
            p_uop_qty = linked_move_operation.move_id.product_uop_qty
            self.quantity = p_qty * (self.product_uop_qty / p_uop_qty)

        return {'warning': warning}

    @api.onchange('quantity')
    def _onchange_quantity(self):
        warning = {}
        pack_operation = self.packop_id
        if len(pack_operation.linked_move_operation_ids) > 1:
            warning.update({
                'title': _('Warning'),
                'message': _("The product_uop_qty changing do have any effect "
                             "in case the linked moves are more than one")})
        linked_move_operation = pack_operation.linked_move_operation_ids[:1]
        if linked_move_operation:
            p_qty = linked_move_operation.move_id.product_uom_qty
            p_uop_qty = linked_move_operation.move_id.product_uop_qty
            self.product_uop_qty = p_uop_qty * (self.quantity / p_qty)

        return {'warning': warning}
