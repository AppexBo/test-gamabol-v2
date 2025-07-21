# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = ['account.journal']
    
    
    employee_expense_journal = fields.Boolean(
        string='Diario de gasto para empleados',
    )
    employee_expense_secuence = fields.Integer(
        string='Secuencia de gasto para empleados',
    )

    def generate_employee_expense_secuence(self):
        self.write({'employee_expense_secuence' : self.employee_expense_secuence+1})
        return self.employee_expense_secuence
    
    
    
    @api.constrains('type')
    def _check_type(self):
        for record in self:
            if record.type != 'purchase' and record.employee_expense_journal:
                raise UserError('El diario de gasto para empleados solo puede ser usado en factura de compras')