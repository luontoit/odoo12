# -*- coding: utf-8 -*-
{
    'name': "LF: Run Script to Create Commission Vendor Bills for Invoices",

    'summary': """
        Converted from script to 1-time server action since it's easier to call a function on all records for vendor bills""",

    'description': """
        Task ID: 2311848
        A server action to create Commission Vendor Bills retro-actively (in the past) for every Invoice in his DB where the Source Document is set. 
        This is to retroactively use the commission development (link below) on existing invoices.
    """,

    'author': "Odoo Inc",
    'website': "http://www.odoo.com",
    'license': "OEEL-1",
    'category': 'Custom Development',
    'version': '1.0',
    'depends': ['base', 'product'],
    'data': [
        'data/unique_product.xml'
    ]
}
