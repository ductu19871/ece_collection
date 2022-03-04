# -*- coding: utf-8 -*-
{
    'name': "ece",

    'summary': """
        Ecobiz ecomerce""",

    'description': """
        Ecobiz ecomerce
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product','sale','website', 'website_sale',
        'website_sale_delivery','website_sale_wishlist','ndt_ghn_extend','payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'data/cash_payment.xml',
        'web_demo/data.xml',
        'views/sale.xml',
        'views/product_template.xml',
        'views/js_template.xml',
        'templates/product.xml',
        'templates/address.xml',
        'templates/card_line.xml',
        'templates/payment_delivery.xml',
        'templates/layout.xml',
        'test_templates/payment.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
