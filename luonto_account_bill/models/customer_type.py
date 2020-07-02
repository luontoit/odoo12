from odoo import models, api, fields

class CustomerType(models.Model):
    _name="luonto_account_bill.customer_type"
    _description="Customer Type"

    name=fields.Char(string="Name")
    commission=fields.Float(string="Commission Percentage", widget="percentage")