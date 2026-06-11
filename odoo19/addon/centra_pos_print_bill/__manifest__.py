{

    'author': 'Centralasis Proactive Solutions Ltd.',
    'company': 'Centralasis Proactive Solutions Ltd.',
    'maintainer': 'Centralasis Proactive Solutions Ltd.',
    'website': "https://www.centralasis.com",
    'name': 'PoS Print Bill',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'description': 'This module allows to print bill before the order is paid',
    'summary': 'This module allows to print bill before the order is paid',
    'depends': ['point_of_sale',],
    'installable': True,
    'license': 'OPL-1',

    'price': 15.00,
    'currency': 'USD',

    'assets': {
        'point_of_sale._assets_pos': [
            'centra_pos_print_bill/static/src/**/**',

        ],
    }
}
