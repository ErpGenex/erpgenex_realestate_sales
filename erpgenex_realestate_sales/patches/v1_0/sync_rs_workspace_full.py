# Copyright (c) 2026, Omnexa
import os
import frappe
from frappe.modules.import_file import import_file_by_path

def _ensure_pages():
	p = frappe.get_app_path("erpgenex_realestate_sales", "erpgenex_realestate_sales", "page")
	if not os.path.isdir(p):
		return
	for folder in os.listdir(p):
		jp = os.path.join(p, folder, f"{folder}.json")
		if os.path.isfile(jp):
			import_file_by_path(jp, force=True)

def execute():
	_ensure_pages()
	if frappe.db.exists("Workspace", "RE Marketing"):
		from erpgenex_realestate_sales.workspace.rs_workspace import sync_rs_workspace_menu
		sync_rs_workspace_menu(save=True, rebuild=True)
