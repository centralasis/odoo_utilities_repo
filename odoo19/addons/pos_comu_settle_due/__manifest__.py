
{

    'author': 'Centralasis Proactive Solutions Ltd.',
    'company': 'Centralasis Proactive Solutions Ltd.',
    'maintainer': 'Centralasis Proactive Solutions Ltd.',
    'website': "https://www.centralasis.com",
    'name': 'Point of Sale Community Settle Due',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'For community users to settle ammount Due in th POS UI.',
    'depends': ['point_of_sale', 'account'],
    'installable': True,
    'license': 'OPL-1',

    'data': [
        'views/pos_order_views.xml',
        'views/account_move_views.xml',
        'data/pos_comu_settle_due.xml',
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'pos_comu_settle_due/static/src/**/*',

        ],
    }



}
