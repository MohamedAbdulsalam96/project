from frappe import _


def get_data(data):
	return {
		'fieldname': 'task',
		'non_standard_fieldnames': {
			'ToDo': 'reference_name',
		},
		'transactions': [
			{
				'label': _('Activity'),
				'items': ['Timesheet']
			},
			{
				'label': _('Accounting'),
				'items': ['Expense Claim']
			},
            {
				'label': _('Test Cases'),
				'items': ['Test Cases']
			},
            {
				'label': _('Test Session'),
				'items': ['Test Session']
			},
			{
				'label': _('Related Issues'),
				'items': ['Issue']
			},
			{
				'label': _('Planning'),
				'items': ['ToDo']
			},
			
		]
	}