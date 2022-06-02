# -*- coding: utf-8 -*-

from openerp import models, fields, api

class FinancieraMercadoPagoCheckoutPro(models.Model):
	_name = 'financiera.mercado.pago.checkout.pro'

	id = fields.Char('ID')
	partner_id = fields.Many2one('res.partner', 'Cliente')
	additional_info = fields.Char('Informacion Adicional')
	auto_return = fields.Char('Auto return')
	binary_mode = fields.Char('Modo Binario')
	client_id = fields.Char('ID de cliente')
	collector_id = fields.Integer('ID de Collector')
	date_created = fields.Char('Fecha de creacion')
	date_of_expiration = fields.Char('Fecha de vencimiento del medio de pago en efectivo')
	expiration_date_from = fields.Char('Fecha desde')
	expiration_date_to = fields.Char('Fecha hasta')
	expires = fields.Char('Determina si expira')
	external_reference = fields.Char('Referencia externa')
	init_point = fields.Char('Link de Pago')
	items = fields.One2many('financiera.mercado.pago.checkout.pro.line', 'checkout_pro_id', 'Items')
	# Si el checkout esta asociado unicamente a una cuota
	cuota_id = fields.Many2one('financiera.prestamo.cuota', 'Cuota')
	# Si el checkout esta asociado a multiples cuotas - vence si se genera un checkout nuevo
	cuota_ids = fields.One2many('financiera.prestamo.cuota', 'checkout_pro_id', 'Cuotas')
	notification_url = fields.Char('Url de notificaciones')
	operation_type = fields.Char('Tipo de operacion')
	sandbox_init_point = fields.Char('Sandbox link')
	site_id = fields.Char('ID de sitio')
	total_amount = fields.Float('Monto total', digits=(16,2))
	last_updated = fields.Char('Fecha de ultima actualizacion')
	company_id = fields.Many2one('res.company', 'Empresa')


class FinancieraMercadoPagoCheckoutProLine(models.Model):
	_name = 'financiera.mercado.pago.checkout.pro.line'

	checkout_pro_id = fields.Many2one('financiera.mercado.pago.checkout.pro', 'ID del Checkout')
	currency_id = fields.Char('Moneda')
	title = fields.Char('Titulo')
	quantity = fields.Integer('Cantidad')
	unit_price = fields.Float('Precio', digits=(16,2))
	company_id = fields.Many2one('res.company', 'Empresa')































