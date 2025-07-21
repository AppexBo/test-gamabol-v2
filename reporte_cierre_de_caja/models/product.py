# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ , tools


class ProductProduct(models.Model):
	_inherit = 'product.product'

	custom_pos_categ_ids = fields.Many2many(related='pos_categ_ids',string="Custom Pos Category",domain="[('id', 'in', custom_pos_categ_ids)]") 
	reporte_cierre_de_caja_catrgory = fields.Many2one('pos.category',string="POS Category Reports",domain="[('id', 'in', custom_pos_categ_ids)]")

	@api.onchange('pos_categ_ids')
	def _onchange_pos_categ_ids(self):
		if self.pos_categ_ids:
			
			self.reporte_cierre_de_caja_catrgory = False

class ProductTemplate(models.Model):
	_inherit = 'product.template'


	# reporte_cierre_de_caja_catrgory = fields.Many2one('pos.category',string="POS Category Reports",compute='_compute_pos_reports_catrgory',
	# 	inverse='_set_reporte_cierre_de_caja_catrgory',domain=lambda self: [('id', 'in', self._check_categ())])
	custom_pos_categ_ids = fields.Many2many(related='pos_categ_ids',string="Custom Pos Category") 
	reporte_cierre_de_caja_catrgory = fields.Many2one('pos.category',string="POS Category Reports",compute='_compute_pos_reports_catrgory',
		inverse='_set_reporte_cierre_de_caja_catrgory',domain="[('id', 'in', custom_pos_categ_ids)]",)

	def _set_reporte_cierre_de_caja_catrgory(self):
		self._set_product_variant_field('reporte_cierre_de_caja_catrgory')


	@api.depends('product_variant_ids.reporte_cierre_de_caja_catrgory')
	def _compute_pos_reports_catrgory(self):
		self._compute_template_field_from_variant_field('reporte_cierre_de_caja_catrgory')


	@api.onchange('pos_categ_ids')
	def _onchange_pos_categ_ids(self):
		if self.pos_categ_ids:

			self.reporte_cierre_de_caja_catrgory = False

