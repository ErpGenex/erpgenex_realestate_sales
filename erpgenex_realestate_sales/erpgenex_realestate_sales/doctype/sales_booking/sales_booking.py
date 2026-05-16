import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from erpgenex_realestate_sales.coherence import assert_linked_company, nonnegative_amount, validate_payment_plan
from erpgenex_realestate_sales.accounting import create_sales_invoice_from_booking
from erpgenex_realestate_sales.erpgenex_realestate_sales.doctype.sales_commission_schedule.sales_commission_schedule import (
	compute_commission,
)

_OPEN_PIPELINE = frozenset({"Approved", "Registered"})
_TERMINAL = "Registered"


class SalesBooking(Document):
	def validate(self):
		assert_linked_company("RE Unit Inventory", self.re_unit_inventory, self.company, None)
		self._validate_linked_reservation()
		self._guard_registered_immutability()
		self._reject_parallel_pipeline_bookings()
		self._reject_bad_inventory_transition()
		if self.agreement_value is not None:
			nonnegative_amount(self.agreement_value, _("Agreement Value"))
		if self.commission_schedule:
			cs_co = frappe.db.get_value("Sales Commission Schedule", self.commission_schedule, "company")
			if cs_co and cs_co != self.company:
				frappe.throw(_("Commission schedule belongs to another company."), title=_("Sales Booking"))
			self.commission_amount = compute_commission(self.commission_schedule, flt(self.agreement_value))
		else:
			self.commission_amount = 0
		self.payment_plan_total = sum(flt(r.amount) for r in (self.payment_plan or []))
		validate_payment_plan(self.payment_plan or [], flt(self.agreement_value))
		if self.status == "Registered" and self.signature_status != "Signed":
			frappe.msgprint(
				_("Signature status is not Signed — confirm SPA before revenue recognition."),
				indicator="orange",
				alert=True,
			)

	def _validate_linked_reservation(self):
		rkey = getattr(self, "unit_reservation", None)
		if not rkey:
			return
		fields = frappe.db.get_value(
			"Unit Reservation",
			rkey,
			["company", "re_unit_inventory", "customer", "status"],
			as_dict=True,
		)
		if not fields:
			frappe.throw(_("Unit Reservation does not exist."), title=_("Sales Booking"))

		if fields.company != self.company:
			frappe.throw(_("Reservation belongs to another company."), title=_("Sales Booking"))

		if fields.re_unit_inventory != self.re_unit_inventory:
			frappe.throw(_("Reservation refers to another unit."), title=_("Sales Booking"))

		rc = getattr(self, "customer", None)
		if rc and fields.customer and fields.customer != rc:
			frappe.throw(_("Customer differs from linked reservation."), title=_("Sales Booking"))

	def _guard_registered_immutability(self):
		if self.is_new():
			return
		prev = frappe.db.get_value("Sales Booking", self.name, "status")
		if prev != _TERMINAL:
			return
		if self.status != _TERMINAL:
			frappe.throw(_("A registered booking cannot change status."), title=_("Sales Booking"))

		prev_unit = frappe.db.get_value("Sales Booking", self.name, "re_unit_inventory")
		if prev_unit != self.re_unit_inventory:
			frappe.throw(_("Cannot re-point a registered booking to another unit."), title=_("Sales Booking"))

	def _reject_parallel_pipeline_bookings(self):
		if self.status not in _OPEN_PIPELINE:
			return
		filters: dict = {
			"re_unit_inventory": self.re_unit_inventory,
			"status": ["in", list(_OPEN_PIPELINE)],
		}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Sales Booking", filters):
			frappe.throw(
				_("Another approved or registered booking already exists for this unit."),
				title=_("Sales Booking"),
			)

	def _reject_bad_inventory_transition(self):
		if self.status not in _OPEN_PIPELINE:
			return
		stat = frappe.db.get_value("RE Unit Inventory", self.re_unit_inventory, "status")
		if stat in {"Sold", "Handed Over"}:
			frappe.throw(
				_("This unit inventory is already {0}.").format(stat.lower()),
				title=_("Sales Booking"),
			)

	def on_update(self):
		if self.status == _TERMINAL and not self.sales_invoice:
			try:
				create_sales_invoice_from_booking(self.name)
			except Exception:
				frappe.log_error(title=f"Sales Booking invoice: {self.name}")
		if self.status == "Approved":
			self._set_inventory("Reserved")
		elif self.status == _TERMINAL:
			self._set_inventory("Sold")
		elif self.status == "Cancelled":
			active_res = frappe.db.exists(
				"Unit Reservation",
				{"re_unit_inventory": self.re_unit_inventory, "status": "Active"},
			)
			self._set_inventory("Held" if active_res else "Available")

	def _set_inventory(self, status: str) -> None:
		frappe.db.set_value(
			"RE Unit Inventory",
			self.re_unit_inventory,
			"status",
			status,
			update_modified=False,
		)
