{
    'name': "Custom Website Changes",
    'summary': """No powered by Odoo, Language dropdown on header""",
    'description': """
        Banner
    """,
    'author': 'Zmakan Technical Solutions',
    'company': 'Zmakan Technical Solutions',
    'website': 'www.zmakan.com',
    'version': '14.0',

    'depends': ['base','website'],
    'data': [
        #'security/ir.model.access.csv'
        'views/website_templates.xml',
    ],
    'installable': True,
}