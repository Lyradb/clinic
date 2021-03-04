# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta
import base64, platform, rsa

def calculate_age(born):
    bdate = False
    if born:
        if isinstance(born, str):
            year = int(born[:4])
            month = int(born[5:7])
            day = int(born[8:])
        else:
            year = born.year
            month = born.month
            day = born.day
        today = date.today()
        bdate = today.year - year - ((today.month, today.day) < (month, day))
    return bdate

def _get_bmi_state(bmi):
        bmi_state = None
        if bmi < 18.5:
            bmi_state = 'under'
        elif bmi >= 18.5 and bmi <= 24.9:
            bmi_state = 'normal'
        elif bmi >= 20 and bmi <= 29.9:
            bmi_state = 'over'
        elif bmi >= 40:
            bmi_state = 'obese'
            
        return bmi_state

class ConfigProductPrescription(models.Model):
    _name = 'product.prescription'
    _description = 'Product Prescription'

    name = fields.Char(string="Prescription", )
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))

class ConfigProductFunction(models.Model):
    _name = 'config.product.function'
    _description = 'Product Generic Names'

    name = fields.Char(string="Function", )
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)
    
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
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))
        
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    generic_ids = fields.Many2many(
        string="Generic Name",
        comodel_name="config.product.generic",
        domain="[('active', '=', True)]",
        track_visibility=True,
    )
    
    function_ids = fields.Many2many(
        string="Function",
        comodel_name="config.product.function",
        domain="[('active', '=', True)]",
    )
    
    generic_names = fields.Char(string="Generic Name", compute="compute_generic_ids")
    
    def compute_generic_ids(self):
        for r in self:
            meds = ""
            sep = ""
            for rec in r.generic_ids:
                meds = "%s%s%s" % (meds, sep, rec.name) 
                sep = " + "
            r.generic_names = meds
        pass
    
    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))

# class ProductProduct(models.Model):
#     _inherit = 'product.product'
    
#     generic_ids = fields.Many2many(
#         string="Generic Name",
#         comodel_name="config.product.generic",
#         domain="[('active', '=', True)]",
#         track_visibility=True,
#     )
    
#     function_ids = fields.Many2many(
#         string="Function",
#         comodel_name="config.product.function",
#         domain="[('active', '=', True)]",
#     )
    
#     @api.constrains('name')
#     def _validate_name(self):
#         id = self.id
#         name = self.name
        
#         res = self.search([['name', '=ilike', name], ['id', '!=', id]])
#         if res:
#             raise ValidationError(_("Record already exists."))
    
class ConfigLaboratoryType(models.Model):
    _name = 'config.laboratory.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name", track_visibility=True, required=True)
    long_name = fields.Char(string="Name", track_visibility=True, required=True)
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)
    
    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))
    
class ConfigLaboratory(models.Model):
    _name = 'config.laboratory'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'type_id, name'
    
    name = fields.Char(string="Name", track_visibility=True, required=True)
    long_name = fields.Char(string="Long Name", track_visibility=True, required=True)
    unit = fields.Char(string="Unit", track_visibility=True)
    ref_interval = fields.Char(string="Reference Interval", track_visibility=True)
    type_id = fields.Many2one(comodel_name="config.laboratory.type", string="Type")
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)
    
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
    
    name = fields.Char(string="Name", track_visibility=True, required=True)
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)

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
    _order = 'group, name'
    
    name = fields.Char(string="Name", track_visibility=True, required=True)
    unit = fields.Char(string="Unit", track_visibility=True)
    ref_interval = fields.Char(string="Reference Interval", track_visibility=True)
    group = fields.Integer(string="Display Group", track_visibility=True)
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)

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
    _order = 'group, name'
    
    name = fields.Char(string="Name", track_visibility=True, required=True)
    unit = fields.Char(string="Unit", )
    ref_interval = fields.Char(string="Reference Interval", track_visibility=True)
    group = fields.Integer(string="Display Group", track_visibility=True)
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)

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
        domain=[('active','=','True,')],
        track_visibility=True
    )
    
    patient_id = fields.Many2one(
        string="Patient Name",
        comodel_name="res.partner",
        related='booking_id.patient_id',
        track_visibility=True
    )
    
    lab_cbc_id = fields.Many2one(
        string="Complete Blood Count",
        comodel_name="config.lab.test.cbc", 
        required=True,
        track_visibility=True
    )
    
    result  = fields.Float(string='Result', required=True, track_visibility=True)
    unit = fields.Char(string="Unit", related='lab_cbc_id.unit', track_visibility=True)
    ref_interval = fields.Char(string="Reference Interval", 
                               related='lab_cbc_id.ref_interval')
    group = fields.Integer(string="Display Group", related='lab_cbc_id.group')
        
class ConfigLabTestUrinalysis(models.Model):
    _name = 'config.lab.test.urinalysis'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'group, name'
    
    name = fields.Char(string="Name", track_visibility=True, required=True)
    unit = fields.Char(string="Unit", track_visibility=True)
    ref_interval = fields.Char(string="Reference Interval", track_visibility=True)
    group = fields.Integer(string="Display Group", track_visibility=True)
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)

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
        domain=[('active','=','True')],
         track_visibility=True
    )
    
    patient_id = fields.Many2one(
        string="Patient Name",
        comodel_name="res.partner",
        related='booking_id.patient_id'
    )
    
    lab_urinal_id = fields.Many2one(
        string="Urinalysis",
        comodel_name="config.lab.test.urinalysis", 
        required=True, track_visibility=True
    )
    
    result  = fields.Float(string='Result', required=True, track_visibility=True)
    unit = fields.Char(string="Unit", related='lab_urinal_id.unit')
    ref_interval = fields.Char(string="Reference Interval", 
                               related='lab_urinal_id.ref_interval')
    group = fields.Integer(string="Display Group", related='lab_urinal_id.group')

class TestBloodChemistryResult(models.Model):
    _name = 'test.blood.chem.result'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'group, blood_chem_req_id'
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
        domain=[('active','=','True')], 
        track_visibility=True
    )
    
    patient_id = fields.Many2one(
        string="Patient Name",
        comodel_name="res.partner",
        related='booking_id.patient_id', 
        track_visibility=True
    )
    
    blood_chem_req_id = fields.Many2one(
        string="Blood Chemistry",
        comodel_name="config.blood.chem.request", 
        required=True, track_visibility=True
    )
    
    result  = fields.Float(string='Result', required=True, track_visibility=True)
    unit = fields.Char(string="Unit", related='blood_chem_req_id.unit')
    ref_interval = fields.Char(string="Reference Interval", 
                               related='blood_chem_req_id.ref_interval')
    group = fields.Integer(string="Display Group", related='blood_chem_req_id.group')
    
class ConfigXrayExamRequest(models.Model):
    _name = 'config.xray.exam.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'group, name'
    
    name = fields.Char(string="Name", track_visibility=True, required=True)
    group = fields.Integer(string="Display Group", track_visibility=True)
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)

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
    
    name = fields.Char(string="Name", track_visibility=True, required=True)

    @api.constrains('name')
    def _validate_name(self):
        id = self.id
        name = self.name
        
        res = self.search([['name', '=ilike', name], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))
        
class ConfigReligion(models.Model):
    _name = 'config.religion'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name", track_visibility=True, required=True)

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
        string="Physician",
        comodel_name="res.users",
        required=True,
        domain="[('active','=',True),('is_physician','=',True)]",
        default=lambda self: self.env.user.id, track_visibility=True)
    
    name = fields.Char(string="Name", compute='_compute_name')
    effectivity_date = fields.Datetime(string="Effectivity Date", required=True, default=lambda self: fields.datetime.now(), track_visibility=True)
    pf_currency_id = fields.Many2one('res.currency', string='Currency', default= lambda self: self.env.user.company_id.currency_id.id, track_visibility=True)
    pf = fields.Monetary(string='Professional Fee', currency_field='pf_currency_id', required=True, track_visibility=True)
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)

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
    _description = 'MD License and Others'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'effectivity_date desc'
    _rec_name = 'name'
    
    user_id = fields.Many2one(
        string="Physician",
        comodel_name="res.users",
        default=lambda self: self.env.user.id,
        track_visibility=True,
        required=True,
        domain="[('active','=',True),('is_physician','=',True)]",)
    
    name = fields.Char(string="Name", compute='_compute_name')
    effectivity_date = fields.Date(string="Effectivity Date", required=True, default=lambda self: fields.datetime.now().date(), track_visibility=True)
    license_no = fields.Char(string="License No.", track_visibility=True, required=False, 
                             default=lambda self: self.search([('user_id','=',self.env.user.id)], 
                                                              order='effectivity_date desc', limit=1).license_no)
    ptr_no = fields.Char(string="PTR No.", track_visibility=True, required=False)
    s2_no = fields.Char(string="S2 No.", track_visibility=True, required=False)
    active = fields.Boolean(string="Active", default=True, track_visibility=True, required=False)

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = ''
            if rec.license_no:
                name = rec.license_no
            elif rec.ptr_no:
                name = rec.ptr_no
            elif rec.s2_no:
                name = rec.s2_no
                
            result.append((rec.id, "%s (%s)" % (rec.effectivity_date.strftime("%b. %d, %Y"),name)))
        return result
    
    @api.multi
    # @api.depends("effectivity_date")
    def _compute_name(self):
        for rec in self:
            name = ''
            if rec.license_no:
                name = rec.license_no
            elif rec.ptr_no:
                name = rec.ptr_no
            elif rec.s2_no:
                name = rec.s2_no
                
            rec.name = '%s (%s)' % (rec.effectivity_date.strftime("%b. %d, %Y"), name)
        pass

    @api.constrains('effectivity_date','ptr_no','s2_no')
    def _validate_name(self):
        id = self.id
        user_id = self.user_id.id
        ptr_no = self.ptr_no or False
        s2_no = self.s2_no or False
        license_no = self.license_no or False
        
        if license_no:
            res = self.search([['license_no', '=', license_no], ['id', '!=', id], ['user_id','=',user_id]])
            if res:
                raise ValidationError(_("License # already exists."))
            
        if s2_no:
            res = self.search([['s2_no', '=', s2_no], ['id', '!=', id], ['user_id','=',user_id]])
            if res:
                raise ValidationError(_("S2 already exists."))
        
        if ptr_no:
            res = self.search([['ptr_no', '=', ptr_no], ['id', '!=', id], ['user_id','=',user_id]])
            if res:
                raise ValidationError(_("PTR already exists."))
        
