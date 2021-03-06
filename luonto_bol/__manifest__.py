# -- coding: utf-8 --
{
    'name': 'Luonto BOL',

    'summary': 'Luonto BOL',

    'author': 'Odoo',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['sale','web','stock','delivery'],

    # always loaded
    'data': [
        'data/action_bol_report.xml',
        'views/sale_bol_report.xml',
        'views/internal_layout_inherit.xml',
        'views/sale_bol_view.xml',
        'views/stock_picking_inherit.xml',
        'views/delivery_carrier_inherit.xml',
        'views/sale_order_form_inherit.xml',

    ],

    'application': False,
}
