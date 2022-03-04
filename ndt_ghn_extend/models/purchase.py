# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class Purchase(models.Model):
    _inherit = 'purchase.order'

    # hcategory_id = fields.Many2one('res.partner.hcategory',related='partner_id.hcategory_id',store=True, string=u'Nhóm nhà cung cấp')
    vendor_order_state = fields.Char('Trạng thái đơn hàng đối tác')
    vendor_tracking_ref = fields.Char('Mã số Truy vết')# cần phải dùng hàm tính lại
    vendor_tracking_url = fields.Char('URL theo dõi')
    
   
    
