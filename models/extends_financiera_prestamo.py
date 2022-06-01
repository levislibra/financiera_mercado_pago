# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp.exceptions import UserError, ValidationError

import requests
import json

URL_SUSCRIPCION = "https://api.mercadopago.com"

# WEBHOOK_DIR = "https://cloudlibrasoft.com/financiera.mercado.pago/webhook"

class ExtendsFinancieraPrestamo(models.Model):
	_inherit = 'financiera.prestamo' 
	_name = 'financiera.prestamo'

	mercado_pago_suscripcion = fields.Boolean('Mercado Pago - Suscripcion')
	mercado_pago_suscripcion_id = fields.Char('Mercado Pago - Suscripcion ID')
	mercado_pago_version = fields.Integer('Mercado Pago - Version')
	mercado_pago_application_id = fields.Integer('Mercado Pago - Application ID')
	mercado_pago_collector_id = fields.Integer('Mercado Pago - Collector ID')
	mercado_pago_preapproval_plan_id = fields.Char('Mercado Pago - Preapproval Plan ID')
	mercado_pago_reason = fields.Char('Mercado Pago - Descripcion')
	mercado_pago_external_reference = fields.Char('Mercado Pago - Referencia Externa')
	mercado_pago_back_url = fields.Char('Mercado Pago - Url de retorno')
	mercado_pago_init_point = fields.Char('Mercado Pago - Url Checkout')
	mercado_pago_frequency = fields.Integer('Mercado Pago - Valor de la frecuencia')
	mercado_pago_frequency_type = fields.Char('Mercado Pago - Tipo de la frecuencia')
	mercado_pago_start_date = fields.Char('Mercado Pago - Fecha inicial de la suscripcion')
	mercado_pago_end_date = fields.Char('Mercado Pago - Fecha final de la suscripcion')
	mercado_pago_currency_id = fields.Char('Mercado Pago - Moneda ID', help="ARS para Pesos Argentinos.")
	mercado_pago_transaction_amount = fields.Float('Mercado Pago - Suma que se cobrara en cada debito', digits=(16, 2))
	mercado_pago_payer_id = fields.Integer('Mercado Pago - Cliente ID')
	mercado_pago_card_id = fields.Integer('Mercado Pago - Card ID')
	mercado_pago_payment_method_id = fields.Integer('Mercado Pago - Metodo de Pago ID')
	mercado_pago_next_payment_date = fields.Char('Mercado Pago - Fecha del proximo debito')
	mercado_pago_date_created = fields.Char('Mercado Pago - Fecha de creacion')
	mercado_pago_last_modified = fields.Char('Mercado Pago - Fecha de ultima modificacion')
	mercado_pago_status = fields.Char('Mercado Pago - Estado')
	# summarized
	mercado_pago_last_charged_date = fields.Char('Mercado Pago - Fecha del ultimo cobro')
	mercado_pago_charged_quantity = fields.Integer('Mercado Pago - Cantidad')
	mercado_pago_charged_amount = fields.Float('Mercado Pago - Monto', digits=(16, 2))
	mercado_pago_quotas = fields.Integer('Mercado Pago - Cuotas')
	mercado_pago_last_charged_amount = fields.Float('Mercado Pago - Monto del ultimo cobro', digits=(16, 2))
	mercado_pago_pending_charge_amount = fields.Float('Mercado Pago - Monto pendiente por cobrar', digits=(16, 2))
	mercado_pago_semaphore = fields.Char('Mercado Pago - Semaforo')
	mercado_pago_pending_charge_quantity = fields.Char('Mercado Pago - Cantidad de cobros pendientes')
	# mercado_pago_ = fields.Char('Mercado Pago - ')

	@api.model
	def default_get(self, fields):
		rec = super(ExtendsFinancieraPrestamo, self).default_get(fields)
		if len(self.env.user.company_id.mercado_pago_id) > 0:
			rec.update({
				'mercado_pago_suscripcion': self.env.user.company_id.mercado_pago_id.set_default_payment,
			})
		return rec

	@api.one
	def enviar_a_autorizado(self):
		super(ExtendsFinancieraPrestamo, self).enviar_a_autorizado()
		if self.mercado_pago_suscripcion:
			if not self.mercado_pago_suscripcion_id:
				self.mercado_pago_crear_suscripcion()
				self.mobbex_suscripcion_suscriptor_confirm = False

	@api.one
	def mercado_pago_crear_suscripcion(self):
		# Condiciones para poder crear suscripcion de Mercado Pago
		periodo = self.plan_id.periodo == 'mensual'
		cuota_iguales = self.plan_id.amortizacion_tipo == 'sistema_directa' or self.plan_id.interes_iva == False or self.plan_id.interes_iva_incuido_tasa
		gestion_igual = not self.plan_id.cuota_gestion_calcular or (self.plan_id.cuota_gestion_calcular and (self.plan_id.cuota_gestion_tasa_sobre == 'monto_solicitado' or self.plan_id.cuota_gestion_tasa_aplicar == 0))
		if periodo and cuota_iguales and gestion_igual:
			headers = {
				'authorization': "Bearer " + self.company_id.mercado_pago_id.access_token,
				'content-type': 'application/json',
			}
			payer_email = None
			if not self.partner_id.email:
				raise ValidationError("El cliente no tiene definido el email y la suscripcion para Mercado Pago no puede generarse.")
			payer_email = self.partner_id.email
			# Mercado Pago no soporta la cuota cero
			cuota_base = self.cuota_ids[0]
			if cuota_base.numero_cuota == 0:
				cuota_base = self.cuota_ids[1]
			start_date = datetime.strptime(cuota_base.fecha_vencimiento, "%Y-%m-%d") + timedelta(days=self.company_id.mercado_pago_id.days_execute_on_expiration)
			end_date = datetime.strptime(self.cuota_ids[len(self.cuota_ids)-1].fecha_vencimiento, "%Y-%m-%d") + timedelta(days=30)
			transaction_amount = cuota_base.total
			body = {
				'auto_recurring': {
						'frequency': 1,
						'frequency_type': 'months',
						'transaction_amount': round(transaction_amount, 2),
						'start_date': start_date.strftime("%Y-%m-%dT13:15:12.260Z"),
						'end_date': end_date.strftime("%Y-%m-%dT13:15:12.260Z"),
						'currency_id': 'ARS',
				},
				'back_url': self.company_id.mercado_pago_id.return_url,
				'external_reference': str(self.id),
				'payer_email': payer_email,
				'reason': self.name,
				'status': 'pending',
			}
			print("PARAMS: ", body)
			res = requests.post(URL_SUSCRIPCION + "/preapproval", data=json.dumps(body), headers=headers)
			print("response: ", res)
			data = res.json()
			print("DATAAAA: ", data)
			self.mercado_pago_suscripcion_procesar_data(data)

	@api.one
	def button_mercado_pago_crear_suscripcion(self):
		# Condiciones para poder crear suscripcion de Mercado Pago
		periodo = self.plan_id.periodo == 'mensual'
		if not periodo:
			raise ValidationError("La suscripcion a Mercado Pago esta habilitada unicamenta para planes mensuales de cuotas iguales.")
		cuota_iguales = self.plan_id.amortizacion_tipo == 'sistema_directa' or self.plan_id.interes_iva == False or self.plan_id.interes_iva_incuido_tasa
		if not cuota_iguales:
			raise ValidationError("La suscripcion a Mercado Pago esta habilitada unicamenta para planes que generan cuotas iguales (chequear tipo de amortizacion e interes incluido en la tasa).")
		gestion_igual = not self.plan_id.cuota_gestion_calcular or (self.plan_id.cuota_gestion_calcular and (self.plan_id.cuota_gestion_tasa_sobre == 'monto_solicitado' or self.plan_id.cuota_gestion_tasa_aplicar == 0))
		if not gestion_igual:
			raise ValidationError("La suscripcion a Mercado Pago esta habilitada unicamenta para planes que generan cuotas iguales (chequear calculo de gastos de gestion).")
		self.mercado_pago_crear_suscripcion()


	def mercado_pago_suscripcion_procesar_data(self, data):
		if 'id' in data:
			self.mercado_pago_suscripcion_id = data['id']
		if 'version' in data:
			self.mercado_pago_version = data['version']
		if 'application_id' in data:
			mercado_pago_application_id = data['application_id']
		if 'collector_id' in data:
			self.mercado_pago_collector_id = data['collector_id']
		if 'preapproval_plan_id' in data:
			self.mercado_pago_preapproval_plan_id = data['preapproval_plan_id']
		if 'reason' in data:
			self.mercado_pago_reason = data['reason']
		if 'external_reference' in data:
			self.mercado_pago_external_reference = data['external_reference']
		if 'back_url' in data:
			self.mercado_pago_back_url = data['back_url']
		if 'init_point' in data:
			self.mercado_pago_init_point = data['init_point']
		# Object auto_recurring
		if 'auto_recurring' in data and 'frequency' in data['auto_recurring']:
			self.mercado_pago_frequency = data['auto_recurring']['frequency']
		if 'auto_recurring' in data and 'frequency_type' in data['auto_recurring']:
			self.mercado_pago_frequency_type = data['auto_recurring']['frequency_type']
		if 'auto_recurring' in data and 'start_date' in data['auto_recurring']:
			self.mercado_pago_start_date = data['auto_recurring']['start_date']
		if 'auto_recurring' in data and 'end_date' in data['auto_recurring']:
			self.mercado_pago_end_date = data['auto_recurring']['end_date']
		if 'auto_recurring' in data and 'currency_id' in data['auto_recurring']:
			self.mercado_pago_currency_id = data['auto_recurring']['currency_id']
		if 'auto_recurring' in data and 'transaction_amount' in data['auto_recurring']:
			self.mercado_pago_transaction_amount = data['auto_recurring']['transaction_amount']
		if 'payer_id' in data:
			self.mercado_pago_payer_id = data['payer_id']
		if 'card_id' in data:
			mercado_pago_card_id = data['card_id']
		if 'payment_method_id' in data:
			self.mercado_pago_payment_method_id = data['payment_method_id']
		if 'next_payment_date' in data:
			self.mercado_pago_next_payment_date = data['next_payment_date']
		if 'date_created' in data:
			self.mercado_pago_date_created = data['date_created']
		if 'last_modified' in data:
			self.mercado_pago_last_modified = data['last_modified']
		if 'status' in data:
			self.mercado_pago_status = data['status']
		# Object summarized
		if 'summarized' in data and 'last_charged_date' in data['summarized']:
			self.mercado_pago_last_charged_date = data['summarized']['last_charged_date']
		if 'summarized' in data and 'charged_quantity' in data['summarized']:
			self.mercado_pago_charged_quantity = data['summarized']['charged_quantity']
		if 'summarized' in data and 'charged_amount' in data['summarized']:
			self.mercado_pago_charged_amount = data['summarized']['charged_amount']
		if 'summarized' in data and 'quotas' in data['summarized']:
			self.mercado_pago_quotas = data['summarized']['quotas']
		if 'summarized' in data and 'last_charged_amount' in data['summarized']:
			self.mercado_pago_last_charged_amount = data['summarized']['last_charged_amount']
		if 'summarized' in data and 'pending_charge_amount' in data['summarized']:
			self.mercado_pago_pending_charge_amount = data['summarized']['pending_charge_amount']
		if 'summarized' in data and 'semaphore' in data['summarized']:
			self.mercado_pago_semaphore = data['summarized']['semaphore']
		if 'summarized' in data and 'pending_charge_quantity' in data['summarized']:
			self.mercado_pago_pending_charge_quantity = data['summarized']['pending_charge_quantity']

	# @api.one
	# def mobbex_obtener_suscription(self):
	# 	url = URL_SUSCRIPTIONS+self.mobbex_suscripcion_id
	# 	headers = {
	# 		'x-api-key': self.mobbex_id.api_key,
	# 		'x-access-token': self.mobbex_id.access_token,
	# 		'content-type': 'application/json',
	# 	}
	# 	r = requests.get(url, headers=headers)

	# @api.one
	# def mobbex_activate_suscription(self):
	# 	url = URL_SUSCRIPTIONS+self.mobbex_suscripcion_id+'/action/activate'
	# 	headers = {
	# 		'x-api-key': self.mobbex_id.api_key,
	# 		'x-access-token': self.mobbex_id.access_token,
	# 		'content-type': 'application/json',
	# 	}
	# 	r = requests.get(url, headers=headers)


	# @api.one
	# def mobbex_create_suscriptor(self):
	# 	url = URL_SUSCRIPTIONS+self.mobbex_suscripcion_id+'/subscriber'
	# 	headers = {
	# 		'x-api-key': self.mobbex_id.api_key,
	# 		'x-access-token': self.mobbex_id.access_token,
	# 		'content-type': 'application/json',
	# 	}
	# 	current_day = datetime.now()
	# 	if self.partner_id.dni == False:
	# 		raise UserError("Error en DNI del cliente.")
	# 	body = {
	# 		'customer': {
	# 			'identification': self.partner_id.dni,
	# 			'email': self.partner_id.email,
	# 			'name': self.partner_id.name,
	# 			'phone': str(self.partner_id.mobile),
	# 		},
	# 		'reference': str(self.id),
	# 		'startDate': {
	# 			'day': current_day.day,
	# 			'month': current_day.month,
	# 		},
	# 	}
	# 	r = requests.post(url, data=json.dumps(body), headers=headers)
	# 	data = r.json()
	# 	if 'result' in data and data['result'] == True:
	# 		self.mobbex_suscriptor_id = data['data']['uid']
	# 		self.mobbex_suscriptor_sourceUrl = data['data']['sourceUrl']
	# 		self.mobbex_suscriptor_subscriberUrl = data['data']['subscriberUrl']

	# @api.one
	# def mobbex_suscripcion_exitosa(self, payment_status):
	# 	if self.mobbex_id.accept_no_funds:
	# 		self.mobbex_suscripcion_suscriptor_confirm = True
	# 	elif payment_status == '200':
	# 		self.mobbex_suscripcion_suscriptor_confirm = True

