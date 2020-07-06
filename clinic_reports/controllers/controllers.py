# -*- coding: utf-8 -*-
from odoo import http

# class ClinicReports(http.Controller):
#     @http.route('/clinic_reports/clinic_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/clinic_reports/clinic_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('clinic_reports.listing', {
#             'root': '/clinic_reports/clinic_reports',
#             'objects': http.request.env['clinic_reports.clinic_reports'].search([]),
#         })

#     @http.route('/clinic_reports/clinic_reports/objects/<model("clinic_reports.clinic_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('clinic_reports.object', {
#             'object': obj
#         })