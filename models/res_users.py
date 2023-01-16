from odoo import fields,models


class User(models.Model):
    _inherit="res.users"
    property_u_ids = fields.One2many("estate.property", "user_id", string="Properties")