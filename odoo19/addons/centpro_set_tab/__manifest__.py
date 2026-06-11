
{

    'author': 'Centralasis Proactive Solutions Ltd.',
    'company': 'Centralasis Proactive Solutions Ltd.',
    'maintainer': 'Centralasis Proactive Solutions Ltd.',
    'website': "https://www.centralasis.com",
    'name': 'POS Bar Configurations',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Set Tab for POS Bar',
    'depends': ['point_of_sale', 'account', 'pos_restaurant'],
    'installable': True,
    'license': 'OPL-1',


    'assets': {
        'point_of_sale._assets_pos': [
            'centpro_set_tab/static/src/**/**',

        ],
    }




}
