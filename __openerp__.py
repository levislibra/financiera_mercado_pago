# -*- coding: utf-8 -*-
{
    'name': "Financiera Mercado Pago",

    'summary': """
        Suscripcion a Mercado Pago con cobro autorizado y links de pagos de cuotas.""",

    'description': """
        Suscripcion a Mercado Pago con cobro autorizado y links de pagos de cuotas.
    """,

    'author': "Librasoft",
    'website': "https://libra-soft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','financiera_prestamos'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/mercado_pago_config.xml',
				'views/mercado_pago_checkout_pro.xml',
				'views/extends_res_company.xml',
				'views/extends_financiera_prestamo.xml',
				'views/extends_financiera_prestamo_cuota.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}