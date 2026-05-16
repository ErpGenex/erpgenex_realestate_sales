# Copyright (c) 2026, ErpGenEx

from frappe.tests.utils import FrappeTestCase

from erpgenex_realestate_sales.accounting import posting_reference


class TestSalesAccounting(FrappeTestCase):
	def test_posting_reference_format(self):
		self.assertEqual(posting_reference("SBK-0001"), "Sales Booking:SBK-0001")
