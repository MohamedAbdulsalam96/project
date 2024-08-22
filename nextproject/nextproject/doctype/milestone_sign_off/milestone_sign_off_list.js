frappe.listview_settings['Milestone Sign Off'] = {
     get_indicator: function (doc) {
         if (doc.status1 === "To Be Signed") {
             return [__("To Be Signed"), "orange" ];
         }
         else if (doc.status1 === "Partially Signed") {
             return [__("Partially Signed"), "red"];
         }
         else if (doc.status1 === "Fully Signed") {
             return [__("Fully Signed"), "yellow"];
         }
             
     },
 };
 