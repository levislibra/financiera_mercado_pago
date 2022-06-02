# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp.exceptions import UserError, ValidationError

import mercadopago
import requests
import json

# WEBHOOK_DIR = "https://cloudlibrasoft.com/financiera.mercado.pago/webhook"

class ExtendsFinancieraPrestamoCuota(models.Model):
	_inherit = 'financiera.prestamo.cuota'
	_name = 'financiera.prestamo.cuota'

	# Sirve para multiples cuotas - Vence si se genera un nuevo Checkout
	checkout_pro_id = fields.Many2one('financiera.mercado.pago.checkout.pro', 'Mercado Pago - ID del Checkout')
	# Siver para guardar los link de pago de la cuota
	checkout_pro_ids = fields.One2many('financiera.mercado.pago.checkout.pro', 'cuota_id', 'Mercado Pago - Links de pago')