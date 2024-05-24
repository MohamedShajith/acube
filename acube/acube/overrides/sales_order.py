import frappe
from frappe import _, msgprint, qb
from frappe.utils import flt, fmt_money

@frappe.whitelist()
def stock_popup(name):
	doc = frappe.get_doc("Sales Order",name)
	company = doc.company
	item_details = doc.items
	data = ''
	data += '<table class="table table-bordered" style = font-size:10px><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:orange" colspan=6><center>Sales Order Details</center></th></tr>'
	data += '''<tr><td style="padding:1px;border: 1px solid black;text-align:center" colspan=3><b>Document Name</b></td><td style="padding:1px;border: 1px solid black;text-align:center" colspan=3><b>Order Type</b></td></tr>
				<tr><td style="padding:1px;border: 1px solid black;text-align:center" colspan=3>%s</td><td style="padding:1px;border: 1px solid black;text-align:center" colspan=3>%s</td></tr>'''%(doc.name,doc.order_type)
	data += '<h4><center><b>STOCK DETAILS</b></center></h4>'
	data += '<table class="table table-bordered" style = font-size:10px>'
	data += '<td colspan=1 style="width:20%;padding:1px;border:1px solid black;background-color:orange;color:white;"><center><b>ITEM CODE</b></center></td>'
	data += '<td colspan=1 style="width:40%;padding:1px;border:1px solid black;background-color:orange;color:white;"><center><b>ITEM NAME</b></center></td>'
	data += '<td colspan=1 style="width:15%;padding:1px;border:1px solid black;background-color:orange;color:white;"><center><b>STOCK</b></center></td>'	
	data += '<td colspan=1 style="width:15%;padding:1px;border:1px solid black;background-color:orange;color:white;"><center><b>TO RECEIVE</b></center></td>'
	data += '<td colspan=1 style="width:15%;padding:1px;border:1px solid black;background-color:orange;color:white;"><center><b>TO SELL</b></center></td>'
	for j in item_details:
		country = frappe.get_value("Company",{"name":company},["country"])
		warehouse_stock = frappe.db.sql("""
		select sum(b.actual_qty) as qty from `tabBin` b join `tabWarehouse` wh on wh.name = b.warehouse join `tabCompany` c on c.name = wh.company where c.country = '%s' and b.item_code = '%s'
		""" % (country,j.item_code),as_dict=True)[0]

		if not warehouse_stock["qty"]:
			warehouse_stock["qty"] = 0		
		new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order` 
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 and `tabPurchase Order`.status != 'Closed' """ % (j.item_code), as_dict=True)[0]
		if not new_po['qty']:
			new_po['qty'] = 0
		if not new_po['d_qty']:
			new_po['d_qty'] = 0
		in_transit = new_po['qty'] - new_po['d_qty']
		pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,sum(`tabPurchase Order Item`.qty) as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by rate asc limit 1""" % (j.item_code), as_dict=True)
	
		new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
		left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
		where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1 and `tabSales Order`.status != "Closed" """ % (j.item_code), as_dict=True)[0]
		if not new_so['qty']:
			new_so['qty'] = 0
		if not new_so['d_qty']:
			new_so['d_qty'] = 0
		del_total = new_so['qty'] - new_so['d_qty']
		i = 0
		for po in pos:
			data += '<tr>'
			data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (j.item_code)
			data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (j.item_name)
			data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (warehouse_stock['qty'] or 0)
			data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(in_transit or 0)
			data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(del_total or 0)
			data += '</tr>'
		i += 1
	data += '</tr>'
	data += '</table>'
	return data