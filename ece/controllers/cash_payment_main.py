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
        # request.env['payment.transaction'].sudo().form_feedback(post, 'transfer')
        request.env['payment.transaction'].sudo().form_feedback(post, 'cash')

        # nên tách đơn hàng ở đây.
        order = request.website.sale_get_order()
        print ('***order trước khi tách đơn***', order)
        # order.tach_don()
        return werkzeug.utils.redirect('/payment/process')
        # return werkzeug.utils.redirect('/shop/confirmation')

    # @http.route(['/payment/process'], type="http", auth="public", website=True, sitemap=False)
    # def payment_status_page(self, **kwargs):
    #     # When the customer is redirect to this website page,
    #     # we retrieve the payment transaction list from his session
    #     tx_ids_list = self.get_payment_transaction_ids()
    #     payment_transaction_ids = request.env['payment.transaction'].sudo().browse(tx_ids_list).exists()

    #     render_ctx = {
    #         'payment_tx_ids': payment_transaction_ids.ids,
    #     }
    #     return request.render("payment.payment_process_page", render_ctx)
