from odoo import fields,models
class Estate_Tags(models.Model):
    _name="estate.tag"
    _description="All estate tags"
    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The Tag must be unique"),
    ]
    _order="name desc"
    name=fields.Char('Tag',required=True,editable="bottom")
    color_index=fields.Integer()
