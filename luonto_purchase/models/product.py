# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pt_packaging_ids = fields.One2many(comodel_name='product.packaging', inverse_name='product_tmpl_id',
                                       help='Packaging in which the product is received.')