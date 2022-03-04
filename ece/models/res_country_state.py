from odoo import api,models, fields


class State(models.Model):

    _inherit = 'res.country.state'
    district_ids = fields.One2many('res.country.district','state_id')

    def get_website_sale_district(self, mode='billing'):
        rs =  self.sudo().district_ids
        print ('self.sudo().district_ids', self.sudo().district_ids)
        return rs


class District(models.Model):

    _inherit = 'res.country.district'
    ward_ids = fields.One2many('res.country.ward','district_id')

    def get_website_sale_ward(self, mode='billing'):
        rs =  self.sudo().ward_ids
        return rs





