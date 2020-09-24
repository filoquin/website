# -*- coding: utf-8 -*-
{
    'name': "Decidir 1.0",

    'summary': """
        Implement Decidir 1.0 payment method""",

    'description': """
    Decidir 1.0
    ---------------
    Implement Decidir 1.0 payment method
    """,

    'author': "filoquin",
    'website': "http://www.sipecu.com.at",

    'category': 'payment',
    'version': '13.0.0.1',

    'depends': ['payment'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/payment_acquirer.xml',
        'views/templattes.xml',
    ],

}
