# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MasterType(models.Model):
	_inherit = 'master.type'

	number_of_location = fields.Selection([
		('single', 'Single'),
		('multi', 'Multi'),
		], default='single', string='Number of Location', copy=False)