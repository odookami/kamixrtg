# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
import datetime

class product_st(models.Model):
	_inherit = 'product.st'

	active = fields.Boolean('Active', default='True')
	
	def dateweek(self):
		x = datetime.datetime.now()
		day = [
			{'h':'Monday', 'val':'0'}, 
			{'h':'Tuesday', 'val':'1'}, 
			{'h':'Wednesday', 'val':'2'}, 
			{'h':'Thursday', 'val':'3'}, 
			{'h':'Friday', 'val':'4'}, 
			{'h':'Saturday', 'val':'5'}, 
			{'h':'Sunday', 'val':'6'}, 
		]
		for i in day:
			if i['h'] == x.strftime("%A"):
				day = i['val']
		return day

	def move_to_filling(self):
		filling_id = self.env['kmi.filling'].search([('okp_id', '=', self.okp_id.id), ('shift', '=', self.shift)])
		okp_filling_id = self.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling' and l.state == "progress")
		if filling_id:
			filling_id.write({'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_filling_id[0].product_id.id})]})
		else:
			filling_id = filling_id.create({
				'name' : 'New',
				'product_id' : okp_filling_id[0].product_id.id,
				'no_urut_bo' : okp_filling_id[0].name,
				'okp_id' : self.okp_id.id,
				'date' : fields.Date.context_today(self),
				'shift' :self.shift,
				'dayofweek': self.dateweek(),
				'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_filling_id[0].product_id.id})],
				})

	def move_to_unscramble(self):
		unscramble_id = self.env['kmi.unscramble'].search([('okp_id', '=', self.okp_id.id), ('shift', '=', self.shift)])
		okp_unscramble_id = self.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling' and l.state == "progress")
		if unscramble_id:
			unscramble_id.write({'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_unscramble_id[0].product_id.id})]})
		else:
			unscramble_id = unscramble_id.create({
				'name' : 'New',
				'product_id' : okp_unscramble_id[0].product_id.id,
				'no_urut_bo' : okp_unscramble_id[0].name,
				'okp_id' : self.okp_id.id,
				'date' : fields.Date.context_today(self),
				'shift' :self.shift,
				'dayofweek': self.dateweek(),
				'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_unscramble_id[0].product_id.id})],
				})

	def move_to_loader(self):
		loader_id = self.env['kmi.loader'].search([('okp_id', '=', self.okp_id.id), ('shift', '=', self.shift)])
		okp_loader_id = self.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling' and l.state == "progress")
		if loader_id:
			loader_id.write({'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_loader_id[0].product_id.id})]})
		else:
			loader_id = loader_id.create({
				'name' : 'New',
				'product_id' : okp_loader_id[0].product_id.id,
				'no_urut_bo' : okp_loader_id[0].name,
				'okp_id' : self.okp_id.id,
				'date' : fields.Date.context_today(self),
				'shift' : self.shift,
				'dayofweek': self.dateweek(),
				'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_loader_id[0].product_id.id})],
				})
			loader_id.action_submit()
		# loader_id.insert_production_record(self.batch_id.number_ref)

		# print('move_to_filling')


	def move_to_unloader(self):
		unloader_id = self.env['kmi.unloader'].search([('okp_id', '=', self.okp_id.id), ('shift', '=', self.shift)])
		okp_unloader_id = self.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling' and l.state == "progress")
		if unloader_id:
			unloader_id.write({'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_unloader_id[0].product_id.id})]})
		else:
			unloader_id = unloader_id.create({
				'name' : 'New',
				'product_id' : okp_unloader_id[0].product_id.id,
				'no_urut_bo' : okp_unloader_id[0].name,
				'okp_id' : self.okp_id.id,
				'date' : fields.Date.context_today(self),
				'shift' : self.shift,
				'dayofweek': self.dateweek(),
				'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_unloader_id[0].product_id.id})],
				})
			unloader_id.action_submit()
		# unloader_id.insert_production_record(self.batch_id.number_ref)
	
	def move_to_retort(self):
		retort_id = self.env['kmi.retort'].search([('okp_id', '=', self.okp_id.id), ('shift', '=', self.shift)])
		# print(retort_id)
		okp_retort_id = self.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling' and l.state == "progress")
		print(okp_retort_id)
		if retort_id:
			retort_id.write({'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_retort_id[0].product_id.id})]})
		else:
			retort_id = retort_id.create({
				'name' : 'New',
				'product_id' : okp_retort_id[0].product_id.id,
				'no_urut_bo' : okp_retort_id[0].name,
				'okp_id' : self.okp_id.id,
				'date' : fields.Date.context_today(self),
				'shift' : self.shift,
				'dayofweek': self.dateweek(),
				'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_retort_id[0].product_id.id})],
				})
			# print('MASUK BREE')
			retort_id.action_submit()
		# retort_id.insert_production_record(self.batch_id.number_ref)

	def move_to_packing(self):
		packing_id = self.env['kmi.packing'].search([('okp_id', '=', self.okp_id.id), ('shift', '=', self.shift)])
		okp_packing_id = self.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling' and l.state == "progress")
		if packing_id:
			packing_id.write({'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_packing_id[0].product_id.id})]})
		else:
			packing_id = packing_id.create({
				'name' : 'New',
				'product_id' : okp_packing_id[0].product_id.id,
				'no_urut_bo' : okp_packing_id[0].name,
				'okp_id' : self.okp_id.id,
				'date' : fields.Date.context_today(self),
				'shift' : self.shift,
				'dayofweek': self.dateweek(),
				'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_packing_id[0].product_id.id})],
				})
			packing_id.action_submit()
		# packing_id.insert_production_record(self.batch_id.number_ref)

	def move_to_labeling(self):
		labeling_id = self.env['kmi.labeling'].search([('okp_id', '=', self.okp_id.id), ('shift', '=', self.shift)])
		okp_labeling_id = self.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling' and l.state == "progress")
		if labeling_id:
			labeling_id.write({'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_labeling_id[0].product_id.id})]})
		else:
			labeling_id = labeling_id.create({
				'name' : 'New',
				'product_id' : okp_labeling_id[0].product_id.id,
				'no_urut_bo' : okp_labeling_id[0].name,
				'okp_id' : self.okp_id.id,
				'date' : fields.Date.context_today(self),
				'shift' : self.shift,
				'dayofweek': self.dateweek(),
				'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_labeling_id[0].product_id.id})],
				})
			labeling_id.action_submit()
		# labeling_id.insert_production_record(self.batch_id.number_ref)


	def action_done(self):
		super(product_st, self).action_done()
		self.move_to_filling()
		self.move_to_unscramble()
		self.move_to_retort()
		self.move_to_packing()
		self.move_to_labeling()
		self.move_to_loader()
		self.move_to_unloader()
