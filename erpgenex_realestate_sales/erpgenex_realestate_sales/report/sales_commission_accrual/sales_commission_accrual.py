from __future__ import annotations

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	params = {"company": filters.company}
	clause = ""
	if filters.get("from_date"):
		clause += " AND sb.booking_date >= %(from_date)s"
		params["from_date"] = filters.from_date
	if filters.get("to_date"):
		clause += " AND sb.booking_date <= %(to_date)s"
		params["to_date"] = filters.to_date

	rows = frappe.db.sql(
		f"""
		SELECT
			sb.name AS sales_booking,
			sb.customer,
			sb.broker,
			sb.commission_schedule,
			sb.agreement_value,
			sb.commission_amount,
			sb.status
		FROM `tabSales Booking` sb
		WHERE sb.company = %(company)s
		  AND IFNULL(sb.commission_amount, 0) > 0
		  {clause}
		ORDER BY sb.modified DESC
		""",
		params,
		as_dict=True,
	)
	columns = [
		{"label": _("Booking"), "fieldname": "sales_booking", "fieldtype": "Link", "options": "Sales Booking", "width": 120},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120},
		{"label": _("Broker"), "fieldname": "broker", "fieldtype": "Link", "options": "Supplier", "width": 110},
		{"label": _("Schedule"), "fieldname": "commission_schedule", "fieldtype": "Link", "options": "Sales Commission Schedule", "width": 130},
		{"label": _("Agreement"), "fieldname": "agreement_value", "fieldtype": "Currency", "width": 110},
		{"label": _("Commission"), "fieldname": "commission_amount", "fieldtype": "Currency", "width": 110},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
	]
	chart = auto_chart_for_columns(rows, columns)
	return columns, rows, None, chart