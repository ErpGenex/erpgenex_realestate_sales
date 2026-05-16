# Copyright (c) 2026, ErpGenEx
# License: MIT

"""Sales Booking → omnexa_accounting Sales Invoice (GAP-SLS-07)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate, today


def posting_reference(booking_name: str) -> str:
	return f"Sales Booking:{booking_name}"


def _default_branch(company: str) -> str:
	branch = frappe.db.get_value("Branch", {"company": company}, "name")
	if not branch:
		frappe.throw(_("No Branch found for company {0}.").format(company), title=_("Sales Booking"))
	return branch


def _resolve_sales_item(company: str) -> str:
	"""Prefer service Item; site may customize via Property Setter later."""
	for filters in (
		{"is_stock_item": 0, "disabled": 0},
		{"disabled": 0},
	):
		name = frappe.db.get_value("Item", filters, "name", order_by="modified desc")
		if name:
			return name
	frappe.throw(
		_("No Item found to post real-estate sales revenue. Create a service Item first."),
		title=_("Sales Booking"),
	)


def create_sales_invoice_from_booking(booking_name: str, *, submit: bool = True) -> str:
	"""Idempotent SI creation for Registered bookings."""
	if not frappe.db.exists("DocType", "Sales Invoice"):
		frappe.throw(_("Install omnexa_accounting before posting sales invoices."))

	booking = frappe.get_doc("Sales Booking", booking_name)
	if booking.sales_invoice and frappe.db.exists("Sales Invoice", booking.sales_invoice):
		return booking.sales_invoice

	if booking.status != "Registered":
		frappe.throw(_("Only Registered bookings can be invoiced."), title=_("Sales Booking"))
	if not booking.customer:
		frappe.throw(_("Customer is required to create a Sales Invoice."), title=_("Sales Booking"))

	ref = posting_reference(booking.name)
	existing = frappe.db.get_value("Sales Invoice", {"company": booking.company, "reference": ref}, "name")
	if existing:
		booking.db_set("sales_invoice", existing, update_modified=False)
		return existing

	item = _resolve_sales_item(booking.company)
	branch = _default_branch(booking.company)
	amount = flt(booking.agreement_value)
	if amount <= 0:
		frappe.throw(_("Agreement Value must be positive to invoice."), title=_("Sales Booking"))

	si = frappe.new_doc("Sales Invoice")
	si.company = booking.company
	si.branch = branch
	si.customer = booking.customer
	si.posting_date = getdate(booking.booking_date or today())
	si.currency = frappe.db.get_value("Company", booking.company, "default_currency") or "EGP"
	si.reference = ref
	if si.meta.has_field("external_reference"):
		si.external_reference = booking.name
	si.append("items", {"item": item, "qty": 1, "rate": amount, "description": booking.re_unit_inventory})
	si.insert(ignore_permissions=True)
	if submit:
		si.submit()
	booking.db_set("sales_invoice", si.name, update_modified=False)
	return si.name


def create_invoices_for_payment_plan(booking_name: str) -> list[str]:
	"""One Sales Invoice per pending installment line."""
	if not frappe.db.exists("DocType", "Sales Invoice"):
		frappe.throw(_("Install omnexa_accounting before posting sales invoices."))

	booking = frappe.get_doc("Sales Booking", booking_name)
	if booking.status != "Registered":
		frappe.throw(_("Booking must be Registered."), title=_("Sales Booking"))
	if not booking.customer:
		frappe.throw(_("Customer is required."), title=_("Sales Booking"))

	item = _resolve_sales_item(booking.company)
	branch = _default_branch(booking.company)
	currency = frappe.db.get_value("Company", booking.company, "default_currency") or "EGP"
	created: list[str] = []

	for row in booking.payment_plan or []:
		if row.status in ("Paid", "Cancelled", "Invoiced"):
			continue
		ref = f"{posting_reference(booking.name)}:{row.installment_no}"
		existing = frappe.db.get_value("Sales Invoice", {"company": booking.company, "reference": ref}, "name")
		if existing:
			created.append(existing)
			continue
		si = frappe.new_doc("Sales Invoice")
		si.company = booking.company
		si.branch = branch
		si.customer = booking.customer
		si.posting_date = row.due_date or getdate(booking.booking_date or today())
		si.currency = currency
		si.reference = ref
		si.append(
			"items",
			{
				"item": item,
				"qty": 1,
				"rate": flt(row.amount),
				"description": f"{booking.re_unit_inventory} inst {row.installment_no}",
			},
		)
		si.insert(ignore_permissions=True)
		si.submit()
		row.status = "Invoiced"
		created.append(si.name)

	booking.save(ignore_permissions=True)
	return created
