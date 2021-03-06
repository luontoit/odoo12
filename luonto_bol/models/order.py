# -*- coding: utf-8 -*-


from odoo import api, fields, models, _, SUPERUSER_ID
import datetime
import base64
import xlrd
from odoo.exceptions import UserError
import base64
import re

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight_term = fields.Selection([('Prepaid','Prepaid'),('Collect','Collect'),('3rd Party','3rd Party')], string="Freight Change Terms", related="carrier_id.freight_term")
    third_party_id = fields.Many2one('res.partner', string="3rd Party")

    def print_bol_report(self):
        render_pdf = self.env.ref('luonto_bol.action_sale_bol_report').render_qweb_pdf(res_ids=self.ids)[0]
        pdf = base64.b64encode(render_pdf)
        filename = self.mapped('name')
        for rec in self:
            for do in rec.picking_ids:
                if do.state == 'done' and do.picking_type_id.code == 'outgoing' and do.include_bol == True:
                    post_vals = {
                        'body': ' Bill of lading for ' + ', '.join(filename),
                        'attachments': [('BOL' + '_'.join(filename) + '.pdf', render_pdf)],
                    }
                    do.message_post(**post_vals)
                    do.include_bol = False
            post_vals = {
                'body': ('Bill of lading for ' + ', '.join(filename)),
                'attachments': [('BOL ' + '_'.join(filename) + '.pdf', render_pdf)],
            }
            rec.message_post(**post_vals)
            
class ReportBOLSale(models.AbstractModel):
    
    _name = 'report.luonto_bol.bol_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        orders = self.env['sale.order'].browse(docids)

        recent_date = self.env['stock.picking'].search([('sale_id','in',docids),('state','=','done'),('picking_type_id.code','=','outgoing'),('include_bol','=',True)], order="date_done DESC", limit=1).date_done
        print(recent_date, '\n\n\n')
        if not recent_date:
            raise UserError(_("Effective Delivery Order Date is not in the same day"))
        range_date = recent_date - datetime.timedelta(days=5)
        range_date = datetime.datetime.strftime(range_date, '%Y-%m-%d')
        range_date = datetime.datetime.strptime(range_date, '%Y-%m-%d')
        
        company = set()
        carrier = set()
        shipping = set()
        invoice = set()
        freight = set()
        third_party = False

        stock = {'qty': 0, 'type':[], 'volume':0, 'seat':0, 'weight':0, 'package':0}
        for rec in orders:
            if rec.third_party_id:
                third_party = rec.third_party_id
            company.add(rec.partner_id)
            if rec.carrier_id and rec.carrier_id.company_name:
                carrier.add(rec.carrier_id.company_name)
            else:
                carrier.add("")
            
            if rec.freight_term:
                freight.add(rec.freight_term)

            if rec.partner_shipping_id:
                shipping.add(rec.partner_shipping_id)

            if rec.partner_invoice_id:
                invoice.add(rec.partner_invoice_id)

            for do in rec.picking_ids:
                if do.state == 'done' and do.picking_type_id.code == 'outgoing' and do.include_bol == True:
                    if do.date_done >= range_date and do.date_done <= recent_date:
                        for move in do.move_line_ids_without_package:
                            if move.product_uom_id and move.product_uom_id.name not in stock['type']:
                                stock['type'].append(move.product_uom_id.name)
                        stock['qty'] += do.total_qty
                        stock['volume'] += do.total_volume
                        stock['seat'] += do.total_seat
                        stock['weight'] += do.weight
                        stock['package'] += do.total_package
                    else:
                        raise UserError(_("Effective Delivery Order Date is not in the same day"))

        
        if not len(company) == 1 or not len(carrier) <= 1:
            raise UserError(_("Sale orders must have the same partner_id and carrier_id."))
        
        if len(carrier) < 1:
            carrier = ""
        else:
            carrier = list(carrier)[0]

        if len(freight) < 1:
            freight = ""
        else:
            freight = list(freight)[0]
        return {
            # 'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'orders': orders,
            'from_company':self.env.company.partner_id,
            'to_company': self.env['res.partner'].sudo().search([('id','=',list(company)[0].id)])[0],
            'carrier':carrier,
            'shipping': list(shipping),
            'invoice': list(invoice),
            'stock': stock,
            'freight_term': freight,
            'company':self.env.company,
            'third_party': third_party
        }
