import frappe
from frappe import _, msgprint, qb

def validate_budget(doc,method):
	comp_settings = frappe.db.get_values("Company",{"name":doc.company},fieldname=["po_budget_validation","maximum_limit"],as_dict=True)[0]
	if comp_settings['po_budget_validation'] == "Yes" and doc.grand_total > comp_settings['maximum_limit']:
		message = _("Grand Total exceeds the maximum permitted limit <b>{0}</b>").format(comp_settings['maximum_limit'])
		frappe.msgprint(
				message,
				title=_("Limit Reached"),
				raise_exception=1
			)