from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'project_allocation_bill',
       
		'transactions': [
			{
				'label': _('Linked Documents'),
				'items': ['Sales Invoice','Sales Order']
			},
			
		]
	}
