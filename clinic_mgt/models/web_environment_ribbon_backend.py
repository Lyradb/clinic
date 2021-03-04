# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from datetime import datetime, timedelta
import platform


class WebEnvironmentRibbonBackend(models.AbstractModel):

    _name = 'web.environment.ribbon.backend'
    _description = 'Web Environment Ribbon Backend'

    @api.model
    def _prepare_ribbon_format_vals(self):
        return {
            'db_name': self.env.cr.dbname,
        }

    @api.model
    def _prepare_ribbon_name(self):
        name_tmpl = self.env['ir.config_parameter'].sudo().get_param(
            'ribbon.name')
        vals = self._prepare_ribbon_format_vals()
        return name_tmpl and name_tmpl.format(**vals) or name_tmpl

    @api.model
    def get_environment_ribbon(self):
        """
        This method returns the ribbon data from ir config parameters
        :return: dictionary
        """
        ir_config_model = self.env['ir.config_parameter']
        name = self._prepare_ribbon_name()
        return {
            'name': name,
            'color': ir_config_model.sudo().get_param('ribbon.color'),
            'background_color': ir_config_model.sudo().get_param(
                'ribbon.background.color'),
        }
        
    def trial_counter(self):
        trial = True
        server = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.server') or ""
        
        if server:
            if server.upper() != 'TRIAL':
                val = ""
                for str in platform.uname():
                    val = "%s%s" % (val,str)
                if val == server:
                    self.env['ir.config_parameter'].set_param('ribbon.name', 'False')
                    trial = False
                else:
                    self.env['ir.config_parameter'].set_param('clinic_mgt.server', 'trial')
                    

        if trial:
            demo = self.env['ir.config_parameter'].sudo().get_param('clinic_mgt.start_demo') or ""
            if not demo:
                demo = fields.Datetime.to_string(fields.Datetime.now()-timedelta(days=60))
                self.env['ir.config_parameter'].set_param('clinic_mgt.start_demo', demo) 
                
            today = fields.Datetime.now()
            demo_start = datetime.strptime(demo,'%Y-%m-%d %H:%M:%S')
            print(today-demo_start)
            days = 60-(today-demo_start).days
            if days > 0:
                msg = "%s/60 Days Trial" % (days)
            else:
                msg = "Trial has Ended"
            msg = "%s<br/>Call: +639071007337<br/>({db_name})" % (msg)
            if days <= 14:
                self.env['ir.config_parameter'].set_param('ribbon.background.color', 'rgba(255,0,0,.6)')
            else:
                self.env['ir.config_parameter'].set_param('ribbon.background.color', 'rgba(26,150,19,.6)')
        
            self.env['ir.config_parameter'].set_param('ribbon.name', msg)
            
        
        
