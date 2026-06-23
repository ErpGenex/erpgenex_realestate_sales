frappe.pages["realestate-sales-analytics-dashboard"].on_page_load = function (wrapper) {
	if (window.omnexa_core && omnexa_core.vertical_portal && omnexa_core.vertical_portal.mountRoleDesk) {
		omnexa_core.vertical_portal.mountRoleDesk(wrapper, "erpgenex_realestate_sales", "analytics-dashboard");
		return;
	}
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("realestate-sales-analytics-dashboard"),
		single_column: true,
	});
	$(page.body).html("<p class=\"text-muted\">" + __("Load omnexa_core vertical portal desk") + "</p>");
};
