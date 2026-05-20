# Copyright (c) 2026, ErpGenEx
import frappe
from frappe.tests.utils import FrappeTestCase


class TestSapParityReSales(FrappeTestCase):
	def test_reservation_doctype_exists(self):
		self.assertTrue(frappe.db.exists("DocType", "Unit Reservation"))
		self.assertTrue(frappe.db.exists("DocType", "Sales Booking"))
