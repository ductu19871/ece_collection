# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.addons.ndt_ghn_extend.models.ghn_api import fetch_ghn_order, get_ghn_order_info, cancel_ghn_shipment, ghn_update_order, get_fee_of_order
import requests


class Stockpicking(models.Model):
    _inherit = 'stock.picking'

    height = fields.Integer("Chiều cao")
    length = fields.Integer("Chiều dài")
    width = fields.Integer("Chiều rộng")
    shipping_status = fields.Char(related='delivery_purchase_id.vendor_order_state', readonly=True, string="Trạng thái đối tác")
    delivery_purchase_id = fields.Many2one('purchase.order', readonly=True, string="PO vận chuyển")

    carrier_order_info = fields.Text()
    carrier_update_info = fields.Text()
    currency_id = fields.Many2one('res.currency', related='delivery_purchase_id.currency_id')
    delivery_amount_total = fields.Monetary(related='delivery_purchase_id.amount_total',string="Phí vận chuyển")
    delivery_so_line_id = fields.Many2one('sale.order.line', related='sale_id.delivery_so_line_id', string="SO item Khách đặt vận chuyển")

    adjustment_weight = fields.Float("Trọng lượng (gram)")

    def stock_update_shipment(self):
        self.carrier_id.update_shipment(self)
           
    def stock_cancel_shipment(self):
        self.carrier_id.cancel_shipment(self)

    def stock_get_shipping_order_status(self):
        self.carrier_id.get_shipping_order_status(self)

    def stock_order_shipping(self):
        if self.carrier_id:
            self.carrier_id.order_shipping(self)
        
class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    ghn_shop_id = fields.Integer('GHN shop')

class Product(models.Model):
    _inherit = 'product.template'

    # weight = fields.Integer('Weight (gram)')
    length = fields.Integer('Length (mm)')
    width = fields.Integer('Width (mm)')
    height = fields.Integer('Height (mm)')

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        rs = super()._get_new_picking_values()
        dimession = {
            'height':self.group_id.sale_id.height,
            'width':self.group_id.sale_id.width,
            'length':self.group_id.sale_id.length,
            'adjustment_weight':self.group_id.sale_id.weight,
        }
        rs.update(dimession)
        return rs
         