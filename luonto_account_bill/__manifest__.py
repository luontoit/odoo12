# -*- coding: utf-8 -*-
{
    'name': "Vendor Bill from Invoice",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Odoo Inc",
    'website': "http://www.odoo.com",
    'category': 'Account',
    'version': '0.1',
    'depends': ['account', 'contacts'],

    'data': [
        'views/partner_views.xml',
        'views/account_move_views.xml',
        'security/ir.model.access.csv'
    ]
}
