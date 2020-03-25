# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

class PriceRule(models.Model):
    _inherit = 'delivery.price.rule'

    variable = fields.Selection(selection_add=[('num_seats', 'Number of Seats')])
    variable_factor = fields.Selection(selection_add=[('num_seats', 'Number of Seats')])

class ProviderGrid(models.Model):
    _inherit = 'delivery.carrier'

    # Added num_seats a new condition, to calculate the number of frieght seats. 
    def _get_price_available(self, order):
        self.ensure_one()
        total = weight = volume = quantity = num_seats = 0
        total_delivery = 0.0
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty
            quantity += qty
            #################### change starts here######################
            num_seats += (int(line.product_id.seat_qty_for_freight) or 0.0)
            ################## ends here#########################
        total = (order.amount_total or 0.0) - total_delivery

        total = order.currency_id._convert(
            total, order.company_id.currency_id, order.company_id, order.date_order or fields.Date.today())
            ###################### change starts here #################################
        return self._get_price_from_picking(total, weight, volume, quantity, num_seats)
    
    def _get_price_from_picking(self, total, weight, volume, quantity, num_seats):
        price = 0.0
        criteria_found = False
        price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume * weight, 'quantity': quantity, 'num_seats': num_seats}
        ################################## ends here ######################
        for line in self.price_rule_ids:
            test = safe_eval(line.variable + line.operator + str(line.max_value), price_dict)
            if test:
                price = line.list_base_price + line.list_price * price_dict[line.variable_factor]
                criteria_found = True
                break
        if not criteria_found:
            raise UserError(_("No price rule matching this order; delivery cost cannot be computed."))

        return price