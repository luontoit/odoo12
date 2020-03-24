# -*- coding: utf-8 -*-


from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    seat_qty_for_freight = fields.Integer(string="Freight Qty")