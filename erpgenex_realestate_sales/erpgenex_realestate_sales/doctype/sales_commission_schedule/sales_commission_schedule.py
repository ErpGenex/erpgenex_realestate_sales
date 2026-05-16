# Copyright (c) 2026, ErpGenEx

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class SalesCommissionSchedule(Document):
	def validate(self):
		if self.commission_type == "Percent of Agreement" and flt(self.rate_percent) < 0:
			frappe.throw(_("Rate % cannot be negative."))
		if self.commission_type == "Fixed Amount" and flt(self.fixed_amount) < 0:
			frappe.throw(_("Fixed amount cannot be negative."))


def compute_commission(schedule_name: str, agreement_value: float) -> float:
	row = frappe.db.get_value(
		"Sales Commission Schedule",
		schedule_name,
		["commission_type", "rate_percent", "fixed_amount"],
		as_dict=True,
	)
	if not row:
		return 0.0
	if row.commission_type == "Fixed Amount":
		return flt(row.fixed_amount)
	return flt(agreement_value) * flt(row.rate_percent) / 100.0
