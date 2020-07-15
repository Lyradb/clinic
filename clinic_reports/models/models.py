# # -*- coding: utf-8 -*-
#
from odoo import models, fields, api
#
# class AppointmentEntry(models.Model):
#     _name = 'clinic.appointment.entry'
#

class ClinicBooking(models.Model):
    _inherit = 'clinic.booking'

    def get_license(self,physician):
        return self.env['config.md.license'].search([('user_id','=',physician.id)], order='effectivity_date desc', limit=1).license_no

    def get_ptr(self,physician):
        return self.env['config.md.license'].search([('user_id', '=', physician.id)], order='effectivity_date desc',
                                                    limit=1).ptr_no
    def get_s2(self,physician):
        return self.env['config.md.license'].search([('user_id', '=', physician.id)], order='effectivity_date desc',
                                                    limit=1).s2_no


