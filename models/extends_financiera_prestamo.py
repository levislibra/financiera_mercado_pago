# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp.exceptions import UserError, ValidationError

import mercadopago
import requests
import json

URL_SUSCRIPCION = "https://api.mercadopago.com"

# WEBHOOK_DIR = "https://cloudlibrasoft.com/financiera.mercado.pago/webhook"

class ExtendsFinancieraPrestamo(models.Model):
	_inherit = 'financiera.prestamo' 
	_name = 'financiera.prestamo'

	mercado_pago_checkout_pro = fields.Boolean('Mercado Pago - Link de pago')

	@api.model
	def default_get(self, fields):
		rec = super(ExtendsFinancieraPrestamo, self).default_get(fields)
		if len(self.env.user.company_id.mercado_pago_id) > 0:
			rec.update({
				'mercado_pago_checkout_pro': self.env.user.company_id.mercado_pago_id.set_default_payment,
			})
		return rec

	@api.one
	def enviar_a_acreditacion_pendiente(self):
		super(ExtendsFinancieraPrestamo, self).enviar_a_acreditacion_pendiente()
		if self.mercado_pago_checkout_pro:
			self.mercado_pago_crear_checkouts()

	@api.one
	def mercado_pago_crear_checkouts(self):
		if len(self.company_id.mercado_pago_id) > 0:
			# sdk = mercadopago.SDK(self.company_id.mercado_pago_id.access_token)
			for cuota_id in self.cuota_ids:
				headers = {
					'authorization': "Bearer " + self.company_id.mercado_pago_id.access_token,
					'content-type': 'application/json',
				}
				# Crea un ítem en la preferencia
				preference_data = {
						"items": [
								{
										"title": cuota_id.name,
										"quantity": 1,
										"unit_price": cuota_id.saldo,
								},
						]
				}
				print("creado cuota: ", cuota_id.numero_cuota)
				res = requests.post("https://api.mercadopago.com/checkout/preferences", data=json.dumps(preference_data), headers=headers)
				print("response: ", res)
				preference = res.json()
				print("preference: ", preference)
				# preference_response = sdk.preference().create(preference_data)
				# preference = preference_response["response"]
				checkout_pro_vals = {
					'partner_id': cuota_id.partner_id.id,
					'additional_info': preference['additional_info'],
					'auto_return': preference['auto_return'],
					'binary_mode': preference['binary_mode'],
					'client_id': preference['client_id'],
					'collector_id': preference['collector_id'],
					'date_created': preference['date_created'],
					'date_of_expiration': preference['date_of_expiration'],
					'expiration_date_from': preference['expiration_date_from'],
					'expiration_date_to': preference['expiration_date_to'],
					'expires': preference['expires'],
					'external_reference': preference['external_reference'],
					'id': preference['id'],
					'init_point': preference['init_point'],
					# 'items': preference['items'],
					'cuota_id': cuota_id.id,
					'notification_url': preference['notification_url'],
					'operation_type': preference['operation_type'],
					'sandbox_init_point': preference['sandbox_init_point'],
					'site_id': preference['site_id'],
					'total_amount': preference['total_amount'],
					'last_updated': preference['last_updated'],
				}
				checkout_pro_id = self.env['financiera.mercado.pago.checkout.pro'].create(checkout_pro_vals)
				cuota_id.checkout_pro_ids = [checkout_pro_id.id]