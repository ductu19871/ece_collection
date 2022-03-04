# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    ward_id = fields.Many2one('res.country.ward', u'Ward')
    district_id = fields.Many2one('res.country.district', u'District')

    @api.onchange('state_id') 
    def _state_id_onchange(self):
        self.district_id = False
        self.ward_id = False
        
    # @api.onchange('ward_id', 'district_id', 'state_id')
    # def _onchange_district(self):
    #     city = []
    #     if self.ward_id:
    #         city.append(self.ward_id.name)
    #     if self.district_id:
    #         city.append(self.district_id.name)
    #     if self.state_id:
    #         city.append(self.state_id.name)
    #     if city:
    #         str_city = ', '.join(city)
    #         self.city = str_city


