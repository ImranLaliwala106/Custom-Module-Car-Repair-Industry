from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    check_bool = fields.Boolean(string="Check to make records uneditable", related ="company_id.check_bool", readonly=False)
    
class CheckBool(models.Model):
    _inherit = 'res.company'
    
    check_bool = fields.Boolean(store=True)