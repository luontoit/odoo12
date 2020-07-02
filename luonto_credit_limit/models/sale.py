# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_credit_limit_exceeded = fields.Boolean(related="partner_id.is_credit_limit_exceeded")

<<<<<<< HEAD
    # @api.multi
=======
>>>>>>> 13.0-luonto-migration
    # def action_confirm(self):
    #     result = super(SaleOrder, self).action_confirm()
    #     for order in self:
    #         if order.is_credit_limit_exceeded:
    #             composer = self.env['mail.compose.message'].with_context(
    #                 active_id=order.id,
    #                 active_ids=order.ids,
    #                 active_model=self._name,
    #                 default_composition_mode='comment',
    #                 default_model=self._name,
    #                 default_res_id=order.id,
    #             ).create({'body': "Total Amount Due %s Over The Credit Limit %s" % (order.partner_id.current_credit, order.partner_id.credit_limit)})
    #             composer.send_mail()
    #     return result
