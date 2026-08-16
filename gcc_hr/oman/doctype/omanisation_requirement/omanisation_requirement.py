# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


class OmanisationRequirement(Document):
	def validate(self):
		if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
			frappe.throw(_("Effective To cannot be before Effective From."))
		# company is genuinely optional here -- blank means a global fallback
		# rule (matched by activity/business_size, or the ultimate fallback).
		if self.company:
			enforce_company_country(self.company, "Oman")
