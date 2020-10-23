# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_volume = fields.Float(string="Total Volume", compute="_compute_total_measures", default=0.0, store=True)
    total_seat = fields.Float(string="Total Seat Qty", compute="_compute_total_measures", default=0.0, store=True)
    total_package = fields.Float(string="Total Packages", compute="_compute_total_measures", default=0.0, store=True)
    total_qty = fields.Float(string="Total Qty", compute="_compute_total_measures",  default=0.0, store=True)
    include_bol = fields.Boolean(string="Include BOL", default=False)

    def action_done(self):
        self.include_bol = True
        super(StockPicking, self).action_done()

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
                else:
                    vol += move.product_id.volume * move.product_uom_qty
                    qty += move.product_uom_qty
                    seat += move.product_id.seat_qty_for_freight * move.product_uom_qty
                
            picking.total_volume = vol
            picking.total_qty += qty
            picking.total_seat += seat
            picking.total_package = len(picking.move_line_ids_without_package)