from dateutil.relativedelta import relativedelta

from odoo import api,fields, models
from datetime import datetime
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_compare, float_is_zero


class Estate_Model(models.Model):
    _name= "estate.property"
    _description="Table of existing estates"
    _order="id desc"
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "Expected price should be greater than 0"),
        ("check_selling_price", "CHECK(selling_price >= 0)", "Selling price must be from 0 or above"),
    ]
    name=fields.Char(required=True,default="House")
    description=fields.Char()
    postcode=fields.Char()
    date_availability=fields.Date(default=datetime.now()+relativedelta(months=3),copy=False)
    expected_price=fields.Float(required=True)
    selling_price=fields.Float(readonly=True,copy=False)
    bedrooms=fields.Integer(default=2)
    living_area=fields.Integer()
    facades=fields.Integer()
    garage=fields.Boolean()
    garden=fields.Boolean()
    garden_area=fields.Integer()
    active = fields.Boolean(default=True)
    garden_orientation=fields.Selection(
        selection=[('north','North'),('west','West'),('south','South'),('east','East')],
        string='orient',
        default='north')
    state = fields.Selection(
        [("new", "New"),
         ("offer_received", "Offer Received"),
         ("offer_accepted", "Offer Accepted"), 
         ("sold", "Sold"),
         ("canceled", "Canceled")
        ], 
        copy=False,required=True,default="new")
    

    type_property=fields.Many2one('estate.type',string='Type of property')
    user_id = fields.Many2one("res.users", string="Salesperson ",default=lambda self: self.env.user,readonly=True)
    partner_id=fields.Many2one('res.partner',string='Buyer',readonly=True,copy=False)
    estate_tag_ids=fields.Many2many('estate.tag',string='Tag')
    estate_offer_ids=fields.One2many('estate.offer','property_id',string="Offers")

    total_area=fields.Integer('Total Area',compute="_compute_area")
    best_offer=fields.Float('Best offer',compute="_compute_offer")

    @api.depends('garden_area','living_area')
    def _compute_area(self):
        for prop in self:
            prop.total_area=prop.garden_area+prop.living_area
    
    @api.depends('estate_offer_ids')
    def _compute_offer(self):
        for prop in self:
            if prop.estate_offer_ids :
                prop.best_offer=max(prop.estate_offer_ids.mapped("price"))
            else :
                prop.best_offer=0
    
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden==True:
            self.garden_area=10
            self.garden_orientation="north"
        if self.garden==False: 
            self.garden_orientation=None
            self.garden_area=0
    
    def Sold_action(self):
        if "canceled" in self.mapped("state"):
            raise UserError("Property is canceled,cannot be sold")
        else:
            self.write({"state": "sold"})

    def Cancel_action(self):
        if "sold" in self.mapped("state"):
            raise UserError("Sold properties cannot be canceled.")
        else:
            self.write({"state": "canceled"})
    
    @api.constrains('expected_price','selling_price')
    def _check_price(self):
        for prop in self:
            if (not float_is_zero(prop.selling_price,precision_rounding=0.01) and float_compare(prop.selling_price,prop.expected_price*90/100,precision_rounding=0.01)<0) :
                raise UserError('Selling price must be higher than 90% of the expected price.')

    def unlink(self):
        if set(self.mapped("state")) <= {"sold", "offer_received","offer_accepted"}:
            raise UserError("Only New and Canceled properties can be deleted.")
        return super().unlink()