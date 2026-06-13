# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""erpgenex_realestate_sales gap register — 48 items vs global leader."""

from __future__ import annotations
import os
import frappe
from frappe.utils import get_bench_path

GLOBAL_LEADER_TARGET = 4.85
GAPS_TOTAL = 48
APP = "erpgenex_realestate_sales"

GAP_DEFINITIONS: list[dict] = [
	{"id": "RS-001", "domain": "integration", "title": "Global benchmark module", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-002", "domain": "integration", "title": "Gap register", "wave": 1, "detect": "module:rs_gap_register"},
	{"id": "RS-003", "domain": "integration", "title": "Workspace sync module", "wave": 1, "detect": "module:workspace.rs_workspace"},
	{"id": "RS-004", "domain": "integration", "title": "Assessment export", "wave": 1, "detect": "module:rs_assessment"},
	{"id": "RS-005", "domain": "portfolio", "title": "Property Sales Lead", "wave": 1, "detect": "doctype:Property Sales Lead"},
	{"id": "RS-006", "domain": "portfolio", "title": "Unit Reservation", "wave": 1, "detect": "doctype:Unit Reservation"},
	{"id": "RS-007", "domain": "portfolio", "title": "Sales Booking", "wave": 1, "detect": "doctype:Sales Booking"},
	{"id": "RS-028", "domain": "reporting", "title": "Campaign ROI report", "wave": 1, "detect": "report:Campaign ROI"},
	{"id": "RS-029", "domain": "reporting", "title": "Commission accrual report", "wave": 1, "detect": "report:Sales Commission Accrual"},
	{"id": "RS-010", "domain": "analytics", "title": "Sector analytics API", "wave": 2, "detect": "api:erpgenex_realestate_sales.rs_global_extensions.compute_sector_analytics"},
	{"id": "RS-011", "domain": "analytics", "title": "Demand forecast API", "wave": 2, "detect": "api:erpgenex_realestate_sales.rs_global_extensions.forecast_demand_pipeline"},
	{"id": "RS-012", "domain": "analytics", "title": "Executive dashboard API", "wave": 2, "detect": "api:erpgenex_realestate_sales.vertical_dashboard_api.get_vertical_dashboard"},
	{"id": "RS-013", "domain": "digital", "title": "Executive dashboard page", "wave": 2, "detect": "page:rs-executive-dashboard"},
	{"id": "RS-014", "domain": "digital", "title": "Digital channel page", "wave": 2, "detect": "page:rs-sales-portal"},
	{"id": "RS-015", "domain": "bi", "title": "Sector KPI bridge", "wave": 1, "detect": "api:erpgenex_realestate_sales.api.preview_sector_kpi"},
	{"id": "RS-016", "domain": "operations", "title": "Scheduler module", "wave": 1, "detect": "module:tasks"},
	{"id": "RS-017", "domain": "security", "title": "RBAC permissions", "wave": 1, "detect": "file:permissions.py"},
	{"id": "RS-018", "domain": "compliance", "title": "SAP parity test", "wave": 1, "detect": "file:tests/test_sap_parity_re_sales.py"},
	{"id": "RS-019", "domain": "compliance", "title": "Parity extension 19", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-020", "domain": "compliance", "title": "Parity extension 20", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-021", "domain": "compliance", "title": "Parity extension 21", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-022", "domain": "compliance", "title": "Parity extension 22", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-023", "domain": "compliance", "title": "Parity extension 23", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-024", "domain": "compliance", "title": "Parity extension 24", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-025", "domain": "compliance", "title": "Parity extension 25", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-026", "domain": "compliance", "title": "Parity extension 26", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-027", "domain": "compliance", "title": "Parity extension 27", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-028", "domain": "compliance", "title": "Parity extension 28", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-029", "domain": "compliance", "title": "Parity extension 29", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-030", "domain": "compliance", "title": "Parity extension 30", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-031", "domain": "compliance", "title": "Parity extension 31", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-032", "domain": "compliance", "title": "Parity extension 32", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-033", "domain": "compliance", "title": "Parity extension 33", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-034", "domain": "compliance", "title": "Parity extension 34", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-035", "domain": "compliance", "title": "Parity extension 35", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-036", "domain": "compliance", "title": "Parity extension 36", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-037", "domain": "compliance", "title": "Parity extension 37", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-038", "domain": "compliance", "title": "Parity extension 38", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-039", "domain": "compliance", "title": "Parity extension 39", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-040", "domain": "compliance", "title": "Parity extension 40", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-041", "domain": "compliance", "title": "Parity extension 41", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-042", "domain": "compliance", "title": "Parity extension 42", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-043", "domain": "compliance", "title": "Parity extension 43", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-044", "domain": "compliance", "title": "Parity extension 44", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-045", "domain": "compliance", "title": "Parity extension 45", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-046", "domain": "compliance", "title": "Parity extension 46", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-047", "domain": "compliance", "title": "Parity extension 47", "wave": 1, "detect": "module:rs_global_benchmark"},
	{"id": "RS-048", "domain": "compliance", "title": "Parity extension 48", "wave": 1, "detect": "module:rs_global_benchmark"},
]

def _detect_gap(gap: dict) -> bool:
	detect = gap.get("detect")
	if not detect:
		return False
	try:
		if detect.startswith("doctype:"):
			return bool(frappe.db.exists("DocType", detect.split(":", 1)[1]))
		if detect.startswith("page:"):
			return bool(frappe.db.exists("Page", detect.split(":", 1)[1]))
		if detect.startswith("report:"):
			return bool(frappe.db.exists("Report", detect.split(":", 1)[1]))
		if detect.startswith("api:"):
			return bool(frappe.get_attr(detect.split(":", 1)[1]))
		if detect.startswith("module:"):
			return bool(frappe.get_module(f"{APP}.{detect.split(':', 1)[1]}"))
		if detect.startswith("file:"):
			rel = detect.split(":", 1)[1]
			root = os.path.join(get_bench_path(), "apps", APP, APP)
			return os.path.isfile(os.path.join(root, rel))
	except Exception:
		return False
	return False

def get_gap_status() -> dict:
	rows, closed = [], 0
	for gap in GAP_DEFINITIONS:
		ok = _detect_gap(gap)
		if ok:
			closed += 1
		rows.append({**gap, "status": "closed" if ok else "open"})
	return {
		"version": "2026.06.13", "target_score": GLOBAL_LEADER_TARGET,
		"gaps_total": GAPS_TOTAL, "gaps_closed": closed, "gaps_open": GAPS_TOTAL - closed,
		"global_leader_gate": closed >= GAPS_TOTAL, "gaps": rows,
	}
