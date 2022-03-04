# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64
import contextlib
import io
import tempfile
from odoo.exceptions import UserError

EXCLUDE_FIELDS = ['create_uid','create_date','write_uid','write_date','__last_update','id', 'display_name']

class NDTDLXML(models.AbstractModel):
    _name = 'ndtdl.xml'

    def _default_exclude_ids(self):
        model_id = self.map_active_model()
        fields = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','in',EXCLUDE_FIELDS)]).ids
        return fields


    def _default_include_ids(self):
        model_id = self.map_active_model()
        fields = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','not in',EXCLUDE_FIELDS)]).ids
        return fields


    def _default_number_record(self):
        active_ids = self._context.get('active_ids',[])
        return len(active_ids)


    data = fields.Binary('File', readonly=True)
    name = fields.Char('File name')
    model_id = fields.Many2one('ir.model', compute='_compute_model_id')
    select_model_id = fields.Many2one('ir.model')
    model_name = fields.Char(compute='_compute_model_name')
    exclude_ids = fields.Many2many('ir.model.fields','exclude_ndtdl_rel' 'exclude_id', 'ndtdl_id', default=_default_exclude_ids)
    include_ids = fields.Many2many('ir.model.fields', 'include_ndtdl_rel', 'include_id', 'ndtdl_id', default=_default_include_ids)
    take_field_by = fields.Selection([('include_field','Include'), ('exclude_field','Exclude')],
         default='include_field', required=True )
    number_record = fields.Integer(default=_default_number_record)
    out = fields.Text()
    limit = fields.Integer()
    offset = fields.Integer()
    domain = fields.Char()
    order_by_field_id = fields.Many2one('ir.model.fields', domain="[('model','=',model_name)]")
    asc_desc = fields.Selection([('asc','asc'),('desc','desc')],required=True)

    @api.depends('model_id','select_model_id')
    def _compute_model_name(self):
        self.model_name = (self.select_model_id or self.model_id).model

    @api.onchange('select_model_id')
    def _onchage_include_ids(self):
        if self.select_model_id:
            self.include_ids = [(6,0,self.env['ir.model.fields'].\
                search([('model_id','=',self.select_model_id.id),
                ('name','not in',EXCLUDE_FIELDS),
                ('ttype', 'not in',['one2many'])
                ]).ids)]


    @api.depends('name')
    def _compute_model_id(self):
        self.model_id = self.map_active_model()

    
    def get_record_xml(self, record, fn_and_field):
        field_name, field = fn_and_field
        val =  getattr(record, field_name)
        if val == False:
            return None
        if field.type.lower() == 'many2one':
            ref = val.get_external_id()
            if ref:
                ref = list(ref.values())[0]
                field_xml = '<field name="%s" ref="%s"/>'%(field_name, ref)
            else:
                field_xml = ''
        else:
            field_xml = '<field name="%s">%s</field>'%(field_name, val)
        return field_xml

    
    def get_record_xml_with_fields(self, record, fn_and_field_dict):
        x_id = record.get_external_id()[record.id]
        field_xmls = []
        for fn_and_field in fn_and_field_dict.items():
            field_xml = self.get_record_xml(record, fn_and_field)
            if field_xml:
                field_xmls.append(field_xml)
        fields_xml_txt = '\n\t\t\t'.join(field_xmls)
        record_xml = '''<record model="%s" id="%s">\n\t\t\t%s\n\t\t</record>'''%(record._name, x_id, fields_xml_txt)

        return record_xml
    
    def get_records_xml_with_fields(self, records, fn_and_field_dict):
        records_xml = (self.get_record_xml_with_fields(record, fn_and_field_dict) for record in records)
        records_xml_txt = '\n\t\t'.join(records_xml)
        rt = '''<odoo>\n\t<data>\n\t\t%s\n\t</data>\n</odoo>'''%(records_xml_txt)
        
        return rt


    def map_active_model(self):
        if not self.select_model_id:
            active_model = self._context.get('active_model')
            ir_model = self.env['ir.model'].search([('model','=',active_model)])
        else:
            ir_model = self.select_model_id
        return ir_model


    def get_active_model(self):
        if self.select_model_id:
            active_model = self.select_model_id.model
        else:
            active_model = self._context.get('active_model')
        return active_model


    def get_model(self):
        active_model = self.get_active_model()
        model = self.env[active_model]
        return model


    def get_records(self):
        model = self.get_model()

        if not self.select_model_id:
            # rcs = model.browse(self._context.get('active_ids'))
            domain = [('id','in',self._context.get('active_ids'))]
        else:
            domain = eval(self.domain or '[]')
        limit = self.limit
        offset = self.offset
        order = self.order_by_field_id.name and '%s %s'%(self.order_by_field_id.name, self.asc_desc) or None
        rcs = model.search( domain, limit=limit, offset=offset, order=order)
        return rcs


    # @api.multi
    def get_xml_file(self):
        this = self[0]
        active_model = self.get_active_model()
        system_fn_and_field_dict = self.env[active_model]._fields
        choice_fields = self.include_ids
        choice_fields_names = choice_fields.mapped('name')
        choice_fields_names.sort()
        take_fn_and_field_dict = {f.name:system_fn_and_field_dict[f.name] for f in choice_fields }
        if not take_fn_and_field_dict:
            raise UserError('take_fn_and_field_dict is empty')
        records = self.get_records()
        str_out = self.get_records_xml_with_fields(records, take_fn_and_field_dict)
        # tmp = tempfile.NamedTemporaryFile()
        # with open(tmp.name, 'w') as f:
        data = base64.b64encode( bytes(str_out, "utf-8") )
        filename = active_model.replace('.','_') +'_data'
        extension = 'xml'
        name = "%s.%s" % (filename, extension)
        this.write({'data': data, 'name': name})
        if not self.select_model_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ndtdl.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'context':self._context,
                'res_id': this.id,
                'views': [(False, 'form')],
                'target': 'new',
            }


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super().fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        return result


class NDTDownload(models.TransientModel):
    _name = "ndtdl.wizard"
    _inherit = 'ndtdl.xml'



    
    


    

    