class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    birthdate = fields.Date(string="Birthdate")
    
    gender = fields.Selection( string="Gender",
                              selection=[
                                ('male', 'Male'),
                                ('female', 'Female'),
                                ], track_visibility=True
                            )
    
    civil_status = fields.Selection(
        string="Civil Status",
        selection=[
                (1, 'Single'),
                (2, 'Married'),
                (3, 'Separated'),
                (4, 'Not stated'),
                (5, 'Single parent'),
                (6, 'Widow/ widower'),
                (7, 'Child'),
                (8, ''),
        ], track_visibility=True
    )
    
    occupation_id = fields.Many2one(
        string="Occupation",
        comodel_name="config.occupation",
    )
    
    religion_id = fields.Many2one(
        string="Religion",
        comodel_name="config.religion",
    )
    
    appointment_ids = fields.One2many(
        string="Appointments",
        comodel_name="clinic.booking",
        inverse_name="patient_id",
    )
    
    finding_ids = fields.One2many(
        string="Findings",
        comodel_name="clinic.findings",
        inverse_name="patient_id",
    )
    
    admission_ids = fields.One2many(
        string="Admission",
        comodel_name="clinic.admission",
        inverse_name="patient_id",
    )

    weight = fields.Char(string='Weight (Kg)', track_visibility=True)
    height = fields.Char(string='Height (Ft)', track_visibility=True)
    image_path = fields.Char(string="Image_path")
    is_hospital = fields.Boolean(string="Hospital", default=False) 
    is_physician = fields.Boolean(string="Physician", default=False) 
    
    bmi = fields.Float(string="BMI", required=False, compute='_compute_bmi')
    bmi_state = fields.Selection(string="State", selection=[('under', 'Underweight'),
                                                            ('normal', 'Normal'),
                                                            ('over', 'Overweight'),
                                                            ('obese', 'Obese'), ], compute='_compute_bmi')
    
    # company_type = fields.Selection(selection_add=[
    #             ('hospital', 'Hospital'),
    #     ],)  
    
    
    @api.one
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        self.bmi = None
        self.bmi_state = None
        self.bmi_age = None
        if self.weight and self.height:
            self.bmi = bmi = (self.weight / (self.height/3.2808) / (self.height/3.2808)) * 10000
            bmi = round(bmi, 2)
            self.bmi_state = _get_bmi_state(bmi)
        pass
    
    def _get_bmi_state(bmi):
        bmi_state = None
        if bmi < 18.5:
            bmi_state = 'under'
        elif bmi >= 18.5 and bmi <= 24.9:
            bmi_state = 'normal'
        elif bmi >= 20 and bmi <= 29.9:
            bmi_state = 'over'
        elif bmi >= 40:
            bmi_state = 'obese'
            
        return bmi_state

        
        
    @api.model
    def create(self, vals):
        # user = self.env['res.uers'].browse(vals['user_id'])
        # if not user.has_group('clinic_mgt.group_md_appointment_admin'):
        #     raise ValidationError(_("%s is not a physician." % (user.name)))
        if vals.get('image_path'):
            image_path = vals['image_path']
            if len(image_path)<7:
                image_path = get_module_resource('clinic_mgt', 'static/pictures', '%s.jpg' % image_path)
            vals['image'] = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
        return super(ResPartner, self).create(vals)
    
    @api.multi
    def write(self, vals):
        # if vals.get('user_id'):
        #     user = self.env['res.uers'].browse(vals['user_id'])
        #     if not user.has_group('clinic_mgt.group_md_appointment_admin'):
        #         raise ValidationError(_("%s is not a physician." % (user.name)))
        if vals.get('image_path'):
            image_path = vals['image_path']
            if len(image_path)<7:
                image_path = get_module_resource('clinic_mgt', 'static/pictures', '%s.jpg' % image_path)
            vals['image'] = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
        return super(ResPartner, self).write(vals)
    
    # history = fields.Text(string="History", compute='_get_history')
        
    # @api.multi
    # # @api.depends("field1", "field2", )
    # def _get_history(self):
    #     history = ""
    #     for rec in self.finding_ids:
    #         if history:
    #             history = """<p><br></p>  <p style="text-align: center; "><b><font style="color: rgb(255, 0, 0);">FINDINGS:</font></b></p><p style="text-align: left;"><b><br></b></p>
    #             %s
    #             <p><br></p>  <p style="text-align: center; "><b><font style="color: rgb(255, 0, 0);">RECOMMENDATIONS:</font></b></p><p style="text-align: left;"><b><br></b></p>
    #             %s
    #             <p style="text-align: center; "><b>========================================================================================================================================================</b></p>
    #             %s""" % (rec.findings, rec.recommendation,  history)
    #         else:
    #             history = """<p><br></p>  <p style="text-align: center; "><b><font style="color: rgb(255, 0, 0);">FINDINGS:</font></b></p><p style="text-align: left;"><b><br></b></p>
    #             %s
    #             <p><br></p>  <p style="text-align: center; "><b><font style="color: rgb(255, 0, 0);">RECOMMENDATIONS:</font></b></p><p style="text-align: left;"><b><br></b></p>
    #             %s""" % (rec.findings, rec.recommendation)
                
    #     pass
    
class ClinicSaleOrder(models.Model):
    _name = 'sale.order' # optional
    _inherit = 'sale.order'

    clinic_booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
    )

    admission_id = fields.Many2one(
        string="Admission",
        comodel_name="clinic.admission",
    )
    
class ClinicAccountInvoice(models.Model):
    _name = 'account.invoice' # optional
    _inherit = 'account.invoice'

    clinic_booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
    )

    admission_id = fields.Many2one(
        string="Admission",
        comodel_name="clinic.admission",
    )
    
class ResUsersClinic(models.Model):
    _name = 'res.users' # optional
    _inherit = 'res.users'
    
    is_physician = fields.Boolean(string="Physician", invisible=True, store=True)
    default_physician = fields.Boolean(string="Default Physician", invisible=True, default=False)
    
    @api.model
    def create(self, vals):
        usercount = self.search_count([('active','=',True)])
        userlimit = self.env['ir.config_parameter'].sudo().get_param('user.limit_count') or "0"
        if usercount >= int(userlimit):
            raise ValidationError(_("You have reached the %s user limit count, please deactivate other users first." % userlimit))
        
        if vals.get('login') and not vals.get('email'):
            vals['email'] = vals['login']
        
        return super(ResUsersClinic, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if vals.get('login') and not vals.get('email'):
            vals['email'] = vals['login']
            
        return super(ResUsersClinic, self).write(vals)
    
    # @api.model
    # def create(self, vals):
    #     vals['is_physician'] = self.has_group('clinic_mgt.group_md_appointment_admin') or False
    #     found = False
    #     for rec in self:
    #         if rec.is_physician:
    #             found = Trues
    #             break
    #     if not found:
    #         vals['default_physician'] = True
    #     ret = super(ResUsersClinic, self).create(vals)
    
    # @api.multi
    # def write(self, vals): 
    #     vals['is_physician'] = self.has_group('clinic_mgt.group_md_appointment_admin') or False
    #     if not vals['is_physician'] and self.default_physician:
    #         vals['default_physician'] = False
    #     return super(ResUsersClinic, self).write(vals)
    
    @api.multi
    def action_default_physician(self):
        id = self.id
        default_physician = self.default_physician
        
        for rec in self:
            if id != rec.id and rec.is_physician and default_physician:
                rec.default_physician = False
        self.default_physician = True
        self.env['ir.config_parameter'].sudo().set_param('clinic_mgt.physician_id',id)
        
        
   # @api.onchange('group_id')
    def _onchange_physician(self, id):
        res = self.browse(id)
        res.is_physician = res.has_group('clinic_mgt.group_md_appointment_admin') or False
        if res.is_physician:
            found = self.search([('active','=',True),('is_physician','=',True)])
            if not found:
                res.default_physician = True
        return True
    
    
class clinicMedicalCertificate(models.Model):
    _name = 'clinic.medical.certificate'
    _description = 'Clinic Medical Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'

    date_issued = fields.Date(string="Date Issued", track_visibility=True, required=False)
    last_checkup = fields.Date(string="Last Checkup", track_visibility=True, required=False, readonly=True)
    
    diagnosis = fields.Text(string="Diagnosis",
        track_visibility=True)
    
    recommendation = fields.Text(string="Recommendation",
        track_visibility=True )
    
    @api.constrains('diagnosis','recommendation')
    def _validate_name(self):
        date_issued = self.date_issued
        recommendation = self.recommendation.replace('<p><br></p>','')
        diagnosis = self.diagnosis.replace('<p><br></p>','')
        
        if not date_issued and (recommendation or diagnosis):
            raise ValidationError(_("Medical Certificate: Date Issued is required."))
        
        
class ClinicFindings(models.Model):
    _name = 'clinic.findings'
    _description = 'Clinic Findings'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'booking_date desc'

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'clinic_mgt', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
    
    patient_id = fields.Many2one(
        string="Patient Name",
        comodel_name="res.partner",
        domain="[('is_company', '=', False),('active', '=', True)]",
        context={"company_type": "person"},
        required=True, track_visibility=True
    )
    
    remarks_ids = fields.Many2many(
        string="Remarks",
        comodel_name="clinic.booking.remarks",
        domain="[('active', '=', True)]", readonly=True,
        track_visibility=True
    )
    lab_request_date = fields.Date(string="Request Date", readonly=False, required=False, track_visibility=True)
    
    booking_date = fields.Date(string="Consultation Date", readonly=False, required=True,
                                       default=lambda self: fields.datetime.now().date(), track_visibility=True)
    
    is_followup = fields.Boolean(string="Follow-Up?", default=False)
    
    follow_up_date = fields.Date(string="Follow-Up Date", readonly=False, required=False, track_visibility=True)
    
    patient_name = fields.Char(string="Patient Name", related='patient_id.name', track_visibility=True, store=True)
    
    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the Patient, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo" , attachment=True,
                                 help="Medium-sized photo of the Patient. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
                                help="Small-sized photo of the Patient. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")
        
    street = fields.Char(string="Street", placeholder="Street 1",
                          track_visibility=True)
    street2 = fields.Char(string="Street 2", placeholder="Street 2",
                           track_visibility=True)
    city = fields.Char(string="City", placeholder="Municipality/City",
                        track_visibility=True)
    state_id = fields.Many2one(
        'res.country_id.state', 'State',  track_visibility=True)
    zip = fields.Char(string='Postal', placeholder = 'Postal',
                       track_visibility=True)
    phone = fields.Char(string='Phone', placeholder="Phone",
                         track_visibility=True)
    mobile = fields.Char(string='Mobile', placeholder="Mobile",
                          track_visibility=True)
    email = fields.Char(string='Email', placeholder="Email",
                         track_visibility=True)
    website = fields.Char(string='website', related='patient_id.website',
                           track_visibility=True)
    country_id = fields.Many2one('res.country_id', string='Country', 
                                 placeholder='Country', track_visibility=True)
    
    findings = fields.Text(string="Significant Findings", track_visibility=True)
    
    for_admission = fields.Boolean(string="For Admission?", default=False)
    
    admission_req = fields.Text(string="Admission Request", track_visibility=True)
    
    physician_id = fields.Many2one(
        string="Physician",
        comodel_name="res.users",
        track_visibility=True,
        required=False,
        readony=True,
        domain="[('active','=',True),('is_physician','=',True)]",
        default=lambda self: self.env['res.users'].search([('default_physician','=',True),('is_physician','=',True)],
                                                order='id desc', limit=1).id or False)
    
    license_no = fields.Char(string="License No.", compute="_get_license_no")
    ptr_no = fields.Char(string="PTR No.", compute="_get_license_no")
    s2_no = fields.Char(string="S2 No.", compute="_get_license_no")
    
    physician_name = fields.Char(string="Physician Name", related='physician_id.name')
    
    prescribe_med_ids = fields.One2many(
        string="Prescription",
        comodel_name="clinic.prescription",
        inverse_name="findings_id",
        track_visibility=True
    )
    
    appointment_ids = fields.One2many(
        string="Appointments",
        related="patient_id.appointment_ids",
        domain="[('booking_date','<',booking_date)]",
    )
    
    finding_ids = fields.One2many(
        string="Findings",
        related="patient_id.finding_ids",
        domain="[('booking_date','<',booking_date)]",
    )
    
    admission_ids = fields.One2many(
        string="Admission",
        related="patient_id.admission_ids",
        domain="[('booking_date','<',booking_date)]",
    )
    
    pf_currency_id = fields.Many2one('res.currency', string='Currency', default= lambda self: self.env.user.company_id.currency_id.id)
    pf = fields.Monetary(string='Professional Fee', store=True,
                        currency_field='pf_currency_id', required=False)
    
    current_meds = fields.Char(string="Medicines", compute="compute_prescribe_med_ids")
    
    @api.onchange("booking_date", "physician_id")
    def _onchange_physician(self):
        booking_date = self.booking_date
        physician = self.physician_id.identchars()
        vals = {}
        self.license_no  = self.env['config.md.license'].search([('license_no','!=',False),('user_id','=',physician),('effectivity_date','<=',booking_date),('active','=',True)], 
                                                    order='effectivity_date desc', 
                                                    limit=1).license_no or False
        vals['license_no'] = self.license_no
        self.ptr_no  = self.env['config.md.license'].search([('ptr_no','!=',False),('user_id','=',physician),('effectivity_date','<=',booking_date),('active','=',True)], 
                                                    order='effectivity_date desc', 
                                                    limit=1).ptr_no or False
        vals['ptr_no'] = self.license_no
        self.s2_no  = self.env['config.md.license'].search([('s2_no','!=',False),('user_id','=',physician),('effectivity_date','<=',booking_date),('active','=',True)], 
                                                    order='effectivity_date desc', 
                                                    limit=1).s2_no or False
        vals['s2_no'] = self.license_no
        return vals
    
    # @api.multi
    # @api.depends('booking_date','physician_id')
    def _get_license_no(self):
        booking_date = self.booking_date
        physician = self.physician_id.id
        self.license_no  = self.env['config.md.license'].search([('license_no','!=',False),('user_id','=',physician),('effectivity_date','<=',booking_date),('active','=',True)], 
                                                    order='effectivity_date desc', 
                                                    limit=1).license_no or False
        self.ptr_no  = self.env['config.md.license'].search([('ptr_no','!=',False),('user_id','=',physician),('effectivity_date','<=',booking_date),('active','=',True)], 
                                                    order='effectivity_date desc', 
                                                    limit=1).ptr_no or False
        self.s2_no  = self.env['config.md.license'].search([('s2_no','!=',False),('user_id','=',physician),('effectivity_date','<=',booking_date),('active','=',True)], 
                                                    order='effectivity_date desc', 
                                                    limit=1).s2_no or False
        pass
        
    
    def compute_prescribe_med_ids(self):
        for r in self:
            meds = ""
            sep = ""
            for rec in r.prescribe_med_ids:
                meds = "%s%s%s" % (meds, sep, rec.product_id.name) 
                sep = ", "
            r.current_meds = meds
        pass
    
