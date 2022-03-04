# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request

class ece(models.Model):
    # _name = 'ece.ece'
    _inherit = 'ir.model.data'

    @api.model
    def set_noupdate_false(self, xml_id):
        id,_,_ = self.xmlid_lookup(xml_id)
        imd = self.browse(id)
        imd.noupdate = False

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('company_id')
    def _check_sale_product_company(self):
        pass


class ProductWishlist(models.Model):
    _inherit = 'product.wishlist'

    @api.model
    def current(self):
        """Get all wishlist items that belong to current user or session,
        filter products that are unpublished."""
        if not request:
            return self

        if request.website.is_public_user():
            wish = self.sudo().search([('id', 'in', request.session.get('wishlist_ids', []))])
        else:
            wish = self.search([("partner_id", "=", self.env.user.partner_id.id), ('website_id', '=', request.website.id)])

        return wish.sudo().filtered(lambda x: x.sudo().product_id.product_tmpl_id.website_published and x.sudo().product_id.product_tmpl_id.sale_ok)

