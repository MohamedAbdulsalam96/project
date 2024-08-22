from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'test_case',
        'non_standard_fieldnames': {
            'Test Session':'test_case',
        },
		'transactions': [
			{
				'label': _('Test Session'),
				'items': ['Test Session']
			},
		]
	}