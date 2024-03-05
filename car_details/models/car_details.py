from odoo import models,fields,api,_

class CarDetails(models.Model):
    _name = "car.details.model"
    _description = "Car Details"
    _rec_name = "license_plate"
    
    car = fields.Char(string="Car")
    license_plate = fields.Char(string="License Plate")
    car_model = fields.Char(string="Model")
    chassis_number = fields.Integer(string="Chassis Number")
    fuel_type = fields.Selection(string="Fuel Type",selection=[('petrol','Petrol'),('diesel','Diesel')])
    manufacturing_year = fields.Selection(string="Car Manufacturing Year",selection=[
        ('2018','2018'),
        ('2019','2019'),
        ('2020','2020'),
        ('2021','2021'),
        ('2022','2022'),
        ('2023','2023'),
    ])
    under_guaranteed = fields.Selection(string="Under Guarantee?",selection=[('yes','Yes'),('no','No')])
    nature_service = fields.Selection(string="Nature of Service",selection=[('half_service','Half Service'),('full_service','Full Service')])
    service_charge = fields.Float(string="Serice Charge")
    oil_price = fields.Float(string="Oil Price")
    washing_charge = fields.Float(string="Washing Charge")
    cost_total = fields.Float(string="Total", compute="_compute_subtotal")

    # TO CALCULATE TOTAL COST
    @api.depends('service_charge','oil_price','washing_charge')
    def _compute_subtotal(self):
        for rec in self:
            rec.cost_total = rec.service_charge + rec.oil_price + rec.washing_charge