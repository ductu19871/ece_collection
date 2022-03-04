# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist
from odoo.addons.website_sale.controllers.main import WebsiteSale 
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery 
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist 
from odoo.exceptions import UserError

####
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
# from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression
_logger = logging.getLogger(__name__)

def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}


class TableCompute(object):

    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey, ppr):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= ppr:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(ppr):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products, ppg=20, ppr=4):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        x = 0
        for p in products:
            x = min(max(p.website_size_x, 1), ppr)
            y = min(max(p.website_size_y, 1), ppr)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % ppr, pos // ppr, x, y, ppr):
                pos += 1
            # if 21st products (index 20) and the last line is full (ppr products in it), break
            # (pos + 1.0) / ppr is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) // ppr) > maxy:
                break

            if x == 1 and y == 1:   # simple heuristic for CPU optimization
                minpos = pos // ppr

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos // ppr) + y2][(pos % ppr) + x2] = False
            self.table[pos // ppr][pos % ppr] = {
                'product': p, 'x': x, 'y': y,
                'ribbon': p.website_ribbon_id,
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos // ppr))
            index += 1

        # Format table according to HTML needs
        rows = sorted(self.table.items())
        rows = [r[1] for r in rows]
        for col in range(len(rows)):
            cols = sorted(rows[col].items())
            x += len(cols)
            rows[col] = [r[1] for r in cols if r[1]]

        return rows


class WebsiteSaleWishlist1(WebsiteSaleWishlist):

    # def _get_pricelist_context(self):
    #     print (1111111111111111111111111111) # chuwngs to nos co vao day.
    #     pricelist_context = dict(request.env.context)
    #     pricelist = False
    #     if not pricelist_context.get('pricelist'):
    #         pricelist = request.website.get_current_pricelist()
    #         pricelist_context['pricelist'] = pricelist.id
    #     else:
    #         pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

    #     return pricelist_context, pricelist

    # @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    # def address(self, **kw):
    #     Partner = request.env['res.partner'].with_context(show_address=1).sudo()
    #     order = request.website.sale_get_order()

    #     redirection = self.checkout_redirection(order)
    #     if redirection:
    #         return redirection

    #     mode = (False, False)
    #     can_edit_vat = False
    #     def_country_id = order.partner_id.country_id
    #     values, errors = {}, {}

    #     partner_id = int(kw.get('partner_id', -1))

    #     # IF PUBLIC ORDER
    #     if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
    #         mode = ('new', 'billing')
    #         can_edit_vat = True
    #         country_code = request.session['geoip'].get('country_code')
    #         if country_code:
    #             def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
    #         else:
    #             def_country_id = request.website.user_id.sudo().country_id
    #     # IF ORDER LINKED TO A PARTNER
    #     else:
    #         if partner_id > 0:
    #             if partner_id == order.partner_id.id:
    #                 mode = ('edit', 'billing')
    #                 can_edit_vat = order.partner_id.can_edit_vat()
    #             else:
    #                 shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
    #                 if partner_id in shippings.mapped('id'):
    #                     mode = ('edit', 'shipping')
    #                 else:
    #                     return Forbidden()
    #             if mode:
    #                 values = Partner.browse(partner_id)
    #         elif partner_id == -1:
    #             mode = ('new', 'shipping')
    #         else: # no mode - refresh without post?
    #             return request.redirect('/shop/checkout')

    #     # IF POSTED
    #     if 'submitted' in kw:
    #         print ('kw when submitted', kw)
    #         pre_values = self.values_preprocess(order, mode, kw)
    #         errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
    #         post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

    #         if errors:
    #             errors['error_message'] = error_msg
    #             values = kw
    #         else:
    #             partner_id = self._checkout_form_save(mode, post, kw)
    #             if mode[1] == 'billing':
    #                 order.partner_id = partner_id
    #                 order.with_context(not_self_saleperson=True).onchange_partner_id()
    #                 # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
    #                 order.partner_invoice_id = partner_id
    #                 if not kw.get('use_same'):
    #                     kw['callback'] = kw.get('callback') or \
    #                         (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
    #             elif mode[1] == 'shipping':
    #                 order.partner_shipping_id = partner_id

    #             # TDE FIXME: don't ever do this
    #             order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
    #             if not errors:
    #                 return request.redirect(kw.get('callback') or '/shop/confirm_order')

    #     country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
    #     country = country and country.exists() or def_country_id
    #     render_values = {
    #         'website_sale_order': order,
    #         'partner_id': partner_id,
    #         'mode': mode,
    #         'checkout': values,
    #         'can_edit_vat': can_edit_vat,
    #         'country': country,
    #         'country_states': country.get_website_sale_states(mode=mode[1]),
    #         'countries': country.get_website_sale_countries(mode=mode[1]),
    #         'error': errors,
    #         'callback': kw.get('callback'),
    #         'only_services': order and order.only_services,
    #     }
    #     return request.render("website_sale.address", render_values)


        

    @http.route()
    def add_to_wishlist(self, product_id, price=False, **kw):
        if not price:
            pricelist_context, pl = self._get_pricelist_context()
            # p = request.env['product.product'].with_context(pricelist_context, display_default_code=False).browse(product_id)
            p = request.env['product.product'].sudo().with_context(pricelist_context, display_default_code=False).browse(product_id)
            price = p._get_combination_info_variant()['price']

        Wishlist = request.env['product.wishlist']
        if request.website.is_public_user():
            Wishlist = Wishlist.sudo()
            partner_id = False
        else:
            partner_id = request.env.user.partner_id.id

        wish_id = Wishlist._add_to_wishlist(
            pl.id,
            pl.currency_id.id,
            request.website.id,
            price,
            product_id,
            partner_id
        )

        if not partner_id:
            request.session['wishlist_ids'] = request.session.get('wishlist_ids', []) + [wish_id.id]

        return wish_id


class WebsiteSale1(WebsiteSale):

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get('sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get('sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
        })
        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()
        print ('**values***', values)
        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.cart", values)



    @http.route()# thêm dòng Product = Product.sudo()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)
        Product = Product.sudo()
        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)


