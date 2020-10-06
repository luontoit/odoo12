# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    company_name = fields.Char(String="Company Name")