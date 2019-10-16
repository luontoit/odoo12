# -*- coding: utf-8 -*-
{
    'name': "Luonto Furniture: Attribute Value Exclusions",

    'summary': """
        Development to facilitate which colors are available for each fabric type. 
    """,

    'description': """
        1. Ability to upload available attribute values (ie. colors) available for another attribute value (ie. fabric style).

        2. An action to apply these attribute value combinations to all product templates that have the attribute value as one of the options.

        3. The sales tools (ecommerce shop and sale.order) will hide the attribute values (colors) not available for a selected attribute value (fabric style).
    """,

    'author': "Odoo PS-US",
    'website': "http://www.odoo.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_automation', 'stock', 'website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/fields.xml',
        'data/actions.xml',
        'views/product_attribute_views.xml',
        'views/templates.xml',
    ],
}