# -*-  coding:utf-8 -*-
import csv
from odoo import models, fields, api, tools
from odoo.exceptions import UserError
import os

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']
    
    def create_account_tax_groups(self):
        self.create_l10n_bo_account_tax_groups()

    def get_account_tax_group_csv_path(self):
        module_path = os.path.dirname(__file__)
        csv_file_path = os.path.join(module_path, '..', 'data', 'account.tax.group.csv')
        if not os.path.exists(csv_file_path):
            raise UserError("El archivo CSV no se encuentra en la ruta especificada.")
        return csv_file_path
    
    def get_csv_reader(self):
        csv_file_path = self.get_account_tax_group_csv_path()
        LIST = []
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for line in csv_reader:
                LIST.append(line)
        return LIST

    def create_l10n_bo_account_tax_groups(self):
        RES_CURRENCY_RATE : models.Model = self.env['account.tax.group']
        base_bo = self.env.ref('base.bo')
        RES_CURRENCY_RATE_IDS = self.get_csv_reader()
        RECORD_IDS = []
        for RES_CURRENCY_RATE_ID in RES_CURRENCY_RATE_IDS:
            rate_id = RES_CURRENCY_RATE.search(
                [
                    ('purchase_edi_group','=',RES_CURRENCY_RATE_ID['purchase_edi_group']),
                    ('purchase_edi_description','=',RES_CURRENCY_RATE_ID['purchase_edi_description'])
                ], limit=1
            )
            if not rate_id:
                RECORD = {
                    'purchase_edi_group' : RES_CURRENCY_RATE_ID['purchase_edi_group'],
                    'inverse_company_rate' : RES_CURRENCY_RATE_ID['purchase_edi_description'],
                    'name' : RES_CURRENCY_RATE_ID['name'],
                    'country_id' : base_bo.id,
                    'sequence' : RES_CURRENCY_RATE_ID['sequence'],
                }
                RECORD_IDS.append(RECORD)
        
        if RECORD_IDS:
            RES_CURRENCY_RATE.create(RECORD_IDS)