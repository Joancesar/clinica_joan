# -*- coding: utf-8 -*-

{
    'name': 'Clinica Veterinaria Joan y Jorge',
    'sequence': 120,
    'version': '2.0',
    'depends': ['base','mail'],
    'category': 'Veterinaria',
    'summary': 'Clinica Veterinaria',
    'description': "Modulo Chido para controlar tienda de animales o algo no se",
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/clinica_security.xml',
        'views/clinica_view.xml',
        'views/sequence.xml',
        'views/estilos.xml',
        'views/report.xml',
        'data/mail_template.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
}
