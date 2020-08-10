# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    label = fields.Char(string='Pack Label')

    @api.depends('quant_ids')
    def _compute_weight(self):
        for package in self:
            weight = 0.0
            if self.env.context.get('picking_id'):
                # TODO: potential bottleneck: N packages = N queries, use groupby ?
                current_picking_move_line_ids = self.env['stock.move.line'].search([
                    ('result_package_id', '=', package.id),
                    ('picking_id', '=', self.env.context['picking_id'])
                ])
                for ml in current_picking_move_line_ids:
                    if package.packaging_id and package.packaging_id.product_tmpl_id:
                        weight += package.packaging_id.weight
                    else:
                        weight += ml.product_uom_id._compute_quantity(
                            ml.qty_done, ml.product_id.uom_id) * ml.product_id.weight
            else:
                if package.packaging_id and package.packaging_id.product_tmpl_id:
                    weight += package.packaging_id.weight
                else:
                    for quant in package.quant_ids:
                        weight += quant.quantity * quant.product_id.weight
            package.weight = weight
