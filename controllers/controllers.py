# -*- coding: utf-8 -*-
from openerp import http

# class FinancieraMercadoPago(http.Controller):
#     @http.route('/financiera_mercado_pago/financiera_mercado_pago/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financiera_mercado_pago/financiera_mercado_pago/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financiera_mercado_pago.listing', {
#             'root': '/financiera_mercado_pago/financiera_mercado_pago',
#             'objects': http.request.env['financiera_mercado_pago.financiera_mercado_pago'].search([]),
#         })

#     @http.route('/financiera_mercado_pago/financiera_mercado_pago/objects/<model("financiera_mercado_pago.financiera_mercado_pago"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financiera_mercado_pago.object', {
#             'object': obj
#         })