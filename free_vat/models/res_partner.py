# -*- coding: utf-8 -*-

from odoo import models

class ResPartner(models.Model):
    _inherit = ['res.partner']
    
    def _update_fields_values(self, fields):
        res : dict =  super(ResPartner, self)._update_fields_values(fields)
        if res.get('vat', False):
            res.pop('vat')
        return res