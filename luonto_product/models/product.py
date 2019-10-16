# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = "product.product"

    is_exclude = fields.Boolean(string="Is Excluded Variant",
                                store=True)


class ProductAttributeValue(models.Model):

    _inherit = "product.attribute.value"

    attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        relation='sub_attr',
        column1='parent_attr',
        column2='child_attr',
        string="Sub Attributes")