class WebsiteSaleDelivery1(WebsiteSaleDelivery):

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        # print ('cos vo day khong')
        order = request.website.sale_get_order()
        carrier_id = post.get('carrier_id')
        if carrier_id:
            carrier_id = int(carrier_id)
        if order:
            company = 'all' if not carrier_id else None
            order._check_carrier_quotation(force_carrier_id=carrier_id, company=company)
            if carrier_id:
                return request.redirect("/shop/payment")
        return super(WebsiteSaleDelivery, self).payment(**post)# suửa chổ này

    # @http.route(['/shop/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)

    @http.route()
    def update_eshop_carrier(self, **post):
        order = request.website.sale_get_order()
        company_id = int(post['company_id'])
        carrier_id = int(post['carrier_id'])
        post.update({'company_id': company_id})
        if order:
            bool_return, price =  order._check_carrier_quotation(force_carrier_id=carrier_id, company=company_id)
            #@Todo 
            post['price'] = price
        return self._update_website_sale_delivery_return(order, **post)

    
    def _update_website_sale_delivery_return(self, order, **post):
        Monetary = request.env['ir.qweb.field.monetary']
        carrier_id = int(post['carrier_id'])
        currency = order.currency_id
        total_new_amount_delivery = order.amount_delivery
        # rate = order.carrier_id.browse(carrier_id).with_context(web_company=post['company_id']).rate_shipment(order)
        amount_delivery= post['price']
        if order:
            return {
                'company_id': post['company_id'],
                'status': order.delivery_rating_success,
                'error_message': order.delivery_message,
                'carrier_id': carrier_id,
                'is_free_delivery': not bool(order.amount_delivery),
                'is_free_delivery': not bool(amount_delivery),
                # 'new_amount_delivery': Monetary.value_to_html(order.amount_delivery, {'display_currency': currency}),
                'total_new_amount_delivery': Monetary.value_to_html(total_new_amount_delivery, {'display_currency': currency}),
                'new_amount_delivery': Monetary.value_to_html(amount_delivery, {'display_currency': currency}),
                'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
                'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': currency}),
            }
        return {}



    # def _update_website_sale_delivery_return(self, order, **post):
    #     Monetary = request.env['ir.qweb.field.monetary']
    #     carrier_id = int(post['carrier_id'])
    #     currency = order.currency_id
    #     amount_delivery = order.amount_delivery
    #     rate = order.carrier_id.browse(carrier_id).rate_shipment(order)
    #     # print ('**amount_delivery***', amount_delivery)
    #     amount_delivery= rate['price']
    #     if order:
    #         return {
    #             'company_id': post['company_id'],
    #             'status': order.delivery_rating_success,
    #             'error_message': order.delivery_message,
    #             'carrier_id': carrier_id,
    #             'is_free_delivery': not bool(amount_delivery),
    #             'new_amount_delivery': Monetary.value_to_html(amount_delivery, {'display_currency': currency}),
    #             'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
    #             'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
    #             'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': currency}),
    #         }
    #     return {}


    @http.route(['/shop/carrier_rate_shipment'], type='json', auth='public', methods=['POST'], website=True)
    def cart_carrier_rate_shipment(self, carrier_id, **kw):
        order = request.website.sale_get_order(force_create=True)
        company_id = kw.get('company_id')
        if not int(carrier_id) in order._get_delivery_methods().ids:
            raise UserError(_('It seems that a delivery method is not compatible with your address. Please refresh the page and try again.'))

        Monetary = request.env['ir.qweb.field.monetary']

        res = {'carrier_id': carrier_id}
        carrier = request.env['delivery.carrier'].sudo().browse(int(carrier_id)).with_context(web_company=company_id)
        rate = carrier.rate_shipment(order, company_id)
        
        if rate.get('success'):
            # tax_ids = carrier.product_id.taxes_id.filtered(lambda t: t.company_id == order.company_id)
            # if tax_ids:
            #     fpos = order.fiscal_position_id
            #     tax_ids = fpos.map_tax(tax_ids, carrier.product_id, order.partner_shipping_id)
            #     taxes = tax_ids.compute_all(
            #         rate['price'],
            #         currency=order.currency_id,
            #         quantity=1.0,
            #         product=carrier.product_id,
            #         partner=order.partner_shipping_id,
            #     )
            #     if request.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
            #         rate['price'] = taxes['total_excluded']
            #     else:
            #         rate['price'] = taxes['total_included']
            print ("rate['price']",rate['price'],'company_id', company_id)
            print ('carrier._context', carrier._context)
            res['status'] = True
            res['new_amount_delivery'] = Monetary.value_to_html(rate['price'], {'display_currency': order.currency_id})
            res['is_free_delivery'] = not bool(rate['price'])
            res['error_message'] = rate['warning_message']
        else:
            res['status'] = False
            res['new_amount_delivery'] = Monetary.value_to_html(0.0, {'display_currency': order.currency_id})
            res['error_message'] = rate['error_message']
        res['company_id'] = company_id
        return res



