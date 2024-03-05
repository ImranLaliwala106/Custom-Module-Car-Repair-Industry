{
    'name' : 'Car Repair Industry',
    'version' : '17.0',
    'description': '''Car Repair Industry''',

    'depends': ['base','mail','product','purchase','sale'],
    'data': [
        'security/security_groups.xml',
        'security/security_access.xml',
        'security/ir.model.access.csv',
        'views/car_repair_view.xml',
        'views/product_view.xml',
        'data/car_repair.sequence.xml',
        'data/mail_template.xml',
        'data/mail_template_on_filter_1.xml',
        'data/car_repair_schedule.xml',
        'data/mail_template_reminder.xml',
        'wizard/car_repair_wizard_view.xml',
        'report/car_repair_report.xml',
        'report/car_repair_filter_report.xml',
    ],  
    
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}