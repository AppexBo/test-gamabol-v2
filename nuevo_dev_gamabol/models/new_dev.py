
from odoo import fields, models

class ReportPosOrder(models.Model):
    _inherit = 'report.pos.order'

    barcode = fields.Char(string='Código de Barras', readonly=True)

    def _select(self):
        return f"""
            {super()._select()},
            pp.barcode AS barcode
        """

    def _from(self):
        return f"""
            {super()._from()}
            LEFT JOIN product_product pp ON pp.id = l.product_id
        """

    def _group_by(self):
        return f"""
            {super()._group_by()},
            pp.barcode
        """

