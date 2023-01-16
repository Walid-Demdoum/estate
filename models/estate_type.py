from odoo import api,fields,models

class Estate_Type(models.Model):
    _name="estate.type"
    _description="Table of existing estate types"
    _sql_constraints = [
        ("check_name_is_unique", "UNIQUE(name)", "The Type must be unique"),
    ]
    _order="name desc"

    name=fields.Char('Type',required=True)
    sequence=fields.Integer('Sequence',default=1)
    property_ids = fields.One2many("estate.property", "type_property", string="Properties")
    
    offer_ids=fields.One2many("estate.offer","property_type_id")
    offer_count=fields.Integer(compute="_compute_offer")

    @api.depends("offer_ids.property_type_id")
    def _compute_offer(self):
        for record in self:
            record.offer_count = len(record.offer_ids) if record.offer_ids else 0.0

    def action_offers(self):
        res = self.env.ref("estate_offers_action").read()[0]
        res["domain"] = [("id", "in", self.offer_ids.ids)]
        return res