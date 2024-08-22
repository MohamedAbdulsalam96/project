// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

var res = []

frappe.ui.form.on('Performance Bonus', {


	onload: function (frm) {
        
		frm.set_query('fiscal_year', function() {
			return {
				filters: {
					'company':frm.doc.company
				}
			}
		});

		frm.set_query('salary_component', function() {
			return {
				filters: {
					'type': 'Earning',
					'company':frm.doc.company
				}
			}
		});
		
		frm.call({
			method:'get_bonus_emp',
			doc:frm.doc,
	   callback: function(response) {
		   if(response.message){
			   cur_frm.fields_dict['performance_bonus_items'].grid.get_field('employee').get_query = function(doc, cdt, cdn) {
				   return {
					   filters: [
								  ['name', 'in' , response.message]
					   ]
				   }
			   }
			   frm.refresh_field("budget_items")
		   }


			}
	  })
	}

	
	// refresh: function (frm) {
		
	
		
	// },
    
	// bonus_period_monthly: function (frm) {
	//     console.log('hhhhh')
	// 	const bonus = new Bonus()
	// 	bonus.setupEventListeners()
		
	// }

	// bonus_periodicity: function (frm) {
       
	// 	frm.call({
	// 		doc:frm.doc,
	// 		method: 'get_performance_bonus_item',
	// 		args: {
	// 			filters:null,
	// 			fiscal_year:doc.fiscal_year,
	// 			employee_name:doc.performance_bonus_items[0].employee,
	// 			company:doc.company,
	// 			periodicity: doc.bonus_periodicity,
				
	// 		  }
	// 	}).then(r => {
	// 		res=r
	// 		console.log(res)
	// 	})
       
	// },



    

	

});

frappe.ui.form.on('Performance Bonus Items', {
    
	
	
	employee: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		var t_periods = ''
		if (frm.doc.bonus_periodicity=='Monthly') {
			t_periods=frm.doc.bonus_period_monthly
		}
		if (frm.doc.bonus_periodicity=='Quarterly') {
			t_periods=frm.doc.bonus_period_quarterly
		}
		if (frm.doc.bonus_periodicity=='Half Yearly') {
			t_periods=frm.doc.bonus_period_half_yearly
		}
		
		if (frm.doc.fiscal_year && frm.doc.company && frm.doc.bonus_periodicity) {
			
			frappe.call({
			
				method: 'nextproject.nextproject.doctype.performance_bonus.performance_bonus.get_performance_bonus_item',
				
				args: {
					filters:null,
					fiscal_year:frm.doc.fiscal_year,
					employee_name:row.employee,
					company:frm.doc.company,
					periodicity: frm.doc.bonus_periodicity,
					periods: t_periods,
					
					
				  }
			}).then(r => {
				res=r
				console.log("res:", r)
				res = r
				
				for (const i of r.message) {
					for (const key in i) {
						if (i.hasOwnProperty(key)) {
							
							// console.log(`${key} : ${i[key]}`)
							frappe.model.set_value(cdt, cdn, key, i[key]);	
							
						}
					}
				}
				for (let i = 0; i <res.length; i++){
					console.log(i)
				}
				
				
			})

		}

		
	}
	
	
});

// class Bonus{
	
// 	constructor() {
      
//         this.setupEventListeners();
//     }
	
// 	setupEventListeners() {
      
//         frappe.ui.form.on('Performance Bonus Items', {
//             employee: this.onEmployeeChange.bind(this)
//         });
//     }
    
// 	onEmployeeChange (frm, cdt, cdn) {
// 		var row = locals[cdt][cdn];
// 		var t_periods = ''
// 		if (frm.doc.bonus_periodicity=='Monthly') {
// 			t_periods=frm.doc.bonus_period_monthly
// 		}
// 		if (frm.doc.bonus_periodicity=='Quarterly') {
// 			t_periods=frm.doc.bonus_period_quarterly
// 		}
// 		if (frm.doc.bonus_periodicity=='Half Yearly') {
// 			t_periods=frm.doc.bonus_period_half_yearly
// 		}
		
// 		frappe.call({
			
// 			method: 'nextproject.nextproject.doctype.performance_bonus.performance_bonus.get_performance_bonus_item',
			
// 			args: {
// 				filters:null,
// 				fiscal_year:frm.doc.fiscal_year,
// 				employee_name:row.employee,
// 				company:frm.doc.company,
// 				periodicity: frm.doc.bonus_periodicity,
// 				periods: t_periods,
				
				
// 			  }
// 		}).then(r => {
// 			res=r
// 			console.log("res:", r)
// 			res = r
			
// 			for (const i of r.message) {
// 				for (const key in i) {
// 					if (i.hasOwnProperty(key)) {
						
// 						console.log(`${key} : ${i[key]}`)
// 						frappe.model.set_value(cdt, cdn, key, i[key]);	
						
// 					}
// 				}
// 			}
// 			for (let i = 0; i <res.length; i++){
// 				console.log(i)
// 			}
			
			
// 		})
// 	}

// }