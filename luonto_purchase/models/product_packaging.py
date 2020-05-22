# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    product_tmpl_id = fields.Many2one(comodel_name='product.template',
                                 string='Product Template',
                                 help='template to which this package is associated.',)
    label = fields.Char(string='Label in Pack')
    weight = fields.Float(string='Weight in Pack')
    volume = fields.Float(string='Volume in Pack')