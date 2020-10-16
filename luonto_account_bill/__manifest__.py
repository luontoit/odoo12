# -*- coding: utf-8 -*-
{
    'name': "Vendor Bill from Invoice",

    'summary': """
        Create a vendor bill with commission from invoice""",

    'description': """
        Task ID: 2258960
        1)  We want to create a Vendor Bill for a Salesperson whenever these conditions are met:
            There are Storable Products on the Invoice
            There is a Salesperson on the Invoice

        2)  The Vendor Bill will be created based on Non-taxed Amount of the Storable Products in the Invoice.
            If the Customer in the Initial Invoice has type: “X” than commission = sum(Non-taxed Amount of Storable Products) * x_studio_commission_percentage (related field from res.partner from new model x_customer_type)
            The Invoice Line of the commission Vendor Bill should have as Account: 6010 – Commission Expenses.
            All the information related to dates in the original customer invoice should remain on the Vendor Bill.
            (Posting Date / Accounting Date)
            
        3)  Create a link between the two documents. Once the Vendor Bill is created from the Invoice, there should be a Many-To-One from the Bill to the Invoice.
            This way we can create related fields from the Invoice, like whether the invoice was fully paid or not. The related field I can create it with Studio
    """,

    'author': "Odoo Inc",
    'website': "http://www.odoo.com",
    'category': 'Custom Development',
    'license': 'OEEL-1',
    'version': '1.0',
    'depends': ['account_accountant', 'contacts'],

    'data': [
        'views/partner_views.xml',
        'views/account_move_views.xml',
        'security/ir.model.access.csv'
    ]
}
