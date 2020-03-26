# -*- coding: utf-8 -*-
{
    'name': "Luonto Furniture: Attribute Value Exclusions",

    'summary': """
        Development to facilitate which colors are available for each fabric type. 
    """,

    'description': """
        Task ID: 2042753 - CIC
        
        1. Ability to upload available attribute values (ie. colors) available for another attribute value (ie. fabric style).

        2. An action to apply these attribute value combinations to all product templates that have the attribute value as one of the options.

        3. The sales tools (ecommerce shop and sale.order) will hide the attribute values (colors) not available for a selected attribute value (fabric style).
    
        ​​​​4. Product configurator on backend sales should also make the incompatible attribute values invisible.
        
        5. Scheduled action to run the attribute changes. Do you think this would be the best way to run the sub attribute action without having to break it into chunks?

        6. They would like it to be mandatory to select an option other than "Please Select" on the ecommerce.

        7. The additional price should not appear in parentheses next to the attribute value. The reason is that he uses percentage margin pricelists and it will show the customer a different final price than the additional price indicates.
    """,

    'author': "Odoo PS-US",
    'website': "http://www.odoo.com",

    'category': 'Custom Development',
    'version': '0.1',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['base_automation', 'stock', 'website_sale'],

    # always loaded
    'data': [
        'data/actions.xml',
        'views/product_attribute_views.xml',
        'views/templates.xml',
    ],
}