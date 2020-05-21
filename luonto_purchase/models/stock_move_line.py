# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pt_package_id = fields.Many2one(comodel_name='product.packaging', copy=False)