# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    enable_footnote = fields.Boolean(
        string='Habilitar Nota de Pie (Delivery)',
        copy=False,
        default=False
    )
    
