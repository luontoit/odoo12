# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_credit_limit_exceeded = fields.Boolean(related="partner_id.is_credit_limit_exceeded")
