# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

"""Contract (erpnext.crm) doc_events hook -- gcc_hr extends the core Contract
doctype with GCC salary-breakdown Custom Fields (fixtures/custom_field.json)
instead of introducing a parallel "GCC Employment Contract" doctype."""


def compute_total_salary(doc, method=None):
	if doc.party_type != "Employee":
		return
	doc.gcc_total_salary = (
		(doc.gcc_basic_salary or 0)
		+ (doc.gcc_housing_allowance or 0)
		+ (doc.gcc_transport_allowance or 0)
		+ (doc.gcc_other_allowances or 0)
	)
