from __future__ import unicode_literals

from frappe import _


def get_data(data):
	return {
		'fieldname': 'ticket',
		'transactions': [
			{
				'label': _('Links'),
				'items': ['Task', 'Sales Invoice']
			}
		]
	}