# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    company_name = fields.Char(String="Company Name")
    freight_term = fields.Selection([('Prepaid','Prepaid'),('Collect','Collect'),('3rd Party','3rd Party')], string="Freight Change Terms", )