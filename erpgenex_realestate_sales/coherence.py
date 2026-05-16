"""Cross-document checks for Erpgenex Real Estate Sales."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


def assert_linked_company(link_doctype: str, link_name: str, expected_company: str, label: str | None = None) -> None:
	if not link_name or not expected_company:
		return
	title = label or frappe.unscrub(link_doctype)
	if not frappe.db.exists(link_doctype, link_name):
		frappe.throw(_("{0} {1} does not exist.").format(title, frappe.bold(link_name)))
	lc = frappe.db.get_value(link_doctype, link_name, "company")
	if lc and lc != expected_company:
		frappe.throw(
			_("{0} {1} belongs to company {2}. Expected {3}.").format(
				title, frappe.bold(link_name), frappe.bold(lc), frappe.bold(expected_company)
			),
			title=_("Company mismatch"),
		)


def nonnegative_amount(value, label: str) -> None:
	if flt(value) < 0:
		frappe.throw(_("{0} cannot be negative.").format(label))


def check_reservation_expiry(reservation_until, status: str) -> None:
	if status != "Active" or not reservation_until:
		return
	from frappe.utils import getdate, today

	if getdate(reservation_until) < getdate(today()):
		frappe.throw(_("Active reservations cannot have a past expiry date."), title=_("Unit Reservation"))


_QUALIFIED_PLUS = frozenset({"Qualified", "Negotiation", "Won"})
_NEGOTIATION_PLUS = frozenset({"Negotiation", "Won"})


def require_lead_inventory_links(
	status: str,
	development_project: str | None,
	re_unit_inventory: str | None,
) -> None:
	if status in _QUALIFIED_PLUS and not development_project:
		frappe.throw(
			_("Development Project is required when the lead is Qualified or beyond."),
			title=_("Property Sales Lead"),
		)
	if status in _NEGOTIATION_PLUS and not re_unit_inventory:
		frappe.throw(
			_("RE Unit Inventory is required when the lead is in Negotiation or Won."),
			title=_("Property Sales Lead"),
		)
	if development_project and re_unit_inventory:
		ui_project = frappe.db.get_value("RE Unit Inventory", re_unit_inventory, "development_project")
		if ui_project and ui_project != development_project:
			frappe.throw(
				_("Unit {0} belongs to project {1}, not {2}.").format(
					frappe.bold(re_unit_inventory),
					frappe.bold(ui_project),
					frappe.bold(development_project),
				),
				title=_("Property Sales Lead"),
			)


def validate_payment_plan(rows, agreement_value: float, *, atol: float = 0.02) -> None:
	if not rows:
		return
	total = sum(flt(r.amount) for r in rows)
	if agreement_value and abs(total - flt(agreement_value)) > atol:
		frappe.throw(
			_("Payment plan total ({0}) must match agreement value ({1}).").format(
				flt(total, 2), flt(agreement_value, 2)
			),
			title=_("Sales Booking"),
		)
	seen: set[int] = set()
	for row in rows:
		if flt(row.amount) <= 0:
			frappe.throw(_("Installment amounts must be positive."), title=_("Sales Booking"))
		no = int(row.installment_no or 0)
		if no in seen:
			frappe.throw(_("Duplicate installment number {0}.").format(no), title=_("Sales Booking"))
		seen.add(no)


def optional_branch_company(branch: str, expected_company: str) -> None:
	if not branch or not expected_company:
		return
	br_co = frappe.db.get_value("Branch", branch, "company")
	if br_co and br_co != expected_company:
		frappe.throw(
			_("Branch {0} is scoped to company {1}.").format(frappe.bold(branch), frappe.bold(br_co)),
			title=_("Branch"),
		)
