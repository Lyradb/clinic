# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from datetime import timedelta, date, datetime
import base64

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

class ConfigProductGeneric(models.Model):
    _name = 'product.prescription'
    _description = 'Product Prescription'

    name = fields.Char(string="Prescription", )
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))

class ConfigProductGeneric(models.Model):
    _name = 'config.product.generic'
    _description = 'Product Generic Names'

    name = fields.Char(string="Generic Name", )
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    generic_ids = fields.Many2many(
        string="Generic Name",
        comodel_name="config.product.generic",
        domain="[('active', '=', True)]",
    )
    
    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))
    
    

class ConfigLaboratoryRequest(models.Model):
    _name = 'config.laboratory.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name", track_visibility='onchange', required=True)
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))

class ConfigBloodChemistryRequest(models.Model):
    _name = 'config.blood.chem.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name", track_visibility='onchange', required=True)
    unit = fields.Char(string="Unit", )
    ref_interval = fields.Char(string="Reference Interval", )
    group = fields.Integer(string="Group")
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))
        
class ConfigLabTestCbc(models.Model):
    _name = 'config.lab.test.cbc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name", track_visibility='onchange', required=True)
    unit = fields.Char(string="Unit", )
    ref_interval = fields.Char(string="Reference Interval", )
    group = fields.Integer(string="Group")
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))

class TestLabCbcResult(models.Model):
    _name = 'test.lab.cbc.result'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
        domain=[('active','=','True')]
    )
    
    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="res.partner",
        related='booking_id.patient_id'
    )
    
    lab_cbc_id = fields.Many2one(
        string="Complete Blood Count",
        comodel_name="config.lab.test.cbc", 
        required=True
    )
    
    result  = fields.Float(string='Result', required=True)
    unit = fields.Char(string="Unit", related='lab_cbc_id.unit')
    ref_interval = fields.Char(string="Reference Interval", 
                               related='lab_cbc_id.ref_interval')
    group = fields.Integer(string="Group", related='lab_cbc_id.group')
        
class ConfigLabTestUrinalysis(models.Model):
    _name = 'config.lab.test.urinalysis'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name", track_visibility='onchange', required=True)
    unit = fields.Char(string="Unit", )
    ref_interval = fields.Char(string="Reference Interval", )
    group = fields.Integer(string="Group")
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))

class TestLabUrinalysisResult(models.Model):
    _name = 'test.lab.urinalysis.result'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
        domain=[('active','=','True')]
    )
    
    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="res.partner",
        related='booking_id.patient_id'
    )
    
    lab_urinal_id = fields.Many2one(
        string="Urinalysis",
        comodel_name="config.lab.test.urinalysis", 
        required=True
    )
    
    result  = fields.Float(string='Result', required=True)
    unit = fields.Char(string="Unit", related='lab_urinal_id.unit')
    ref_interval = fields.Char(string="Reference Interval", 
                               related='lab_urinal_id.ref_interval')
    group = fields.Integer(string="Group", related='lab_urinal_id.group')

class TestBloodChemistryResult(models.Model):
    _name = 'test.blood.chem.result'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
        domain=[('active','=','True')]
    )
    
    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="res.partner",
        related='booking_id.patient_id'
    )
    
    blood_chem_req_id = fields.Many2one(
        string="Blood Chemistry",
        comodel_name="config.blood.chem.request", 
        required=True
    )
    
    result  = fields.Float(string='Result', required=True)
    unit = fields.Char(string="Unit", related='blood_chem_req_id.unit')
    ref_interval = fields.Char(string="Reference Interval", 
                               related='blood_chem_req_id.ref_interval')
    group = fields.Integer(string="Group", related='blood_chem_req_id.group')
    
class ConfigXrayExamRequest(models.Model):
    _name = 'config.xray.exam.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name", track_visibility='onchange', required=True)
    group = fields.Integer(string="Group")
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))
        

class ConfigOccupation(models.Model):
    _name = 'config.occupation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name", track_visibility='onchange', required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))
        

