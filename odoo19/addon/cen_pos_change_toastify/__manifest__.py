{

    'author': 'Centralasis Proactive Solutions Ltd.',
    'company': 'Centralasis Proactive Solutions Ltd.',
    'maintainer': 'Centralasis Proactive Solutions Ltd.',
    'website': "https://www.centralasis.com",
    'name': 'POS Change Toastiy Notification',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'description': 'This module shows PoS change in the form of a toastiy notification',
    'summary': 'This module shows PoS change in the form of a toastiy notification',
    'depends': ['point_of_sale',],
    'installable': True,
    'license': 'OPL-1',

    'price': 25.00,
    'currency': 'USD',

    'images': ['static/description/banner.gif'],

    'assets': {
        'point_of_sale._assets_pos': [
            'cen_pos_change_toastify/static/src/**/**',

        ],
    }
}
