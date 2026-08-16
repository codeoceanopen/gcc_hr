# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GOSISettings(Document):
	def validate(self):
		if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
			frappe.throw(_("Effective To cannot be before Effective From."))


def get_applicable_settings(category: str, on_date) -> "GOSISettings | None":
	"""Effective-dated lookup: the row for this category whose effective_from
	is the latest one on/before `on_date` and (if set) effective_to is on/
	after it."""
	on_date = frappe.utils.getdate(on_date)
	rows = frappe.get_all(
		"GOSI Settings",
		filters={"applicable_employee_category": category, "effective_from": ["<=", on_date]},
		fields=["name", "effective_from", "effective_to"],
		order_by="effective_from desc",
	)
	for row in rows:
		if not row.effective_to or frappe.utils.getdate(row.effective_to) >= on_date:
			return frappe.get_doc("GOSI Settings", row.name)
	return None
