import frappe
from frappe import _
from frappe.model.document import Document

from erpgenex_realestate_sales.coherence import (
	assert_linked_company,
	optional_branch_company,
	require_lead_inventory_links,
)

_TERMINAL_LEAD = frozenset({"Won", "Lost"})


class PropertySalesLead(Document):
	def validate(self):
		optional_branch_company(self.branch, self.company)
		require_lead_inventory_links(self.status, self.development_project, self.re_unit_inventory)
		if self.development_project:
			assert_linked_company(
				"Development Project", self.development_project, self.company, _("Development Project")
			)
		if self.re_unit_inventory:
			assert_linked_company("RE Unit Inventory", self.re_unit_inventory, self.company, None)
		if self.status == "Won" and not self.customer:
			frappe.throw(_("Link a Customer before marking the lead as Won."), title=_("Property Sales Lead"))
		if not self.is_new() and self.status in _TERMINAL_LEAD:
			prev = frappe.db.get_value("Property Sales Lead", self.name, "status")
			if prev in _TERMINAL_LEAD and prev != self.status:
				frappe.throw(_("A closed lead cannot change status."), title=_("Property Sales Lead"))
