from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Denomination(models.Model):
    _name = 'config.denomination'
    _rec_name = 'denomination'
    _description = 'Denomination'
    _order = 'currency_id, denomination desc'

    denomination = fields.Float(string="Denomination", required=False)
    active = fields.Boolean(string="Active", default=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    
class CashierCashcountDenom(models.Model):
    _name = 'cashier.cashcount.denom'
    _rec_name = 'name'
    _description = 'Cashier Cash Count Denomination'
    _order = 'denomination desc'
    
    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%sx%s=%s" % (rec.denomination, rec.count, rec.total)))
        return result
    
    name = fields.Char(string="Name", compute='_compute_name', readonly=True)
    cc_id = fields.Many2one(comodel_name="cashier.cashcount", string="Cash Count", required=False)
    cc2_id = fields.Many2one(comodel_name="cashier.recon", string="Cash Count", required=False)
    denomination = fields.Monetary(string="Denomination", required=True, readonly=True,
                                track_visibility='onchange', currency_field='currency_id')
    count = fields.Integer(string="Count", required=True, track_visibility='onchange', default=0)
    total = fields.Monetary(string='Total', currency_field='currency_id', required=True,
                            compute="_compute_total", track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    color = fields.Integer(string='Color Index')

    @api.multi
    def _compute_name(self):
        for rec in self:
            rec.name = "%sx%s=%s" % (rec.denomination, rec.count, rec.total)
        pass
    
    @api.one
    @api.depends('denomination', 'count')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.denomination * rec.count
        pass
    
    # def action_edit_cc(self):
    #     context = {'default_employee_id': self.id}
    #     ret = {'type': 'ir.actions.act_window',
    #             'name': "Cash Count" % self.name,
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'cashier.cashcount.denom',
    #             'target': 'new',
    #             'context': context, }
        
    #    return ret
    
class CashierCashcount(models.Model):
    _name = 'cashier.cashcount'
    _rec_name = 'transaction_date'
    _description = 'Cashier Cash Count'

    name = fields.Char(string="CC #", required=False, store=True, compute="_get_name",
                       track_visibility='onchange', readonly=True)
    recon_id = fields.Many2one(comodel_name="cashier.recon", string="Cashier Recon", required=False,
                               track_visibility='onchange')
    transaction_date = fields.Date(string="Transaction Date", required=False, readonly=True,
                                   track_visibility='onchange',
                                   default=lambda self: fields.datetime.now().date())
    cc_ids = fields.One2many(comodel_name="cashier.cashcount.denom", inverse_name="cc_id", string="Cash Counts",
                             required=False, nocreate=True)
    state = fields.Selection(string="Status", selection=[('ok', 'OK'), ('void', 'Void'), ], required=False,
                             default='ok',
                             track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    cash_total = fields.Monetary(string='Cash Count Total', currency_field='currency_id', required=False, track_visibility=True, readonly=True, compute='_compute_cc_ids', store=True)
    
    @api.multi
    @api.depends("recon_id")
    def _get_name(self):
        for rec in self:
            recon_id = rec.recon_id.id
            count = self.search_count([('recon_id','=',recon_id)])
            rec.name = "CC%s" % (count)
        pass
    
    @api.model
    def create(self, vals):
        res = super(CashierCashcount, self).create(vals)
        cc_ids = []
        if res:
            found = self.env['config.denomination'].search([("active","=",True)])
            for rec in found:
                cc_ids.append((0,0,{'cc_id':res, 'denomination':rec.denomination}))  
        res.write({'cc_ids': cc_ids})

        return res
    
    @api.one
    @api.depends('cc_ids')
    def _compute_cc_ids(self):
        total = 0.00
        for res in self.cc_ids:
            total += res.denomination * res.count
        self.cash_total = total
        pass

    # @api.onchange('cc_ids')
    # def _onchange_cc_ids(self):
    #     total = 0.00
    #     for res in self.cc_ids:
    #         total += res.denomination * res.count
    #     self.cash_total = total
    #     pass
    
class CashierRecon(models.Model):
    _name = 'cashier.recon'
    _rec_name = 'name'
    _description = 'Cashier Cashcount'
    _inherit = ['mail.thread']
    _order = 'transaction_date desc, recon_date desc'
    _mail_post_access = 'read'
    
    @api.multi
    @api.constrains('recon_date','company_id')
    def validate_type(self):
        id = self.id
        recon_date = self.recon_date
        company_id = self.company_id.id
        res = self.search([('id', '!=', id), ('company_id', '=', company_id), ('recon_date','=',recon_date)])
        if res:
            raise ValidationError(_('Reconcillation Date Already Exists.'))
        
    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "CR#%s" % self.recon_date.strftime("%Y%m%d")))
        return result
    
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company", readonly=True, default=lambda self: self.env.user.company_id.id)
    name = fields.Char(string="DCCR #", compute="_compute_get_name",
                       track_visibility='onchange', readonly=True, default='New')
    billing_ids = fields.One2many(string="Billing Number", comodel_name="clinic.booking",inverse_name="recon_id",
                                  domain=[("state","in",["bo","done","free"])], nocreate=True)
    billing_amount = fields.Monetary(string='Prof. Fee Total', currency_field='currency_id', compute="_compute_bill")
    paid_amount = fields.Monetary(string='Amount Paid Total', currency_field='currency_id', compute="_compute_bill")
    meds_total = fields.Monetary(string='Medicines Total', currency_field='currency_id', compute="_compute_bill")
    others_total = fields.Monetary(string='Others Total', currency_field='currency_id', compute="_compute_bill")
    total_due = fields.Monetary(string='Sub-Total', currency_field='currency_id', compute="_compute_bill")
    disc_total = fields.Monetary(string='Discount Total', currency_field='currency_id', compute="_compute_bill")
    cashcount_ids = fields.One2many(comodel_name="cashier.cashcount", inverse_name="recon_id", string="Cash Count", required=False)
    cc_ids = fields.One2many(string="Cash Count", comodel_name="cashier.cashcount.denom", inverse_name="cc2_id",)
    
    state = fields.Selection(string="Status",
                             selection=[('draft', 'Open'), ('confirm', 'Closed'), ('post', 'Posted')],
                             required=False, default='draft', track_visibility='onchange')
    transaction_date = fields.Datetime(string="Transaction Date", required=True, readonly=True,
                                   default=lambda self: fields.datetime.now(),
                                   track_visibility='onchange')
    recon_date = fields.Date(string="Reconcillation Date", default=lambda self: fields.datetime.now().date(), required=True, readonly=True)
    cashcount = fields.Monetary(string='Cash Count Total', currency_field='currency_id', required=False, track_visibility=True, readonly=True, 
                                compute='_compute_source', store=False)
    balance = fields.Monetary(string='Short(-)/Over(+)', currency_field='currency_id', required=False, track_visibility=True, readonly=True, 
                                compute='_compute_source', store=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    
    @api.model
    def default_get(self, fields):
        res = super(CashierRecon, self).default_get(fields)
        cc_ids = []
        found = self.env['config.denomination'].search([("active","=",True)])
        for rec in found:
            cc_ids.append((0,0,{'denomination':rec.denomination}))  
        res['cc_ids'] = cc_ids
        return res
    
    def _compute_get_name(self):
        self.name = 'CR#%s' % self.recon_date.strftime("%Y%m%d")
        pass
    
    # @api.model
    # def create(self, vals):
    #     res = super(CashierRecon, self).create(vals)
    #     cc_ids = []
    #     if res:
    #         found = self.env['config.denomination'].search([("active","=",True)])
    #         for rec in found:
    #             cc_ids.append((0,0,{'cc_id':res, 'denomination':rec.denomination}))  
    #     res.write({'cc_ids': cc_ids})

    #     return res
    
    def _compute_source(self):
        total = 0.0
        for xrec in self:
            for rec in xrec.cc_ids: 
                total += rec.total 
            xrec.cashcount = total
            xrec.balance = xrec.paid_amount-total
    
    def _compute_bill(self):
        for recs in self:
            bill = 0.0
            paid = 0.0
            meds_total = 0.0
            disc_total = 0.0
            others_total = 0.0
            for rec in recs.billing_ids:
                if rec.state in ['bo','done']:
                    bill += rec.pf_due
                    meds_total += rec.meds_due
                    others_total += rec.other_due
                    paid += rec.amount_paid
                    disc_total += rec.discount
            recs.total_due = bill+meds_total+others_total
            recs.others_total = others_total
            recs.billing_amount = bill
            recs.paid_amount = paid
            recs.meds_total = meds_total
            recs.disc_total = disc_total
        pass
    
    def action_new_cashcount(self):
        recon_id = self.id
        self.env['cashier.cashcount'].create({'recon_id':recon_id})
    
    def action_close_recon(self):
        self.state = 'confirm'
        
    def action_previous_state(self):
            self.state = 'draft'
    
class CashierClinicBilling(models.Model):
    _name = 'clinic.booking'
    _inherit = 'clinic.booking'

    recon_id = fields.Many2one(string="Reconcillation", comodel_name="cashier.recon", readonly=True)
