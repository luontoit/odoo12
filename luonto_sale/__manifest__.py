# -*- coding: utf-8 -*-
{
    'name': "Luonto Furniture: Delivery Method Pricing Rule",

    'summary': """
       Delivery method pricing rule based on number of seats
    """,

    'description': """
        Task ID: 2216387 - AAL
        
        1. Creating the new Field to be applied as a Rule on the pop-up wizard for Select the Delivery Pricing Rules on delivery.carrier model. 
            a. This new field will be "Number of Seats".

        2. On the Sales Order form view, once the product is selected on SO lines, user is ready to "Get Rate" from Delivery Carrier.
            The way this rate is calculated, if the "Number of Seats" is selected as the Rule condition on the Carrier, is:
            Database will access the record for field "x_studio_seat_qty_for_freight" of each product on the SO Line. Then it will sum all of them, then the price will be computed based on the Rules.
    """,

    'author': "Odoo PS-US",
    'website': "http://www.odoo.com",
    'license': 'OEEL-1',

    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['delivery'],

    # always loaded
    'data': [
       'views/product_template.xml'
    ],
}