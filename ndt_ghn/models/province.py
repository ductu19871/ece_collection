# -*- coding: utf-8 -*-

from types import TracebackType
from odoo import api, fields, models
import re
import requests
from unidecode import unidecode
import traceback
# headers = ''
# headers = {'token': '81f253e7-e8da-11ea-84a7-3e05d9a3136e'}
# response = requests.post('https://online-gateway.ghn.vn/shiip/public-api/master-data/province', 
#         headers=headers)
# print(response.json())
class Jsonb(fields.Char):
    column_cast_from = ('jsonb',)
    _slots = {
        'size': None,                   # maximum size of values (deprecated)
    }

    @property
    def column_type(self):
        return ('jsonb','jsonb')

    def convert_to_read(self, value, record, use_name_get=True):
        if isinstance(value,dict):
            value = str(value)
            value = value.replace("'",'"')
        return value
        
    def convert_to_column(self, value, record, values=None):
        if isinstance(value, dict):
            value = json.dumps(value)
        elif isinstance(value,str):
            value = value.replace("'",'"')
        return value

    def convert_to_cache(self, value, record, validate=True):
        if value and isinstance(value, str):
            value = value.replace("'",'"')
            value = json.loads(value)
        return value


def replacetrim_province(name):
    name = re.sub('tỉnh |thành phố |tp |thủ đô ','',name,flags= re.I)
    name = re.sub('-',' ',name)
    name = re.sub(' +',' ', name)
    name = name.strip()
    return name

def replacetrim_quan(name):
    name = re.sub('Huyện đảo','Huyện',name,flags= re.I)
    name = re.sub('-|–',' ',name)
    name = re.sub("'",' ',name,flags= re.I)
    name = re.sub(' +',' ', name)
    name = name.strip()
    return name


def replace_quan_huyen(name):
    name = re.sub('^thixa|^thanhpho|^quan|^huyen','',name,flags= re.I)
    return name

def change_name_quan_huyen(name):
    change_names = {'XIMACAI':'SIMACAI',
        'QUYNHON':'QUINHON','PHUQUI':'PHUQUY'}#'KRONG A NA':'KRONG ANA',
    for i,j in change_names.items():
        name, count = re.subn(i,j,name, flags=re.I)
        if count != 0:
            return name
    return name

def replace_space(name):
    name = re.sub(' +','',name)
    return name

def fetch_ghn(url, headers, data):
    response = requests.post(url, 
    headers=headers, json =  data)
    json_response = response.json()
    return json_response

token = '81f253e7-e8da-11ea-84a7-3e05d9a3136e'

def get_ghn_item_by_name(region_obj, ghn_items, item_name = 'DistrictName',\
    methods = [replacetrim_quan, unidecode, replace_space, replace_quan_huyen, change_name_quan_huyen]):
    name = region_obj.name.upper()
    replaced_ghn_regions = {}
    for method in methods:
        name = method(name)
        if not replaced_ghn_regions:
            for ghn_item in ghn_items:
                replaced_ghn_region_name = method(ghn_item[item_name].upper())
                replaced_ghn_regions[replaced_ghn_region_name] = ghn_item
        else:
            replaced_ghn_regions2 = {}
            for i, j in replaced_ghn_regions.items():
                replaced_ghn_region_name = method(i)
                replaced_ghn_regions2[replaced_ghn_region_name] = j
            replaced_ghn_regions = replaced_ghn_regions2
        get_item = replaced_ghn_regions.get(name)
        if get_item:
            break
    return get_item

