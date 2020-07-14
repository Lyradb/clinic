# # -*- coding: utf-8 -*-
#
from odoo import models, fields, api
#
# class AppointmentEntry(models.Model):
#     _name = 'clinic.appointment.entry'
#
# class Partner(models.Model):
#     _inherit = 'res.partner'
#
#     partner_type = fields.Selection([('patient','Patient'),('doctor','Doctor'),('staff','Staff')])
#     diagnosis = fields.Text('Diagnosis',required_if_partner_type='patient')
#     license_no = fields.Char('License Number',required_if_partner_type='doctor')
#     ptr_no = fields.Char('PTR Number',required_if_partner_type='doctor')
#     s2_no = fields.Char('S2 Number',required_if_partner_type='doctor')
#     exam_date = fields.Date('Date Examined',required_if_partner_type='patient')
#     blood_pressure = fields.Char('Blood Pressure')
#     heart_rate = fields.Char('Heart Rate')
#     temperature = fields.Char('Body Temperature')
# class Users(models.Model):
#     _inherit = 'res.users'
#
#     license_no = fields.Char(default = lambda self:self.env['config.md.license'].search('user_id','=',self.env.user.id))
#     ptr_no = fields.Char(default = lambda self:self.env['config.md.license'].search('user_id','=',self.env.user.id))
#     s2_no = fields.Char(default = lambda self:self.env['config.md.license'].search('user_id','=',self.env.user.id))
#

#
# class ClinicBooking(models.Model):
#     _inherit = 'clinic.booking'
#
#     medical_certificate = fields.One2many('medical.certificate', 'booking_id', 'Medical Certificate')
#
# class Certificate(models.Model):
#     _name = 'medical.certificate'
#
#     name = fields.Char(string='Title', compute='_get_name')
#     date = fields.Date(string='Date')
#     booking_id = fields.Many2one('clinic.booking', 'Booking Record')
#     patient_id = fields.Many2one('clinic.booking',related='booking_id.patient_id',string='Patient', domain=[('active','=',True)])
#     physician_id = fields.Many2one('clinic.booking',related='booking_id.physician_id',string='Attending Physician')
#     recommendation = fields.Text(string='Recommendation')
#
#     @api.depends('patient', 'doctor', 'date')
#     def _get_name(self):
#         self.name = '%s - %s (%s)' % (self.patient_id.patinet_name, self.physician_id.name, str(self.date))

# class Inventory(models.Model):
#     _name = 'clinic.medicine.inventory'
#
#     name = fields.Char(string='Medicine')
#     classification = fields.Char(string='Classification')
#     unit = fields.Char(string='Unit')
#     selling_price = fields.Monetary(string='Selling Price')
#     qty_in = fields.Integer(string='Qty IN')
#     qty_out = fields.Integer(string='Qty OUT')
#     on_hand = fields.Char(string='On Hand')
#     amount = fields.Monetary(string='Amount')
#     date = fields.Date(string='Date')
#     item_stock_line_ids = fields.One2many("item.stock.line", inverse_name="medicine_id", string="Item Stock Lines")
#
# class Stock(models.Model):
#     _name = 'clinic.item.stock.line'
#
#     name = fields.Char(string='Name')
#     medicine_id = fields.Many2one('medicine.inventory', 'item_stock_line_ids')
#     date = fields.Date(string='Date')
#     trans_type = fields.Selection([('inventory_received','Inventory Receipt'),
#                                    ('medicine_transfer','Medicine Transfer'),
#                                    ('walk_in_med_sales','Walk-in Med Sales')], string='Transaction Type')
#     selling_price = fields.Monetary(string='Selling Price', related='medicine_id.selling_price')
#     qty_in = fields.Integer(string='Qty IN', related='medicine_id.qty_in')
#     qty_out = fields.Integer(string='Qty OUT', related='medicine_id.qty_out')
#     balance = fields.Integer(string='Balance')