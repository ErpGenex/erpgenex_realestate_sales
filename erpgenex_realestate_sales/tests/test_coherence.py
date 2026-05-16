# Copyright (c) 2026, ErpGenEx
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from erpgenex_realestate_sales.coherence import check_reservation_expiry, require_lead_inventory_links
from erpgenex_realestate_sales.tasks import expire_unit_reservations


class TestRealestateSalesCoherence(FrappeTestCase):
	def test_require_lead_links_qualified(self):
		self.assertRaises(frappe.ValidationError, require_lead_inventory_links, "Qualified", None, None)

	def test_reservation_expiry_blocks_active_past_date(self):
		self.assertRaises(
			frappe.ValidationError,
			check_reservation_expiry,
			add_days(today(), -1),
			"Active",
		)

	def test_expire_unit_reservations_noop_without_data(self):
		self.assertEqual(expire_unit_reservations(), 0)
