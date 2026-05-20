# Copyright (c) 2026, ErpGenEx
from frappe.utils import flt


def preview_sales_commission(sale_value: float, rate_percent: float = 2.5) -> dict:
	value = flt(sale_value)
	rate = flt(rate_percent) / 100.0
	commission = flt(value * rate, 2)
	return {
		"sale_value": value,
		"rate_percent": flt(rate_percent),
		"commission_amount": commission,
		"net_to_developer": flt(value - commission, 2),
		"sap_module": "RE-SD",
	}
