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

    # @http.route(['/shop/country_infos/<model("res.country.state"):country>'], type='json', auth="public", methods=['POST'], website=True)
    # def country_infos(self, country, mode, **kw):
    #     return dict(
    #         fields=['country_id', 'state_id'],
    #         states=[(st.id, st.name, st.code) for st in country.get_website_sale_states(mode=mode)],
    #         phone_code='123',
    #         zip_required=False,
    #         state_required=False,
    #     )

    @http.route(['/shop/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def country_infos(self, country, mode, **kw):
        return dict(
            fields=country.get_address_fields(),
            states=[(st.id, st.name, st.code) for st in country.get_website_sale_states(mode=mode)],
            phone_code=country.phone_code,
            zip_required=country.zip_required,
            state_required=country.state_required,
        )

    @http.route(['/shop/state_infos/<model("res.country.state"):state>'], type='json', auth="public", methods=['POST'], website=True)
    def state_infos(self, state, **kw):
        print ('**state**', state)
        return dict(
            # fields=country.get_address_fields(),
            states=[(st.id, st.name, st.code) for st in state.get_website_sale_district()],
            # phone_code=country.phone_code,
            # zip_required=country.zip_required,
            # state_required=country.state_required,
        )
    #  /shop/district_infos/
    @http.route(['/shop/district_infos/<model("res.country.district"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def district_infos(self, country, **kw):
        print ('**country**', country)
        return dict(
            # fields=country.get_address_fields(),
            states=[(st.id, st.name, st.code) for st in country.get_website_sale_ward()],
            # phone_code=country.phone_code,
            # zip_required=country.zip_required,
            # state_required=country.state_required,
        )


   

