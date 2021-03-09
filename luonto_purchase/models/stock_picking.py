# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, float_round

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _put_in_pack(self, move_line_ids):
        self.ensure_one()
        if self.env.context.get('split_packages'):
            package = False
            for pick in self:
                move_lines_to_pack = self.env['stock.move.line']

                precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                if float_is_zero(move_line_ids[0].qty_done, precision_digits=precision_digits):
                    for line in move_line_ids:
                        line.qty_done = line.product_uom_qty

                for ml in move_line_ids:
                    package = self.env['stock.quant.package'].create({
                        'packaging_id': ml.pt_package_id and ml.pt_package_id.id or False,
                        'label': ml.pt_package_id and ml.pt_package_id.label or '',
                    })
                    if float_compare(ml.qty_done, ml.product_uom_qty,
                                     precision_rounding=ml.product_uom_id.rounding) >= 0:
                        ml.result_package_id = package.id
                    else:
                        quantity_left_todo = float_round(
                            ml.product_uom_qty - ml.qty_done,
                            precision_rounding=ml.product_uom_id.rounding,
                            rounding_method='UP')
                        done_to_keep = ml.qty_done
                        new_move_line = ml.copy(
                            default={'product_uom_qty': 0, 'qty_done': ml.qty_done})
                        ml.write({'product_uom_qty': quantity_left_todo, 'qty_done': 0.0})
                        new_move_line.write({'product_uom_qty': done_to_keep})
                        new_move_line.result_package_id = package.id
                    package_level = self.env['stock.package_level'].create({
                        'package_id': package.id,
                        'picking_id': pick.id,
                        'location_id': False,
                        'location_dest_id': move_line_ids.mapped('location_dest_id').id,
                        'move_line_ids': [(6, 0, move_lines_to_pack.ids)],
                        'company_id': pick.company_id.id,
                    })
            return package
        else:
            return super(StockPicking, self)._put_in_pack(move_line_ids)
    
    def split_in_pack(self):
        StockMoveLine = self.env['stock.move.line']
        if self.move_line_ids:
            self.move_line_ids.unlink()
        split = False
        for move in self.move_lines:
            if int(move.product_id.x_studio_package_qty) > 1 and move.product_id.pt_packaging_ids:
                split = True
                if len(move.product_id.pt_packaging_ids) != int(move.product_id.x_studio_package_qty):
                    raise UserError(_("Package Quantity does not match for product template %s." % (move.product_id.name)))
                for i in range(int(move.product_uom_qty)):
                    for packaging in move.product_id.pt_packaging_ids:
                        StockMoveLine.create({
                            'move_id': move.id,
                            'picking_id': self.id,
                            'product_id': move.product_id.id,
                            'location_id': move.location_id.id,
                            'location_dest_id': move.location_dest_id.id,
                            'product_uom_id': move.product_id.uom_id.id,
                            'product_uom_qty': packaging.qty,
                            'pt_package_id': packaging.id,
                            'qty_done': packaging.qty
                        })
                move._recompute_state()
        return super(StockPicking, self.with_context({'split_packages': split})).action_put_in_pack()
