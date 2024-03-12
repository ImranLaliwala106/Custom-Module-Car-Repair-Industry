from odoo import models,fields,_,api
from odoo.exceptions import UserError
import xlwt,base64
from io import BytesIO

class CarRepairExcel(models.TransientModel):
    _name = 'car.repair.custom.excel'
    _description = 'Car Repair Custom Excel'
    _rec_name = 'datas_fname'
    
    file_name = fields.Binary(string='Report')
    datas_fname = fields.Char(string='Filename')
    start_date = fields.Date()
    end_date = fields.Date()
    
class CarRepairWizard(models.TransientModel):
    _name = "car.repair.industry.wizard"
    _description = "Car Repair Wizard"
    
    record_ids = fields.Many2many('car.repair.industry', string='Filtered Records', compute='_compute_filtered_record_ids')
    
    start_date = fields.Date()
    end_date = fields.Date()
    
    # TO PRINT PDF REPORT OF RECORDS BETWEEN TWO DATES
    @api.depends('start_date', 'end_date')
    def _compute_filtered_record_ids(self):
        for record in self:
            domain = [('date_reciept', '>=', record.start_date), ('to_date', '<=', record.end_date)]
            record.record_ids = self.env['car.repair.industry'].search(domain)

    def print_records(self):
        if self.start_date and self.end_date < self.start_date:
            raise UserError("End date cannot be before start date.")
        
        return self.env.ref('car_repair_industry.action_filter_report_car_repair').report_action(self)

    # TO PRINT EXCEL REPORT OF RECORDS BETWEEN TWO DATES
    def print_excel(self):
        domain=[]
        if self.start_date:
            domain.append(('date_reciept','>=',self.start_date))
        if self.end_date:
            domain.append(('to_date','<=',self.end_date))
        
        repair_industries = self.env['car.repair.industry'].search(domain)
        
        filename = "Custom Excel Report"
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet1 = workbook.add_sheet('Quotation', cell_overwrite_ok=True)
        
        date_format = xlwt.XFStyle()
        date_format.num_format_str = "dd/mm/yyyy"
            
        format1 = xlwt.easyxf('align:horiz center,vert center; font:color black,bold True;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid, fore_color aqua')
        format2 = xlwt.easyxf('align:horiz center; font:color black;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid,fore_color white')
        format3 = xlwt.easyxf('align:horiz center,vert center; font:color black;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid,fore_color white')
        format4 = xlwt.easyxf('align:horiz center,vert center; font:color black,bold True;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid,fore_color white')
        format5 = xlwt.easyxf('align:horiz center,vert center; font:color black,bold True;borders:top_color black,bottom_color black,right_color black,left_color black,left thin, right thin, top thin, bottom thin;pattern:pattern solid,fore_color yellow')

        row_index = 9

        for repair_industry in repair_industries:
            car_details_ids = repair_industry.car_details_ids
            
            if car_details_ids:
                for rec in car_details_ids:
                    sheet1.write(row_index, 5, rec.car, format2)
                    sheet1.write(row_index, 6, rec.license_plate, format2)
                    sheet1.write(row_index, 7, rec.cost_total, format2)
                    row_index += 1

                sheet1.write_merge(row_index - len(car_details_ids), row_index - 1, 1, 1, repair_industry.sr_no, format3)
                sheet1.write_merge(row_index - len(car_details_ids), row_index - 1, 2, 2, repair_industry.client_name.name, format3)
                sheet1.write_merge(row_index - len(car_details_ids), row_index - 1, 3, 3, repair_industry.login_company.phone, format3)
                sheet1.write_merge(row_index - len(car_details_ids), row_index - 1, 4, 4, repair_industry.login_company.email, format3)
                sheet1.write_merge(row_index, row_index, 1, 6, 'TOTAL', format4)
                sheet1.write_merge(row_index, row_index, 7, 7, repair_industry.subtotal, format4)
                
                row_index += 2
            
        sheet1.col(1).width = 7000
        sheet1.col(2).width = 7000
        sheet1.col(3).width = 7000
        sheet1.col(4).width = 10000
        sheet1.col(5).width = 15000
        sheet1.col(6).width = 6000
        sheet1.col(7).width = 7000
        
        sheet1.write_merge(1, 2, 1, 2, 'Start Date', format1)
        sheet1.write_merge(3, 4, 1, 2, self.start_date, date_format)
        sheet1.write_merge(1, 2, 6, 7, 'End Date', format1)
        sheet1.write_merge(3, 4, 6, 7, self.end_date, date_format)
        sheet1.write_merge(6, 7, 1, 1, 'Sr No', format1)
        sheet1.write_merge(6, 7, 2, 2,'Client Name', format1)
        sheet1.write_merge(6, 7, 3, 3,'Phone', format1)
        sheet1.write_merge(6, 7, 4, 4,'Email', format1)
        sheet1.write_merge(6, 7, 5, 5,'Car Model', format1)
        sheet1.write_merge(6, 7, 6, 6,'License Plate', format1)
        sheet1.write_merge(6, 7, 7, 7,'Total Cost', format1)

        total_cost = sum(rec.cost_total for repair_industry in repair_industries for rec in repair_industry.car_details_ids)
        sheet1.write_merge(row_index + 1, row_index + 2, 1, 6, 'SUBTOTAL', format5)
        sheet1.write_merge(row_index + 1, row_index + 2, 7, 7, total_cost, format5)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        excel_id = self.env['custom.excel.class'].create({"datas_fname": filename, "file_name": out})

        return {
            "res_id": excel_id.id,
            'name': "Car Repair Details",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'custom.excel.class',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


    
    
    