# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Luonto: Credit Limit',
    'summary': 'Luonto: Credit Limit',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.0',
    'author': 'Odoo Inc',
    'description': """
Luonto: Credit Limit
====================
    """,
    'category': 'Custom Development',
    'depends': ['sale', 'base', 'account', 'sale_stock'],
    'data': [
        'views/partner_views.xml',
        'views/sale_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
