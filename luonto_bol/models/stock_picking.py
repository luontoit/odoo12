# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_volume = fields.Float(string="Total Volume", compute="_compute_total_measures", default=0.0)
    total_seat = fields.Float(string="Total Seat Qty", compute="_compute_total_measures", default=0.0,)

    total_qty = fields.Float(string="Total Qty", compute="_compute_total_measures",  default=0.0)

    @api.depends('move_line_ids_without_package')
    def _compute_total_measures(self):
        for picking in self:
            vol = 0
            qty = 0
            seat = 0
            for move in picking.move_line_ids_without_package:
                if picking.state == 'done':
                    vol += move.product_id.volume * move.qty_done
                    qty += move.qty_done
                    seat += move.product_id.seat_qty_for_freight * move.qty_done

                
            picking.total_volume = vol
            picking.total_qty += qty
            picking.total_seat += seat