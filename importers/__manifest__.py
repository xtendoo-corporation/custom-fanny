{
    'name': 'Invoice Import Wizard',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Import invoices from Excel files',
    'description': 'Module that allows importing invoices from an Excel file',
    'author': 'Dani Domínguez',
    'depends': ['account'],
    'data': [
        'views/import_invoice_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}
