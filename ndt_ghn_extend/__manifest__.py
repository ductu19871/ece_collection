# -*- coding: utf-8 -*-
{
    
    'name': "NDT GHN Extend",
    'summary':"NDT GHN Extend",
    'version': '0.1',
    'website': "http://www.vidoo.vn",
    'author': "Nguyen Duc Tu",
    "license": "AGPL-3",
    'depends': ['base','ndt_ghn','delivery','stock','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        # 'data/test.yml',
        'views/res_company.xml',
        'views/sale.xml',
        'views/stock.xml',
        'views/purchase.xml',
        'views/res_config_settings.xml',
    ],
    "external_dependencies": {"python": ["requests"]},
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}