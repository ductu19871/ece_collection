# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.addons.ndt_ghn_extend.models.ghn_api import get_service

# class RP(models.Model):
#     _inherit = 'res.partner'

#     def test_yml(self):
#         self.name = self.name + ' 2'


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    height = fields.Integer("Chiều cao")
    length = fields.Integer("Chiều dài")
    width = fields.Integer("Chiều rộng")
    weight = fields.Integer('Trọng lượng (gram)')
    delivery_service_type_id = fields.Many2one('ndt.delivery.service.type','Loại dịch vụ')
    delivery_payment_type_id = fields.Selection([('1','Cửa hàng'), ('2','Người mua')], default='2',string="Người trả phí vận chuyển")
    delivery_cod_amount = fields.Monetary(string="Số tiền thu hộ")
    delivery_so_line_id = fields.Many2one('sale.order.line', compute='_compute_delivery_so_line_id', string="SO item Khách đặt vận chuyển")
    # is_use_api_shipping = fields.Boolean(related='carrier_id.is_use_api_shipping')
    delivery_type = fields.Selection(related='carrier_id.delivery_type')

    def calculate_dimension(self):
        total, weight, volume, quantity, self.height, self.width, self.length = \
            self._calculate_dimension()
        self.weight = weight#*1000
        self.height, self.width, self.length = 10, 10, 10
        # res = {'warning': {
        #         'title': str((self.total, self.weight, self.volume, self.quantity, self.height, self.width, self.length)),
        #         'message':str((self.total, self.weight, self.volume, self.quantity, self.height, self.width, self.length))
        # }
        # }
        # return res


    def _calculate_dimension(self):
        order = self
        total = weight = volume = quantity = height = width = length = 0
        total_delivery = 0.0
        for count, line in enumerate(order.order_line):
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            volume += (line.product_id.volume or 0.0) * qty


            weight += (line.product_id.weight or 0.0) * qty


            quantity += qty
        return total, weight, volume, quantity, height, width, length
    

    @api.depends('order_line','carrier_id')
    # @api.one
    def _compute_delivery_so_line_id(self):
        line = self.env['sale.order.line'].search([('order_id','=',self.id),
            ('product_id','=',self.carrier_id.product_id.id)], limit=1, order='id desc')
        self.delivery_so_line_id = line
        
    # @api.onchange('delivery_service_type_id', 'carrier_id', 'warehouse_id', 'partner_shipping_id')
    # def onchange_cal_delivery_price(self):
    #     if self.carrier_id == self.env.ref('ndt_ghn_extend.giao_hang_nhanh_delivery_carrier'):
    #         self.delivery_price = self.env['delivery.carrier'].cal_ghn_fee(self)
    #         print ('***self.delivery_price***', self.delivery_price)


    @api.onchange('carrier_id')
    def onchange_carrier_id(self): # ghi đè hàm gốc, cần xem lại
        if self.state in ('draft', 'sent'):
            self.delivery_price = 0.0
            self.delivery_rating_success = False
            self.delivery_message = False


    @api.onchange('carrier_id','warehouse_id','partner_shipping_id')
    def onchange_cal_domain_delivery_service_type_id(self):
        if self.carrier_id and self.warehouse_id:
            token = self.env['ir.config_parameter'].sudo().get_param('ndt_ghn_extend.ghn_token')
            ghn_shop_id = self.warehouse_id.ghn_shop_id
            from_district = int(self.warehouse_id.partner_id.district_id.ghn_id)
            to_district_id = int(self.partner_shipping_id.district_id.ghn_id)
            ghn_rt = get_service(token, ghn_shop_id, from_district, to_district_id)
            service_ids = [server['service_type_id'] for server in ghn_rt]
            value = self.env['ndt.delivery.service.type'].search([('code','=',service_ids[-1])])
            return {'domain': {'delivery_service_type_id': [('code', 'in', service_ids)]},
                    'value': {'delivery_service_type_id':value.id}
            }


    @api.onchange('amount_total','delivery_payment_type_id')
    def onchage_cal_delivery_cod_amount(self):
        if self.delivery_payment_type_id =='2':
            self.delivery_cod_amount = self.amount_total
        else:
            self.delivery_cod_amount = 0


    # @api.multi
    # def action_confirm(self):
    #     res = super(SaleOrder, self.with_context(default_weight=self.weight,
    #         default_length=self.length, default_height=self.height, default_width=self.width)).action_confirm()
        
    #     return res

# {
#     "code": 200,
#     "message": "Success",
#     "data":[
#     {
#     "service_id":53322
#     "short_name":"Đi bộ"
#     "service_type_id":1
#     },
#      {
#     "service_id":53320
#     "short_name":"Bay"
#     "service_type_id":2
#     },
#      {
#     "service_id":53324
#     "short_name":"Cồng kềnh - Nặng"
#     "service_type_id":0
#     }
#     ]
# }


   
    
        # return 
