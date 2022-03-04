# -*- coding: utf-8 -*-
{
    
    'name': "NDT GHN",
    'summary':"NDT GHN",
    'version': '0.1',
    'website': "http://www.vidoo.vn",
    'author': "Nguyen Duc Tu",
    "license": "AGPL-3",
    'depends': ['base','partner_vn_localization','ndt_download_xml'],
    'data': [
        'data/cronjob_data.xml',
        'data/ir_actions_server.xml',
        'data/res_country_state_data.xml',
        'data/res_country_district_data.xml',
        'data/res_country_ward_data.xml',
        'views/province.xml',
        'views/district.xml',
        'views/ward.xml',
        'views/xml_download.xml',
        # 'security/ir.model.access.csv',
    ],
    "external_dependencies": {"python": ["requests"]},
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}