class ConfigMdPf(models.Model):
    _name = 'config.md.pf'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'effectivity_date desc'
    
    user_id = fields.Many2one(
        string="User ID",
        comodel_name="res.users",
        default=lambda self: self.env.user.id
    )
    name = fields.Char(string="Name", compute='_compute_name')
    effectivity_date = fields.Datetime(string="Effectivity Date", required=True, default=lambda self: fields.datetime.now())
    pf_currency_id = fields.Many2one('res.currency', string='Currency', default= lambda self: self.env.user.company_id.currency_id.id)
    pf = fields.Monetary(string='Professional Fee', currency_field='pf_currency_id', required=True)
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.multi
    @api.depends("effectivity_date")
    def _compute_name(self):
        for rec in self:
            rec.name = '%s' % (rec.effectivity_date.strftime('%Y %b %d'))
        pass

    @api.constrains('effectivity_date','pf')
    def _validate_name(self):
        id = self.id
        user_id = self.user_id.id
        pf = self.pf
        pf_currency_id = self.pf_currency_id.id,
        effectivity_date = self.effectivity_date
        
        res = self.search([['effectivity_date','=',effectivity_date], ['pf', '=', pf], ['id', '!=', id], ['user_id','=',user_id], ['pf_currency_id','=',pf_currency_id]])
        if res:
            raise ValidationError(_("PF with same date of effectivity already exists."))
        
class ConfigMdLicense(models.Model):
    _name = 'config.md.license'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'effectivity_date desc'
    
    user_id = fields.Many2one(
        string="User ID",
        comodel_name="res.users",
        default=lambda self: self.env.user.id
    )
    name = fields.Char(string="Name", compute='_compute_name')
    effectivity_date = fields.Datetime(string="Effectivity Date", required=True, default=lambda self: fields.datetime.now())
    license_no = fields.Char(string="License No.", track_visibility='onchange', required=True, 
                             default=lambda self: self.search([('user_id','=',self.env.user.id)], order='effectivity_date desc', limit=1).license_no)
    ptr_no = fields.Char(string="PTR No.", track_visibility='onchange', required=True)
    s2_no = fields.Char(string="S2 No.", track_visibility='onchange', required=True)
    active = fields.Boolean(string="Active", default='True', track_visibility='onchange', required=True)

    @api.multi
    @api.depends("effectivity_date")
    def _compute_name(self):
        for rec in self:
            rec.name = '%s-%s' % (rec.ptr_no, rec.s2_no)
        pass

    @api.constrains('effectivity_date','ptr_no','s2_no')
    def _validate_name(self):
        id = self.id
        user_id = self.user_id.id
        ptr_no = self.ptr_no
        s2_no = self.s2_no
        
        res = self.search([['s2_no', '=ilike', s2_no], ['id', '!=', id], ['user_id','=',user_id]])
        if res:
            raise ValidationError(_("S2 already exists."))
        
        res = self.search([['ptr_no', '=ilike', ptr_no], ['id', '!=', id], ['user_id','=',user_id]])
        if res:
            raise ValidationError(_("PTR already exists."))
        
class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    birthdate = fields.Date(string="Birthdate")
    gender = fields.Selection( string="Gender",
                            selection=[
                                    ('male', 'Male'),
                                    ('Female', 'Female'),
                            ],
                        )
    civil_status = fields.Selection(
        string="Civil Status",
        selection=[
                ('single', 'Single'),
                ('married', 'Married'),
                ('widow', 'Widow'),
        ],
    )
    
class ClinicAccountInvoice(models.Model):
    _name = 'account.invoice' # optional
    _inherit = 'account.invoice'

    clinic_booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
    )
    
    
