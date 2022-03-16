# -*- coding: utf-8 -*-

from odoo import models, fields, api

class WM(models.Model):
    
    _inherit = 'website.menu'

    active = fields.Boolean(default=True)