from dateutil.relativedelta import relativedelta

from odoo import api,fields,models
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_compare, float_is_zero

class Estate_Offer(models.Model):
    _name="estate.offer"
    _description="Estate offers"
    _sql_constraints = [
        ("check_price", "CHECK(price>0)", "The offer price must be positive"),]
    _order="price desc"
    
    price=fields.Float(required=True)
    state=fields.Selection([
        ('accepted','Accepted'),('refused','Refused'),('pending','Pending')],copy=False,default="pending")
    
    validity = fields.Integer(string="Validity (days)",default=7)
    date_deadline=fields.Date('DEAD LINE',compute="_compute_deadline",inverse="_inverse_deadline")
    
    partner_ids=fields.Many2one('res.partner',string="Buyer",required=True)
    property_id=fields.Many2one('estate.property',ondelete="cascade",string="Property", required=True)
    #####
    property_type_id=fields.Many2one("estate.type",related="property_id.type_property", string="Property Type", store=True)
    #####


    @api.depends('validity','create_date')
    
    def _compute_deadline(self):
        for prop in self:
            date=prop.create_date.date() if prop.create_date else fields.Date.today()
            prop.date_deadline=date + relativedelta(days=prop.validity)
    def _inverse_deadline(self):
        for prop in self:
            date=prop.create_date.date() if prop.create_date else fields.Date.today()
            prop.validity=(prop.date_deadline - date).days

    def Accept_Offer(self):
        if "offer_accepted" in self.mapped("property_id.state") :
            raise UserError('An offer is previously accepted.')
        if "sold" in self.mapped("property_id.state") or "canceled" in self.mapped("property_id.state") :
            raise UserError('The property has been sold or canceled.')
        self.write({"state": "accepted"})
        self.mapped("property_id").write(
            {"state":"offer_accepted",
            "selling_price":self.price,
            "partner_id":self.partner_ids.id})

    
    def Reject_Offer(self):
        return self.write({"state": "refused"})

    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            if prop.estate_offer_ids:
                max_offer = max(prop.mapped("estate_offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"
        return super().create(vals)