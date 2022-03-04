# -*- coding: utf-8 -*-

from odoo import api, fields, models
from .district import fetch_ghn_ward_data
from .province import get_ghn_item_by_name
from . province import fetch_ghn, replacetrim_quan, get_ghn_item_by_name
from unidecode import unidecode
import re 

def replace_xa(name):
    name = re.sub('^xa |^thi tran |^phuong 0|^phuong ','',name,flags= re.I)
    return name 

def change_name_xa(name):
    #'^Ngoc Yeu':'NGOK YEU',
    change_names = {'ngok yeu' : 'ngoc yeu',
        '^thu 3':'THU BA','^Dle Yang':'DLIE YANG','Ngok':'NGOC',
        '^bac Nga':'PAC NGA','^Muong Tranh':'MUONG CHANH','Xín Vàng':'Xím Vàng',
        'Chương Dương Độ':'Chương Dương',
        'Đắk Plô':'Đắk blô','Hải Châu 2':'Hải Châu II','Lâm Sa':'Lâm xa','Chi Lê':'Chi Nê',
        'Plei Cần':'Plei Kần','Phúc Thành B':'Phúc Thành','Bun Tở':'Bum Tở','Hà Ra':'Hra',
        'Pờ Y':'Bờ Y','Thôn Mòn':'Thôm Mòn','Phiêng Kôn':'Phiêng Côn','Nong Lay':'Noong Lay'
        }#'KRONG A NA':'KRONG ANA',
    for i,j in change_names.items():
        name, count = re.subn(unidecode(i), unidecode(j).upper(),name, flags=re.I)
        if count != 0:
            return name
    return name
class Ward(models.Model):
    _description = 'Ward'
    _inherit = 'res.country.ward'
    
    _sql_constraints = [
        ('unique_ghn_code', 'unique (ghn_code)', 'unique_ghn_code'),
        # ('unique_ghn_id', 'unique (ghn_id)', 'unique_ghn_id')
    ]

    ghn_code = fields.Char()
    # ghn_code_duplicate = fields.Char()
    
    def get_ghn_ward_with_ghn_datas(self, ghn_items):
        ghn_ward_item = get_ghn_item_by_name(self, ghn_items, item_name = 'WardName',
                methods = [replacetrim_quan, unidecode, replace_xa, change_name_xa])
        if ghn_ward_item:
            ghn_code = ghn_ward_item['WardCode']
            available_ward = self.search([('ghn_code','=',ghn_code)])
            if available_ward:
                self.ghn_code_duplicate = ghn_ward_item['WardCode']
            else:
                self.ghn_code = ghn_ward_item['WardCode']
                    
        
        
    # @api.one
    def get_ghn_ward(self):
        str_ghn_district= self.district_id.ghn_id
        ghn_items = fetch_ghn_ward_data(str_ghn_district)
        self.get_ghn_ward_with_ghn_datas(ghn_items)
        # ghn_ward_item = get_ghn_item_by_name(self, ghn_items, item_name = 'WardName',
        #         methods = [replacetrim_quan, unidecode, replace_xa, change_name_xa])
        # if ghn_ward_item:
        #     try:
        #         self.ghn_code = ghn_ward_item['WardCode']
        #     except:
        #         self.ghn_code_duplicate = ghn_ward_item['WardCode']
        # else:
        #     name = self.name.upper()
        #     print ('name  not map**** ', name)