class ClinicBooking(models.Model):
    _name = 'clinic.booking'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'booking_date desc, sequence'

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'clinic_mgt', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    sequence = fields.Integer(string="Priority #", readonly=True)
    
    name = fields.Char(string="Booking Number", readonly=True)
    
    transaction_date = fields.Datetime(string="Transaction Date", readonly=True,
                                       default=lambda self: fields.datetime.now())
    booking_date = fields.Date(string="Consultation Date", readonly=False, required=True,
                                       default=lambda self: fields.datetime.now().date())
    patient_id = fields.Many2one(
        string="Patient Name",
        comodel_name="res.partner",
        domain="[('is_company', '=', False)]",
        context={"company_type": "person"},
        required=True
    )
    
    patient_name = fields.Char(string="Patient Name", related='patient_id.name')
    
    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the Customer, limited to 1024x1024px.",
                          related='patient_id.image')
    image_medium = fields.Binary("Photo", default=_default_image, attachment=True,
                                 help="This field holds the image used as photo for the Customer, limited to 1024x1024px.",
                                 related='patient_id.image_medium')
    image_small = fields.Binary("Photo", default=_default_image, attachment=True,
                                 help="This field holds the image used as photo for the Customer, limited to 1024x1024px.",
                                 related='patient_id.image_small')
    street = fields.Char(string="Street", related='patient_id.street',
                         default='', track_visibility='onchange')
    street2 = fields.Char(string="Street 2", related='patient_id.street2',
                          default='', track_visibility='onchange')
    city = fields.Char(string="City", related='patient_id.city',
                       default='', track_visibility='onchange')
    state_id = fields.Many2one(
        'res.country.state', 'State', related='patient_id.state_id', default='', track_visibility='onchange')
    zip = fields.Char(string='Postal', related='patient_id.zip',
                      default='', track_visibility='onchange')
    phone = fields.Char(string='Phone', related='patient_id.phone',
                        default='', track_visibility='onchange')
    mobile = fields.Char(string='Mobile', related='patient_id.mobile',
                         default='', track_visibility='onchange')
    email = fields.Char(string='Email', related='patient_id.email',
                        default='', track_visibility='onchange')
    website = fields.Char(string='website', related='patient_id.website',
                          default='', track_visibility='onchange')
    country_id = fields.Many2one('res.country', string='Country',
                                 related='patient_id.country_id', default='', track_visibility='onchange')
    civil_status = fields.Selection(
        string="Civil Status",
        selection=[
                ('single', 'Single'),
                ('married', 'Married'),
                ('widow', 'Widow'),
        ],
    )
    
    occupation_id = fields.Many2one(
        string="Occupation",
        comodel_name="config.occupation",
    )
    
    birthdate = fields.Date(string="Birthdate")
    
    gender = fields.Selection( string="Gender",
                              selection=[
                                ('male', 'Male'),
                                ('Female', 'Female'),
                                ]
                            )
    
    age = fields.Integer(string="Age", compute='_compute_age')
    
    bp = fields.Char(string="Blood Pressure", )
    temp = fields.Char(string="Temperature", )
    heart_rate = fields.Char(string="Hear Rate", )
    weight = fields.Float(string='Weight (Kg)')
    height = fields.Float(string='Height (Ft)')
    
    chief_complaint = fields.Text(string="Chief Complaint", )
    findings = fields.Text(string="Significant Findings/Remarks",
        track_visibility=True)
    recommendation = fields.Text(string="Recommendation",
        track_visibility=True )
    
    physician_id = fields.Many2one(
        string="Physician",
        comodel_name="res.users",
        track_visibility=True
    )
        
    state = fields.Selection(
        string="Status",
        selection=[
                ('draft', 'Draft'),
                ('confirm', 'Confirm'),
                ('opd', 'Out-Patient'),
                ('bo', 'Bill-Out'),
                ('done', 'Paid'),
                ('free', 'Free'),
                ('transfer', 'Transfered'),
                ('void', 'Cancelled'),
        ],
        help="""Draft - Booked for consultation.
        Confirm - Confirmed consultation.
        Out-Patient - Scheduled for or Ongoing Consultation.
        Bill-Out - Patient needs to pay.
        Free - Patient is free of charge.
        Done - Checkup is done.
        Cancelled - Transaction is void."""
    )
     
    group_state = fields.Selection(
        string="Status",
        selection=[
                ('0draft', 'Draft'),
                ('1confirm', 'Confirm'),
                ('2opd', 'Out-Patient'),
                ('3bo', 'Bill-Out'),
                ('4done', 'Paid'),
                ('5free', 'Free'),
                ('6transfer', 'Transfered'),
                ('7void', 'Cancelled'),
        ],
        compute="_compute_state", store=True,
        help="""Draft - Booked for consultation.
        Confirm - Confirmed consultation.
        Out-Patient - Scheduled for or Ongoing Consultation.
        Bill-Out - Patient needs to pay.
        Free - Patient is free of charge.
        Done - Checkup is done.
        Cancelled - Transaction is void."""
    )
    
    transfer_to_id = fields.Many2one(
        string="Transferred to",
        comodel_name="clinic.booking",
        readonly=True
    )
    
    lab_request_ids = fields.Many2many(
        string="Laboratory Request",
        comodel_name="config.laboratory.request",
    )
    
    grp1_blood_chem_ids = fields.Many2many(
        string="Blood Chemistry Request",
        comodel_name="config.blood.chem.request",
        domain=[('group','=',1)],
    )
    
    grp2_blood_chem_ids = fields.Many2many(
        string="Blood Chemistry Request",
        comodel_name="config.blood.chem.request",
        domain=[('group','=',2)],
    )
    
    grp3_blood_chem_ids = fields.Many2many(
        string="Blood Chemistry Request",
        comodel_name="config.blood.chem.request",
        domain=[('group','=',3)],
    )
    
    blood_chem_views = fields.Char(string="Views", placeholder='Views')
    blood_chem_others = fields.Char(string="Others", placeholder='Others')
    
    result_date = fields.Date(string="Result Date", )
    
    test_blood_chem_ids = fields.One2many(
        string="Blood Chemistry",
        comodel_name="test.blood.chem.result",
        inverse_name="booking_id",
    )
    
    test_blood_chem_others = fields.Char(string="Blood Chemistry Others", )
    
    test_urinalysis_ids = fields.One2many(
        string="Urinalysis",
        comodel_name="test.lab.urinalysis.result",
        inverse_name="booking_id",
        track_visibility=True
    )
    
    test_urinalysis_others = fields.Char(string="Urinalysis Others", )
    
    test_cbc_ids = fields.One2many(
        string="Complete Blood Count",
        comodel_name="test.lab.cbc.result",
        inverse_name="booking_id",
        track_visibility=True
    )
    
    grp1_xray_exam_ids = fields.Many2many(
        string="X-ray Examination Request",
        comodel_name="config.xray.exam.request",
        domain=[('group','=',1)],
        track_visibility=True
    )
    
    grp2_xray_exam_ids = fields.Many2many(
        string="X-ray Examination Request",
        comodel_name="config.xray.exam.request",
        domain=[('group','=',2)],
        track_visibility=True
    )
    
    xray_exam_others = fields.Char(string="Others", placeholder='Others')
    
    test_cbc_others = fields.Char(string="CBC Others", )
    
    test_xray_views = fields.Text(string="X-Ray Views", )
    test_xray_others = fields.Text(string="X-Ray Others", )
    
    prescribe_med_ids = fields.One2many(
        string="Prescription",
        comodel_name="clinic.prescription",
        inverse_name="booking_id",
        track_visibility=True
    )
    
    active = fields.Boolean(string="Active", default="True")

    invoice_id = fields.Many2one(
        string="Invoice",
        comodel_name="account.invoice",
        track_visibility=True
    )
    
    @api.multi
    @api.depends("state")
    def _compute_state(self):
        for rec in self:
            state = rec.state
            if state == 'draft':
                rec.group_state = '0draft'
            elif state == 'confirm':
                rec.group_state = '1confirm'
            elif state == 'opd':
                rec.group_state = '2opd'
            elif state == 'bo':
                rec.group_state = '3bo'
            elif state == 'free':
                rec.group_state = '4free'
            elif state == 'done':
                rec.group_state = '5done'
            elif state == 'transfer':
                rec.group_state = '6transfer'
            elif state == 'void':
                rec.group_state = '7void'
        pass
    
    def action_confirm(self):
        if self.state == 'draft':
            self.state = 'confirm'
     
    def action_opd(self):       
        if  self.state == 'confirm':
            self.state = 'opd'
            
    def action_check_invoice(self):
        if not self.invoice_id:
                
            res = self.env['config.md.pf'].search([('effectivity_date','<=',fields.datetime.now().date()),
                                                                    ('user_id','=',self.physician_id.id)],order='effectivity_date desc',limit=1)
            if not res:
                raise ValidationError(_('Please set Consultation Fee first.'))
            else:
                pf = res.pf 
                inv = self.env.ref('clinic_mgt.product_clinic_pf')
           
                context =  {
                        'default_reference': self.name,
                        'default_partner_id': self.patient_id.id,
                        'default_date_invoice': fields.datetime.now().date(),
                        'default_date_due': fields.datetime.now().date(),
                        'default_invoice_line_ids': [(0,0,{'name':'Consultation', 'display_type': 'line_section'}),
                            (0,0,{'product_id': inv.id,
                                                    'name': inv.name,
                                                    'quantity': 1.00,
                                                    'price_unit': pf,}),
                            (0,0,{'name':'Medicines', 'display_type': 'line_section'})],
                        'default_clinic_booking_id':self.id,
                        'default_type':'out_invoice', 
                        'default_journal_type': 'sale'
                        }
                domain = [('type','=','out_invoice')]
                view_id = self.env.ref('account.invoice_form').id
        
        ret = {'type': 'ir.actions.act_window',
                'name': "Create Invoice",
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'account.invoice',
                'target': 'new',
                'domain': domain,
                'context': context,}
        return ret
           

    def action_nothing(self):
        raise ValidationError(_('Patient priority number is %s.' % self.sequence))
    
    def action_bill_out(self):
        if  self.state == 'opd':
            self.write({'state':'bo',
                            'physician_id':self.env.user.id})
                
    
    def action_free(self):
        if  self.state == 'opd':
            self.state = 'free'
    
    def action_done(self):
        if  self.state == 'bo':
            if not self.invoice_id:
                raise ValidationError(_("Need to create invoice first."))
            self.state = 'done'  
    
    def action_void(self):
        self.state = 'void'
        
    def action_prev_state(self):
        if self.state == "confirm":
            self.state = "draft"
        elif self.state == "opd":
            self.state = "confirm"
        elif self.state == "bo":
            self.state = "opd"
        elif self.state == "free":
            self.state = "opd"
        elif self.state == "done":
            self.state = "opd"
           
    @api.constrains('patient_id','booking_date')
    def _validate_booking(self):
        id = self.id
        patient_id = self.patient_id.id
        booking_date = self.booking_date
        active = self.active
        
        # if booking_date < fields.datetime.now().date():
        #     raise ValidationError(_("Backtrack Booking is not allowed."))
            
        
        res = self.search([['patient_id', '=', patient_id],
                           ['booking_date','=',booking_date], 
                           ['id', '!=', id], ['active','=',True]])
        if res:
            raise ValidationError(_("Record already exists."))
    
    @api.multi
    def _compute_age(self):
        for rec in self:
            if rec.birthdate:
                rec.age = calculate_age(rec.birthdate)
        pass
    
    @api.onchange("patient_id")
    def _onchange_field(self):
        if self.patient_id:
            res = self.env['res.partner'].browse(self.patient_id.id)
            self.birthdate = res.birthdate
            self.gender = res.gender
    
    @api.model
    def create(self, vals):
        sequence = 1
        booking_date = vals['booking_date']
        vals['state'] = 'draft'
        vals['name'] = self.env['ir.sequence'].next_by_code('clinic.booking') or '/'
        rec = self.search_count([('booking_date','=',booking_date)])
        if rec:
            sequence = rec+1
        res = False
        vals['sequence'] = sequence
        if vals.get('patient_id'):
            res = self.env['res.partner'].browse(vals['patient_id'])
            vals['birthdate'] = res.birthdate
            vals['gender'] = res.gender
            
        ret = super(ClinicBooking, self).create(vals)
        if ret and (vals.get('birthdate') or vals.get('gender')):
            res = self.env['res.partner'].browse(vals['patient_id'])
            if res:
                if vals.get('birthdate'):
                    res.birthdate = vals['birthdate']
                if vals.get('gender'):
                    res.gender = vals['gender'] 
                
        return ret
    
    @api.multi
    def write(self, vals):
        res = False
        if vals.get('patient_id'):
            res = self.env['res.partner'].browse(vals['patient_id'])
            if not vals.get('birthdate'):
                vals['birthdate'] = res.birthdate
            if not vals.get('gender'):
                vals['gender'] = res.gender
            
        ret = super(ClinicBooking, self).write(vals)
        if ret and (vals.get('birthdate') or vals.get('gender')):
            patient_id = vals['patient_id'] if vals.get('patient_id') else self.patient_id.id
            res = self.env['res.partner'].browse(patient_id)
            if vals.get('birthdate'):
                res.birthdate = vals['birthdate']
            if vals.get('gender'):
                res.gender = vals['gender'] 
                
        return ret
    
    @api.multi
    def transfer_booking(self):
        for rec in self:
            ret = rec.copy(default={
                'patient_id': rec.patient_id.id,
                'booking_date': rec.booking_date,
                'civil_status': rec.civil_status,
                'appointment_id': rec.appointment_id.id,
            })
            rec.write({
                'state':'transfer',
                'transfer_to_id':ret
                })
        pass
    
class MdPrescription(models.Model):
    _name = 'clinic.prescription'
    _description = 'MD Prescription'
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
    )
    
    product_id = fields.Many2one(
        string="Name",
        comodel_name="product.product",
    )
    
    generic_ids = fields.Many2many(
        string="Generic Name",
        comodel_name="config.product.generic",
        related="product_id.generic_ids"
    )
    
    prescription_ids = fields.Many2many(
        string="Prescription",
        comodel_name="product.prescription",
        domain="[('active', '=', True)]",
    )
    
    

    
    
    
        

        
