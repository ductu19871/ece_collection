# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
from odoo.exceptions import UserError
from odoo.addons.ndt_ghn_extend.models.ghn_api import fetch_ghn_fee
from odoo.addons.ndt_ghn_extend.models.ghn_api import fetch_ghn_order, get_ghn_order_info, cancel_ghn_shipment, ghn_update_order, get_fee_of_order
import inspect
class ProviderGridNDT(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('base_on_api', 'Dựa trên API')], string='Loại giao hàng',ondelete={'base_on_api':'cascade'})
    # is_use_api_shipping = fields.Boolean()

    def rate_shipment(self, order,company=None):
        # print ('self._context rate_shipment**', self._context)
        # print ('caller name: rate_shipment', inspect.stack()[1][3])
        # print ('*********rate_shipment.*******', company)
        ''' Compute the price of the order shipment

        :param order: record of sale.order
        :return dict: {'success': boolean,
                       'price': a float,
                       'error_message': a string containing an error message,
                       'warning_message': a string containing a warning message}
                       # TODO maybe the currency code?
        '''
        self.ensure_one()
        if hasattr(self, '%s_rate_shipment' % self.delivery_type):
            res = getattr(self, '%s_rate_shipment' % self.delivery_type)(order)
            # apply margin on computed price
            res['price'] = float(res['price']) * (1.0 + (self.margin / 100.0))
            # save the real price in case a free_over rule overide it to 0
            res['carrier_price'] = res['price']
            # free when order is large enough
            if res['success'] and self.free_over and order._compute_amount_total_without_delivery() >= self.amount:
                res['warning_message'] = _('The shipping is free since the order amount exceeds %.2f.') % (self.amount)
                res['price'] = 0.0
            return res

    def base_on_api_rate_shipment(self, order):
        print ('******self._context base_on_api_rate_shipment******', self._context)
        # raise ValueError('adslkfldf')
        
        carrier = self._match_address(order.partner_shipping_id)
        if not carrier:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: this delivery method is not available for this address.'),
                    'warning_message': False}

        try:
            price_unit = self._get_price_available_api(order)
        except UserError as e:
            return {'success': False,
                    'price': 0.0,
                    'error_message': e.name,
                    'warning_message': False}
        if order.company_id.currency_id.id != order.pricelist_id.currency_id.id:
            price_unit = order.company_id.currency_id.with_context(date=order.date_order).compute(price_unit, order.pricelist_id.currency_id)

        rs =  {'success': True,
                'price': price_unit,
                'error_message': False,
                'warning_message': False,
                }
        return rs


    #end 14/10

    def _get_price_available_api(self, order):
        self.ensure_one()
        total = weight = volume = quantity = 0
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
        total = (order.amount_total or 0.0) - total_delivery
        total = order.currency_id.with_context(date=order.date_order).compute(total, order.company_id.currency_id)
        return self._get_price_from_picking_api(order, total, weight, volume, quantity)


    def _get_price_from_picking_api(self, order, total, weight, volume, quantity):
        price = None
        if self == self.env.ref('ndt_ghn_extend.giao_hang_nhanh_delivery_carrier'):
            price = self.cal_ghn_fee(order, weight)
        
        return price


    def cal_ghn_fee(self, order, weight):
        price = None
        token = self.env['ir.config_parameter'].sudo().get_param('ndt_ghn_extend.ghn_token')
        shop_id = order.warehouse_id.ghn_shop_id
        service_id, service_type_id = False, int(order.delivery_service_type_id.code)
        # print ('**service_type_id**', service_type_id)
        from_district = int(order.warehouse_id.partner_id.district_id.ghn_district_id)# ghn_district_id is tring
        # print ('**from_district***', from_district)
        partner_shipping_id = order.partner_shipping_id or order.partner_id
        to_district_id = partner_shipping_id.district_id.ghn_district_id# ghn_district_id is tring
        to_ward_code = partner_shipping_id.ward_id.ghn_code
        print ('**to_ward_code**', to_ward_code)
        
        #
        company_id = self._context.get('web_company')
        print ('*company_id từ context', company_id,"isinstance(company_id, int)",isinstance(company_id, int),'type(company_id)',type(company_id))
        if isinstance(company_id, int):
            # from_ward = self.env['res.company'].browse(company_id).ward_ghn_code
            shop_id = self.env['res.company'].browse(company_id).ghn_shop_id


        

        # demo_ward = self.env['res.country.ward'].browse(1)
        # to_ward_code = demo_ward.ghn_code
        # to_district_id = demo_ward.district_id.ghn_id

        # print ('demo_ward, to_ward_code, to_district_id', demo_ward, to_ward_code, to_district_id )
       
        ghn_rs = fetch_ghn_fee(token, shop_id, to_district_id, to_ward_code,
            service_type_id or 2, service_id, from_district,  height= order.height or 10, 
            length=order.length or 10, width=order.width or 10, weight=int(order.weight or weight),
        )


        price = float(ghn_rs['total'])
        print ('company_id', company_id, '**shop_id**', shop_id,'price',price)
        return price


    def order_shipping(self, picking): # viết mới, ko có ở hàm gốc
        self.ensure_one()
        if hasattr(self, '%s_order_shipping' % self.delivery_type):
            return getattr(self, '%s_order_shipping' % self.delivery_type)(picking)


    def base_on_api_order_shipping(self, picking): # không có ở hàm gốc
        if self == self.env.ref('ndt_ghn_extend.giao_hang_nhanh_delivery_carrier'):
            shipping_status, carrier_tracking_ref, carrier_tracking_url, carrier_price = self.ghn_order(picking)
        self.create_carrier_po(picking, shipping_status, carrier_tracking_ref, carrier_tracking_url, carrier_price)
   


    def base_on_api_cancel_shipment(self, pickings): # already implent
        carrier_tracking_ref = pickings.carrier_tracking_ref
        if carrier_tracking_ref:
            token = self.env['ir.config_parameter'].sudo().get_param('ndt_ghn_extend.ghn_token')
            if self == self.env.ref('ndt_ghn_extend.giao_hang_nhanh_delivery_carrier'):
                cancel_ghn_shipment(token, [carrier_tracking_ref])
                cancel_status = 'cancel'
                pickings.delivery_purchase_id.vendor_order_state = cancel_status
                pickings.delivery_purchase_id.button_cancel()


    def update_shipment(self, picking): # không có ở gốc
        carrier_update_info = False
        if picking.carrier_tracking_ref:
            if self == self.env.ref('ndt_ghn_extend.giao_hang_nhanh_delivery_carrier'):
                token = self.env['ir.config_parameter'].sudo().get_param('ndt_ghn_extend.ghn_token')
                update_data = {
                    'height': int(picking.height), 
                    'length': int(picking.length),
                    'width': int(picking.width), 
                    'weight': int(picking.weight)
                    }
                rt = ghn_update_order(token, picking.carrier_tracking_ref, update_data)
                carrier_update_info = get_ghn_order_info(token, picking.carrier_tracking_ref)
                price_info = get_fee_of_order(token, picking.carrier_tracking_ref)
                price = price_info['detail']['main_service']
                picking.delivery_purchase_id.order_line.price_unit = price
                # carrier_update_info = 'đã update giá'
                # rs = 'info:%s,price_info:%s, price:%s'%(info, price_info, price)
            picking.carrier_update_info = carrier_update_info

    def get_shipping_order_status(self, picking): # không có ở hàm gốc
        if picking.carrier_tracking_ref:
            token = self.env['ir.config_parameter'].sudo().get_param('ndt_ghn_extend.ghn_token')
            info = get_ghn_order_info(token, picking.carrier_tracking_ref)
            shipping_status = info['status']
            picking.delivery_purchase_id.vendor_order_state = shipping_status

    def base_on_api_get_tracking_link(self, picking):
        self.ensure_one()
        if self == self.env.ref('ndt_ghn_extend.giao_hang_nhanh_delivery_carrier'):
            carrier_tracking_url = 'https://donhang.ghn.vn/?order_code=' + picking.carrier_tracking_ref
            return carrier_tracking_url
        


    def ghn_order(self, picking):
        if picking.delivery_purchase_id and picking.delivery_purchase_id.vendor_order_state != 'cancel':
            raise UserError('Bạn phải xóa đơn giao vận trước khi tạo lại đơn giao vận')
        sale_id = picking.sale_id
        if not sale_id:
            raise UserError('Không có Báo giá gốc cho Picking này')
        to_district_id = int(sale_id.partner_shipping_id.district_id.ghn_id)
        to_ward_code = sale_id.partner_shipping_id.ward_id.ghn_code 
        to_address = sale_id.partner_shipping_id.street
        token = self.env['ir.config_parameter'].sudo().get_param('ndt_ghn_extend.ghn_token')
        shop_id = sale_id.warehouse_id.ghn_shop_id
                    
        service_id = None
        service_type_id = int(sale_id.delivery_service_type_id.code)
        items = []
        for stock_move in picking.move_lines:
            item = {}
            item['name'] = stock_move.product_id.name
            item['quantity'] = int(stock_move.quantity_done) or 1
            items.append(item)
        to_name = sale_id.partner_shipping_id.name
        to_phone = sale_id.partner_shipping_id.phone
        if not to_phone:
            raise UserError('Người nhận không có số phone')# cái này nên valid bên SO sát hơn.
        order_rs = fetch_ghn_order(token, shop_id, to_district_id,
            to_ward_code, 
            to_address,
            service_id,
            service_type_id,
            int(sale_id.delivery_payment_type_id),
            int(sale_id.delivery_cod_amount),
            sale_id.name,
            to_name,
            to_phone,
            items,
            picking.height, picking.length, picking.width, int(picking.adjustment_weight))
        picking.carrier_order_info = order_rs
        carrier_tracking_ref = order_rs['order_code']
        picking.carrier_tracking_ref =carrier_tracking_ref
        carrier_price = order_rs['fee']['main_service']
        info = get_ghn_order_info(token, carrier_tracking_ref) #
        shipping_status = info['status']
        return shipping_status, carrier_tracking_ref, picking.carrier_tracking_url, carrier_price
        

    def create_carrier_po(self, picking, shipping_status, carrier_tracking_ref, carrier_tracking_url, ghn_price, re_get_ghn_info=False):

        PO = self.env['purchase.order']
        carrier_product = self.env.ref('ndt_ghn_extend.giao_hang_nhanh_delivery')
        po_data = {'partner_id':self.env.ref('ndt_ghn_extend.giao_hang_nhanh').id, 
                    'order_line':[(0,0,{'product_id':carrier_product.id,
                                        'product_qty':1, 'price_unit':ghn_price, 'name':carrier_tracking_ref, 'date_planned':fields.Datetime.now(),
                                        'product_uom':carrier_product.uom_po_id.id
                                        })
                                ]
                    }
        carrier_po_id = PO.create(po_data)
        carrier_po_id.vendor_order_state = shipping_status
        carrier_po_id.vendor_tracking_ref = carrier_tracking_ref
        carrier_po_id.vendor_tracking_url = carrier_tracking_url
        picking.delivery_purchase_id = carrier_po_id


class DeliveryServiceType(models.Model):
    _name ='ndt.delivery.service.type'

    name = fields.Char()
    carrier_id = fields.Many2one('delivery.carrier')
    code = fields.Char()