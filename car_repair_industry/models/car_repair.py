from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta
import xlwt,base64
from io import BytesIO
from odoo.addons.base.models import ir_actions


class CustomExcel(models.TransientModel):
    _name = 'custom.excel.class'
    _rec_name = 'datas_fname'
    _description = "Custom Excel"
    
    file_name = fields.Binary(string='Report')
    datas_fname = fields.Char(string='Filename')
    
class CarRepairDetails(models.Model):
    _name = "car.repair.industry"
    _description = "Car Repair Industry"
    _rec_name = 'subject'
    _order = 'priority desc'
    _inherit = ['mail.thread','mail.activity.mixin']
    _check_company_auto = True

    company_id = fields.Many2one('res.company',string="Company ID",default=lambda self: self.env.company)
    sr_no = fields.Char(readonly=True, index=True, copy=False, default=lambda self: _('New'))
    subject = fields.Char(string="Subject", size=200)
    assigned_to = fields.Selection(string="Assigned to",
                                   selection=[('A','Albert'),('B',"Brian"),('C','Carl'),('D','David')])
    make_editable = fields.Boolean(related="company_id.check_bool", string="Check to make uneditable")
    editable_bool = fields.Boolean(string="Make Uneditable")
    priority = fields.Selection(string="Priority",
                                selection=[('low','Low'),
                                           ('normal','Normal'),
                                           ('high','High'),
                                           ('very_high','Very High')])
    # TO SET TODAY DATE BY DEFAULt
    date_reciept = fields.Date(string="Date of Receipt", default=lambda x: fields.Date.context_today(x))
    to_date = fields.Date(string="End date")
    # TO ADD DRAG OPTION IN CALENDAR VIEW
    duration = fields.Float()
    image = fields.Binary(string="Images")
    status = fields.Selection(string="Status",readonly=True, tracking=True, selection=
                              [('received','RECEIVED'),
                               ('in_diagnosis','IN DIAGNOSIS'),
                               ('quotation_sent','QUOTATION SENT'),
                               ('quotation_approved','QUOTATION APPROVED'),
                               ('work_in_progress','WORK IN PROGRESS'), 
                               ('done','DONE')])
    # TO DRAG RECORDS
    sequence = fields.Integer(string="Seq")
    client_name = fields.Many2one('res.users',string="User", default=lambda self: self.env.user.id)
    login_company = fields.Many2one('res.company',string="Company", default=lambda self: self.env.user.company_id.id)
    client_address = fields.Char(string="Client")
    # TO GET INFO OF RELATED FIELDS UPON SELECTING
    street = fields.Char(string="Street", related='login_company.street')
    street2 = fields.Char(string="Street2", related='login_company.street2')
    city = fields.Char(string="City", related='login_company.city')
    state_id = fields.Char(string="State")
    zip = fields.Char(string="Zip", related='login_company.zip')
    country_id = fields.Many2one('res.country',string="Country", related='login_company.country_id')
    phone = fields.Char(string="Phone", related='login_company.phone')
    mobile = fields.Char(string="Mobile", related='login_company.mobile')
    email = fields.Char(string="Email", related='login_company.email')
    contact_number = fields.Char(string="Contact Number")
    car_details_ids = fields.Many2many('car.details.model',string="Car Model")
    subtotal = fields.Float('car_details_ids.cost_total', compute='_total_charge')
    
    # TO GENERATE SEQUENCE NUMBERS
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sr_no',_('New')) ==_('New'):
                vals['sr_no'] = self.env['ir.sequence'].next_by_code('car.repair.industry.sequence') or _('New')
        res = super(CarRepairDetails, self).create(vals)
        return res
    
    def default_get(self, fields):
        res = super(CarRepairDetails,self).default_get(fields)
        res['status'] = 'received'
        res['assigned_to'] = 'A'
        res['priority'] = 'normal'
        return res
    
    # OVERRIDE UNLINK METHOD TO DELETE RECORDS THAT ARE NOT IN DONE STATE
    def unlink(self):
        done_records = self.filtered(lambda x: x.status == 'done')
        if done_records:
            raise ValidationError("Record in done stage cannot be deleted")
        return super(CarRepairDetails, self-done_records).unlink()          
    
    # SUM OF SELECTED CARS
    @api.depends('car_details_ids.cost_total')
    def _total_charge(self):
        for record in self:
            total = sum(record.car_details_ids.mapped('cost_total'))
            record.subtotal = total
        
    # OBJECT BUTTONS
    def print_receipt(self):
        print("Receipt printed")
    
        # STATUS BUTTONS
    def do_diagnosis(self):
        for rec in self:
            rec.status = 'in_diagnosis'

    def do_quotation(self):
        for rec in self:
            rec.status = 'quotation_sent'
            
    def do_quotation_approved(self):
        for rec in self:
            rec.status = 'quotation_approved'
            
    def do_work_in_progress(self):
        for rec in self:
            rec.status = 'work_in_progress'
            
    def do_done(self):
        for rec in self:
            rec.status = 'done'
            
    # TO PRINT EXCEL REPORT OF PARTICULAR RECORD
    def print_excel(self):
        filename = self.subject
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet1 = workbook.add_sheet('Quotation',cell_overwrite_ok=True)
        date_format = xlwt.XFStyle()
        date_format.num_format_str = "dd/mm/yyyy"
        format1 = xlwt.easyxf('align:horiz center,vert center; font:color black,bold True;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid, fore_color aqua')
        format2 = xlwt.easyxf('align:horiz center; font:color black;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid,fore_color white')
        format3 = xlwt.easyxf('align:horiz center,vert center; font:color black;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid,fore_color white')
        format4 = xlwt.easyxf('align:horiz center,vert center; font:color black,bold True;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid,fore_color white')
        
        i=1
        car_model = []
        for rec in self.car_details_ids:
            car_model.append(rec.car) 
        for car_mod in car_model:
            sheet1.write(i,5,car_mod,format2)
            i+=1
            
        i=1
        cars = []
        for rec in self.car_details_ids:
            cars.append(rec.license_plate)
        for lic_plate in cars:
            sheet1.write(i,6,lic_plate,format2)
            i+=1
        
        i=1
        car_cost = []
        for rec in self.car_details_ids:
            car_cost.append(rec.cost_total) 
        for carcost in car_cost:
            sheet1.write(i,7,carcost,format2)
            i+=1
            
        sheet1.col(2).width = 7000
        sheet1.col(3).width = 7000
        sheet1.col(4).width = 10000
        sheet1.col(5).width = 15000
        sheet1.col(6).width = 6000
        sheet1.col(7).width = 7000
        sheet1.write(0,2,'Client Name',format1)
        sheet1.write(0,3,'Phone',format1)
        sheet1.write(0,4,'Email',format1)
        sheet1.write(0,5,'Car Model',format1)
        sheet1.write(0,6,'License Plate',format1)
        sheet1.write(0,7,'Total Cost',format1)
        sheet1.write_merge(1, len(cars), 2, 2, self.client_name.name,format3)
        sheet1.write_merge(1, len(cars), 3, 3, self.login_company.phone,format3)
        sheet1.write_merge(1, len(cars), 4, 4, self.login_company.email,format3)
        sheet1.write_merge(len(cars)+1, len(cars)+2, 2, 6,'TOTAL',format4)
        sheet1.write_merge(len(cars)+1, len(cars)+2, 7, 7,sum(car_cost),format4)
            
        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())
        
        excel_id = self.env['custom.excel.class'].create({"datas_fname":filename,
                                                          "file_name": out})
        
        return{
            "res_id":excel_id.id,
            'name': "Car Repair Details",
            'view_type':'form',
            'view_mode':'form',
            'res_model':'custom.excel.class',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }

    # TO SEND EMAIL OF PARTICULAR RECORD TO USER AND FOLLOWERS
    def action_send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        
        try:
            template_id = ir_model_data._xmlid_lookup('car_repair_industry.email_template_car_repair_new')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
            template_id = self.env.ref('car_repair_industry.email_template_car_repair_new')[1]
        ctx = {
            'default_model': 'car.repair.industry',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    # SCHEDULE ACTION TO SEND REMINDER MAILS TO THOSE WHOSE LAST SERVICE WAS 3 MONTHS AGO
    @api.model
    def action_done(self):  
        current_company_id = self.env.user.company_id.id
        reminder_mails = datetime.now() - timedelta(days=90)
        records = self.env['car.repair.industry'].search([('company_id', '=', current_company_id), ('status', '=', 'done'), ('to_date', '=', reminder_mails.strftime('%Y-%m-%d'))])
        if records:
            template_id = self.env.ref('car_repair_industry.car_repair_reminder_mail')
            if template_id:
                current_company_users = self.env['res.users'].search([('company_id', '=', current_company_id)])
                recipient_ids = [(4, user.partner_id.id) for user in current_company_users]
                    
                ctx = {
                    'default_model': 'car.repair.industry',
                    'default_res_id': self.id,
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id.id,
                    'default_composition_mode': 'comment',
                    'mark_so_as_sent': True,
                    'default_partner_ids': recipient_ids,
                }
                template = self.env['mail.template'].browse(template_id.id)
                template.with_context(ctx).send_mail(self.id, force_send=True)
    
    def write(self, vals):
        make_editable = vals.get('make_editable', self.make_editable)
        editable_bool = vals.get('editable_bool', self.editable_bool)

        if make_editable:
            if 'editable_bool' in vals:
                editable_bool = vals['editable_bool']

            if editable_bool:
                excluded_field = [field for field in vals if field != 'editable_bool']
                if excluded_field:
                    raise ValidationError("You cannot update record")
        return super(CarRepairDetails, self).write(vals)