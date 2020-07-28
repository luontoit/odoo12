from odoo import models, api, fields
from datetime import date

class AccountMove(models.Model):
    _inherit="account.move"

    v_bill_id=fields.Many2one('account.move', string="Vendor Bill")
    invoice_id=fields.Many2one('account.move', string="Invoice Source")

    def action_invoice_paid(self):
        if self.v_bill_id:
            for line in self.v_bill_id.line_ids:
                line.date_maturity = date.today()

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.partner_id.c_type and self.invoice_user_id and self.type == "out_invoice":
            sum = 0
            for line in self.invoice_line_ids:
                if line.product_id.type == "product":
                    sum += line.price_subtotal
            if sum > 0:
                move_dic = [
                    {
                        'type': 'in_invoice',
                        'partner_id': self.invoice_user_id.partner_id.id,
                        'invoice_id': self.id,
                        'journal_id': self.env['account.journal'].search([('code', '=', 'BILL')]).id,
                        'state': 'draft',
                        'invoice_date': self.invoice_date,
                        'date': self.invoice_date
                    }
                ]
                jn_entry = self.create(move_dic)
                lines = [
                    {
                        'name': 'Commission',
                        'quantity': 1.00,
                        'account_id': self.env['account.account'].search([('code', '=', '6010')]).id,
                        'move_id': jn_entry.id,
                        'price_unit': sum*self.partner_id.c_type.commission
                    },
                    {
                        'account_id': self.env['account.account'].search([('code', '=', '2010')]).id,
                        'move_id': jn_entry.id,
                        'credit': sum*self.partner_id.c_type.commission
                    }
                ]
            
                inv_lines = self.env['account.move.line'].create(lines)
                self.v_bill_id = jn_entry.id
                jn_entry.update({'invoice_line_ids': [inv_lines[0].id]})
                self.v_bill_id.action_post()
        return res