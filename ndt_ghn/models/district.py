# -*- coding: utf-8 -*-

from odoo import api, fields, models
from . province import fetch_ghn, replacetrim_quan, get_ghn_item_by_name
from unidecode import unidecode
import json
import traceback


def fetch_ghn_ward_data(ghn_district_id):
        headers = {'token': '81f253e7-e8da-11ea-84a7-3e05d9a3136e'}
        url = 'https://online-gateway.ghn.vn/shiip/public-api/master-data/ward?district_id'
        data = {"district_id": int(ghn_district_id)}#int(self.ghn_district_id)}
        r = fetch_ghn(url, headers, data)
        return r['data']

class District(models.Model):
    _inherit = 'res.country.district'
    _sql_constraints = [
        ('unique_ghn_district_code', 'unique (ghn_district_code)', 'unique_ghn_district_code'),
        ('unique_ghn_district_id', 'unique (ghn_district_id)', 'unique_ghn_district_id'),
    ]
    ghn_district_code = fields.Char()
    ghn_district_id = fields.Integer('GHN id',requried=True)
    char_json_wards_data = fields.Char()
    ward_ids = fields.One2many('res.country.ward','district_id')
    is_done_ward = fields.Boolean()
   
    def get_ghn_ward_one_district(self):
        ghn_district_id = self.ghn_district_id
        ward_ghn_items = fetch_ghn_ward_data(ghn_district_id)
        self.char_json_wards_data = ward_ghn_items
        wards = self.env['res.country.ward'].search([('district_id','=',self.id)]) 
        for ward in wards:
            ward.get_ghn_ward_with_ghn_datas(ward_ghn_items)
    
    def from_ghn_create_ward_per_one_district(self): #new
        try:
            ghn_district_id = self.ghn_district_id
            ward_ghn_items = fetch_ghn_ward_data(ghn_district_id)
            data_list = []
            state_name = self.state_id.name
            district_name = self.name
            for item in ward_ghn_items:
                WardCode = item['WardCode']
                name = item['WardName']
                district_id = self.id
                rs = self.env['res.country.ward'].search([('ghn_code','=', WardCode)])
                if not rs:
                    rs = self.env['res.country.ward'].create({
                        'name':name,
                        'ghn_code':WardCode,
                        'code':WardCode,
                        'district_id':district_id
                    })
                    xml_id = 'ndt_ghn_.' + unidecode(state_name + '__' + district_name + '__' + name  + '_' + str(rs.id)).replace(' ','_') 
                    data_list.append({'xml_id': xml_id, 'record': rs})
            self.is_done_ward = True
        except:
            print ('district_name**', district_name, 'state_name', state_name)
            traceback.print_exc()
            # raise

        self.env['ir.model.data']._update_xmlids(data_list)
                
    def from_ghn_create_ward_per_mutil_district(self): #new
        for r in self:
            r.from_ghn_create_ward_per_one_district()


    def get_ghn_ward_all_district(self):
        for district in self.search(['|', ('ghn_district_id','!=',False), ('ghn_district_id','!=',0)]):
            district.get_ghn_ward_one_district()

    def action_update_this_district_ghn_code(self):
        ghn_items = self.state_id.fetch_district_ghn_items_of_this_province()
        self.update_this_district_ghn_code(ghn_items)

    def update_this_district_ghn_code(self, districts_ghn_items):
        district = self
        item = get_ghn_item_by_name(district, districts_ghn_items, item_name = 'DistrictName')
        if item:
            district.ghn_district_id = item['DistrictID']
            district.ghn_code = item['Code']
        else:
            print ('name  not map**** ', district.name)

            

        