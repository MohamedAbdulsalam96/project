let col_list = []

frappe.query_reports["Resource Allocation"] = {
	
	"filters": [

		{
			"fieldname":"company",
			"label": ("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd":1
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"reqd":1
		},

		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"reqd":1
		},
		{
			"fieldname":"periodicity",
			"label": ("Periodicity"),
			"fieldtype": "Select",
			"default":"Daily",
			"options": ["Daily","Weekly", "Monthly","Fortnightly","Yearly"]
		},
		{
			"fieldname":"employee",
			"label": ("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			get_query: () => {
				return {
					filters: {
						'status': "Active",
						
					}
				};
			}
		},
		{
			"label": "Designation",
			"fieldname": ("designation"),
			"fieldtype": "Link",
			"options":"Designation"
		},
		{
			"label": "Department",
			"fieldname": ("department"),
			"fieldtype": "Link",
			"options":"Department"
		},
		{
			"label": "Reports To (Name)",
			"fieldname": ("reports_to_name"),
			"fieldtype": "Link",
			"options":"Employee"
		}


	],
	after_datatable_render: function(datatable_obj) {
		$(datatable_obj.wrapper).find(".dt-row-0").find('input[type=checkbox]').click();
	},
	get_datatable_options(options) {
		return Object.assign(options, {
			checkboxColumn: true,
			events: {
				onCheckRow: function (data) {
					if (!data) return;
					const data_doctype = $(
						data[2].html
					)[0].attributes.getNamedItem("data-doctype").value;
					const tree_type = frappe.query_report.filters[0].value;
					if (data_doctype != tree_type) return;

					row_name = data[2].content;
					length = data.length;

					if (tree_type == "Customer") {
						row_values = data
							.slice(4, length - 1)
							.map(function (column) {
								return column.content;
							});
					} else if (tree_type == "Item") {
						row_values = data
							.slice(5, length - 1)
							.map(function (column) {
								return column.content;
							});
					} else {
						row_values = data
							.slice(3, length - 1)
							.map(function (column) {
								return column.content;
							});
					}

					entry = {
						name: row_name,
						values: row_values,
					};

					let raw_data = frappe.query_report.chart.data;
					let new_datasets = raw_data.datasets;

					let element_found = new_datasets.some((element, index, array)=>{
						if(element.name == row_name){
							array.splice(index, 1)
							return true
						}
						return false
					})

					if (!element_found) {
						new_datasets.push(entry);
					}

					let new_data = {
						labels: raw_data.labels,
						datasets: new_datasets,
					};
					chart_options = {
						data: new_data,
						type: "line",
					};
					frappe.query_report.render_chart(chart_options);

					frappe.query_report.raw_chart_data = new_data;
				},
			},
		});
	},
};
