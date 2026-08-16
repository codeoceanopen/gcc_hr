# Copyright (c) 2026, GCC HR Compliance and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from gcc_hr.gcc_hr_core.doctype.gcc_hr_company_settings.gcc_hr_company_settings import (
	enforce_company_country,
)


class QatarizationRequirement(Document):
	def validate(self):
		# company is genuinely optional here -- blank means a global fallback
		# rule (matched by activity/business_size, or the ultimate fallback).
		if self.company:
			enforce_company_country(self.company, "Qatar")
