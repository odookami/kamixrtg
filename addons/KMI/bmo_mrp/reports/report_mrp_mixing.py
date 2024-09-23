from os import stat
import re
import xlwt
import base64, io
import itertools
from PIL import Image
from io import StringIO, BytesIO
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import platform

class MrpReportMixing(models.TransientModel):        
	_name = 'mrp.report.mixing'
	_description = 'MRP Mixing Report'
	
	mrp_data = fields.Char('Name', size=256)
	file_name = fields.Binary('Internal Transfer Report', readonly=True)
	
class WizardWizardsMrp(models.TransientModel):        
	_name = 'wizard.reports.mrp'
	_description = 'MRP Wizard'
	
	# @api.multi
	def action_mrp_report(self):          
		custom_value = {}
		# mrp = self.env['mrp.production'].browse(self._context.get('active_ids', list()))
		picking = self.env['stock.picking'].browse(self._context.get('active_ids', list()))  
		prod_group = self.env['product.group']    
		workbook = xlwt.Workbook()

		header = ["No", "Item Code", "Sub Item Code", "Item Description", "UOM", \
					"Quantity","LOT", "Quantity BKB-OKP", \
					"Paraf (WHS)", "Verifikator (PRD)", "Keterangan"]

		data = []
		data_unic = []
		no = 1
		for rec in picking:
			for op in rec.move_ids_without_package:
				for detop in op.move_line_ids:
					prod_search = prod_group.search([('product_id', '=', detop.product_id.id)], limit=1)
					if rec.state not in ['draft', 'waiting', 'confirmed']:
						paraf = 'yes'
					else:
						paraf = 'no'

					if not prod_search:
						data.append({
							'No'           	     : str(no),
							'Item Code'          : detop.product_id.default_code or '',
							'Sub Item Code'    	 : '',
							'Item Description' 	 : detop.product_id.name or '',
							'UOM'   	 	   	 : detop.product_uom_id.name or '',
							'Quantity'     	   	 : op.product_uom_qty or '',
							'LOT'	 	   	   	 : detop.lot_id.name if detop.lot_id else '',
							'Quantity BKB-OKP' 	 : detop.qty_done or '',
							'Paraf (WHS)'      	 : paraf,
							'Verifikator (PRD)'	 : op.verifikator if op.verifikator else '',
							'Keterangan'	 	 : '',
						})
						no += 1
						data_unic.append(detop.product_id.default_code)
					else:
						data.append({
							'No'           	     : str(no),
							'Item Code'          : detop.product_id.default_code or '',
							'Sub Item Code'    	 : '',
							'Item Description' 	 : detop.product_id.name or '',
							'UOM'   	 	   	 : detop.product_uom_id.name or '',
							'Quantity'     	   	 : op.product_uom_qty or '',
							'LOT'	 	   	   	 : detop.lot_id.name if detop.lot_id else '',
							'Quantity BKB-OKP' 	 : detop.qty_done or '',
							'Paraf (WHS)'      	 : paraf,
							'Verifikator (PRD)'	 : op.verifikator if op.verifikator else '',
							'Keterangan'	 	 : '',
						})
						no += 1

					if prod_search:
						for prod in prod_search.product_group_line:
							data.append({
								'No'           	     : str(no),
								'Item Code'          : '-',
								'Sub Item Code'    	 : prod.product_id.default_code,
								'Item Description' 	 : prod.product_id.name or '',
								'UOM'   	 	   	 : prod.uom_id.name,
								'Quantity'     	   	 : prod.qty,
								'LOT'	 	   	   	 : '-',
								'Quantity BKB-OKP' 	 : prod.qty,
								'Paraf (WHS)'      	 : paraf,
								'Verifikator (PRD)'	 : '',
								'Keterangan'	 	 : '',
							})
							no += 1
												  
			style10 = xlwt.easyxf('font: name Times New Roman bold on;borders:left medium, right medium, top medium, bottom medium;align: vert center, horiz center;', num_format_str='#,##0.00')
			style11 = xlwt.easyxf('font: name Times New Roman bold on;borders:left medium, right medium, top medium, bottom medium;', num_format_str='#,##0.00')
			style12 = xlwt.easyxf('font: name Times New Roman bold on;borders:left medium, right medium, top medium, bottom medium;align: horiz right;', num_format_str='#,##0.00')

			sheet = workbook.add_sheet(rec.name)

			sheet.write(1, 1, 'No OKP', style10)
			sheet.write(1, 2, rec.batch_production_id.okp_id.name, style10)

			# no_batch = rec.name.split()
			# sheet.write(2, 2, no_batch[-1], style10)
			sheet.write(2, 1, 'No Batch', style10)
			sheet.write(2, 2, rec.mo_id.number_ref, style10)
						
			no = 3;
			for line in data:
				no += 1
				col = -1
				for i in header:
					sheet.row(no).height = 5 * 75
					sheet.row(no).height_mismatch = True
					col += 1
					sheet.write(no, col, line[i], style11)

			colh = -1
			for x in header:
				colh += 1
				style11.alignment.wrap = 1
				sheet.write(3, colh, x, style11)
			
			n = no
			# sheet.write(n+3, 0,'No:', style11)
			sheet.write(n+3, 1, 'Proses', style10)
			sheet.write(n+3, 2, 'Analisa', style10)
			sheet.write(n+3, 3, rec.lot_amf_1_id.name if rec.lot_amf_1_id else '', style10)
			sheet.write_merge(n+3, n+3, 4, 5, rec.lot_amf_2_id.name if rec.lot_amf_2_id else '', style10)

			if rec.check_tipe_product == 'Benecol':
				sheet.write_merge(n+4, n+7, 1, 1, 'Thawing PSE 12-24 jam (sebelum melting)', style10)
				sheet.write(n+4, 2, 'Start Thawing (Tanggal)', style10)
				sheet.write(n+5, 2, 'Start Thawing (Jam)', style10)
				sheet.write(n+6, 2, 'Finish Thawing (Tanggal)', style10)
				sheet.write(n+7, 2, 'Finish Thawing (Jam)', style10)

				sheet.write_merge(n+8, n+9, 1, 1, 'PSE pernah dilakukan melting sebelumnya*', style10)
				sheet.write(n+8, 2, 'Tanggal Melting', style10)
				sheet.write(n+9, 2, 'Umur Melting sebelumnya', style10)

				sheet.write_merge(n+10, n+37, 1, 1, 'Melting PSE dalam kompor selama 15 jam', style10)
				sheet.write(n+10, 2, 'Start Melting (tanggal)', style10)
				sheet.write(n+11, 2, 'Start Melting (jam)', style10)
				sheet.write(n+12, 2, 'Nomor Kompor', style10)
				sheet.write(n+13, 2, 'Nomor Jaket', style10)
				sheet.write(n+14, 2, 'Finish Melting (tanggal)', style10)
				sheet.write(n+15, 2, 'Finish Melting (jam)', style10)
				sheet.write(n+16, 2, 'Suhu PSE (70-85°C dalam jaket)', style10)
				sheet.write(n+17, 2, 'Check Pertama Jam', style10)
				sheet.write(n+18, 2, 'Suhu', style10)
				sheet.write(n+19, 2, 'Check Kedua Jam', style10)
				sheet.write(n+20, 2, 'Suhu', style10)
				sheet.write(n+21, 2, 'Suhu PSE (70-85°C After Melting 15 Jam)', style10)
				sheet.write(n+22, 2, 'Warna PSE', style10)
				sheet.write(n+23, 2, 'Abnormal', style10)
				sheet.write(n+24, 2, 'Jam Ke-1', style10)
				sheet.write(n+25, 2, 'Suhu Ke-1', style10)
				sheet.write(n+26, 2, 'Warna Ke-1', style10)
				sheet.write(n+27, 2, 'Jam Ke-2', style10)
				sheet.write(n+28, 2, 'Suhu Ke-2', style10)
				sheet.write(n+29, 2, 'Warna Ke-2', style10)
				sheet.write(n+30, 2, 'Jam Ke-3', style10)
				sheet.write(n+31, 2, 'Suhu Ke-3', style10)
				sheet.write(n+32, 2, 'Warna Ke-3', style10)
				sheet.write(n+33, 2, 'Jam Ke-4', style10)
				sheet.write(n+34, 2, 'Suhu Ke-4', style10)
				sheet.write(n+35, 2, 'Warna Ke-4', style10)
				sheet.write(n+36, 2, 'Tanggal Serah Terima', style10)
				sheet.write(n+37, 2, 'Jam Serah Terima', style10)

				sheet.write(n+4, 3, rec.date_start_thawing if rec.date_start_thawing else '', style10)
				sheet.write(n+5, 3, rec.hour_start_thawing if rec.hour_start_thawing else '', style10)
				sheet.write(n+6, 3, rec.date_finish_thawing if rec.date_finish_thawing else '', style10)
				sheet.write(n+7, 3, rec.hour_finish_thawing if rec.hour_finish_thawing else '', style10)

				sheet.write(n+8, 3, rec.date_melting_pernah if rec.date_melting_pernah else '', style10)
				sheet.write(n+9, 3, rec.age_melting_pernah if rec.age_melting_pernah else '', style10)

				sheet.write(n+10, 3, rec.date_start_meling if rec.date_start_meling else '', style10)
				sheet.write(n+11, 3, rec.hour_start_meling if rec.hour_start_meling else '', style10)
				sheet.write(n+12, 3, rec.no_kompor_meling if rec.no_kompor_meling else '', style10)
				sheet.write(n+13, 3, rec.no_jaket_meling if rec.no_jaket_meling else '', style10)
				sheet.write(n+14, 3, rec.date_finish_meling if rec.date_finish_meling else '', style10)
				sheet.write(n+15, 3, rec.hour_finish_meling if rec.hour_finish_meling else '', style10)
				sheet.write(n+16, 3, rec.suhu_jaket if rec.suhu_jaket else '', style10)
				sheet.write(n+17, 3, rec.check_pertama_jam if rec.check_pertama_jam else '', style10)
				sheet.write(n+18, 3, rec.suhu_pertama_jam if rec.suhu_pertama_jam else '', style10)
				sheet.write(n+19, 3, rec.check_kedua_jam if rec.check_kedua_jam else '', style10)
				sheet.write(n+20, 3, rec.suhu_kedua_jam if rec.suhu_kedua_jam else '', style10)
				sheet.write(n+21, 3, rec.suhu_after_melting if rec.suhu_after_melting else '', style10)
				sheet.write(n+22, 3, rec.warna_pse if rec.warna_pse else '', style10)
				sheet.write(n+23, 3, rec.abnormal if rec.abnormal else '', style10)
				sheet.write(n+24, 3, rec.jam_ke_1 if rec.jam_ke_1 else '', style10)
				sheet.write(n+25, 3, rec.suhu_ke_1 if rec.suhu_ke_1 else '', style10)
				sheet.write(n+26, 3, rec.warna_ke_1 if rec.warna_ke_1 else '', style10)
				sheet.write(n+27, 3, rec.jam_ke_2 if rec.jam_ke_2 else '', style10)
				sheet.write(n+28, 3, rec.suhu_ke_2 if rec.suhu_ke_2 else '', style10)
				sheet.write(n+29, 3, rec.warna_ke_2 if rec.warna_ke_2 else '', style10)
				sheet.write(n+30, 3, rec.jam_ke_3 if rec.jam_ke_3 else '', style10)
				sheet.write(n+31, 3, rec.suhu_ke_3 if rec.suhu_ke_3 else '', style10)
				sheet.write(n+32, 3, rec.warna_ke_3 if rec.warna_ke_3 else '', style10)
				sheet.write(n+33, 3, rec.jam_ke_4 if rec.jam_ke_4 else '', style10)
				sheet.write(n+34, 3, rec.suhu_ke_4 if rec.suhu_ke_4 else '', style10)
				sheet.write(n+35, 3, rec.warna_ke_4 if rec.warna_ke_4 else '', style10)
				sheet.write(n+36, 3, rec.tanggal_terima if rec.tanggal_terima else '', style10)
				sheet.write(n+37, 3, rec.jam_terima if rec.jam_terima else '', style10)

				sheet.write_merge(n+4, n+4, 4, 5, rec.date_start_thawing_2 if rec.date_start_thawing_2 else '', style10)
				sheet.write_merge(n+5, n+5, 4, 5, rec.hour_start_thawing_2 if rec.hour_start_thawing_2 else '', style10)
				sheet.write_merge(n+6, n+6, 4, 5, rec.date_finish_thawing_2 if rec.date_finish_thawing_2 else '', style10)
				sheet.write_merge(n+7, n+7, 4, 5, rec.hour_finish_thawing_2 if rec.hour_finish_thawing_2 else '', style10)

				sheet.write_merge(n+8, n+8, 4, 5, rec.date_melting_pernah_2 if rec.date_melting_pernah_2 else '', style10)
				sheet.write_merge(n+9, n+9, 4, 5, rec.age_melting_pernah_2 if rec.age_melting_pernah_2 else '', style10)

				sheet.write_merge(n+10, n+10, 4, 5, rec.date_start_meling_2 if rec.date_start_meling_2 else '', style10)
				sheet.write_merge(n+11, n+11, 4, 5, rec.hour_start_meling_2 if rec.hour_start_meling_2 else '', style10)
				sheet.write_merge(n+12, n+12, 4, 5, rec.no_kompor_meling_2 if rec.no_kompor_meling_2 else '', style10)
				sheet.write_merge(n+13, n+13, 4, 5, rec.no_jaket_meling_2 if rec.no_jaket_meling_2 else '', style10)
				sheet.write_merge(n+14, n+14, 4, 5, rec.date_finish_meling_2 if rec.date_finish_meling_2 else '', style10)
				sheet.write_merge(n+15, n+15, 4, 5, rec.hour_finish_meling_2 if rec.hour_finish_meling_2 else '', style10)
				sheet.write_merge(n+16, n+16, 4, 5, rec.suhu_jaket_2 if rec.suhu_jaket_2 else '', style10)
				sheet.write_merge(n+17, n+17, 4, 5, rec.check_pertama_jam_2 if rec.check_pertama_jam_2 else '', style10)
				sheet.write_merge(n+18, n+18, 4, 5, rec.suhu_pertama_jam_2 if rec.suhu_pertama_jam_2 else '', style10)
				sheet.write_merge(n+19, n+19, 4, 5, rec.check_kedua_jam_2 if rec.check_kedua_jam_2 else '', style10)
				sheet.write_merge(n+20, n+20, 4, 5, rec.suhu_kedua_jam_2 if rec.suhu_kedua_jam_2 else '', style10)
				sheet.write_merge(n+21, n+21, 4, 5, rec.suhu_after_melting_2 if rec.suhu_after_melting_2 else '', style10)
				sheet.write_merge(n+22, n+22, 4, 5, rec.warna_pse_2 if rec.warna_pse_2 else '', style10)
				sheet.write_merge(n+23, n+23, 4, 5, rec.abnormal_2 if rec.abnormal_2 else '', style10)
				sheet.write_merge(n+24, n+24, 4, 5, rec.jam_ke_1_2 if rec.jam_ke_1_2 else '', style10)
				sheet.write_merge(n+25, n+25, 4, 5, rec.suhu_ke_1_2 if rec.suhu_ke_1_2 else '', style10)
				sheet.write_merge(n+26, n+26, 4, 5, rec.warna_ke_1_2 if rec.warna_ke_1_2 else '', style10)
				sheet.write_merge(n+27, n+27, 4, 5, rec.jam_ke_2_2 if rec.jam_ke_2_2 else '', style10)
				sheet.write_merge(n+28, n+28, 4, 5, rec.suhu_ke_2_2 if rec.suhu_ke_2_2 else '', style10)
				sheet.write_merge(n+29, n+29, 4, 5, rec.warna_ke_2_2 if rec.warna_ke_2_2 else '', style10)
				sheet.write_merge(n+30, n+30, 4, 5, rec.jam_ke_3_2 if rec.jam_ke_3_2 else '', style10)
				sheet.write_merge(n+31, n+31, 4, 5, rec.suhu_ke_3_2 if rec.suhu_ke_3_2 else '', style10)
				sheet.write_merge(n+32, n+32, 4, 5, rec.warna_ke_3_2 if rec.warna_ke_3_2 else '', style10)
				sheet.write_merge(n+33, n+33, 4, 5, rec.jam_ke_4_2 if rec.jam_ke_4_2 else '', style10)
				sheet.write_merge(n+34, n+34, 4, 5, rec.suhu_ke_4_2 if rec.suhu_ke_4_2 else '', style10)
				sheet.write_merge(n+35, n+35, 4, 5, rec.warna_ke_4_2 if rec.warna_ke_4_2 else '', style10)
				sheet.write_merge(n+36, n+36, 4, 5, rec.tanggal_terima_2 if rec.tanggal_terima_2 else '', style10)
				sheet.write_merge(n+37, n+37, 4, 5, rec.jam_terima_2 if rec.jam_terima_2 else '', style10)

			if rec.check_tipe_product == 'Chilgo':
				sheet.write_merge(n+4, n+9, 1, 1, 'Pelelehan AMF dalam steam box selama 1.5 jam', style10)
				sheet.write(n+4, 2, 'AMF Pernah dimelting? Y or N', style10)
				sheet.write(n+5, 2, 'Tanggal Melting dan Jumlah (jam)', style10)
				sheet.write(n+6, 2, 'Start Melting', style10)
				sheet.write(n+7, 2, 'Tanggal', style10)
				sheet.write(n+8, 2, 'Jam', style10)
				sheet.write(n+9, 2, 'Presure', style10)
				sheet.write_merge(n+10, n+17, 1, 1, 'Pencatatan suhu dan pressure steam box', style10)
				sheet.write(n+10, 2, 'Suhu (1 Jam)', style10)
				sheet.write(n+11, 2, 'Presure (1 Jam)', style10)
				sheet.write(n+12, 2, 'Suhu (1.5 Jam)', style10)
				sheet.write(n+13, 2, 'Presure (1.5 Jam)', style10)
				sheet.write(n+14, 2, 'Finish Melting', style10)
				sheet.write(n+15, 2, 'Tanggal', style10)
				sheet.write(n+16, 2, 'Jam', style10)
				sheet.write(n+17, 2, 'Suhu', style10)
				sheet.write_merge(n+18, n+20, 1, 1, 'Preparasi AMF (wadah stainless)', style10)
				sheet.write(n+18, 2, 'Qty Timbang AMF', style10)
				sheet.write(n+19, 2, 'Warna AMF (standar : jernih)', style10)
				sheet.write(n+20, 2, 'Suhu (standar : 60 - 95°C)', style10)
				
				sheet.write(n+4, 3, rec.melting_amf if rec.melting_amf else '', style10)
				sheet.write(n+5, 3, rec.date_melting if rec.date_melting else '', style10)
				sheet.write(n+6, 3, rec.start_melting if rec.start_melting else '', style10)
				sheet.write(n+7, 3, rec.date_melting_amf if rec.date_melting_amf else '', style10)
				sheet.write(n+8, 3, rec.hour_melting_amf if rec.hour_melting_amf else '', style10)
				sheet.write(n+9, 3, rec.pressure if rec.pressure else '', style10)
				sheet.write(n+10, 3, rec.suhu_satu_jam if rec.suhu_satu_jam else '', style10)
				sheet.write(n+11, 3, rec.pressure_satu_jam if rec.pressure_satu_jam else '', style10)
				sheet.write(n+12, 3, rec.suhu_satu_jam_set if rec.suhu_satu_jam_set else '', style10)
				sheet.write(n+13, 3, rec.pressure_satu_jam_set if rec.pressure_satu_jam_set else '', style10)
				sheet.write(n+14, 3, rec.finish_melting if rec.finish_melting else '', style10)
				sheet.write(n+15, 3, rec.date_melting_pressure if rec.date_melting_pressure else '', style10)
				sheet.write(n+16, 3, rec.hour_melting_pressure if rec.hour_melting_pressure else '', style10)
				sheet.write(n+17, 3, rec.suhu_pressure if rec.suhu_pressure else '', style10)
				sheet.write(n+18, 3, rec.preparasi_amf if rec.preparasi_amf else '', style10)
				sheet.write(n+19, 3, rec.warna_amf if rec.warna_amf else '', style10)
				sheet.write(n+20, 3, rec.suhu_standar if rec.suhu_standar else '', style10)

				sheet.write_merge(n+4, n+4, 4, 5, rec.melting_amf_2 if rec.melting_amf_2 else '', style10)
				sheet.write_merge(n+5, n+5, 4, 5, rec.date_melting_2 if rec.date_melting_2 else '', style10)
				sheet.write_merge(n+6, n+6, 4, 5, rec.start_melting_2 if rec.start_melting_2 else '', style10)
				sheet.write_merge(n+7, n+7, 4, 5, rec.date_melting_amf_2 if rec.date_melting_amf_2 else '', style10)
				sheet.write_merge(n+8, n+8, 4, 5, rec.hour_melting_amf_2 if rec.hour_melting_amf_2 else '', style10)
				sheet.write_merge(n+9, n+9, 4, 5, rec.pressure_2 if rec.pressure_2 else '', style10)
				sheet.write_merge(n+10, n+10, 4, 5, rec.suhu_satu_jam_2 if rec.suhu_satu_jam_2 else '', style10)
				sheet.write_merge(n+11, n+11, 4, 5, rec.pressure_satu_jam_2 if rec.pressure_satu_jam_2 else '', style10)
				sheet.write_merge(n+12, n+12, 4, 5, rec.suhu_satu_jam_set_2 if rec.suhu_satu_jam_set_2 else '', style10)
				sheet.write_merge(n+13, n+13, 4, 5, rec.pressure_satu_jam_set_2 if rec.pressure_satu_jam_set_2 else '', style10)
				sheet.write_merge(n+14, n+14, 4, 5, rec.finish_melting_2 if rec.finish_melting_2 else '', style10)
				sheet.write_merge(n+15, n+15, 4, 5, rec.date_melting_pressure_2 if rec.date_melting_pressure_2 else '', style10)
				sheet.write_merge(n+16, n+16, 4, 5, rec.hour_melting_pressure_2 if rec.hour_melting_pressure_2 else '', style10)
				sheet.write_merge(n+17, n+17, 4, 5, rec.suhu_pressure_2 if rec.suhu_pressure_2 else '', style10)
				sheet.write_merge(n+18, n+18, 4, 5, rec.preparasi_amf_2 if rec.preparasi_amf_2 else '', style10)
				sheet.write_merge(n+19, n+19, 4, 5, rec.warna_amf_2 if rec.warna_amf_2 else '', style10)
				sheet.write_merge(n+20, n+20, 4, 5, rec.suhu_standar_2 if rec.suhu_standar_2 else '', style10)
			
			col_width = 256 * 25
			try:
				for i in itertools.count():
					sheet.col(i).width = col_width
					sheet.col(0).width = 256 * 5
					sheet.col(1).width = 256 * 15
					sheet.col(2).width = 256 * 20
					sheet.col(3).width = 256 * 50
					sheet.col(4).width = 256 * 7
					sheet.col(5).width = 256 * 10
					sheet.col(6).width = 256 * 20
					sheet.col(7).width = 256 * 20
					sheet.col(8).width = 256 * 12
					sheet.col(9).width = 256 * 17
					sheet.col(10).width = 256 * 17
					sheet.col(11).width = 256 * 17
					sheet.col(12).width = 256 * 17
					
			except ValueError:
				pass

		if platform.system() == 'Linux':
			filename = ('/tmp/Picking Report' + '.xls')
		else:
			filename = ('Verifikasi produk RM' + '.xls')

		workbook.save(filename)
		fp = open(filename, "rb")
		file_data = fp.read()
		out = base64.encodestring(file_data)
					   
# Files actions         
		attach_vals = {
				'mrp_data': 'Verifikasi produk RM'+ '.xls',
				'file_name': out,
			} 
			
		act_id = self.env['mrp.report.mixing'].create(attach_vals)
		fp.close()
		return {
		'type': 'ir.actions.act_window',
		'res_model': 'mrp.report.mixing',
		'res_id': act_id.id,
		'view_type': 'form',
		'view_mode': 'form',
		'context': self.env.context,
		'target': 'new',
		}