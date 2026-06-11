{

    'author': 'Centralasis Proactive Solutions Ltd.',
    'company': 'Centralasis Proactive Solutions Ltd.',
    'maintainer': 'Centralasis Proactive Solutions Ltd.',
    'website': "https://www.centralasis.com",
    'name': 'POS Payment/Validate Order Shortcut',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'description': 'POS Payment/Validate Order Shortcut',
    'summary': 'POS Payment/Validate Order Shortcut',
    'depends': ['point_of_sale',],
    'installable': True,
    'license': 'OPL-1',



    'price': 45.00,
    'currency': 'USD',

    'assets': {
        'point_of_sale._assets_pos': [
            'centra_pos_payment_shortcuts/static/src/**/**',

        ],
    }
}