class Province(models.Model):
    _inherit = ['res.country.state']
    _sql_constraints = [
        ('unique_ghn_province_code', 'unique (ghn_province_code)', 'unique_ghn_province_code'),
        ('unique_ghn_province_id', 'unique (ghn_province_id)', 'unique_ghn_province_id'),
    ]

    ghn_province_code = fields.Char()
    ghn_province_id = fields.Integer()
    char_json_districts_data = fields.Char()
    note = fields.Char()
    

    def clone_ghn_district_per_1_province(self): #new
        try:
            districts_per_province_ghn_items = self.fetch_district_ghn_items_of_this_province()
            state_id = self.id
            state_name = self.name
            data_list = []
            for district_item in districts_per_province_ghn_items:
                name = district_item['DistrictName']
                ghn_district_id = district_item['DistrictID']
                code = district_item.get('Code')
                if not self.env['res.country.district'].search([('name','=',name),('state_id','=', state_id)]):
                    rs = self.env['res.country.district'].create({'name':name,
                        'ghn_district_id':ghn_district_id, 'code':code, 'state_id': state_id, 'ghn_district_code':code})
                    xml_id = 'ndt_ghn_.' + unidecode(state_name + '__' + name + '_' + str(rs.id)).replace(' ','_') 
                    data_list.append({'xml_id': xml_id, 'record': rs})
            self.env['ir.model.data']._update_xmlids(data_list)
        except:
            traceback.print_exc()
            raise

    def clone_ghn_district_per_multi_provinces(self): #new
        for r in self:
            r.clone_ghn_district_per_1_province()
    
    def _get_all_ghn_province_items(self):
        headers = {'token': token}
        response = requests.post('https://online-gateway.ghn.vn/shiip/public-api/master-data/province', 
                headers=headers)
        rtj = response.json()
        ghn_provinces = rtj['data']
        return ghn_provinces

    def update_province_ghn_code_from_availabe_provines(self):
        ghn_provinces = self._get_all_ghn_province_items()
        for r in self.search(['|',('country_id.name','ilike','Vietnam'),('country_id.name','ilike','việt nam')]):
            name = replacetrim_province(r.name)
            map = 0
            for ghn_item in ghn_provinces:
                ProvinceName = ghn_item['ProvinceName']
                ProvinceName = replacetrim_province(ProvinceName)
                if ProvinceName == name:
                    map = 1
                else:
                    name = unidecode(name)
                    ProvinceName = unidecode(ProvinceName)
                    
                    if name == ProvinceName:
                        map = 1 
                if map ==1:
                    break
            if map ==1:
                r.ghn_province_id = ghn_item['ProvinceID']
                r.ghn_province_code = ghn_item['Code']
            if map==0:
                print ('name  not map**** ', name)

    def update_ghn_province_code_from_all_ghn_provines(self):#New
        ghn_provinces = self._get_all_ghn_province_items()
        available_vn_provinces = \
            self.search(['|',('country_id.name','ilike','Vietnam'),('country_id.name','ilike','việt nam')])
        available_vn_provinces_dicts = {i.name:i  for i in available_vn_provinces}
        for ghn_item in ghn_provinces:
            map = False
            ProvinceName = ghn_item['ProvinceName']
            for avail_province in available_vn_provinces:
                name = avail_province.name
                if ProvinceName == name:
                    map = True
                else:
                    trim_ProvinceName= replacetrim_province(ProvinceName)
                    trimed_name = replacetrim_province(name)
                    if trim_ProvinceName == trimed_name:
                        map = True
                        avail_province.note = ProvinceName
                
                if map == True:
                    avail_province.ghn_province_id = ghn_item['ProvinceID']
                    avail_province.ghn_province_code = ghn_item['Code']
                    break
            if map ==0:
                print (map==0, ProvinceName)
    
    def fetch_district_ghn_items_of_this_province(self):
        headers = {'token': '81f253e7-e8da-11ea-84a7-3e05d9a3136e'}
        url = 'https://online-gateway.ghn.vn/shiip/public-api/master-data/district'
        data = {"province_id":int(self.ghn_province_id)}
        r = fetch_ghn(url, headers, data)
        return r['data']

    def get_ghn_districts_one_province(self):
        districts_ghn_items = self.fetch_district_ghn_items_of_this_province()
        self.char_json_districts_data = districts_ghn_items

        districts = self.env['res.country.district'].search([('state_id','=',self.id)])  
        for district in districts:
            district.update_this_district_ghn_code(districts_ghn_items)

    def get_ghn_district_all_province(self):
        for province in self.search(['|',('country_id.name','ilike','Vietnam'),('country_id.name','ilike','việt nam')]):
            province.get_ghn_districts_one_province()
        
        




    
   