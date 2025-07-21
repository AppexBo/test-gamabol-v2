# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from xml.sax.saxutils import escape

class AccountMoveLine(models.Model):
    _inherit = ['account.move.line']

    # Agregar a la vista tre
    specialty = fields.Char(
        string='Especialidad',
    )
    
    def getSpeciality(self, to_xml = False):
        if to_xml:
            return escape(self.specialty)
        return self.specialty
    
    # Agregar a la vista tree
    doctor_id = fields.Many2one(
        string='Médico',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    
    
    room_number = fields.Integer(
        string='Nro. Quirofano/sala',
    )
    
    doctors_specialty = fields.Char(
        string='Especialidad del doctor',
    )
    
    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        self.doctors_specialty = self.getSpecialityTagsDoctor()
        self.specialty = self.doctor_id.ref if self.doctor_id else False
    
    
    def getSpecialityDoctor(self, to_xml = False):
        description = self.doctors_specialty
        if to_xml:
            return escape(description)
        return description
    

    def getRoomNumber(self):
        if self.room_number>0:
            return self.room_number
        raise UserError('El Nro Quirofano/sala debe ser mayor a 0')
    
    def getSpecialityTagsDoctor(self):
        speciality = False
        if self.doctor_id and self.doctor_id.category_id:
            speciality = ''
            for category_id in self.doctor_id.category_id:
                speciality += category_id.name + ','
            speciality = speciality[:-1]
        return speciality
    
    

    def getDoctorName(self, to_xml = False):
        if self.doctor_id:
            if to_xml:
                return escape(self.doctor_id.name)
            return self.doctor_id.name
        raise UserError('Necesita un médico en la linea de producto')
    
    def getDoctorNITCODE(self):
        if self.doctor_id:
            if self.doctor_id.vat:
                return self.doctor_id.vat
            if self.doctor_id.code:
                return self.doctor_id.code
            raise UserError('El medico necesita un NIT o un Codigo')
        raise UserError('Necesita un médico en la linea de producto')
    
    def getTuition(self):
        if self.doctor_id:
            if self.doctor_id.code:
                return self.doctor_id.code
        return False
    
    doctor_bill_number = fields.Integer(
        string='Nro. factura medico',
    )

    def getDoctorBillNumber(self):
        return self.doctor_bill_number
    
    def getProductDescription(self, to_xml = False):
        if to_xml:
            return escape(self.product_id.name)
        return self.product_id.name