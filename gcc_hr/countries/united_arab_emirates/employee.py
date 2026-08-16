# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""UAE-specific employee identity. Dispatched generically from
gcc_hr_core/doctype/employee_compliance_profile/employee_compliance_profile.py
via gcc_hr.countries.get_country_attr(country, "employee", "sync_employee") --
this module is never imported directly by core. Mirrors
countries/saudi_arabia/employee.py and countries/qatar/employee.py."""

import frappe


def sync_employee(employee_doc):
	if frappe.db.exists("UAE Employee Profile", employee_doc.name):
		return
	frappe.get_doc(
		{
			"doctype": "UAE Employee Profile",
			"employee": employee_doc.name,
		}
	).insert(ignore_permissions=True)
