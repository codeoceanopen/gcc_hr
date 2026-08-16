# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""override_doctype_dashboards entries are additive across apps -- see
frappe/model/meta.py:get_dashboard_data(), which loops every app's hook for
a given doctype and threads `data` through each in turn. Registering our own
handler for "Employee" here runs *alongside* hrms's, not instead of it."""


def get_dashboard_for_employee(data):
	data.setdefault("transactions", []).append(
		{
			"label": "GCC HR Compliance",
			"items": ["Employee Compliance Profile", "HR Compliance Document", "HR Compliance Check"],
		}
	)
	data.setdefault("non_standard_fieldnames", {})["HR Compliance Check"] = "employee"
	return data
