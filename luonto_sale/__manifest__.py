# -*- coding: utf-8 -*-
{
    'name': "Luonto Furniture: Delivery Method Pricing Rule",

    'summary': """
       This “Number of Seats” field will be on the product form with technical name “x_studio_seat_qty_for_freight”
        We want this “Number of Seats” to appear in this “Create Pricing Rules” screen. And then calculate the shipping costs accordingly upon selection of that specific Carrier 
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

    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['delivery'],

    # always loaded
    'data': [
       
    ],
}