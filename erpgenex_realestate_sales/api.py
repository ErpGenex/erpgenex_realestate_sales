"""Integration API contracts for **`erpgenex_realestate_sales`** ↔ **`omnexa_accounting`**.

Implement revenue recognition, tax, and instalment schedules per CFO policy.
See: ``Docs/2026-05-15/integration/realestate_sales_omnexa_accounting_contract.md``
"""

from __future__ import annotations

import frappe


@frappe.whitelist()
def post_sales_invoice_for_booking(booking_name: str) -> dict[str, str]:
	"""Create/submit Sales Invoice for a Registered booking (GAP-SLS-07)."""
	frappe.has_permission("Sales Booking", "write", doc=booking_name, throw=True)
	from erpgenex_realestate_sales.accounting import create_sales_invoice_from_booking

	si = create_sales_invoice_from_booking(booking_name)
	return {"sales_invoice": si, "booking": booking_name}


@frappe.whitelist()
def describe_sales_accounting_integration() -> dict[str, str]:
	"""Document-only: returns pointers for finance teams wiring Sales Booking → AR."""
	return {
		"contract_doc": "Docs/2026-05-15/integration/realestate_sales_omnexa_accounting_contract.md",
		"booking_doctype": "Sales Booking",
		"target_posting": "omnexa_accounting Sales Invoice (site-specific Item & tax mapping required)",
	}


@frappe.whitelist()
def preview_sales_commission(sale_value: float, rate_percent: float = 2.5) -> dict:
	from erpgenex_realestate_sales.re_sales_parity import preview_sales_commission as _preview

	return _preview(sale_value, rate_percent)
