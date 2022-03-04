# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request

class Company(models.Model):

    _inherit = 'res.company'

    ward_ghn_code = fields.Char(related='partner_id.ward_id.ghn_code', store=True)
    ghn_shop_id = fields.Char()