# -*- coding: utf-8 -*-

from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = ['account.move']
    

    def _post(self,soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        for record in res:
            record.create_employee_expense_receipt()
        return res
    
    def create_employee_expense_receipt(self):
        if self.journal_id.employee_expense_journal:
            employee_receipt = self.env['hr.employee.expense.receipt'].search([('account_move_id','=', self.id)], limit=1)
            vals = {
                        'sequence' : self.journal_id.generate_employee_expense_secuence(),
                        'vat' : self.getEmisorNIT(),
                        'partner_id' : self.getRazonSocialSupplier(),
                        'authorization_code' : self.getCuf() if self.cuf else '',
                        'invoice_number' : self.invoice_number,
                        'dui_dim_number' : self.getDUIDIMNumber(),
                        'dui_dim_invoice_date' : self.getEmisionDate(),
                        'amount_total' : self.getAmountTotalSupplier(),
                        'amount_ice' : self.getAmountIceFromSupplier(),
                        'amount_iehd' : self.getAmountIehdFromSupplier(),
                        'amount_ipj' : self.getAmountIpjFromSupplier(),
                        'rate' : self.getAmountRateFromSupplier(),
                        'amount_no_iva' : self.getAmountNoIvaFromSupplier(),
                        'exempt' : self.getAmountExemptFromSupplier(),
                        'zero_rate' : self.getAmountZeroRateFromSupplier(),
                        'amount_subtotal' : self.getAmountSubTotalSupplier(),
                        'amount_discount' : self.getAmountDisccountSupplier(),
                        'amount_gift_card' : self.getAmountGifCardSuppllier(),
                        'purchase_type' : self.purchase_type,
                        'control_code' : self.getControlCodeSupplier(),
                        'account_move_id' : self.id,
                        'hr_employee_receipt_id' : self.env['hr.employee.receipt.register'].search([], limit=1 ).id
                    }
            if employee_receipt:
                employee_receipt.write(vals)
            else:
                self.env['hr.employee.expense.receipt'].create(vals)
        
        
