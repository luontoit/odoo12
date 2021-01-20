# -*- coding: utf-8 -*-
{
    'name': "Pivot Scheduler",

    'summary': """Send Pivot view (Business Intelligence Report) automatically through pre-defined users by Minutes, Hours, Days, Months.""",

    'description': """
Module to send Pivot view (Business Intelligence Report) automatically 
=========================================================
    """,

    'author': "Jothimani Rajagopal",
    'website': "http://www.linkedin.com/in/jothimani-r",
    'category': 'Utilities',
    'version': '13.0.1',
    'depends': ['base', 'mail'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/ir_actions_data.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'price': 249.00,
    'currency': 'USD',
    'live_test_url': 'http://3.138.96.201:8069'
}
