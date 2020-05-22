# -*- coding: utf-8 -*-
{
    'name': "Luonto Furniture: Product and Attribute Value Changes",

    'summary': """
        Development to facilitate which colors are available for each fabric type. 
    """,

    'description': """
        Task ID: 2042753 - CIC

        1. Ability to upload available attribute values (ie. colors) available for another attribute value (ie. fabric style).
        2. An action to apply these attribute value combinations to all product templates that have the attribute value as one of the options.
        3. The sales tools (ecommerce shop and sale.order) will hide the attribute values (colors) not available for a selected attribute value (fabric style).

        4. Product configurator on backend sales should also make the incompatible attribute values invisible.

        5. Scheduled action to run the attribute changes. Do you think this would be the best way to run the sub attribute action without having to break it into chunks?
        6. They would like it to be mandatory to select an option other than "Please Select" on the ecommerce.
        7. The additional price should not appear in parentheses next to the attribute value. The reason is that he uses percentage margin pricelists and it will show the customer a different final price than the additional price indicates.

        Task ID: 2210524 - CIC

        1.) Always display attribute values in alphabetical ascending order on the ecommerce and product configurator views. Currently it is displaying out of order and it is time-consuming to make them appear in alphabetical order manually.
        2.) When selecting sub-attribute values from an attribute value there should be option to select multiple sub attributes at the same time in the popup window. It takes a long time to do this manually.
        3.) Add “Reset” button to ecommerce product page and product configurator popup. Right justified to the same line as the Upholstery grade title. That reset button should reset all the dropdown fields on this one product to "Please Select", the first default option as an attribute value.
        4.) If the upholstery color code is selected first, the upholstery grade and name should be automatically selected since those are the only configurable selections available. Currently configuration works well "broad to narrow" use case, but not the opposite direction. If user knows the exactly color code, the upholstery name and grade should automatically configure based on attribute value logic. Video: https://drive.google.com/file/d/1s_EP4kReedU8VtJnebpi-BOwk-NDzh0d/view?usp=sharing
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