# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ExtendsResCompany(models.Model):
	_name = 'res.company'
	_inherit = 'res.company'

	mercado_pago_id = fields.Many2one('financiera.mercado.pago.config', 'Configuracion Mercado Pago')