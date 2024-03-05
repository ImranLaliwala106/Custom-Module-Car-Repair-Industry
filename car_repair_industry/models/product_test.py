from odoo import models,fields,api,_
from odoo.osv import expression
import re

class ProductTest(models.Model):
    _inherit='product.template'   
    
    choose_to_add = fields.Boolean(string="Add Other Product", default=True)
    add_product = fields.Char(string="Add product")
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None, order=True):
       args = list(args or [])
       if name:
           args += ['|',(self._rec_name, operator, name),('add_product', operator, name)]
           return self._search(args, limit=limit, access_rights_uid=name_get_uid)