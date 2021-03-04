# # -*- coding: utf-8 -*-
#
from odoo import models, fields, api, _
from datetime import datetime



class ClinicBookingLabReq(models.Model):
    _name = 'clinic.booking.laboratory.request'
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
    )
    
    lab_id = fields.Many2one(
        string="Laboratory",
        comodel_name="config.laboratory.request",
    )
    
    name = fields.Char(string="Name", related='lab_id.name')
    
class ClinicBookingBloodChem(models.Model):
    _name = 'clinic.booking.config.blood.chem.request'
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
    )
    
    lab_id = fields.Many2one(
        string="Blood Chemistry",
        comodel_name="config.blood.chem.request",
    )
    
    selected = fields.Boolean(string='Checked?')
    
    group = fields.Integer(string="Display Group", track_visibility=True,
                           related='lab_id.group')
    
    name = fields.Char(string="Name", related='lab_id.name')
    
    selected = fields.Boolean(string='Checked?')
    

class ClinicBookingXRayReq(models.Model):
    _name = 'clinic.booking.config.xray.exam.request'
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
    )
    
    lab_id = fields.Many2one(
        string="X-Ray request",
        comodel_name="config.xray.exam.request",
    )
    
    group = fields.Integer(string="Display Group", track_visibility=True,
                           related='lab_id.group')
    
    selected = fields.Boolean(string='Checked?')
    
    name = fields.Char(string="Name", related='lab_id.name')
    
class ClinicBooking(models.Model):
    _inherit = 'clinic.booking'
    
    lab_req_ids = fields.One2many(
        string="Laboratory Request",
        comodel_name="clinic.booking.laboratory.request",
        inverse_name="booking_id",
    )
    
    lab_bloodchem_ids = fields.One2many(
        string="Laboratory Request",
        comodel_name="clinic.booking.config.blood.chem.request",
        inverse_name="booking_id",
    )
    
    lab_xray_ids = fields.One2many(
        string="XRay Request",
        comodel_name="clinic.booking.config.xray.exam.request",
        inverse_name="booking_id",
    )
    
    med_cert_report = fields.Text(string="Diagnosis/Recommendation",
        track_visibility=False, compute="_compute_med_cert_report", store=False)
    
    # @api.multi
    # @api.depends("diagnosis", "recommendation", )
    def _compute_med_cert_report(self):
        for r in self:
            last_checkup = r.last_checkup if r.last_checkup else r.booking_date
            last_checkup = datetime.strftime(r.last_checkup,'%B %d, %Y')
            diagnosis = r.diagnosis.replace('<p>','').replace('</p>','').replace('<br>','')
            recommendation = r.recommendation.replace('<p>','').replace('</p>','').replace('<br>','')
            r.med_cert_report = """
            <p style="margin-bottom: 0in; line-height: 100%">was seen and examined on <strong>%s</strong> and was diagnosed to have %s.</p>
            <p style="margin-bottom: 0in; line-height: 100%">I therefore recommend %s.</p>
                """ % (last_checkup, diagnosis, recommendation)
        pass

    def fill_lab_request(self, booking_id):
        recs = self.env['clinic.booking'].browse(booking_id)
        for r in recs:
            #if r.lab_request_ids: # and not r.lab_req_ids:
            vals = [(5,0),]
            res = self.env['config.laboratory.request'].search([('active','=',True)])
            for rec in res:
                selected = False
                for sel in r.lab_request_ids:
                    if sel.id == rec.id:
                        selected = True
                vals.append((0,0,{'booking_id': r.id,'lab_id': rec.id, 'selected': selected})) 
            if vals:
                r.lab_req_ids = vals
            
            #if (r.grp1_blood_chem_ids or r.grp2_blood_chem_ids or r.grp3_blood_chem_ids): #and not r.lab_bloodchem_ids:
            vals = [(5,0),]
            res = self.env['config.blood.chem.request'].search([('active','=',True)])
            for rec in res:
                selected = False
                for sel in r.grp1_blood_chem_ids:
                    if sel.id == rec.id:
                        selected = True
                        break
                if not selected:
                    for sel in r.grp2_blood_chem_ids:
                        if sel.id == rec.id:
                            selected = True
                            break
                if not selected:
                    for sel in r.grp3_blood_chem_ids:
                        if sel.id == rec.id:
                            selected = True
                            break
                vals.append((0,0,{'booking_id': r.id,'lab_id': rec.id, 'selected': selected})) 
            if vals:
                r.lab_bloodchem_ids = vals
            
           # if (r.grp1_xray_exam_ids or r.grp2_xray_exam_ids): # and not r.lab_xray_ids:
            vals = [(5,0),]
            res = self.env['config.xray.exam.request'].search([('active','=',True)])
            for rec in res:
                selected = False
                for sel in r.grp1_xray_exam_ids:
                    if sel.id == rec.id:
                        selected = True
                        break
                if not selected:
                    for sel in r.grp2_xray_exam_ids:
                        if sel.id == rec.id:
                            selected = True
                            break
                if not selected:
                    for sel in r.grp3_xray_exam_ids:
                        if sel.id == rec.id:
                            selected = True
                            break
                vals.append((0,0,{'booking_id': r.id,'lab_id': rec.id, 'selected': selected})) 
            if vals:
                r.lab_xray_ids = vals
    
    def get_license(self,physician,effectivity_date):
        physician = physician if physician else self.env.user.id
        ret = self.env['config.md.license'].search([('license_no','!=',False),('user_id','=',physician),('effectivity_date','<=',effectivity_date),('active','=',True)], 
                                                    order='effectivity_date desc', 
                                                    limit=1).license_no or False
        return ret
    
    def get_ptr(self, physician, effectivity_date):
        physician = physician if physician else self.env.user.id
        ret = self.env['config.md.license'].search([('ptr_no','!=',False),('user_id','=',physician),('effectivity_date','<=',effectivity_date),('active','=',True)], 
                                                    order='effectivity_date desc',
                                                    limit=1).ptr_no or False
        return ret
    
    def get_s2(self, physician, effectivity_date):
        physician = physician if physician else self.env.user.id
        ret = self.env['config.md.license'].search([('s2_no','!=',False),('user_id','=',physician),('effectivity_date','<=',effectivity_date),('active','=',True)], 
                                                    order='effectivity_date desc',
                                                    limit=1).s2_no or False
        return ret
    
class ClinicReferral(models.Model):
    _inherit = 'clinic.referral'

    def get_license(self,physician,effectivity_date):
        physician = physician if physician else self.env.user.id
        ret = self.env['config.md.license'].search([('license_no','!=',False),('user_id','=',physician),('effectivity_date','<=',effectivity_date),('active','=',True)], 
                                                    order='effectivity_date desc', 
                                                    limit=1).license_no or False
        return ret
    def get_ptr(self,physician,effectivity_date):
        physician = physician if physician else self.env.user.id
        ret = self.env['config.md.license'].search([('ptr_no','!=',False),('user_id','=',physician),('effectivity_date','<=',effectivity_date),('active','=',True)], 
                                                    order='effectivity_date desc',
                                                    limit=1).ptr_no or False
        return ret
    def get_s2(self,physician,effectivity_date):
        physician = physician if physician else self.env.user.id
        ret = self.env['config.md.license'].search([('s2_no','!=',False),('user_id','=',physician),('effectivity_date','<=',effectivity_date),('active','=',True)], 
                                                    order='effectivity_date desc',
                                                    limit=1).s2_no or False
        return ret


