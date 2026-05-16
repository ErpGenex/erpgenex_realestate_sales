# Copyright (c) 2026, ErpGenEx
# License: MIT

from __future__ import annotations

import frappe
from frappe.utils import getdate, today


def expire_unit_reservations() -> int:
	"""Mark Active reservations past reservation_until as Expired and release inventory."""
	expiry = getdate(today())
	names = frappe.get_all(
		"Unit Reservation",
		filters={"status": "Active", "reservation_until": ["<", expiry]},
		pluck="name",
	)
	count = 0
	for name in names:
		doc = frappe.get_doc("Unit Reservation", name)
		if doc.status != "Active":
			continue
		doc.status = "Expired"
		doc.save(ignore_permissions=True)
		count += 1
	if count:
		frappe.logger("erpgenex_realestate_sales").info("Expired %s unit reservation(s)", count)
	return count
