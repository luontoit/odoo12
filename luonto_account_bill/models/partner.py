from odoo import models, api, fields

class Partner(models.Model):
    _inherit="res.partner"

    c_type=fields.Many2one('luonto_account_bill.customer_type', string='Customer Type')