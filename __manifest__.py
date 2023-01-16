{
    'name': 'estate',
    'version': '1.0',
    'author': 'HTCompass',
    'category': 'Real Estate/Brokerage',
    'summary': 'Create your estates here, and get the track of them',
    'description': "This is description",
    'depends':['base',],
    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_offer.xml',
        'views/res_user_views.xml',
        'views/estate_type_view.xml',
        'views/estate_tags.xml',
        'views/estate_menus.xml',
    ],
    'demo': [
    ],
    'sequence': 1,
    'application': True,
    'autoinstall': False,
    'installable': True
}