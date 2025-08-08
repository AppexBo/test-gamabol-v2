# -*- coding: utf-8 -*-

from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = ['account.move']
    
    
    code_environment = fields.Selection(
        string='Habilitación Nota de Pie ',
        related='company_id.l10n_bo_code_environment',
        readonly=True,
        store=True
    )
    