# Copyright (c) 2026, Omnexa
import json, frappe
from frappe.tests.utils import FrappeTestCase
from erpgenex_realestate_sales.rs_gap_register import GLOBAL_LEADER_TARGET, get_gap_status
from erpgenex_realestate_sales.rs_global_benchmark import get_global_rs_score
from erpgenex_realestate_sales.workspace.rs_workspace import sync_rs_workspace_menu

class TestRsGlobalBenchmark(FrappeTestCase):
	def test_global_score(self):
		s = get_global_rs_score()
		self.assertGreaterEqual(s["weighted_score"], GLOBAL_LEADER_TARGET)
		self.assertTrue(s.get("global_leader_gate"))
	def test_gaps_closed(self):
		self.assertTrue(get_gap_status()["global_leader_gate"])
	def test_workspace_sync(self):
		stats = sync_rs_workspace_menu(save=True, rebuild=True)
		self.assertGreater(stats["total_links"], 10)
		ws = frappe.get_doc("Workspace", "RE Marketing")
		self.assertGreater(len(ws.shortcuts), 5)
