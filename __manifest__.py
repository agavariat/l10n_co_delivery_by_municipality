# -*- coding: utf-8 -*-

{
    'name': 'Delivery Charges By Municipality',
    'category': 'Delivery',
    'version': '12.0.0.1',
    'summary': 'Delivery Charges By Municipality',
    'depends': [
        'website_sale_delivery',
        'l10n_co_res_partner',
    ],
    'data': [
        'views/view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
