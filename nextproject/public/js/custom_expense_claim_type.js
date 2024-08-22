frappe.ui.form.on("Expense Claim Type", {
    setup:function(frm){
        console.log("kkkkkkkkkkkk")
        frm.set_query("income_account","accounts",function(frm,cdn,cdt){
            console.log("llllllllllllll")
			var child = locals[cdn][cdt]
            console.log("ggggggggggggggggg")
            return{
                filters:{
					'is_group':0,
					"company":child.company,
                    'account_type' : "Income Account",
                }
            }
        }
    )
	}
})