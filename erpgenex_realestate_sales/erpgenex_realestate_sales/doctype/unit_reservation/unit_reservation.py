import frappe
from frappe import _
from frappe.model.document import Document

from erpgenex_realestate_sales.coherence import assert_linked_company, check_reservation_expiry, nonnegative_amount


class UnitReservation(Document):
	def validate(self):
		assert_linked_company("RE Unit Inventory", self.re_unit_inventory, self.company, None)
		check_reservation_expiry(self.reservation_until, self.status)
		if self.earnest_amount is not None:
			nonnegative_amount(self.earnest_amount, _("Earnest / Deposit"))

		ui_status = frappe.db.get_value("RE Unit Inventory", self.re_unit_inventory, "status")

		if self.status == "Active":
			if ui_status in {"Sold", "Handed Over"}:
				frappe.throw(
					_("Cannot keep an Active reservation against a Sold or handed-over inventory record."),
					title=_("Unit Reservation"),
				)
			conflict_filters = reservation_filters_active(self.re_unit_inventory, exclude_name=self.name)
			if frappe.db.exists("Unit Reservation", conflict_filters):
				frappe.throw(
					_("Another active reservation already exists for this unit."),
					title=_("Unit Reservation"),
				)

	def on_update(self):
		if self.status == "Converted":
			return

		if self.status == "Active":
			frappe.db.set_value(
				"RE Unit Inventory",
				self.re_unit_inventory,
				"status",
				"Held",
				update_modified=False,
			)
			return

		if self.status not in {"Expired", "Cancelled", "Draft"}:
			return

		curr = frappe.db.get_value("RE Unit Inventory", self.re_unit_inventory, "status")
		if curr != "Held":
			return

		active_booking = frappe.db.exists(
			"Sales Booking",
			booking_filters_open(self.re_unit_inventory),
		)
		frappe.db.set_value(
			"RE Unit Inventory",
			self.re_unit_inventory,
			"status",
			"Reserved" if active_booking else "Available",
			update_modified=False,
		)


def reservation_filters_active(unit: str, exclude_name: str | None = None) -> dict:
	out: dict = {"re_unit_inventory": unit, "status": "Active"}
	if exclude_name:
		out["name"] = ["!=", exclude_name]
	return out


def booking_filters_open(unit: str) -> dict:
	return {"re_unit_inventory": unit, "status": ["in", ["Approved", "Registered"]]}
