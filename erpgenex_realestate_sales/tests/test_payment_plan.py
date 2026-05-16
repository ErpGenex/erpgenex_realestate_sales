# Copyright (c) 2026, ErpGenEx

import frappe
from frappe.tests.utils import FrappeTestCase

from erpgenex_realestate_sales.coherence import validate_payment_plan


class TestPaymentPlan(FrappeTestCase):
	def test_plan_must_match_agreement(self):
		row = frappe._dict(installment_no=1, amount=50000)
		self.assertRaises(frappe.ValidationError, validate_payment_plan, [row], 100000)
