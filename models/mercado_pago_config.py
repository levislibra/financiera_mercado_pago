# -*- coding: utf-8 -*-

from openerp import models, fields, api

class FinancieraMercadoPagoConfig(models.Model):
	_name = 'financiera.mercado.pago.config'

	name = fields.Char('Nombre')
	api_key = fields.Char('API Key')
	access_token = fields.Char('Token')
	set_default_payment = fields.Boolean('Marcar como medio de pago por defecto')
	return_url = fields.Char('Url posterior a la suscripcion')
	company_id = fields.Many2one('res.company', 'Empresa', required=False)
	journal_id = fields.Many2one('account.journal', 'Diario de Cobro', domain="[('type', 'in', ('cash', 'bank'))]")
	factura_electronica = fields.Boolean('Factura electronica')
