# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "luonto_nacha_files",
    'summary': """
         Generation of NACHA Files""",
    'description': """
        Generation of NACHA Files for ACH Batch Payments
    """,
    'author': "Odoo",
    'website': "http://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'license': 'OEEL-1',
    'depends': ['account'],
    'data': [
        'data/action_generate_nacha_file.xml',
    ],

}
