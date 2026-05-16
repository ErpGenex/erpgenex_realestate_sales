from __future__ import annotations

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	params: dict = {"company": filters.company}
	where = "company = %(company)s AND IFNULL(campaign, '') != ''"
	if filters.get("from_date"):
		where += " AND DATE(creation) >= %(from_date)s"
		params["from_date"] = filters.from_date
	if filters.get("to_date"):
		where += " AND DATE(creation) <= %(to_date)s"
		params["to_date"] = filters.to_date

	rows = frappe.db.sql(
		f"""
		SELECT
			campaign,
			COUNT(*) AS leads,
			SUM(CASE WHEN status = 'Won' THEN 1 ELSE 0 END) AS won,
			SUM(CASE WHEN status = 'Lost' THEN 1 ELSE 0 END) AS lost,
			SUM(CASE WHEN status IN ('Qualified', 'Negotiation') THEN 1 ELSE 0 END) AS pipeline
		FROM `tabProperty Sales Lead`
		WHERE {where}
		GROUP BY campaign
		ORDER BY leads DESC
		""",
		params,
		as_dict=True,
	)
	for r in rows:
		r["conversion_percent"] = round(100.0 * (r.won or 0) / max(1, r.leads), 2)

	columns = [
		{"label": _("Campaign"), "fieldname": "campaign", "fieldtype": "Data", "width": 160},
		{"label": _("Leads"), "fieldname": "leads", "fieldtype": "Int", "width": 80},
		{"label": _("Won"), "fieldname": "won", "fieldtype": "Int", "width": 70},
		{"label": _("Lost"), "fieldname": "lost", "fieldtype": "Int", "width": 70},
		{"label": _("Pipeline"), "fieldname": "pipeline", "fieldtype": "Int", "width": 90},
		{"label": _("Conversion %"), "fieldname": "conversion_percent", "fieldtype": "Percent", "width": 110},
	]
	return columns, rows
