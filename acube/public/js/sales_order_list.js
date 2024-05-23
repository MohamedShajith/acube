frappe.listview_settings['Sales Order'] = {
	add_fields: [
		"base_grand_total",
		"customer_name",
		"currency",
		"delivery_date",
		"per_delivered",
		"per_billed",
		"status",
		"order_type",
		"name",
		"skip_delivery_note",
	],
	get_indicator: function (doc) {
		if (doc.status === "Closed") {
			// Closed
			return [__("Closed"), "green", "status,=,Closed"];
		} else if (doc.status === "On Hold") {
			// on hold
			return [__("On Hold"), "orange", "status,=,On Hold"];
		} else if (doc.status === "Completed") {
			return [__("Completed"), "green", "status,=,Completed"];
		} else if (!doc.skip_delivery_note && flt(doc.per_delivered, 2) < 100) {
			if (frappe.datetime.get_diff(doc.delivery_date) < 0) {
				// not delivered & overdue
				return [__("Overdue"), "red", "per_delivered,<,100|delivery_date,<,Today|status,!=,Closed"];
			} else if (flt(doc.grand_total) === 0) {
				// not delivered (zeroount order)
				return [__("To Deliver"), "orange", "per_delivered,<,100|grand_total,=,0|status,!=,Closed"];
			} else if (flt(doc.per_billed, 2) < 100) {
				// not delivered & not billed
				return [
					__("To Deliver and Bill"),
					"orange",
					"per_delivered,<,100|per_billed,<,100|status,!=,Closed",
				];
			} else {
				// not billed
				return [__("To Deliver"), "orange", "per_delivered,<,100|per_billed,=,100|status,!=,Closed"];
			}
		} else if (
			flt(doc.per_delivered, 2) === 100 &&
			flt(doc.grand_total) !== 0 &&
			flt(doc.per_billed, 2) < 100
		) {
			// to bill
			return [__("To Bill"), "orange", "per_delivered,=,100|per_billed,<,100|status,!=,Closed"];
		} else if (doc.skip_delivery_note && flt(doc.per_billed, 2) < 100) {
			return [__("To Bill"), "orange", "per_billed,<,100|status,!=,Closed"];
		}
	},
	onload: function (listview) {
		var method = "erpnext.selling.doctype.sales_order.sales_order.close_or_unclose_sales_orders";

		listview.page.add_menu_item(__("Close"), function () {
			listview.call_for_selected_items(method, { status: "Closed" });
		});

		listview.page.add_menu_item(__("Re-open"), function () {
			listview.call_for_selected_items(method, { status: "Submitted" });
		});

		listview.page.add_action_item(__("Sales Invoice"), () => {
			erpnext.bulk_transaction_processing.create(listview, "Sales Order", "Sales Invoice");
		});

		listview.page.add_action_item(__("Delivery Note"), () => {
			erpnext.bulk_transaction_processing.create(listview, "Sales Order", "Delivery Note");
		});

		listview.page.add_action_item(__("Advance Payment"), () => {
			erpnext.bulk_transaction_processing.create(listview, "Sales Order", "Payment Entry");
		});
	},
	button: {
		show(doc) {
			return doc.name;
		},
		get_label() {
			return __("Details", null, "Access");
		},
		get_description(doc) {
			return __("Click here to show details for {0}", [`${doc.name}`]);
		},
		action(doc) {
			let d = new frappe.ui.Dialog({
				size: "small",
				title: 'Sales Order Details',
				fields: [
					{
						label: 'Sales Order Details',
						fieldname: 'so_details',
						fieldtype: 'HTML'
					},
				],

			});
			frappe.db.get_value("Sales Order",doc.name,'order_type')
				.then(r => { 
				if(r.message.order_type){
					var html = "<table border = 1 width = 100%  style =text-align:center> <tr><th>Document Name</th><th>Order type</th></tr><tr><td>"+doc.name+"</td><td>"+r.message.order_type+"</td></tr></table>"
					d.fields_dict.so_details.$wrapper.html(html);
					d.fields_dict.sodetails.$wrapper.html(html);
				}
				
			})
			d.show();
			
		},
	},
};