class ClinicReferral(models.Model):
    _name = 'clinic.referral'
    _description = 'Clinic Referral'
    _order='referral_date desc, transaction_date desc, name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'clinic_mgt', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
    
    name = fields.Char(string="Booking Number", readonly=True)
    
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id.id)
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
        domain="[('state','in',['opd','done','bo','free'])]",
        readonly=True
    )
    
    transaction_date = fields.Datetime(string="Transaction Date", readonly=True,
                                       default=lambda self: fields.datetime.now())
    
    patient_read_only = fields.Boolean(string="Patient Readonly", default=False)
    
    patient_id = fields.Many2one('res.partner', string='Patient', required=True, store=True, readonly=False)
    
    patient_name = fields.Char(string="Patient Name", related='patient_id.name', track_visibility=True, store=True)
    
    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the Patient, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo" , attachment=True,
                                 help="Medium-sized photo of the Patient. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
                                help="Small-sized photo of the Patient. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")
    
    referral_date = fields.Date(string="Referral Date", required=True, default=lambda self: fields.datetime.now().date(), track_visibility=True)
    referral_partner_id = fields.Many2one('res.partner', string='Address To', required=True, track_visibility=True,
                                            context={'default_company_type':'person','default_is_physician':True},
                                            domain="[('is_company','=',False),('is_physician','=',True),('active','=',True)]")
    
    street = fields.Char(string="Street", placeholder="Street 1")
    street2 = fields.Char(string="Street 2", placeholder="Street 2")
    city = fields.Char(string="City", placeholder="Municipality/City")
    zip = fields.Char(string='Postal', placeholder = 'Postal')
    country_id = fields.Many2one('res.country_id', string='Country', 
                                 placeholder='Country')
    state_id = fields.Many2one('res.country_id.state', 'State')
    
    consultant_partner_id = fields.Many2one(
        string="Physician", comodel_name="res.users",
        track_visibility=True, required=False, readony=False,
        domain="[('is_physician','=',True)]", default=lambda self: self.env.user.id)
    referral_evaluation = fields.Text(string="For Evaluation", track_visibility=True)
    referral_other_probs = fields.Text(string="Other Problems", track_visibility=True)
    referral_remarks = fields.Text(string="Remarks", track_visibility=True)
    
    prescribe_med_ids = fields.One2many(
        string="Prescription",
        comodel_name="clinic.prescription",
        inverse_name="findings_id",
        related='booking_id.prescribe_med_ids'
    )
    
    current_meds = fields.Char(string="Medicines", compute="compute_prescribe_med_ids")
    
    @api.onchange("referral_partner_id")
    def _onchange_referral_partner_id(self):
        vals={}
        if self.referral_partner_id:
            res = self.env['res.partner'].browse(self.referral_partner_id.id)
            if res:
                self.street = res.street
                self.street2 = res.street2
                self.city = res.city
                self.zip = res.zip
                self.country_id = res.country_id.id
                self.state_id = res.state_id.id
                
                vals['street'] = res.street
                vals['street2'] = res.street2
                vals['city'] = res.city
                vals['zip'] = res.zip
                vals['country_id'] = res.country_id.id
                vals['state_id'] = res.state_id.id
    
        return vals
    
    def compute_prescribe_med_ids(self):
        for r in self:
            meds = ""
            sep = ""
            for rec in r.prescribe_med_ids:
                meds = "%s%s%s" % (meds, sep, rec.product_id.name) 
                sep = ", "
            r.current_meds = meds
        pass
    
    @api.constrains('referral_date','patient_id')
    def _validate_referral(self):
        id = self.id
        name = self.name
        referral_date = self.referral_date
        booking_id = self.booking_id.id
        
        res = self.search([['booking_id','=',booking_id],['referral_date', '=', referral_date], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Record already exists."))
        
    @api.onchange("patient_id","referral_date")
    def _onchange_patient(self):
        patient_id = self.patient_id.id
        referral_date = self.referral_date
        vals={'patient_id':patient_id}
        if self.patient_id:
            res = self.env['res.partner'].browse(patient_id)
            if res:
                self.image = res.image
                vals['image'] = res.image
            res = self.env['clinic.booking'].search([('state','not in',['draft','confirm','void','transfer']),
                                                     ('patient_id','=',patient_id),('booking_date','<=',referral_date)],order='booking_date desc',limit=1)
            if res:
                self.booking_id = res.id
                vals['booking_id'] = res.id
    
        return vals
    
    @api.model
    def create(self, vals):
        if vals.get('referral_partner_id'):
            res = self.env['res.partner'].browse(vals['referral_partner_id'])
            if res:
                vals['street'] = res.street
                vals['street2'] = res.street2
                vals['city'] = res.city
                vals['zip'] = res.zip
                vals['country_id'] = res.country_id.id
                vals['state_id'] = res.state_id.id
        if vals.get('patient_id'):
            if not vals.get('image'):
                res = self.env['res.partner'].sudo().browse(vals['patient_id'])
                vals['image'] = res.image
            if not vals.get('booking_id'):
                res = self.env['clinic.booking'].search([('state','not in',['draft','confirm','void','transfer']),('patient_id','=',vals['patient_id']),('booking_date','<=',vals['referral_date'])],order='booking_date desc',limit=1)
                if res:
                    vals['booking_id'] = res.id
        if vals.get('image'):
            tools.image_resize_images(vals)
        if vals.get('referral_evaluation'):
            vals['referral_evaluation'] = vals.get('referral_evaluation').replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
        if vals.get('referral_other_probs'):
            vals['referral_other_probs'] = vals.get('referral_other_probs').replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
        if vals.get('referral_remarks'):
            vals['referral_remarks'] = vals.get('referral_remarks').replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
        vals['name'] = self.env['ir.sequence'].next_by_code('clinic.referral') or '/'
        ret = super(ClinicReferral, self).create(vals)
        return ret

    @api.multi
    def write(self, vals):
        if vals.get('referral_partner_id'):
            res = self.env['res.partner'].browse(vals['referral_partner_id'])
            if res:
                vals['street'] = res.street
                vals['street2'] = res.street2
                vals['city'] = res.city
                vals['zip'] = res.zip
                vals['country_id'] = res.country_id.id
                vals['state_id'] = res.state_id.id
        patient_id = vals['patient_id'] if vals.get('patient_id') else self.patient_id.id
        if vals.get('patient_id'): 
            if not vals.get('image'):
                res = self.env['res.partner'].sudo().browse(patient_id)
                vals['image'] = res.image
            res = self.env['clinic.booking'].search([('state','not in',['draft','confirm','void','transfer']),('patient_id','=',vals['patient_id']),('booking_date','<=',vals['referral_date'],)],order='booking_date desc',limit=1)
            if res:
                vals['booking_id'] = res.id
        if vals.get('image'):
            tools.image_resize_images(vals)
        if vals.get('referral_evaluation'):
            vals['referral_evaluation'] = vals.get('referral_evaluation').replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
        if vals.get('referral_other_probs'):
            vals['referral_other_probs'] = vals.get('referral_other_probs').replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
        if vals.get('referral_remarks'):
            vals['referral_remarks'] = vals.get('referral_remarks').replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
        ret = super(ClinicReferral, self).write(vals)
        return ret
    
class ClinicAdmission(models.Model):
    _name = 'clinic.admission'
    _description = 'Admission'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'admitted_date desc, discharge_date asc'
    
    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'clinic_mgt', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
    
    name = fields.Char(string="Booking Number", readonly=True)
    
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id.id)
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
        domain="[('state','in',['opd','done','bo','free'])]",
        readonly=True
    )
    
    transaction_date = fields.Datetime(string="Transaction Date",
                                       default=lambda self: fields.datetime.now())
    
    admitted_date = fields.Date(string="Admission Date", required=True,
                                       default=lambda self: fields.datetime.now().date())
    
    discharge_date = fields.Date(string="Discharge Date", readonly=False)
    days_admitted = fields.Integer(string="Days Admitted", compute='_get_days_admitted')
    
    
    patient_id = fields.Many2one(
        string="Patient Name",
        comodel_name="res.partner",
        domain="[('is_company', '=', False),('active', '=', True)]",
        context={"company_type": "person"},
        required=True, track_visibility=True
    )
    
    patient_name = fields.Char(string="Patient Name", related='patient_id.name', track_visibility=True, store=True)
    
    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the Patient, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo" , attachment=True,
                                 help="Medium-sized photo of the Patient. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
                                help="Small-sized photo of the Patient. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")
    
    hospital_id = fields.Many2one(
        string="Hospital Name",
        comodel_name="res.partner",
        domain="[('is_company', '=', True),('is_hospital','=',True)]",
        context={"default_company_type": "company","default_is_company": True,"default_is_hospital": True},
        required=True, track_visibility=True
    )
    
    physician_id = fields.Many2one(
        string="Physician",
        comodel_name="res.users",
        track_visibility=True,
        required=True,
        readony=True,
        domain="[('active','=',True),('is_physician','=',True)]",
        default=lambda self: self.env['res.users'].search([('default_physician','=',True),('is_physician','=',True)],
                                                order='id desc', limit=1).id or False)
    
    pf_currency_id = fields.Many2one('res.currency', string='Currency', default= lambda self: self.env.user.company_id.currency_id.id)
    pf = fields.Monetary(string='Professional Fee', store=True,
                        currency_field='pf_currency_id', required=True,)
    phic = fields.Monetary(string='PhilHealth', store=True,
                        currency_field='pf_currency_id', required=False)
    amount_paid = fields.Monetary(string='Amount Paid', store=True,
                        currency_field='pf_currency_id', required=False)
    amount_due = fields.Monetary(string='Amount Due', store=True, readonly=True,
                        currency_field='pf_currency_id', required=False)
    balance = fields.Monetary(string='Balance', store=False, compute="_compute_amount_paid",
                        currency_field='pf_currency_id', required=False)
    active = fields.Boolean(string="Active", default="True") 
    
    state = fields.Selection(
        string="Status",
        selection=[
                ('draft', 'Draft'),
                ('confirm', 'Admitted'),
                ('partial', 'Patially Paid'),
                ('paid', 'Fully Paid'),
                ('void', 'Cancelled'),
        ],
        help="""Draft - Admission.
        Confirm - Confirmed admission.
        Partially Paid - Partially Paid.
        Fully Paid - Fully Paid.
        Cancelled - Transaction is void.""",
        default="draft", track_visibility=True
    )
    
    invoice_id = fields.Many2one(
        string="Invoice",
        comodel_name="account.invoice",
        track_visibility=True,
        compute='_compute_order'
    )
    
    order_id = fields.Many2one(
        string="Sales Order",
        comodel_name="sale.order",
        track_visibility=True,
        compute='_compute_order'
    )
    
    @api.constrains('admitted_date','patient_id')
    def _validate_admission(self):
        id = self.id
        patient_id = self.patient_id.id
        admitted_date = self.admitted_date
        
        res = self.search([['admitted_date', '=', admitted_date], ['patient_id', '=', patient_id], ['id', '!=', id],['state','!=','void']])
        if res:
            raise ValidationError(_("Record already exists."))
        
    def account_payment(self):
        for rec in self:
            if rec.state in ('void','draft'):
                continue
            amount_paid = 0.0
            res = self.env['account.payment'].sudo().search([('invoice_ids','=',rec.invoice_id.id)])
            for r in res:
                amount_paid += r.amount
            
            if amount_paid > 0.0:
                if amount_paid < rec.balance:
                    rec.state = 'partial'
                elif rec.balance <= 0.00:
                    rec.state = 'paid'
                    
            rec.amount_due = rec.pf-rec.phic
            rec.balance = (rec.pf-rec.phic)-amount_paid
        pass
    
    
    
    @api.multi
    @api.depends("pf", "phic", 'amount_paid')
    def _compute_amount_paid(self):
        for rec in self:
            amount_paid = 0.0
            res = self.env['account.payment'].sudo().search([('invoice_ids','=',rec.invoice_id.id)])
            for r in res:
                amount_paid += r.amount
                
            if not res and rec.amount_paid:
                amount_paid = rec.amount_paid
            rec.amount_paid = amount_paid
            
            rec.amount_due = rec.pf-rec.phic
            rec.balance = (rec.pf-rec.phic)-amount_paid
            
            if rec.amount_paid > 0.00 and rec.state not in ('void','draft'):
                if rec.amount_paid > 0.00 and rec.amount_paid < rec.balance:
                    rec.state = 'partial'
                elif rec.balance == 0.00:
                    rec.state = 'paid'
        pass 
    
    def action_create_payment(self):
        context =  {
                    'default_invoice_id': self.invoice_id.id,
                    'default_currency_id':self.pf_currency_id.id,
                    'default_company_currency_id':self.pf_currency_id.id,
                    }
        view_id = self.env.ref('account.view_account_payment_invoice_form').id
        
        target = 'new'

        ret = {'type': 'ir.actions.act_window',
                'name': _('Register Payment'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'account.payment',
                'target': target,
                'context': context,}
        return ret
        
    def action_confirm(self):
        if self.state == 'draft':
            if self.balance <= 0.0:
                self.state = 'paid'
            elif (self.amount_due-self.amount_paid) > 0.0:
                self.state = 'partial'
            else:
                self.state = 'confirm'
        
        # return {'type': 'ir.actions.act_window_refresh'}
    
    @api.multi
    def _compute_order(self):
        for rec in self:
            found = self.env['sale.order'].search([('admission_id','=',rec.id)])
            if found:
                rec.order_id = found.id
                origin = found.name
                if origin:
                    found = self.env['account.invoice'].search([('origin','=',origin)])
                    if found:
                        rec.invoice_id = found.id
        pass
    
    @api.multi
    @api.depends("admitted_date", "discharge_date")
    def _get_days_admitted(self):
        for rec in self:
            days = 0
            ad_date = self.admitted_date
            dis_date = self.discharge_date
            if self.discharge_date:
                days = relativedelta(dis_date, ad_date).days
            rec.days_admitted = days
            pass
    
    @api.multi
    @api.depends("pf", "phic", "amount_paid")
    def _compute_due(self):
        for rec in self:
            rec.amount_due = rec.pf-rec.phic
            rec.balance = (rec.pf-rec.phic)-rec.amount_paid
            
            if rec.amount_paid > 0.00 and rec.state not in ('void','draft'):
                if rec.amount_due != rec.balance:
                    rec.state = 'partial'
                elif rec.balance == 0.00:
                    rec.state = 'paid'
        pass
        
    @api.onchange("pf", "phic", "amount_paid")
    def _onchange_due(self):
        for rec in self:
            rec.amount_due = rec.pf-rec.phic
            rec.balance = (rec.pf-rec.phic)-rec.amount_paid
        pass

    @api.onchange("patient_id")
    def _onchange_patient(self):
        vals={}
        if self.patient_id:
            res = self.env['res.partner'].browse(self.patient_id.id)
            if res:
                self.image = res.image
                vals['image'] = res.image
        return vals

    @api.model
    def create(self, vals):
        pf = vals['pf'] if vals.get('pf') else 0.0
        phic = vals['phic'] if vals.get('phic') else 0.0
        vals['amount_due'] = pf-phic
        if vals.get('patient_id') and not vals.get('image'):
            res = self.env['res.partner'].sudo().browse(vals['patient_id'])
            vals['image'] = res.image
        if vals.get('image'):
            tools.image_resize_images(vals)
        vals['name'] = self.env['ir.sequence'].next_by_code('clinic.admission') or '/'
        ret = super(ClinicAdmission, self).create(vals)
        if ret and vals.get('image'):
            res = self.env['res.partner'].sudo().browse(vals['patient_id'])
            res.image = vals['image']
        return ret

    @api.multi
    def write(self, vals):
        pf = vals['pf'] if vals.get('pf') else self.pf
        phic = vals['phic'] if vals.get('phic') else self.phic
        vals['amount_due'] = pf-phic
        patient_id = vals['patient_id'] if vals.get('patient_id') else self.patient_id.id
        if vals.get('patient_id') and not vals.get('image'):
            res = self.env['res.partner'].sudo().browse(patient_id)
            vals['image'] = res.image
        if vals.get('image'):
            tools.image_resize_images(vals)
        ret = super(ClinicAdmission, self).write(vals)
        if ret and vals.get('image'):
            res = self.env['res.partner'].sudo().browse(patient_id)
            res.image = vals['image']
        return ret
    
                     
    def action_check_order(self):
        uom = False
        if not self.order_id:
            if not self.pf:
                raise ValidationError(_('Please set Professionak Fee first.'))
            else:
                pf = self.pf 
                phic = self.phic
                inv = self.env.ref('clinic_mgt.product_clinic_pf')
                ph = self.env.ref('product_clinic_phic')
                pricelist_id = self.env.ref('product.list0').id or False
                partner_id = self.patient_id.id
                uom = self.env.ref('uom.product_uom_unit').id
                self.env['product.product'].browse(inv)
                
                order_line = [(0,0,{'product_id': inv.id,
                                                    'name': inv.name,
                                                    'product_uom': uom,
                                                    'product_uom_qty': 1.00,
                                                    'qty_delivered': 1.00,
                                                    'price_unit': pf,
                                                    'price_subtotal': 1*pf})]
                if phic:
                    order_line.append((0,0,{'product_id': ph.id,
                                                    'name': ph.name,
                                                    'product_uom': uom,
                                                    'product_uom_qty': 1.00,
                                                    'qty_delivered': 1.00,
                                                    'price_unit': -phic,
                                                    'price_subtotal': 1*-phic}))
           
                context =  {
                        'default_state': 'draft',
                        'default_reference': self.name,
                        'default_partner_id': partner_id,
                        'default_partner_invoice_id': partner_id,
                        'default_partner_shipping_id': partner_id,
                        'default_confirmation_date': fields.datetime.now().date(),
                        'default_pricelist_id': pricelist_id,
                        'default_order_line': order_line,
                        'default_admission_id':self.id,
                        'default_currency_id':self.pf_currency_id.id,
                        'default_company_currency_id':self.pf_currency_id.id,
                        }
                domain = [('state','=','sale')]
                view_id = self.env.ref('sale.view_order_form').id
                
                target = 'new'
        
            ret = {'type': 'ir.actions.act_window',
                    'name': _('Sales Order(s)'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'res_model': 'sale.order',
                    'target': target,
                    'domain': domain,
                    'context': context,}
        else:
            
            ret = {
                'name': _('Sales Order(s)'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'target': 'current',
                'res_id': self.order_id.id,
                'view_mode': 'form',
                }
            
        return ret
    
    def action_check_invoice(self):
        uom = False
        if not self.order_id:
            raise ValidationError(_('Please create Sales Order first.'))
        
        if not self.invoice_id:
            if not self.pf:
                raise ValidationError(_('Please set Professional Fee first.'))
            else:
                pf = self.pf 
                phic = self.phic
                inv = self.env.ref('clinic_mgt.product_clinic_pf')
                ph = self.env.ref('product_clinic_phic')
                
                order_line = [(0,0,{'product_id': inv.id,
                                                    'name': inv.name,
                                                    'product_uom': uom,
                                                    'product_uom_qty': 1.00,
                                                    'qty_delivered': 1.00,
                                                    'price_unit': pf,
                                                    'price_subtotal': 1*pf})]
                if phic:
                    order_line.append((0,0,{'product_id': ph.id,
                                                    'name': ph.name,
                                                    'product_uom': uom,
                                                    'product_uom_qty': 1.00,
                                                    'qty_delivered': 1.00,
                                                    'price_unit': -phic,
                                                    'price_subtotal': 1*-phic}))
           
                context =  {
                        'default_reference': self.name,
                        'default_partner_id': self.patient_id.id,
                        'default_date_invoice': fields.datetime.now().date(),
                        'default_date_due': fields.datetime.now().date(),
                        'default_invoice_line_ids': order_line,
                        'default_admission_id':self.id,
                        'default_currency_id':self.pf_currency_id.id,
                        'default_company_currency_id':self.pf_currency_id.id,
                        'default_type':'out_invoice', 
                        'default_journal_type': 'order',
                        'default_origin': self.order_id.name,
                        }
                domain = [('type','=','out_invoice')]
                view_id = self.env.ref('account.invoice_form').id
        
            ret = {'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'res_model': 'account.invoice',
                    'target': 'new',
                    'domain': domain,
                    'context': context,}
            
        else:
            
            ret = {
                'name': _('Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.invoice',
                'target': 'current',
                'res_id': self.invoice_id.id,
                'view_mode': 'form',
                }
            
        return ret



class ClinicBilling(models.Model):
    _name = 'clinic.billing'
    _description = 'Clinic Billing'
    
    pf_due = fields.Monetary(string='Professional Fee', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=True)
    meds_due = fields.Monetary(string='Medicines', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=True)
    other_due = fields.Monetary(string='Others', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=False)
    discount = fields.Monetary(string='Discount', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=False)
    total_due = fields.Monetary(string='Total Due', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=True, store=True, compute='_compute_balance')
    amount_due = fields.Monetary(string='Amount Due', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=True, store=True, compute='_compute_balance')
    amount_paid = fields.Monetary(string='Amount Paid', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=True, store=True, compute='_compute_balance')
    cash = fields.Monetary(string='Cash Tendered', currency_field='bill_currency_id', required=False, track_visibility=True)
    balance = fields.Monetary(string='Balance', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=True, store=True, compute='_compute_balance')
    change = fields.Monetary(string='Change', currency_field='bill_currency_id', required=False, track_visibility=True, readonly=True, store=True, compute='_compute_balance')
    booking_id = fields.Integer(string='Booking')
    bill_currency_id = fields.Many2one('res.currency', string='Currency', default= lambda self: self.env.user.company_id.currency_id.id, track_visibility=True)
    
    def init(self):
        sql = """
            insert into clinic_billing (booking_id, amount_due, pf_due, cash) 
            select b.id, pf, pf, pf from clinic_findings a 
            inner join clinic_booking b on findings_id = a.id
            and billing_id isnull;
            update clinic_booking a set billing_id = b.id from clinic_billing b 
            where a.id = b.booking_id and billing_id isnull;
            update ir_config_parameter set value = '28800'
            where key = 'inactive_session_time_out_delay' and value = '7200';
            update clinic_medical_certificate cmc 
            set date_issued = (select booking_date from clinic_findings where id = cb.findings_id)
            from clinic_booking cb
            where cmc.id = cb.medcert_id
            and date_issued isnull;
            update clinic_booking set group_state = '4bo'
            where group_state = '3bo';
            update clinic_booking set group_state = '5done'
            where group_state = '4done';
            update clinic_booking set group_state = '6free'
            where group_state = '5free';
            update clinic_booking set group_state = '7transfer'
            where group_state = '6transfer';
            update clinic_booking set group_state = '8void'
            where group_state = '7void';
            insert into cashier_recon (transaction_date, recon_date, currency_id) select distinct booking_date, booking_date, (select id from res_currency where name = 'PHP')
            from clinic_booking b inner join clinic_findings f on b.findings_id = f.id where state in ('free','done','bo') and booking_date not in (select recon_date from cashier_recon);
            update clinic_booking b set recon_id = r.id from clinic_findings f, cashier_recon r 
            where b.findings_id = f.id and f.booking_date = r.recon_date and b.state in ('free','done','bo');
            update clinic_medical_certificate set last_checkup = date_issued where last_checkup isnull;
            update clinic_findings f set patient_name = p.name
            from clinic_booking b, res_partner p where f.patient_id = p.id and b.findings_id = f.id and f.patient_name isnull; 
            """
        res = self.env.cr.execute(sql)
        self.env.cr.commit()
    
    @api.multi
    @api.depends("pf_due", "meds_due", "cash","discount", "other_due")
    def _compute_balance(self):
        for rec in self:
            rec.total_due = rec.pf_due+rec.meds_due+rec.other_due
            rec.amount_due = rec.pf_due+rec.meds_due+rec.other_due-rec.discount
            rec.change = rec.cash-rec.amount_due if rec.cash > rec.amount_due else 0.0
            rec.balance = (rec.amount_due-rec.cash) if rec.cash < rec.amount_due else 0.0
            rec.amount_paid = rec.cash if rec.amount_due > rec.cash else rec.amount_due
        pass
        
    @api.onchange("pf_due", "meds_due", "cash", "discount", "other_due")
    def _onchange_pf_due(self):
        vals = {}
        self.total_due = self.pf_due+self.meds_due+self.other_due
        vals['total_due'] = self.total_due
        self.amount_due = self.total_due-self.discount
        vals['amount_due'] = self.amount_due
        self.change = self.cash-self.amount_due if self.cash > self.amount_due else 0.0
        vals['change'] = self.change
        self.balance = (self.amount_due-self.cash) if self.cash < self.amount_due else 0.0
        vals['balance'] = self.balance
        self.amount_paid = self.cash if self.amount_due > self.cash else self.amount_due
        vals['amount_paid'] - self.amount_paid
        return vals

class ClinicBooking(models.Model):
    _name = 'clinic.booking'
    _description = 'Clinic Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = 'booking_date desc, sequence asc'
    _inherits = {'clinic.findings':'findings_id', 'clinic.medical.certificate': 'medcert_id', 'clinic.billing':'billing_id'}
    
    med_cert_only = fields.Boolean(string="Medical Certificate Only", default=False)
    
    billing_id = fields.Many2one(comodel_name="clinic.billing", 
                                    string="Billing", required=True,
                                    ondelete="restrict", track_visibilty=True,)
    
    medcert_id = fields.Many2one(comodel_name="clinic.medical.certificate", 
                                    string="Medical Certificate", required=True,
                                       ondelete="restrict", track_visibilty=True)
    
    findings_id = fields.Many2one(comodel_name="clinic.findings", 
                                    string="Findings", required=True,
                                    ondelete="restrict", track_visibilty=True,
                                    domain="[('state','in',['bo','done','free'])]")
    
    # booking_type = fields.Selection([
    #     ('opd', 'Out-patient')
    #     ('ipd', 'In-patient')
    # ], string='Booking Type', default='opd')
    
    referral_ids = fields.One2many(
        string="For Referral",
        comodel_name="clinic.referral",
        inverse_name="booking_id",
    )
    
    sequence = fields.Integer(string="Priority #", readonly=True)
    
    priority = fields.Integer(
        string="Priority #",
        compute='_compute_priority',
        # inverse='_inverse_priority',
        # search='_search_priority',
        # help="",
    )
    
    name = fields.Char(string="Booking Number", readonly=True)
    
    transaction_date = fields.Datetime(string="Transaction Date", readonly=False,
                                       default=lambda self: fields.datetime.now())
    
    civil_status = fields.Selection(
        string="Civil Status",
        selection=[
                (1, 'Single'),
                (2, 'Married'),
                (3, 'Separated'),
                (4, 'Not stated'),
                (5, 'Single parent'),
                (6, 'Widow/ widower'),
                (7, 'Child'),
                (8, ''),
        ], track_visibility=True
    )
    
    occupation_id = fields.Many2one(
        string="Occupation",
        comodel_name="config.occupation", track_visibility=True
    )
    
    religion_id = fields.Many2one(
        string="Religion",
        comodel_name="config.religion", track_visibility=True
    )
    
    birthdate = fields.Date(string="Birthdate", track_visibility=True)
    
    gender = fields.Selection( string="Gender",
                              selection=[
                                ('male', 'Male'),
                                ('female', 'Female'),
                                ], track_visibility=True
                            )
    
    age = fields.Integer(string="Age", compute='_compute_age', store=True, readonly=False, track_visibility=True)
     
    sugar = fields.Char(string="Sugar (mmHg)", track_visibility=True)
    bp = fields.Char(string="Blood Pressure (mmHg)", track_visibility=True)
    temp = fields.Char(string="Temperature (°C)", track_visibility=True)
    heart_rate = fields.Char(string="Heart Rate (bpm)", track_visibility=True)
    weight = fields.Char(string='Weight (Kg)', track_visibility=True)
    height = fields.Char(string='Height (Ft)', track_visibility=True)
    
    chief_complaint = fields.Text(string="Chief Complaint", track_visibility=True)
    state = fields.Selection(
        string="Status",
        selection=[
                ('draft', 'New'),
                ('confirm', 'Confirm'),
                ('opd', 'Out-Patient'),
                ('cert', 'Certicate Only'),
                ('bo', 'Bill-Out'),
                ('done', 'Paid'),
                ('free', 'Free Checkup'),
                ('transfer', 'Transfered'),
                ('void', 'Cancelled'),
        ],
        help="""New - Booked for consultation.
        Confirm - Confirmed consultation.
        Out-Patient - Scheduled for or Ongoing Consultation.
        Bill-Out - Patient needs to pay.
        Free - Patient is free of charge.
        Paid - Checkup is done.
        Cancelled - Transaction is void.""",
        default="draft", track_visibility=True
    )
     
    group_state = fields.Selection(
        string="Status",
        selection=[
                ('0draft', 'New'),
                ('1confirm', 'Confirm'),
                ('2opd', 'Out-Patient'),
                ('3cert', 'Medical Certificate Only'),
                ('4bo', 'Bill-Out'),
                ('5done', 'Paid'),
                ('6free', 'Free Checkup'),
                ('7transfer', 'Transfered'),
                ('8void', 'Cancelled'),
        ],
        compute="_compute_state", store=True,
        help="""New - Booked for consultation.
        Confirm - Confirmed consultation.
        Out-Patient - Scheduled for or Ongoing Consultation.
        Bill-Out - Patient needs to pay.
        Free - Patient is free of charge.
        Paid - Checkup is done.
        Cancelled - Transaction is void."""
    )
    
    transfer_to_id = fields.Many2one(
        string="Transferred to",
        comodel_name="clinic.booking",
        readonly=True, track_visibility=True
    )
    
    lab_request_ids = fields.Many2many(
        string="Laboratory Request",
        comodel_name="config.laboratory.request", 
        track_visibility=True
    )
    
    grp1_blood_chem_ids = fields.Many2many(
        string="Blood Chemistry Request",
        comodel_name="config.blood.chem.request",
        domain=[('group','=',1)], track_visibility=True
    )
    
    grp2_blood_chem_ids = fields.Many2many(
        string="Blood Chemistry Request",
        comodel_name="config.blood.chem.request",
        domain=[('group','=',2)], track_visibility=True
    )
    
    grp3_blood_chem_ids = fields.Many2many(
        string="Blood Chemistry Request",
        comodel_name="config.blood.chem.request",
        domain=[('group','=',3)], track_visibility=True
    )
    
    blood_chem_views = fields.Char(string="Views", placeholder='Views', track_visibility=True)
    blood_chem_others = fields.Char(string="Others", placeholder='Others', track_visibility=True)
    
    result_date = fields.Date(string="Result Date", track_visibility=True)
    
    test_blood_chem_ids = fields.One2many(
        string="Blood Chemistry",
        comodel_name="test.blood.chem.result",
        inverse_name="booking_id", track_visibility=True
    )
    
    test_blood_chem_others = fields.Char(string="Blood Chemistry Others", track_visibility=True)
    
    test_urinalysis_ids = fields.One2many(
        string="Urinalysis",
        comodel_name="test.lab.urinalysis.result",
        inverse_name="booking_id",
        track_visibility=True
    )
    
    test_urinalysis_others = fields.Char(string="Urinalysis Others", track_visibility=True)
    
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
    
    grp3_xray_exam_ids = fields.Many2many(
        string="X-ray Examination Request",
        comodel_name="config.xray.exam.request",
        domain=[('group','=',3)],
        track_visibility=True
    )
    
    xray_exam_others = fields.Char(string="Others", placeholder='Others')
    
    test_cbc_others = fields.Char(string="CBC Others")
    
    test_xray_views = fields.Text(string="X-Ray Views")
    test_xray_others = fields.Text(string="X-Ray Others")
    
    active = fields.Boolean(string="Active", default="True")

    invoice_id = fields.Many2one(
        string="Invoice",
        comodel_name="account.invoice",
        track_visibility=True,
        compute='_compute_order'
    )
    
    order_id = fields.Many2one(
        string="Sales Order",
        comodel_name="sale.order",
        track_visibility=True,
        compute='_compute_order'
    )
    
    referral_id = fields.Many2one(
        string="Referral",
        comodel_name="clinic.referral",
        track_visibility=True,
        compute='_compute_referral'
    )
    
    admission_id = fields.Many2one(
        string="Admission",
        comodel_name="clinic.admission",
        track_visibility=True,
        compute='_compute_admission'
    )
    
    lab_result = fields.Binary("Laboratory Result", attachment=True, help="Lab Result", track_visibility=True)
    lab_result1 = fields.Binary("Laboratory Result", attachment=True, help="Lab Result", track_visibility=True)
    lab_result2 = fields.Binary("Laboratory Result", attachment=True, help="Lab Result", track_visibility=True)
    lab_result3 = fields.Binary("Laboratory Result", attachment=True, help="Lab Result", track_visibility=True)

    # file = fields.Many2many(comodel_name="ir.attachment", 
    #                         string="Laboratory Result", 
    #                      required=True, track_visibility=True)
    # filename = fields.Char("Laboratory Result", track_visibility=True)
    
    amount_total = fields.Monetary(string='Total', related='order_id.amount_total', default=0.0, track_visibility=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default= lambda 
                                  self: self.env.user.company_id.currency_id.id, 
                                  related='order_id.currency_id')
    
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id.id)
    
    image_path = fields.Char(string="Image Path")
    
    parent_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
    )
       
    @api.onchange("pf_due", "meds_due", "cash", "discount", "other_due")
    def _onchange_pf_due(self):
        vals = {}
        self.total_due = self.pf_due+self.meds_due+self.other_due
        vals['total_due'] = self.total_due
        self.amount_due = self.total_due-self.discount
        vals['amount_due'] = self.amount_due
        self.change = self.cash-self.amount_due if self.cash > self.amount_due else 0.0
        vals['change'] = self.change
        self.balance = (self.amount_due-self.cash) if self.cash < self.amount_due else 0.0
        vals['balance'] = self.balance
        self.amount_paid = self.cash if self.amount_due > self.cash else self.amount_due
        vals['amount_paid'] = self.amount_paid
        return vals
    
    # @api.multi
    # @api.depends("sequence", "state", )
    def _compute_priority(self):
        for rec in self:
            booking_date = rec.booking_date
            id = rec.id
            res = self.search_count([('state','in',['opd','bo','done','free']),
                                     ('booking_date','=',booking_date),
                                     ('id','<',rec.id)])
            rec.priority = res+1
            pass
    
    # @api.multi
    # def _inverse_priority(self):
    #     for rec in self:
    #         pass
    
    # @api.multi
    # def _search_priority(self, operator, value):
    #     if operator == 'like':
    #         operator = 'ilike'
    #     return [('new_field', operator, value)]
    
    def _update_amount_due(self, id, amount):
        res = self.browse(id)
        for rec in res:
            rec.meds_due = amount-rec.pf_due if amount>rec.pf_due else 0.0
        return True
        
    def account_payment(self):
        for rec in self:
            if rec.state!='bo':
                continue
            amount_paid = 0.0
            res = self.env['account.payment'].sudo().search([('invoice_ids','=',rec.invoice_id.id)])
            for r in res:
                amount_paid += r.amount
            
            if amount_paid >= rec.pf:
                rec.state = 'done'
        pass
    
    @api.onchange("image_path")
    def _onchange_field(self):
        self.image = tools.image_resize_image_big(base64.b64encode(open(self.image_path, 'rb').read()))
    
    @api.multi
    def _compute_order(self):
        for rec in self:
            found = self.env['sale.order'].search([('clinic_booking_id','=',rec.id)])
            if found:
                rec.order_id = found.id
                origin = found.name
                if origin:
                    found = self.env['account.invoice'].search([('origin','=',origin)])
                    if found:
                        rec.invoice_id = found.id
        pass
    
    @api.multi
    def _compute_referral(self):
        for rec in self:
            found = self.env['clinic.referral'].search([('booking_id','=',rec.id),],limit=1)
            if found:
                rec.referral_id = found.id
        pass
    
    @api.multi
    def _compute_admission(self):
        for rec in self:
            found = self.env['clinic.admission'].search([('booking_id','=',rec.id)],limit=1)
            if found:
                rec.admission_id = found.id
        pass
    
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
            elif state == 'cert':
                rec.group_state = '3cert'
            elif state == 'bo':
                rec.group_state = '4bo'
            elif state == 'done':
                rec.group_state = '5done'
            elif state == 'free':
                rec.group_state = '6free'
            elif state == 'transfer':
                rec.group_state = '7transfer'
            elif state == 'void':
                rec.group_state = '8void'
        pass
    
    def action_med_cert_only(self):
        self.med_cert_only = not self.med_cert_only
        
    def action_confirm(self):
        if self.state == 'draft':
            self.state = 'confirm'
        
        # return {'type': 'ir.actions.act_window_refresh'}
    
    def _assign_recon(self, booking_id):
        rec = self.browse(booking_id)
        if rec:
            if rec.state == 'bo' and not rec.recon_id:
                res = self.env['cashier.recon'].search([('company_id','=',self.env.user.company_id.id),('recon_date','=',rec.booking_date)])
                if not res:
                    # cc_ids = []
                    # found = self.env['config.denomination'].search([("active","=",True)])
                    # for rec in found:
                    #     cc_ids.append((0,0,{'denomination':rec.denomination})) 
                    res = self.env['cashier.recon'].create({'recon_date':rec.booking_date}) #, 'cc_ids': (cc_ids)})
                else:
                    if not res.cc_ids:
                        cc_ids = []
                        found = self.env['config.denomination'].search([("active","=",True)])
                        for rec in found:
                            cc_ids.append((0,0,{'cc_id':res.id,'denomination':rec.denomination})) 
                        res.cc_ids = cc_ids
                    res = res.id
                rec.recon_id = res
        return True
            
    def _check_server(self):
        val = ""
        msg = ""
        today = fields.Datetime.to_string(fields.Datetime.now())
        server = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.server') or ""
        
        for str in platform.uname():
            val = "%s%s" % (val,str)
        
        print('Clinic Detail:',val)
        if server:
            if server.upper() != 'TRIAL':
                if val != server:
                    msg = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.msg_reactivate') or ""
            else:
                demo = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.start_demo') or ""
                if not demo:
                    demo = today
                    self.env['ir.config_parameter'].set_param('clinic_mgt.start_demo', demo) 
                
                end_date = datetime.strptime(demo,'%Y-%m-%d %H:%M:%S').date+timedelta(days=60)
                
                  
                if today > end_date:
                    msg = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.msg_activate_demo') or ""
        else:
            msg = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.msg_activate') or ""
                 
        if msg:
            raise ValidationError(_(msg))
        
        return True

    
    def action_same_meds_last(self):
        patient_id = self.patient_id.id
        booking_date = self.booking_date
        id = self.id
        prescribe_med_ids = []
        res = self.search([('id','!=',id),
                     ('patient_id','=',patient_id),
                     ('booking_date','<',booking_date),
                     ('med_cert_only','=',False),
                     ('state','in',['free','bo','opd'])],
                    limit = 1, order='booking_date desc')
        for rec in res.prescribe_med_ids:
            prescribe_med_ids.append((0,0,{'product_id': rec.product_id.id,
                                           'prescription_ids': rec.prescription_ids,
                                            'quantity': rec.quantity}))
        if prescribe_med_ids:
            self.prescribe_med_ids = prescribe_med_ids
        else:
            raise ValidationError(_("No Medication found from last visit."))
        
        
        # return {'type': 'ir.actions.act_window_refresh'}
    
    def action_opd(self):
        vals = {'state':'opd'}
        if  self.state == 'confirm':
            booking_date = self.booking_date
            # if not self.date_issued:
            #     vals['date_issued'] = booking_date.date()
            
            if self.med_cert_only:
                self.last_checkup = self.search([('patient_id','=',self.patient_id.id),
                                                    ('med_cert_only','=',False),
                                                    ('booking_date','<',booking_date),
                                                    ('state','in',['done','paid','free'])],
                                                order='booking_date desc',limit=1).booking_date or False
            else:
                self.last_checkup = booking_date
            
            physician_id = False
            if self.physician_id:
                physician_id = self.physician_id.id
                vals['physician_id'] = physician_id
            
            else:
                physician = self.env['res.users'].search([('is_physician','=',True),('login_date','>=',booking_date),('active','=',True)], order='login_date desc', limit=1) or False
                if not physician:
                    physician = self.env['res.users'].search([('is_physician','=',True),('default_physician','=',True),('active','=',True)]) or False
                if physician:
                    physician_id = physician.id
            
            pf = self.pf
            if not pf:
                pf = self.env['config.md.pf'].search([('id','=',physician_id),('effectivity_date','<=',self.booking_date),('active','=',True)],order='effectivity_date desc', limit=1).pf or 0.0
                vals['pf'] = pf
            self.write(vals)
        
        # return {'type': 'ir.actions.act_window_refresh'}
                     
    def action_check_order(self):
        if not self.order_id:
            
            if not self.pf:
                res = self.env['config.md.pf'].search([('effectivity_date','<=',self.booking_date),
                                                                        ('user_id','=',self.physician_id.id)],order='effectivity_date desc',limit=1)
                
                if not res:res = self.env['config.md.pf'].search([('effectivity_date','>=',self.booking_date),
                                                                        ('user_id','=',self.physician_id.id)],order='effectivity_date asc',limit=1)
                    
                if not res:
                    raise ValidationError(_('Please set Physician Consultation Fee first of %s.') % (self.physician_id.name))
                pf = res.pf
                pf_currency_id = res.pf_currency_id
            else:
                pf = self.pf 
                pf_currency_id = self.pf_currency_id
                
            inv = self.env.ref('clinic_mgt.product_clinic_pf')
            pricelist_id = self.env.ref('product.list0').id or False
            partner_id = self.patient_id.id
            uom = self.env.ref('uom.product_uom_unit').id
            self.env['product.product'].browse(inv)
        
            context =  {
                    'default_state': 'draft',
                    'default_reference': self.name,
                    'default_partner_id': partner_id,
                    'default_partner_invoice_id': partner_id,
                    'default_partner_shipping_id': partner_id,
                    'default_confirmation_date': fields.datetime.now().date(),
                    'default_pricelist_id': pricelist_id,
                    'default_order_line': [(0,0,{'name':'Consultation', 'display_type': 'line_section'}),
                        (0,0,{'product_id': inv.id,
                                                'name': inv.name,
                                                'product_uom': uom,
                                                'product_uom_qty': 1.00,
                                                'qty_delivered': 1.00,
                                                'price_unit': pf,
                                                'price_subtotal': 1*pf}),
                        (0,0,{'name':'Medicines', 'display_type': 'line_section'})],
                    'default_clinic_booking_id':self.id,
                    'default_currency_id': pf_currency_id.id,
                    'default_company_currency_id': pf_currency_id.id,
                    }
            domain = [('state','=','sale')]
            view_id = self.env.ref('sale.view_order_form').id
            
            target = 'new'
    
            ret = {'type': 'ir.actions.act_window',
                    'name': _('Sales Order(s)'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'res_model': 'sale.order',
                    'target': target,
                    'domain': domain,
                    'context': context,}
        else:
            
            ret = {
                'name': _('Sales Order(s)'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'target': 'current',
                'res_id': self.order_id.id,
                'view_mode': 'form',
                }
            
        return ret
    
    
                     
    def action_referral(self):
        if not self.referral_id:
           
            context =  {
                    'default_booking_id':self.id,
                    'default_patient_id': self.patient_id.id,
                    'default_image':self.image,
                    'default_patient_read_only': True,
                    }
            
            view_id = self.env.ref('clinic_mgt.clinic_referral_view_form').id
                
            ret = {
                    'name': _('Referrals'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'clinic.referral',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'new',
                    'context': context}
        else:
            
            ret = {
                'name': _('Referrals'),
                'type': 'ir.actions.act_window',
                'res_model': 'clinic.referral',
                'target': 'current',
                'res_id': self.referral_id.id,
                'view_mode': 'form',
                }
            
        return ret
    
                     
    def action_admission(self):
        if not self.admission_id:
           
            context =  {
                    'default_booking_id':self.id,
                    'default_patient_id':self.patient_id.id,
                    'default_image':self.image,
                    }
            
            view_id = self.env.ref('clinic_mgt.clinic_admission_view_form').id
                
            ret = {
                    'name': _('Referrals'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'clinic.admission',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'new',
                    'context': context}
        else:
            
            ret = {
                'name': _('Admission'),
                'type': 'ir.actions.act_window',
                'res_model': 'clinic.admission',
                'target': 'current',
                'res_id': self.admission_id.id,
                'view_mode': 'form',
                }
            
        return ret
    
    @api.constrains('patient_id','med_cert_only')
    def _validate_name(self):
        id = self.id
        name = self.name
        state = self.state
        booking_date = self.booking_date
        patient_id = self.patient_id.id
        
        res = self.search([['state','not in',['void','cert','transfer']],['booking_date','=',booking_date],['patient_id', '=', patient_id], ['id', '!=', id]])
        if res:
            raise ValidationError(_("Patient is already booked on the same date."))
        
        if self.med_cert_only:
            last_checkup_rec = self.search([('id','!=',id),
                ('patient_id','=',patient_id),
                ('med_cert_only','=',False),
                ('booking_date','<',booking_date),
                ('state','in',['done','paid','free'])],
            order='booking_date desc',limit=1)
            
            if not last_checkup_rec:
                raise ValidationError(_("Patient is has no record for last checkup."))
    
    def action_check_invoice(self):
        if not self.order_id:
            raise ValidationError(_('Please create Sales Order first.'))
        
        if not self.invoice_id:
            res = self.env['config.md.pf'].search([('effectivity_date','<=',self.booking_date),
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
                        'default_currency_id':self.pf_currency_id.id,
                        'default_company_currency_id':self.pf_currency_id.id,
                        'default_type':'out_invoice', 
                        'default_journal_type': 'order',
                        'default_origin': self.order_id.name,
                        }
                domain = [('type','=','out_invoice')]
                view_id = self.env.ref('account.invoice_form').id
        
            ret = {'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'res_model': 'account.invoice',
                    'target': 'new',
                    'domain': domain,
                    'context': context,}
            
        else:
            
            ret = {
                'name': _('Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.invoice',
                'target': 'current',
                'res_id': self.invoice_id.id,
                'view_mode': 'form',
                }
            
        return ret
    
    # def validate_booking(self):
    #     now = fields.datetime.now()
    #     found = self.search([('booking_date','<',now),('state','in',('draft','confirm'))])
    #     for rec in found:
    #         rec.state = 'void'
    
    def action_nothing(self):
        raise ValidationError(_('Patient priority number is %s.' % self.sequence))
    
    def action_bill_out(self):
        vals = {'state':'bo'}
        pf = self.pf if not self.med_cert_only else 0.0
        company_id = self.env.user.company_id.id
        recon_date = self.booking_date
        if self.med_cert_only:
            vals['findings'] = 'Medical Certificate Only'
        if not self.recon_id:
            res = self.env['cashier.recon'].search([('company_id','=',company_id),
                                            ('recon_date','=',recon_date)])
            if res:
                if res.state!='draft':
                    raise ValidationError(_("Sorry, Reconcillation is not Open anymore."))
                else:
                    vals['recon_id'] = res.id
                
                    
        # if pf < 1:
        #     raise ValidationError(_("Invalid Amount, Professional fee is %s." % (self.pf)))
        vals['pf_due'] = pf 
        if not self.physician_id:
            vals['physician_id'] = self.env.user.id
        if  self.state == 'opd':
            self.write(vals)
        # return {'type': 'ir.actions.act_window_refresh'}
                
    def action_free(self):
        if  self.state == 'opd':
            if self.env.user.has_group('clinic_mgt.group_md_appointment_admin'):
                self.write({'state':'free', 'pf': 0.0,
                            'physician_id': self.env.user.id})
            else:
                self.state = 'free'
        elif self.state=='bo':
            if self.order_id:
                raise ValidationError(_("Not Allowed, Sales Order is already created."))
            else:
                self.write({'state':'free', 'pf': 0.0})
        # return {'type': 'ir.actions.act_window_refresh'}
            
    def action_done(self):
        if  self.state == 'bo':
            if self.order_id:
                if self.order_id.state != "sale":
                    raise ValidationError(_("Your Sale Order must be confirm first."))
            # if self.invoice_id:
            #     if self.invoice_id.state != "paid":
            #         raise ValidationError(_("Your Invoice must be paid first."))
            self.state = 'done'
        # return {'type': 'ir.actions.act_window_refresh'}
    
    def action_void(self):
        self.state = 'void'
        # return {'type': 'ir.actions.act_window_refresh'}
        
    def action_prev_state(self):
        if self.state == "confirm":
            self.state = "draft"
        elif self.state == "opd":
            self.state = "confirm"
        elif self.state == "bo":
            self.state = "confirm"
        elif self.state == "done":
            self.state = "bo"
        elif self.state == "free":
            self.state = "opd"
            
        # return {'type': 'ir.actions.act_window_refresh'}
           
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
    
    @api.onchange("birthdate")
    def _onchange_birthdate(self):
        vals = {}
        if self.birthdate:
            self.age = calculate_age(self.birthdate)
            vals['age'] = calculate_age(self.birthdate)
        return vals
    
    # @api.onchange("physician_id")
    # def _onchange_physician(self):
    #     vals = {}
    #     pf = self.pf
    #     if pf < 1:
    #         pf = self.env['config.md.pf'].search(
    #             [('user_id','=',self.physician_id.id),
    #             ('effectivity_date','<=',self.booking_date),
    #             ('active','=',True)],
    #             order='effectivity_date desc', limit=1).pf or 0.00
    #         if pf:
    #             self.pf = pf
    #     vals['pf'] = pf
    
    #     return vals
    
    @api.onchange("patient_id")
    def _onchange_patient(self):
        vals={}
        if self.patient_id:
            res = self.env['res.partner'].browse(self.patient_id.id)
            if res:
                self.image = res.image
                # self.image_medium = res.image_medium
                self.birthdate = res.birthdate
                self.gender = res.gender
                self.civil_status = res.civil_status
                self.occupation_id = res.occupation_id.id
                self.religion_id = res.religion_id.id
                self.age = calculate_age(self.birthdate)
                self.phone = res.phone
                self.mobile = res.mobile
                self.email = res.email
                self.website = res.website
                self.street = res.street
                self.street2 = res.street2
                self.city = res.city
                self.state_id = res.state_id.id
                self.zip = res.zip
                self.country_id = res.country_id.id
                self.height = res.height
                vals['birthdate'] = res.birthdate
                vals['gender'] = res.gender
                vals['civil_status'] = res.civil_status
                vals['occupation_id'] = res.occupation_id.id
                vals['religion_id'] = res.religion_id.id
                vals['age'] = calculate_age(self.birthdate)
                vals['phone'] = res.phone
                vals['mobile'] = res.mobile
                vals['email'] = res.email
                vals['website'] = res.website
                vals['street'] = res.street
                vals['street2'] = res.street2
                vals['city'] = res.city
                vals['state_id'] = res.state_id.id
                vals['zip'] = res.zip
                vals['country_id'] = res.country_id.id
                vals['height'] = res.height
                vals['image'] = res.image
        return vals
    
    @api.model
    def create(self, vals):
        
        if 'is_followup' in vals:
            if vals['is_followup']:
                vals['remarks_ids'] = [(4,self.env.ref('clinic_mgt.config_booking_remarks_follow_up').id)]
            if not vals['is_followup']:
                vals['remarks_ids'] = [(3,self.env.ref('clinic_mgt.config_booking_remarks_follow_up').id)]
                
        if 'med_cert_only' in vals:
            if vals['med_cert_only']:
                vals['remarks_ids'] = [(4,self.env.ref('clinic_mgt.config_booking_remarks_medcert_only').id)]
            if not vals['med_cert_only']:
                vals['remarks_ids'] = [(3,self.env.ref('clinic_mgt.config_booking_remarks_medcert_only').id)]
                
        sequence = 1
        booking_date = vals['booking_date']
        if not vals.get('state'):
            vals['state'] = 'draft'
        vals['name'] = self.env['ir.sequence'].next_by_code('clinic.booking') or '/'
        rec = self.search_count([('booking_date','=',booking_date)])
        if rec:
            sequence = rec+1
        res = False
        vals['sequence'] = sequence
        if vals.get('patient_id'):
            res = self.env['res.partner'].browse(vals['patient_id'])
            if res.image:
                vals['image'] = res.image
            # if res.image_medium and not vals.get('image_medium'):
            #     vals['image_medium'] = res.image_medium
            if res.birthdate:
                vals['birthdate'] = res.birthdate
            if res.gender :
                vals['gender'] = res.gender
            if res.height:
                vals['height'] = res.height
            if res.occupation_id:
                 vals['occupation_id'] = res.occupation_id.id
            if res.religion_id:
                vals['religion_id'] = res.religion_id.id
            if res.civil_status:
                vals['civil_status'] = res.civil_status 
            if res.phone:
                vals['phone'] = res.phone
            if res.mobile:
                vals['mobile'] = res.mobile
            if res.email:
                vals['email'] = res.email
            if res.website:
                vals['website'] = res.website
            if res.street:
                vals['street'] = res.street
            if res.street2:
                vals['street2'] = res.street2
            if res.city:
               vals['city'] =  res.city
            if res.state_id:
                vals['state_id'] = res.state_id.id
            if res.zip:
                vals['zip'] = res.zip
            if res.country_id:
                vals['country_id'] = res.country_id.id
        
        if vals.get('image_path'):
            image_path = vals['image_path']
            if len(image_path)<7:
                image_path = get_module_resource('clinic_mgt', 'static/pictures', '%s.jpg' % image_path)
            vals['image'] = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
        
        if vals.get('image'):
            tools.image_resize_images(vals)
            
        if vals.get('birthdate'):
            bdate = vals['birthdate']
            # if type(bdate)=='str':
            #     bdate = datetime.strptime(bdate,'%Y-%m-%d')
            vals['age'] = calculate_age(bdate)
            
        if vals.get('physician_id'):
            if not vals.get('pf'):
                vals['pf'] = self.env['config.md.pf'].search([('user_id','=',vals['physician_id']),('effectivity_date','<=',fields.datetime.now()),('active','=',True)],order='effectivity_date desc', limit=1).pf or 0.0
            
        if vals.get('diagnosis'):
            if vals['diagnosis'] == '<p><br></p>':
                del vals['diagnosis']
            else:
                vals['diagnosis'] = vals['diagnosis'].replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
                
        if vals.get('recommendation'):
            if vals['recommendation'] == '<p><br></p>':
                del vals['recommendation']
            else:
                vals['recommendation'] = vals['recommendation'].replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
                
        if vals.get('findings'):
            if vals['findings'] == '<p><br></p>':
                del vals['findings']
            else:
                vals['findings'] = vals['findings'].replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
                    
        ret = super(ClinicBooking, self).create(vals)
        if ret:
            if not res:
                res = self.env['res.partner'].browse(vals['patient_id'])
            
            if vals.get('image'):
                res.image = vals['image']
            # if vals.get('image_medium'):
            #     res.image_medium = vals['image_medium']
            if vals.get('birthdate'):
                res.birthdate = vals['birthdate']
            if vals.get('gender'):
                res.gender = vals['gender'] 
            if vals.get('height'):
                res.height = vals['height']
            if vals.get('occupation_id'):
                res.occupation_id = vals['occupation_id'] 
            if vals.get('religion_id'):
                res.religion_id = vals['religion_id'] 
            if vals.get('civil_status'):
                res.civil_status = vals['civil_status'] 
            if vals.get('phone'):
                res.phone = vals['phone']
            if vals.get('mobile'):
                res.mobile = vals['mobile']
            if vals.get('email'):
                res.email = vals['email']
            if vals.get('website'):
                res.website = vals['website']
            if vals.get('street'):
                res.street = vals['street'] 
            if vals.get('street2'):
                res.street2= vals['street2']
            if vals.get('city'):
                res.city = vals['city']
            if vals.get('state_id'):
                res.state_id =  vals['state_id']
            if vals.get('zip'):
                    res.zip = vals['zip'] 
            if vals.get('country_id'):
                res.country_id = vals['country_id']
                
        return ret
    
    @api.multi
    def write(self, vals):
        
        if self.recon_id and 'state' in vals:
            if self.recon_id.state != 'open':
                if self.state in ['opd','bo','done','free','void']:
                    raise ValidationError(_("Not Allowed, Daily Reconcillation is not open anymore.")) 
                if vals['state'] not in  ['void','transfer']:
                    raise ValidationError(_("Not Allowed, Daily Reconcillation is not open anymore.")) 
            
        # if self.state == 'transfer' and vals.get('state'):
        #     raise ValidationError(_("Changes to transferred booking is not allowed."))
        res = False
        if 'is_followup' in vals:
            if vals['is_followup']:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_follow_up').id)]
            if not vals['is_followup']:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_follow_up').id)]
        
        if 'for_admission' in vals:
            if vals['for_admission']:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_admission').id)]
            if not vals['for_admission']:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_admission').id)]
            
        if 'date_issued' in vals:
            if vals['date_issued'] and not self.med_cert_only:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_med_cert').id)]
            if not vals['date_issued']:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_med_cert').id)]
            
        if 'referral_id' in vals:
            if vals['referral_id']:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_referral').id)]
            if not vals['referral_id']:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_referral').id)]
            
        if 'follow_up_date' in vals:
            if vals['follow_up_date']:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_for_follow_up').id)]
            if not vals['follow_up_date']:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_for_follow_up').id)]
            
        if 'lab_request_date' in vals:
            if vals['lab_request_date']:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_lab_req').id)]
            if not vals['lab_request_date']:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_lab_req').id)]
                
        if 'pf' in vals and self.state=="bo":
            if vals['pf'] <= 0.0:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_free_checkup').id)]
            if vals['pf'] > 0:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_free_checkup').id)]
                
        if 'other_due' in vals:
            if vals['other_due'] > 0.0:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_disc').id)]
            if vals['other_due'] == 0.0:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_disc').id)]
                  
        if 'discount' in vals:
            if vals['discount'] > 0.0:
                self.remarks_ids = [(4,self.env.ref('clinic_mgt.config_booking_remarks_others').id)]
            if vals['discount'] == 0.0:
                self.remarks_ids = [(3,self.env.ref('clinic_mgt.config_booking_remarks_others').id)]
                
        if 'med_cert_only' in vals:
            if vals['med_cert_only']:
                vals['remarks_ids'] = [(4,self.env.ref('clinic_mgt.config_booking_remarks_medcert_only').id)]
            if not vals['med_cert_only']:
                vals['remarks_ids'] = [(3,self.env.ref('clinic_mgt.config_booking_remarks_medcert_only').id)]
        
        if vals.get('birthdate'):
            bdate = vals['birthdate']
            vals['age'] = calculate_age(bdate)
            
        if vals.get('physician_id') and not vals.get('pf'):
            vals['pf'] = self.env['config.md.pf'].search([('user_id','=',vals['physician_id']),('effectivity_date','<=',fields.datetime.now()),('active','=',True)],order='effectivity_date desc', limit=1).pf or 0.0
            
        if vals.get('patient_id'):
            res = self.env['res.partner'].browse(vals['patient_id'])
            if res.image:
                vals['image'] = res.image
            if res.birthdate:
                vals['birthdate'] = res.birthdate
            if res.gender:
                vals['gender'] = res.gender
            if res.height:
                vals['height'] = res.height
            if res.occupation_id:
                 vals['occupation_id'] = res.occupation_id.id
            if res.religion_id:
                vals['religion_id'] = res.religion_id.id
            if res.civil_status:
                vals['civil_status'] = res.civil_status
            if res.phone:
                vals['phone'] = res.phone
            if res.mobile:
                vals['mobile'] = res.mobile
            if res.email:
                vals['email'] = res.email
            if res.website:
                vals['website'] = res.website
            if res.street:
                vals['street'] = res.street
            if res.street2:
                vals['street2'] = res.street2
            if res.city:
               vals['city'] =  res.city
            if res.state_id:
                vals['state_id'] = res.state_id.id
            if res.zip:
                vals['zip'] = res.zip
            if res.country_id:
                vals['country_id'] = res.country_id.id
                
        if vals.get('image_path'):
            image_path = vals['image_path']
            if len(image_path)<7:
                image_path = get_module_resource('clinic_mgt', 'static/pictures', '%s.jpg' % image_path)
            vals['image'] = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
        
        if vals.get('image'):
            tools.image_resize_images(vals)
            
        if vals.get('diagnosis'):
            if vals['diagnosis'] == '<p><br></p>':
                del vals['diagnosis']
        if 'diagnosis' in vals:
            vals['diagnosis'] = vals['diagnosis'].replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
                
        if vals.get('recommendation'):
            if vals['recommendation'] == '<p><br></p>':
                del vals['recommendation']
        if 'recommendation' in vals:
            vals['recommendation'] = vals['recommendation'].replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
                
        if vals.get('findings'):
            if vals['findings'] == '<p><br></p>':
                del vals['findings']
        if 'findings' in vals:
            vals['findings'] = vals['findings'].replace('<p>','').replace('t&nbsp;&nbsp;&nbsp;&nbsp;</p>','').replace('</p>','')
                
        ret = super(ClinicBooking, self).write(vals)
        if ret:
            patient_id = vals['patient_id'] if vals.get('patient_id') else self.patient_id.id
            if not res:
                res = self.env['res.partner'].browse(patient_id)
            
            if vals.get('image'):
                res.image = vals['image']
            # if vals.get('image_medium'):
            #     res.image_medium = vals['image_medium']
            if vals.get('birthdate'):
                res.birthdate = vals['birthdate']
            if vals.get('gender'):
                res.gender = vals['gender'] 
            if vals.get('height'):
                res.height = vals['height']
            if vals.get('occupation_id'):
                res.occupation_id = vals['occupation_id'] 
            if vals.get('religion_id'):
                res.religion_id = vals['religion_id'] 
            if vals.get('civil_status'):
                res.civil_status = vals['civil_status'] 
            if vals.get('phone'):
                res.phone = vals['phone']
            if vals.get('mobile'):
                res.mobile = vals['mobile']
            if vals.get('email'):
                res.email = vals['email']
            if vals.get('website'):
                res.website = vals['website']
            if vals.get('street'):
                res.street = vals['street'] 
            if vals.get('street2'):
                res.street2= vals['street2']
            if vals.get('city'):
                res.city = vals['city']
            if vals.get('state_id'):
                res.state_id =  vals['state_id']
            if vals.get('zip'):
                    res.zip = vals['zip'] 
            if vals.get('country_id'):
                res.country_id = vals['country_id']
                
        return ret
    
    @api.multi
    def action_transfer_booking(self):
        context = {'default_booking_id': self.id}
        ret = {'type': 'ir.actions.act_window',
                'name': "Transfer Booking",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.clinic.booking.transfer',
                'target': 'new',
                'context': context, }
        return ret
     
class WizardClinicBookingTransfer(models.TransientModel):
    _name = 'wizard.clinic.booking.transfer'

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'clinic_mgt', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
    
    booking_id = fields.Many2one(
        string="Booking",
        comodel_name="clinic.booking",
        domain="[('state', '=', ['draft','confirm'])]",
        readonly=True
    )
    
    patient_id = fields.Many2one(
        string="Patient Name",
        comodel_name="res.partner",
        related='booking_id.patient_id'
    )
    
    booking_date = fields.Date(string="Consultation Date", required=True,
                               related='booking_id.booking_date', readonly=True)
    
    image = fields.Binary("Photo", attachment=True,
                          help="This field holds the image used as photo for the Customer, limited to 1024x1024px.",
                          related='patient_id.image')
    
    image_medium = fields.Binary("Photo", attachment=True,
                                 help="This field holds the image used as photo for the Customer, limited to 1024x1024px.",
                          related='patient_id.image_medium')
    
    new_booking_date = fields.Date(string="New Consultation Date", required=True)

    @api.multi
    def action_transfer(self):
        for rec in self:
            recs = self.env['clinic.booking'].browse(rec.booking_id.id)
            if recs:
                vals = {
                    'state': 'draft',
                    'parent_id': recs.id,
                    'patient_id': recs.patient_id.id,
                    'booking_date': rec.new_booking_date,
                }
                ret = recs.create(vals)
                if ret:
                    recs.write({
                        'state':'transfer',
                        'transfer_to_id':ret.id
                        })
        pass
    
class MdPrescription(models.Model):
    _name = 'clinic.prescription'
    _description = 'MD Prescription'
    
    findings_id = fields.Many2one(
        string="Findings",
        comodel_name="clinic.findings"
    )
        
    product_id = fields.Many2one(
        string="Name",
        comodel_name="product.product",
        required=True,
    )
    
    quantity = fields.Float(string="Quantity", default=1)
    
    
    currency_id = fields.Many2one('res.currency', string='Currency', default= lambda self: self.env.user.company_id.currency_id.id)
    price_unit = fields.Monetary(string='Price', currency_field='currency_id', required=True, store=True)
    
    generic_ids = fields.Many2many(
        string="Generic Name",
        comodel_name="config.product.generic",
        related="product_id.generic_ids"
    )
    
    function_ids = fields.Many2many(
        string="Function",
        comodel_name="config.product.function",
        related="product_id.function_ids"
    )
    
    prescription_ids = fields.Many2many(
        string="Instructions",
        comodel_name="product.prescription",
        domain="[('active', '=', True)]",
    )
    
    prescription = fields.Char(string="Prescription", compute="compute_prescription_ids")
    
    @api.constrains('findings_id', 'product_id')
    def _validate_name(self):
        for rec in self:
            id = rec.id
            name = rec.product_id.name
            product_id = rec.product_id.id
            findings_id = rec.findings_id.id
            
            res = self.search([['id','!=',id],['findings_id','=',findings_id],['product_id','=',product_id]])
            if res:
                raise ValidationError(_('Prescription "%s" Already Exsits.' % (name)))

    def compute_prescription_ids(self):
        for r in self:
            meds = ""
            sep = ""
            for rec in r.prescription_ids:
                meds = "%s%s%s" % (meds, sep, rec.name) 
                sep = ", "
            r.prescription = meds
        pass
    
    @api.onchange("product_id")
    def _onchange_product_id(self):
        vals = {}
        price = self.product_id.lst_price
        self.price_unit = price
        vals['price_unit'] = price
        
        return vals
    
    @api.model
    def create(self, vals):
        
        if vals.get('product_id'):
            res = self.env['product.product'].browse(vals['product_id'])
            if res:
                price = res.lst_price
                
                vals['price_unit'] = price
        
        return super(MdPrescription, self).create(vals)
    
    @api.multi
    def write(self, vals):
        
        if vals.get('product_id'):
            res = self.env['product.product'].browse(vals['product_id']) 
            if res:
                vals['price_unit'] = res.price
                                 
        return super(MdPrescription, self).write(vals)
    
class ClinicBookingRemarks(models.Model):
    _name = 'clinic.booking.remarks'
    _description = 'Clinic Booking Remarks'
    
    name = fields.Char(string="Remarks", track_visibility=True, required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string="Active", default='True', track_visibility=True, required=True)
    
class ClinicAccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'
    
    @api.model
    def create(self, vals):
        ret = super(ClinicAccountPayment, self).create(vals)
        if ret:
           res = self.env['clinic.admission'].search([('balance','>',0.00),('state','not in',['draft','void','paid'])])
           for r in res: 
               r.account_payment()
           res = self.env['clinic.booking'].search([('pf','>',0.00),('state','=','bo')])
           for r in res: 
               r.account_payment()
        return ret
    
    @api.multi
    def write(self, vals):
        ret = super(ClinicAccountPayment, self).write(vals)
        if ret:
            res = self.env['clinic.admission'].search([('balance','>',0.00),('state','not in',['draft','void','paid'])])
            for r in res: 
                r.account_payment()
            res = self.env['clinic.booking'].search([('pf','>',0.00),('state','=','bo')])
            for r in res: 
                r.account_payment()
        return ret
    
    
class ResCompanyClinic(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'
    
    @api.model
    def create(self, vals):
        uid = self.env.user.id
        admin = self.env.ref('base.user_admin').id
        
        if uid != admin:
            raise ValidationError(_("Restricted: Adding NEW Company is not allowed. Please call +639071007337"))
        
        return super(ResCompanyClinic, self).create(vals)
    
    
class ClinicSettings(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'
    
    email_account = fields.Char(string="Email Account")
    activation_server_key = fields.Char(string="Activation Server Key")
    license_server_key = fields.Char(string="License Server Key")
    physician_id = fields.Many2one(
        string="Physician",
        comodel_name="res.users",
        track_visibility=True,
        required=False,
        readony=True,
        domain="[('active','=',True),('is_physician','=',True)]",)
    
    def set_values(self):
        res = super(ClinicSettings, self).set_values()
        activation_server_key = res.activation_server_key
        physician_id = res.physician_id.id
        val = ""
        for str in platform.uname():
            val = "%s%s" % (val,str)
        if val == activation_server_key:
            self.env['ir.config_parameter'].sudo().set_param('clinic_mgt.server',activation_server_key)
        else:
            raise ValidationError(_("Activation Server Key is invalid."))
        if val == activation_server_key:
            self.env['ir.config_parameter'].sudo().set_param('clinic_mgt.server_license',activation_server_key)
        else:
            raise ValidationError(_("Server License Key is invalid."))
        
        self.env['ir.config_parameter'].sudo().set_param('clinic_mgt.physician_id',physician_id)
        
        found = self.env['res.users'].sudo().search([('id','=',physician_id)])
        physician = self.env['res.users'].sudo().search([('default_physician','=',True)])
        
        if physician:
            physician.default_physician = False
            
        if found:
            found.default_physician = True
        
        return res
        
    def get_values(self):
        res = super(ClinicSettings, self).get_values()
        activation_server_key = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.server')
        physician_id = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.physician_id')
        res.update({'activation_server_key':activation_server_key, 'physician_id': int(physician_id)})
        
        return res