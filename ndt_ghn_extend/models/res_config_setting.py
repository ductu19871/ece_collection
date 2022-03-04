# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ghn_token = fields.Char('GHN token')
   
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['ghn_token'] = self.env['ir.config_parameter'].sudo().get_param('ndt_ghn_extend.ghn_token')
        return res

    @api.model
    def set_values(self):
       
        self.env['ir.config_parameter'].sudo().set_param('ndt_ghn_extend.ghn_token', self.ghn_token)
        super(ResConfigSettings, self).set_values()



  