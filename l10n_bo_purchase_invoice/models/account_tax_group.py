# -*- coding:utf-8 -*-

from odoo import api, models, fields

class AccountTaxgroup(models.Model):
    _inherit = ['account.tax.group']
    

    
    purchase_edi_group = fields.Boolean(
        string='Grupo de compras (BO)',
    )
    
    purchase_edi_description = fields.Char(
        string='Tipo grupo (BO)',
    )
    

    
    purchase_tax_group_type = fields.Selection(
        string='Tipo importe RC',
        selection=[
            ('ice', 'ICE'), 
            ('iehd', 'IEHD'),
            ('ipj', 'IPJ'),
            ('rate', 'Tasas'),
            ('no_iva', 'No sujeto a credito fiscal'),
            ('exempt', 'Exentos'),
            ('cero_rate', 'Gravadas a tasa cero'),
        ],
        help="""
        ICE : Impuesto al consumo espesifico.
        IEHD : Impuesto Especial a los Hidrocarburos y Derivados.
        IPJ : Impuesto a la participación en juegos.
        Tasas : Tributo la prestacion de servicios.
        No sujeto a credito fiscal: Importe sin credito fiscal.
        Exentos: Importe libre de impuestos.
        Gravadas a tasa cero: Ventas gradadas a tasa cero / Tasa cero IVA Ley Nro 1546.
        """
    )
    