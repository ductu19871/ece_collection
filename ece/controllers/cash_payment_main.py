# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TransferController(http.Controller):
    _accept_url = '/payment/cash/feedback'

    @http.route([
        '/payment/cash/feedback',
    ], type='http', auth='public', csrf=False, website=True)
    def transfer_form_feedback(self, **post):
        # print (haha)
        post
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'transfer')
        # nên tách đơn hàng ở đây.
        order = request.website.sale_get_order()
        print ('***order trước khi tách đơn***', order)
        order.tach_don()
        return werkzeug.utils.redirect('/payment/process')
        # return werkzeug.utils.redirect('/shop/confirmation')

