# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class FixdlXML(models.Model):
    _name = 'ndtdl.fixdl'
    _inherit = 'ndtdl.xml'
    

    exclude_ids = fields.Many2many('ir.model.fields','exclude_ndtdlfixdl_rel' 'exclude_id', 'ndtdl_id')
    include_ids = fields.Many2many('ir.model.fields', 'include_ndtdlfixdl_rel', 'include_id', 'ndtdl_id')