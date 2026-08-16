# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class HRComplianceRule(Document):
	def validate(self):
		if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
			frappe.throw(_("Effective To cannot be before Effective From."))
		self.validate_check_method()

	def validate_check_method(self):
		try:
			method = frappe.get_attr(self.check_method)
		except Exception:
			frappe.throw(_("Check Method {0} could not be imported.").format(frappe.bold(self.check_method)))
		if not callable(method):
			frappe.throw(_("Check Method {0} is not callable.").format(frappe.bold(self.check_method)))
