# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError

class HrExpenseSheet(models.Model):
    _inherit = ['hr.expense.sheet']

    
    hr_bo_expense_ids = fields.One2many(
        string='Facturas/Recibos',
        comodel_name='hr.bo.expense',
        inverse_name='hr_expense_sheet_id',
    )
    
    
    def action_sheet_move_create(self):
        if self.hr_bo_expense_ids:
            self.action_publishing_invoices_or_expense_receipts()
            self._compute_state()
        else:
            super(HrExpenseSheet, self).action_sheet_move_create()
        
    def action_publishing_invoices_or_expense_receipts(self):
        for line in self.hr_bo_expense_ids:
            if not line.invoice_id:
                line.create_registries()

    def action_submit_sheet(self):
        for line in self.hr_bo_expense_ids:
            line.validate_fields()
        super(HrExpenseSheet, self).action_submit_sheet()
    
    def action_reset_expense_sheets(self):
        to_continue = True
        for line in self.hr_bo_expense_ids:
            if line.invoice_id and line.invoice_id.state == 'posted':
                to_continue = False
                break
        
        if to_continue:
            self.reset_hr_bo_expense_ids()
            super(HrExpenseSheet, self).action_reset_expense_sheets()
        else:
            raise UserError('Aun tiene Facturas/Recibos asociados al gasto')
        
    def reset_hr_bo_expense_ids(self):
        if self.hr_bo_expense_ids:
            self.hr_bo_expense_ids.unlink()
        self._compute_state()

    @api.depends('account_move_ids', 'payment_state', 'approval_state', 'hr_bo_expense_ids')
    def _compute_state(self):
        super(HrExpenseSheet, self)._compute_state()

        for record in self:
            invoice_receips = [
                True if line.invoice_id else False
                for line in record.hr_bo_expense_ids
            ]

            if all(invoice_receips) and record.hr_bo_expense_ids:
                record.state = 'post'