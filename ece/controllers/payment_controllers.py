# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist
from odoo.addons.website_sale.controllers.main import WebsiteSale 
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.exceptions import ValidationError
from odoo.addons.payment_transfer.controllers.main import TransferController

import logging
import pprint
import werkzeug
_logger = logging.getLogger(__name__)   
import inspect

class WebsiteSale2(WebsiteSale):
    pass
    # @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    # def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
    #     # print (ha1)
    #     """ Method that should be called by the server when receiving an update
    #     for a transaction. State at this point :

    #      - UDPATE ME
    #     """
    #     if sale_order_id is None:
    #         order = request.website.sale_get_order()
    #     else:
    #         order = request.env['sale.order'].sudo().browse(sale_order_id)
    #         assert order.id == request.session.get('sale_last_order_id')

    #     if transaction_id:
    #         tx = request.env['payment.transaction'].sudo().browse(transaction_id)
    #         assert tx in order.transaction_ids()
    #     elif order:
    #         tx = order.get_portal_last_transaction()
    #     else:
    #         tx = None
    #     if not order or (order.amount_total and not tx):
    #         return request.redirect('/shop')
    #     if order and not order.amount_total and not tx:
    #         order.with_context(send_email=True).action_confirm()
    #         return request.redirect(order.get_portal_url())
    #     # clean context and session, then redirect to the confirmation page
    #     request.website.sale_reset()
    #     if tx and tx.state == 'draft':
    #         return request.redirect('/shop')
    #     PaymentProcessing.remove_payment_transaction(tx)
    #     return request.redirect('/shop/confirmation')


    # @http.route(['/shop/payment/transaction/',
    #     '/shop/payment/transaction/<int:so_id>',
    #     '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    @http.route()
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        if not acquirer_id:
            return False
        try:
            acquirer_id = int(acquirer_id)
        except:
            return False
        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()

        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return False

        assert order.partner_id.id != request.website.partner_id.id

        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)
        transaction = order._create_payment_transaction(vals)
        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        return transaction.render_sale_button(order)

