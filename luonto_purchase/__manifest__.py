# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Luonto: Split In Pack",
    'version': '1.0',
    'depends': ['purchase_stock', 'delivery'],
    'author': 'Odoo Inc',
    'license': 'OEEL-1',
    'mainainer': 'Odoo Inc',
    'category': 'Inventory',
    'description': """
Luonto: Split In Pack
=====================
- Splitting the incoming products into packages while receiving.
    """,
    # data files always loaded at installation
    'data': [
        'views/product_views.xml',
        'views/stock_views.xml',
        'views/quant_package_views.xml',
        'views/product_packaging_views.xml',
    ],
}